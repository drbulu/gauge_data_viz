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

        console.log("form data:");
        console.log(formData);
        console.log(JSON.stringify(formData))

        $.post(
            "/search_gauges",
            formData,
            settings = {
                contentType: "application/json"
            }
        )
            .done(function (data) {
                console.log("response to /search_gauges");
                console.log(data);

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
                // $("#output_table_gauge_events").html(
                //     createTableHTML(json_data = data["table_events"], table_id = guage_table_events_id)
                // );
                // convertHTMLTableToDataTableFiltered(table_id = guage_table_events_id);

                // $("#output_table_gauge_interevents").html(
                //     createTableHTML(json_data = data["table_interevents"], table_id = guage_table_interevents_id)
                // );
                // convertHTMLTableToDataTableFiltered(table_id = guage_table_interevents_id);

                // // https://datatables.net/reference/event/search
                // $("#" + guage_table_events_id).on("change", function () {
                //     console.log("Event table changed!");
                // });

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