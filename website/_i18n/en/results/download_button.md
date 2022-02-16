<button onclick="exportData()">
    <span class="button"></span>
    Download
</button>

<script>
function exportData(){
    var table = document.getElementById("Data");
    var rows =[];

    for(var i=0,row; row = table.rows[i];i++){
        column_day = row.cells[0].innerText;
        column_source = row.cells[1].innerText;
        column_rate = row.cells[2].innerText;
 
    /* add a new records in the array */
        rows.push(
            [
                column_day,
                column_source,
                column_rate,
            ]
        );
 
        }
        csvContent = "data:text/csv;charset=utf-8,";
         /* add the column delimiter as comma(,) and each row splitted by new line character (\n) */
        rows.forEach(function(rowArray){
            row = rowArray.join(",");
            csvContent += row + "\r\n";
        });
 
        /* create a hidden <a> DOM node and set its download attribute */
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        var parameters = new URLSearchParams(window.location.search);
        link.setAttribute("download", "week_"+ parameters.get("week") + "_" + parameters.get("metrics") + ".csv");
        document.body.appendChild(link);
        link.click();
}
</script>