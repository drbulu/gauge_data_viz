// "transform": [
//     {"calculate": "datum.isSuccessEWR=true", "as": "event_success"}
// ],


// // get data from chart
// var chart_data = collectDataFromDataTableByID(table_id = "gauge_table_events", select_filtered = false);

// renderVegaliteChart(
//     chart_id="gauge_graph_output_01", 
//     chart_y_axis="eventDuration",
//     chart_data=chart_data, 
//     is_bar_chart=false
// );

// set to const after
var renderVegaliteChart = function (
    chart_id,
    chart_y_var,
    chart_data,    
    is_bar_chart=false
) {
    if (typeof chart_y_var !== "string"){
        console.log("type assertion error! chart_y_axis is '" + chart_y_var + "', expected 'String'!");
        return null
    }

    console.log("Chart y axis type = " + typeof(chart_y_var));
    console.log("Chart y axis = " + chart_y_var);
    // Wrap as a function
    // https://stackoverflow.com/questions/59003674/
    var vegalite_spec_event_ts = {
        "width": "container",
        "height": 400,
        "data": null,
        "encoding": {
            "x": {
                "field": "startDate", 
                "type": "temporal", 
                "timeUnit": "yearmonth", 
                "axis": { "labelAngle": -90 }
            },
            "y": {
                "field": chart_y_var,
                "type": "quantitative",
                "impute": { "value": null } 
            }
        },
        "layer": [
            {
                "mark": { "type": "point", "tooltip": true },
            },
            {
                "mark": { "type": "point", "tooltip": true },
                "encoding": { "color": { "field": "event_success", "type": "nominal" } }
            }
        ],
        "labelExpr": "[timeFormat(datum.value, '%m'), timeFormat(datum.value, '%Y')]",
        "config": {}
    };

    var vegalite_spec_event_bar = {
        "data": null,
        "width": "container",
        "height": 400,
        "mark": { "type": "bar", "tooltip": true },
        "encoding": {
            "x": { "field": "pu", "title": "Planning Unit" },
            "y": { "aggregate": "sum", "field": chart_y_var, "title": "Total " + chart_y_var },
            "color": { "field": "ewr" },
            "order": { "aggregate": "sum", "field": chart_y_var }
        },
        "config": {
            "legend": {
                "orient": "left"
            }
        }
    };
    console.log("checkpoint 1")
    // prepare visualisation specification
    chart_spec = is_bar_chart ? vegalite_spec_event_bar : vegalite_spec_event_ts;
    chart_spec["data"] = { "values": chart_data };
    console.log("checkpoint 2")
    chart_spec["title"] = "Summary " +
        (is_bar_chart ? "Bar" : "Time Series") + 
        " Chart of " + chart_y_var + " Data";
    console.log("checkpoint 3")

    console.log(chart_spec["title"]);
    // render visualisation.
    vegaEmbed("#" + chart_id, chart_spec, { mode: "vega-lite" });
};
