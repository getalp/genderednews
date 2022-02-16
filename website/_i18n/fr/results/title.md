<h2 id="Title" style="font-family:sans-serif;"></h2>

<script>
var parameters = new URLSearchParams(window.location.search);
document.getElementById("Title").innerHTML= "Semaine: " + parameters.get("week");
</script>