<h2 id="Title" style="font-family:sans-serif;"></h2>

<script>
var parameters = new URLSearchParams(window.location.search);
document.getElementById("Title").innerHTML= "Week: " + parameters.get("week");
</script>