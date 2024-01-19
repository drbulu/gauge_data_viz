// Form submission logic: https://stackoverflow.com/questions/5392344/sending-multipart-formdata-with-jquery-ajax

createDropDown = function(label, opts){

    let select_e = $("<select/>");
    select_e.addClass("file_model_format");

    // let options =  '<option value=""><strong>Model Format</strong></option>';
    let options =  '';
    $(opts).each(function(i, v){ 
        options += '<option value="'+v+'">'+v+'</option>';
    })
    select_e.html(options);
    
    list_label = $("<li/>")
    list_label.append(
        '<span class="file_label">'+label+'</span>',
        select_e
    )

    return list_label;
};

$(document).ready(function () {

    $("#file_uploader").change(function(event){
        // 1. get existing files - with annotations
        let current_files = [];         
        $("#file-list > li > span").each(function(i, e){ 
            current_files.push($(e).text());
        });

        // 2. get new set of files
        var new_files = [];
        for (var i = 0; i < $(this).get(0).files.length; ++i) {
            new_files.push($(this).get(0).files[i].name);
        }

        // 3. Set operations - https://stackoverflow.com/a/33034768
        // https://medium.com/@alvaro.saburido/set-theory-for-arrays-in-es6-eb2f20a61848
        // a. files to keep; A = new  B = old
        let files_to_add = new_files.filter(x => !current_files.includes(x));
        // b. files to remobe
        let files_to_remove = current_files.filter(x => !new_files.includes(x));

        // 4. Remove elements in the remove list based on file name
        $("#file-list > li > span").each(function(i, e){ 
            if(files_to_remove.includes($(e).text())){
                $(e).parent().remove();
            };
        });

        // 5. Add new elements based on file name
        // https://stackoverflow.com/questions/40640069/dynamic-dropdown-options-with-jquery
        var model_opts = [
            'Bigmod - MDBA',
            'Source - NSW (res.csv)' ,
            'IQQM - NSW 10,000 years' 
        ];

        $(files_to_add).each(function(i, v){
            $("#file-list").append(createDropDown(v, model_opts))
        });
    });

    $("#scenario-form").submit(function (event) {
        
        // Need to prevent default action, 
        // allowing post response to be captured and 
        // rendered on main page, instead of either
        // a. rendering the result at "/analyse_scenario"
        // b. throwing a 405 on post submission to "/"
        // https://stackoverflow.com/a/42517904
        event.preventDefault();
        var fileFormData = new FormData();
        // // adding plain data as well: https://stackoverflow.com/a/55143036            
        // 1. populate submission metadata 
        file_config = {
            scenario: $("#scenario-name").val(),
            metadata: {}
        };
        $("#file-list > li").each(function(i, e){ 
            file_config["metadata"][$(e).children("span").text()] = $(e).children("select").find(":selected").text();
        });
        // note: catering for future use cases where scenario comparison might be valid.
        file_config_list = [file_config];
        fileFormData.append('metadata', JSON.stringify(file_config_list));
        // appending files
        jQuery.each(jQuery('#file_uploader')[0].files, function(i, file) {
            fileFormData.append('file-'+i, file);
        });

        jQuery.ajax({
            url: '/analyse_scenario',
            data: fileFormData,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            success: function(data){
                // Data processing
                $(data).each(function(i, scenario_data){                    
                    // Assumes that a list of scenarios even though the UI 
                    // only supports one scenario, non-interactive options 
                    // could feasibly support batch processing.
                    $.each(scenario_data, function(k, v) {                        
                        if (k === "scenario_name" ){
                            $("#label_scenario_name").val(scenario_data[k]);
                        } else {
                            let table_div_id = "#output_table_scenario_" + k;
                            let data_table_id = "table_scenario_" + k;
                            $(table_div_id).empty();
                            $(table_div_id).html(
                                createTableHTML(
                                    json_data = v, 
                                    table_id = data_table_id
                                )
                            );
                            convertHTMLTableToDataTableFiltered(table_id=data_table_id);
                        };                        
                    });
                });
            },
            error: function(e) {
                console.log(e.status);
                console.log(e.responseText);
            }
        });

    });

});