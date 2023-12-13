import os
import json
import time
import shutil
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from datetime import datetime

from py_ewr.observed_handling import ObservedHandler

import plotly.graph_objects as go


######################################################
## App initialisation
######################################################



# initialize Flask app with the name of the file
app = Flask(__name__)

PARENT_FOLDER = os.environ.get("PARENT_FOLDER") or app.instance_path
UPLOAD_FOLDER = os.path.join(PARENT_FOLDER, "app_data", "scenario")
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


######################################################
## Helper functions
######################################################


# https://developer.mozilla.org/en-US/docs/Web/CSS/color_value
def render_plotly_table(
        df, 
        header_color="green", 
        cell_color: str="lavender"
    ):

    # format input data for plotly table
    columns = df.columns.tolist()
    values = [df[c].tolist() for c in df.columns]

    # return plotly table as figure
    return go.Figure(data=[go.Table(
        header=dict(values=columns,
                fill_color=header_color,
                align='left'),
        cells=dict(values=values,
               fill_color=cell_color,
               align='left'))
    ])

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

    # 1. getting all events
    events_table_fig = render_plotly_table(
        df=ewr_oh.get_all_events(), 
        header_color="lightcyan", 
        cell_color="lavender"
    )

    interevents_table_fig = render_plotly_table(
        df=ewr_oh.get_all_interEvents(), 
        header_color="orange", 
        cell_color="floralwhite"
    )
    
    return {
        "table_events": events_table_fig.to_html(),
        "table_interevents": interevents_table_fig.to_html() 
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

        form_metadata = json.loads(request.form.get("metadata"))
        
        print("metadata type:\n{}".format(type(form_metadata)))
        print("metadata:\n{}".format(form_metadata))         

        for file in request.files.values():
            print("Data type is: {}".format(type(file)))
            # print("File is: {}, contents =\n".format(file))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print("filename is {}".format(filename))
                file.save(os.path.join(request_tmp_folder, filename))
        
        # now to use form metadata to 
        # form_metadata
        # {'scenario': 'Scenario 1', 'metadata': {'410130.csv': 'Bigmod - MDBA', 'a4261110.csv': 'Source - NSW (res.csv)'}}
        # N. Remove temp folder for uploaded files - Finally
        if os.path.exists(request_tmp_folder) and os.path.isdir(request_tmp_folder):
            shutil.rmtree(request_tmp_folder)
    events_table_fig = None
    interevents_table_fig = None

    return {
        "table_events": "Hello event!",
        "table_interevents": "Hello inter-event!" 
    }


    # return {
    #     "table_events": events_table_fig.to_html(),
    #     "table_interevents": interevents_table_fig.to_html() 
    # }



# executed the above defined Flask app
if __name__ == '__main__':
    # initialize the app by invoking the Flask function run()
    app.run(debug=True)
