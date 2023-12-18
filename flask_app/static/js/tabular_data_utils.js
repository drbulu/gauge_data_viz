const createTableHTML = function(json_data, table_id=""){
    // define table structure
    let data_table = $('<table><thead/><tbody/></table>');
    if (table_id.trim()){
        data_table.attr("id", table_id.trim());
    };

    // define table header row
    let data_header = $("<tr/>");

    // populate data table
    $(json_data).each(function(i, d){        
        let new_row = $("<tr/>");
        $.each(d, function(k, v) {
            if (i == 0){
                data_header.append('<th>' + k + '</th>');
            }
            new_row.append('<td>' + v + '</td>');
        });
        // append elements to table
        if (i == 0){
            data_table.children("thead").html(data_header);
        }
        data_table.children("tbody").append(new_row);
    });
    return data_table;
};


const collectDataFromDataTableByID = function(table_id, select_filtered=false){
    // extract original column names
    var table_col_data = [];    
    $('#'+ table_id + ' thead tr:not(.filters) th').each(function(i, v){
        table_col_data.push($(v).text())
    });

    // extract data as object list
    var data_output = []
    new DataTable.Api( '#' + table_id )
    .rows({search: select_filtered? "applied" : "none"})
    .data()
    .each(function(v, i){ 
        data_dict = {};
        $.each(v, function(k, j){ 
            data_dict[table_col_data[k]] = j
        })
        data_output.push(data_dict);
    });
    return data_output;
};


// https://datatables.net/extensions/fixedheader/examples/options/columnFiltering.html
const convertHTMLTableToDataTableFiltered = function(table_id){
    
    // Setup: Create UI search filter inputs
    $('#'+ table_id + ' thead tr')
        .clone(true)
        .addClass('filters')
        .appendTo('#'+ table_id + ' thead');


    // extract column names from original table
    var table_columns = [];
    $('#'+ table_id + ' thead tr:not(.filters) th').each(function(i, v){
        table_columns.push({name: $(v).text()})
    });

    // transform HTML table to DataTable.
    $('#'+ table_id).DataTable({
        orderCellsTop: true,
        columns: table_columns,
        fixedHeader: true,
        initComplete: function () {
            var api = this.api();
            // For each column
            api
            .columns()
            .eq(0)
            .each(function (colIdx) {
                // Set the header cell to contain the input element
                let cell = $('#'+ table_id + ' .filters th').eq(
                    $(api.column(colIdx).header()).index()
                );
                let title = $(cell).text();
                $(cell).html('<input type="text" placeholder="' + title + '" />');
 
                // On every keypress in this input
                $(
                    'input',
                    $('#'+ table_id + ' .filters th').eq($(api.column(colIdx).header()).index())
                )
                .off('keyup change')
                .on('change', function (e) {
                    // Get the search value
                    $(this).attr('title', $(this).val());
                    let regexr = '({search})'; //$(this).parents('th').find('select').val();
                    // Search the column for that value
                    api
                    .column(colIdx)
                    .search(
                        this.value != ''
                        ? regexr.replace('{search}', '(((' + this.value + ')))')
                        : '',
                        this.value != '',
                        this.value == ''
                    )
                    .draw();
                })
                .on('keyup', function (e) {
                    e.stopPropagation();                        
                    let cursorPosition = this.selectionStart;
                    $(this).trigger('change');
                    $(this)
                    .focus()[0]
                    .setSelectionRange(cursorPosition, cursorPosition);
                });
            });
        },
    });
};