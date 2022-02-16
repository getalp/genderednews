---
#title:  "Contact"
layout: archive
permalink: /contact/
author_profile: false
comments: false
---

{% tf home/ip_check.md %}

{% tf home/lang.md %}

<h1>{% t pages.contact %}</h1>

<p>
{% tf contact/text.md %}
</p>

<form accept-charset="UTF-8" action="https://getform.io/f/b751360c-ad24-457e-ba69-83a9da992ba2" method="POST" enctype="multipart/form-data" target="_blank">
  <div class="form-group">
    <label required="required">Email:</label>
    <input type="email" name="email" class="form-control" id="mail1" aria-describedby="emailHelp" placeholder="{% t contact.enter_email %}">
  </div>
  
  <br>

  <div>
    {% t contact.comment %} <textarea name="comment" rows="5" cols="40" required="required"  placeholder="{% t contact.enter_comment %}"></textarea>
  </div>
  
  <br>

  <button type="submit" class="btn btn-primary">{% t contact.send %}</button>
</form>