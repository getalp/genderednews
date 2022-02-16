<table id="Data"></table>


<script>
var parameters = new URLSearchParams(window.location.search);
if (parameters.get("metrics") == "mentions"){
    fetch('{{site.baseurl}}/assets/data/data_mentions.json')
        .then(function (response) { 
            return response.json();
        })
        .then(function (data) {
                    collectData_Mentions(data);
            })
}
else if (parameters.get("metrics") == "quotes"){
    fetch('{{site.baseurl}}/assets/data/data_quotes.json')
        .then(function (response) { 
            return response.json();
        })
        .then(function (data) {
                    collectData_Quotes(data);
            })
}
else{
    console.log("[metrics] argument is not correct")
}


function collectData_Mentions(data) {
    var mainContainer = document.getElementById("Data");

    var thead = document.createElement("thead");
    var tr = document.createElement("tr");
    var th_day = document.createElement("th");
    th_day.innerHTML = "Jour";
    tr.appendChild(th_day);
    var th_source = document.createElement("th");
    th_source.innerHTML = "Source";
    tr.appendChild(th_source);
    var th_rate = document.createElement("th");
    th_rate.innerHTML = "Taux de masculinité";
    tr.appendChild(th_rate);
    thead.appendChild(tr);
    mainContainer.appendChild(thead);

    var tbody = document.createElement("tbody");
        
    for (var j = 0; j < 7; j++){
            
        var date = new Date(new URLSearchParams(window.location.search).get("week"));
        date.setDate(date.getDate() + j);
        var datestr = date.toISOString().slice(0,10) + " 00:00:00";
            
        for (var i = 0; i < data.length; i++) {

            if (datestr == data[i].date){
                	
                var tr = document.createElement("tr");
                	
                var td_day = document.createElement("td");
                td_day.innerHTML = data[i].date.slice(0,10);
                tr.appendChild(td_day);
                
                var td_source = document.createElement("td");
                td_source.innerHTML = data[i].source_name;
                tr.appendChild(td_source);
                	
                var td_rate = document.createElement("td");
                td_rate.innerHTML = Number.parseFloat(data[i].masculinity_rate).toPrecision(2);
                tr.appendChild(td_rate);
                           	
                tbody.appendChild(tr).style.backgroundColor="#F5F5F5";
            }               
        }
        var tr = document.createElement("tr");
        var td = document.createElement("td");
        tr.appendChild(td);
        td = document.createElement("td");
        tr.appendChild(td);
        td = document.createElement("td");
        tr.appendChild(td);
        tbody.appendChild(tr).style.backgroundColor="#CACACA";
        mainContainer.appendChild(tbody);
    }            
}

function collectData_Quotes(data) {
    var mainContainer = document.getElementById("Data");
    
    var thead = document.createElement("thead");
    var tr = document.createElement("tr");
    var th_day = document.createElement("th");
    th_day.innerHTML = "Jour";
    tr.appendChild(th_day);
    var th_source = document.createElement("th");
    th_source.innerHTML = "Source";
    tr.appendChild(th_source);
    var th_rate = document.createElement("th");
    th_rate.innerHTML = "Part des hommes";
    tr.appendChild(th_rate);
    thead.appendChild(tr);
    mainContainer.appendChild(thead);
    
    var tbody = document.createElement("tbody");
    
    for (var j = 0; j < 7; j++){
            
        var date = new Date(new URLSearchParams(window.location.search).get("week"));
        date.setDate(date.getDate() + j);
        var datestr = date.toISOString().slice(0,10) + " 00:00:00";
            
        for (var i = 0; i < data.length; i++) {

            if (datestr == data[i].date){
                	
                var tr = document.createElement("tr");
                	
                var td_day = document.createElement("td");
                td_day.innerHTML = data[i].date.slice(0,10);
                tr.appendChild(td_day);
                
                var td_source = document.createElement("td");
                td_source.innerHTML = data[i].source_name;
                tr.appendChild(td_source);
                	
                var td_rate = document.createElement("td");
                td_rate.innerHTML = Number.parseFloat(data[i].percentage_men).toPrecision(2);
                tr.appendChild(td_rate);
                           	
                tbody.appendChild(tr).style.backgroundColor="#F5F5F5";
            }               
        }
        var tr = document.createElement("tr");
        var td = document.createElement("td");
        tr.appendChild(td);
        td = document.createElement("td");
        tr.appendChild(td);
        td = document.createElement("td");
        tr.appendChild(td);
        tbody.appendChild(tr).style.backgroundColor="#CACACA";
        mainContainer.appendChild(tbody);
    }            
}
</script>
