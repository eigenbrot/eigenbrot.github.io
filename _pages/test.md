---
layout: single
title: Test
permalink: /test/
comments: False
author_profile: True
---
This is a test!

yurpdurp

<form method="POST" action="https://api.staticman.net/v2/entry/eigenbrot/eigenbrot.github.io/master">
  <input name="options[redirect]" type="hidden" value="http://www.eigenspace.me">
  <!-- e.g. "2016-01-02-this-is-a-post" -->
  <input name="options[slug]" type="hidden" value="{{ page.slug }}">
  <label><input name="fields[name]" type="text">Name</label>
  <label><input name="fields[email]" type="email">E-mail</label>
  <label><textarea name="fields[message]"></textarea>Message</label>
  
  <button type="submit">Go!</button>
</form>