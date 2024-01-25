$(document).ready(function () {

    $.post(
        "/definition_tables"
    )
    .done(function (data) {               
        if(typeof(data) == "string"){
            data = JSON.parse(data);
        }

        // define table ID vars
        const table_ewr_software = "table-ewr-software";
        const table_ewr_definitions = "table-ewr-dfn";
        const table_ewr_descriptions = "table-ewr-desc";

        // populate software version table
        $('#core_software_version_table_output').html(            
            createTableHTML(
                json_data=data["table_software"], 
                table_id=table_ewr_software
            )
        );
        
        // populate definition table
        $("#ewr_table_output_dfn").html(
            createTableHTML(
                json_data=data["table_definitions"], 
                table_id=table_ewr_definitions
            )
        );
        $('#'+ table_ewr_definitions).DataTable({
            orderCellsTop: false,
            fixedHeader: true,
            dom: 'Bfrtip',
            buttons:[
                'copy',
                {
                    extend: "csv",
                    title: table_id
                },
                {
                    extend: 'excel',
                    title: table_id
                }            
            ]
        })

        // populate description table
        $("#ewr_table_output_desc").html(
            createTableHTML(
                json_data=data["table_descriptions"], 
                table_id=table_ewr_descriptions)
        );
        convertHTMLTableToDataTableFiltered(table_id=table_ewr_descriptions);

    })
    .fail(function(e) {
        console.log("error encountered");
        console.log(e.status);
        console.log( JSON.stringify(e) );
    })
    .always(function() {
        
    });

});