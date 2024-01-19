$(document).ready(function () {
    // Date picker setup
    $( "#startdatepicker" ).datepicker(
        { dateFormat: "dd/mm/yy", defaultDate: "01/01/2023" }
    );
    $( "#startdatepicker" ).val("01/01/2023");

    $( "#enddatepicker" ).datepicker(
        { dateFormat: "dd/mm/yy", defaultDate: "31/12/2023" }
    );
    $( "#enddatepicker" ).val("31/12/2023");

    // Form submission logic
    $("#gauge-form").submit(function (event) {
        var formData = {
            gauge_list: $("#gauge-list-input").val().split(/[ ,;]+/),
            date_start: $("#startdatepicker").val(),
            date_end: $("#enddatepicker").val()
        };

        $.post(
            "/search_gauges",
            formData,
            settings = {
                contentType: "application/json"
            }
        )
            .done(function (data) {
                const guage_table_events_id = "gauge_table_events";
                const guage_table_interevents_id = "gauge_table_interevents";

                // Convert to loop
                $.each(data, function(k, v) {
                    // guage_table_events_id=gauge_table_events
                    data_table_id = "table_gauge_" + k;
                    $("#output_table_gauge_" + k).html(
                        createTableHTML(
                            json_data = v, 
                            table_id = data_table_id
                        )
                    );
                    convertHTMLTableToDataTableFiltered(table_id = data_table_id);
                });
            })
            .fail(function (e) {
                console.log(e.status);
                console.log(e.responseText);
            })
            .always(function () {

            });

        event.preventDefault();

    });
});