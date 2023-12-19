import os
import json
import time
import shutil
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from datetime import datetime

from py_ewr.observed_handling import ObservedHandler
from py_ewr.scenario_handling import ScenarioHandler

import pandas as pd


######################################################
## App initialisation
######################################################



# initialize Flask app with the name of the file
app = Flask(__name__)

PARENT_FOLDER = os.environ.get("PARENT_FOLDER") or app.instance_path
UPLOAD_FOLDER = os.path.join(PARENT_FOLDER, "app_data", "scenario")
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# disable autosorting of JSON objects in response: https://stackoverflow.com/a/60780210
app.json.sort_keys = False

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


######################################################
## Helper functions
######################################################


######################################################
## App route definition
######################################################


# define the url for which the application should send an http response to
@app.route('/')
# plain python function to handle the request
def home_page():
    return render_template('index.html')


@app.route('/search_gauges', methods=["POST"])
def search_gauge_observarions():

    # 1. get gauge data
    req_data_form = request.form
    # Flask returns MultiDict for POST
    if "gauge_list[]" in req_data_form.keys():
        # requires list syntax for list variables 
        gauge_query_list = request.form.getlist('gauge_list[]')
    else:
        # uses normal dict syntax
        gauge_query_list = [request.form.get('gauge_list')]
    
    print("getting form list data...")
    print(gauge_query_list)

    # remove duplicate entries 
    gauge_query_list = list(set(gauge_query_list))
    print(gauge_query_list)

    # 2. get date data
    date_list = sorted([
        datetime.strptime(request.form.get('date_start'), "%d/%m/%Y"), 
        datetime.strptime(request.form.get('date_end'), "%d/%m/%Y")
    ])

    print("Dates are: {}".format(
        ", ".join([d.strftime("%d/%m/%Y") for d in date_list])
    )) 

    date_range = {
        'start_date': date_list[0],
        'end_date': date_list[-1]
    }

    # 3 Query Gauge data source: 
    print(
        "Retrieving gauge observation for query:\n{}"
        .format(", ".join(gauge_query_list))
    )
    ewr_oh = ObservedHandler(gauges=gauge_query_list, dates=date_range)
    print("query complete!")    
    
    # if the flask app column ordering fix doesn't work on records
    # rename startDate and endDate to dateStart and dateEnd
    return {
        "table_events": ewr_oh.get_all_events().to_dict(orient='records'),
        "table_interevents": ewr_oh.get_all_interEvents().to_dict(orient='records')
    } 
    

@app.route("/analyse_scenario", methods=["POST"])
def analyse_scenario_files(): 

    if request.files:
        # 1. Create temp folder for uploaded files
        request_tmp_folder = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            "tmp_{}".format(str(int(time.time() * 1000)))
        )
        if not os.path.exists(request_tmp_folder):
            os.makedirs(request_tmp_folder, exist_ok=True)

        print("Uploaded files:\n{}".format(request.files.keys()))

        # expectinc a list of dicts: one per scenario
        form_metadata = json.loads(request.form.get("metadata"))             

        for file in request.files.values():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(request_tmp_folder, filename))
        
        # now to use form metadata to 
        
        
        print(".........................................................")
        scenario_results_list = list()
        for s in form_metadata:
            scenario_results = {
                "scenario_name": s["scenario"],
                "table_events": [],
                "table_interevents": []
            }
            for filename, model_format in s["metadata"].items():
                # 1. process scenario file                
                ewr_sh = ScenarioHandler(
                    scenario_file = os.path.join(request_tmp_folder, filename), 
                    model_format = model_format
                )
                # process events data and add to list
                scenario_results["table_events"].append(
                    ewr_sh.get_all_events()
                )

                scenario_results["table_interevents"].append(
                    ewr_sh.get_all_interEvents()
                )
            # combine scenario events
            scenario_results["table_events"] = pd.concat(
                scenario_results["table_events"], 
                axis = 0
            )
            # combine scenario interevents
            scenario_results["table_interevents"] = pd.concat(
                scenario_results["table_interevents"], 
                axis = 0
            )

            # extract records
            scenario_results["table_events"] = scenario_results["table_events"].to_dict(orient='records')
            scenario_results["table_interevents"] = scenario_results["table_interevents"].to_dict(orient='records')
            
            # append results to list
            scenario_results_list.append(scenario_results)
        
        # N. Remove temp folder for uploaded files - Finally
        if os.path.exists(request_tmp_folder) and os.path.isdir(request_tmp_folder):
            shutil.rmtree(request_tmp_folder)
    else:
        scenario_results_list = [{
            "message": "no files provided"
        }]

    return scenario_results_list

# executed the above defined Flask app
if __name__ == '__main__':
    # initialize the app by invoking the Flask function run()
    app.run(debug=True)
