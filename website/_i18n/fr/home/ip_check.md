<script>
{% if site.lang == "fr" %}
if(sessionStorage.getItem('counter') == null){
    var request = new XMLHttpRequest();

    request.open('GET', 'https://ipapi.co/json');

    request.setRequestHeader('Accept', 'application/json');

    request.onreadystatechange = function () {
        if (this.readyState === 4) {
            const json = JSON.parse(this.responseText)
            if(json.country_code != "FR"){
                location = "{{ site.baseurl_root }}/en{{ page.url}}"
            }
        }
    };
    request.send();
}
{% endif %}

window.addEventListener("unload", function(){
    var count = parseInt(sessionStorage.getItem('counter') || 0);
    sessionStorage.setItem('counter', ++count)
}, false);
</script>
