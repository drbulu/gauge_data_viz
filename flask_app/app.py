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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


######################################################
## App route definition
######################################################


# define the url for which the application should send an http response to
@app.route('/')
# plain python function to handle the request
def home_page():
    return render_template('index.html')


@app.route('/definition_tables', methods=["GET", "POST"])
def description_table():
    dfn_df = pd.read_csv(
        os.path.join(
            app.root_path, 
            "static",
            "csv",
            "MDBA-EWR_category_definition_table.csv"
        )
    )
    desc_df = pd.read_csv(
        os.path.join(
            app.root_path, 
            "static",
            "csv",
            "MDBA-EWR_description_table.csv"
        )
    )
    desc_df["LTWP Area"] = desc_df["LTWP Area"].fillna("All LTWP Areas")
    return {
        "table_definitions": dfn_df.to_dict(orient='records'),
        "table_descriptions": desc_df.to_dict(orient='records')
    }


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

    gauge_results = dict()

    result_call_config = {
        "ewr_results": ewr_oh.get_ewr_results,
        "ewr_yearly_results": ewr_oh.get_yearly_ewr_results,
        "events": ewr_oh.get_all_events,
        "interevents": ewr_oh.get_all_interEvents,
        "successful_events": ewr_oh.get_all_successful_events,
        "successful_interEvents": ewr_oh.get_all_successful_interEvents,
    }
    # process events data and add to list
    for k, v in result_call_config.items():
        data_output = v()        
        gauge_results[k] = data_output.to_dict(orient='records')

    return gauge_results
    

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
        
        scenario_results_list = list()
        for s in form_metadata:
            scenario_results = {
                # "scenario_name": s["scenario"],
                # "table_events": [],
                # "table_interevents": []
                "ewr_results": [],
                "ewr_yearly_results": [],
                "events": [],
                "interevents": [],
                "successful_events": [],
                "successful_interEvents": []
            }
            
            for filename, model_format in s["metadata"].items():
                # 1. process scenario file                
                ewr_sh = ScenarioHandler(
                    scenario_file = os.path.join(request_tmp_folder, filename), 
                    model_format = model_format
                )

                result_call_config = {
                    "ewr_results": ewr_sh.get_ewr_results,
                    "ewr_yearly_results": ewr_sh.get_yearly_ewr_results,
                    "events": ewr_sh.get_all_events,
                    "interevents": ewr_sh.get_all_interEvents,
                    "successful_events": ewr_sh.get_all_successful_events,
                    "successful_interEvents": ewr_sh.get_all_successful_interEvents
                }
                # process events data and add to list
                for k, v in result_call_config.items():                    
                    scenario_results[k].append(v())

                # # process events data and add to list
                # scenario_results["table_events"].append(
                #     ewr_sh.get_all_events()
                # )

                # scenario_results["table_interevents"].append(
                #     ewr_sh.get_all_interEvents()
                # )            
            for k, v in scenario_results.items():
                # combine scenario events
                scenario_results[k] = pd.concat(v, axis = 0)
            # scenario_results["table_events"] = pd.concat(
            #     scenario_results["table_events"], 
            #     axis = 0
            # )
            # # combine scenario interevents
            # scenario_results["table_interevents"] = pd.concat(
            #     scenario_results["table_interevents"], 
            #     axis = 0
            # )

            # # extract records
            for k, v in scenario_results.items():                
                # extract records
                scenario_results[k] = scenario_results[k].to_dict(orient='records')
            # scenario_results["table_events"] = scenario_results["table_events"].to_dict(orient='records')
            # scenario_results["table_interevents"] = scenario_results["table_interevents"].to_dict(orient='records')
            
            # Add scenario_name to results. Important to do AFTER data 
            # processing for simpler, more predictable data processing 
            # logic. "scenario_name" causes pd.concat to fail if not
            # otherwise handled.
            scenario_results["scenario_name"] = s["scenario"]
            
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
