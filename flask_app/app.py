# https://flask.palletsprojects.com/en/3.0.x/quickstart/
from flask import Flask, render_template, request, Response

from datetime import datetime

from py_ewr.observed_handling import ObservedHandler

import plotly.graph_objects as go


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



# initialize Flask app with the name of the file
app = Flask(__name__)

# define the url for which the application should send an http response to
@app.route('/')
# plain python function to handle the request
def home_page():
    return render_template('index.html')



# Data structure and filtering
# possibly change how data is returned so that you can create filterable charts
# https://stackoverflow.com/questions/51838992/json-data-to-plotly
# https://plotly.com/javascript/filter/
# filter on events: https://plotly.com/javascript/plotlyjs-events/

# possible alt strategy:
# https://blog.tensorflow.org/2020/08/introducing-danfo-js-pandas-like-library-in-javascript.html
# https://stackoverflow.com/questions/30610675/python-pandas-equivalent-in-javascript


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

    # if request.files:
    #     print("Uploaded files:\n{}".format(request.files.keys()))
    
    #.

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
