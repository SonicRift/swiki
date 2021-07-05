import pytest
import os
import swiki

def test_delete_html():
  f = open('text.html', 'a')
  f.close()
  swiki.delete_current_html('./')

  assert os.path.isfile('./text.html') == False

def test_place_in_container():
  # With all content
  e1 = swiki.place_in_container('h1', 'my-id', 'this is an h1')
  e2 = swiki.place_in_container('h2', 'my-id2', 'this is an h2')

  # With no ID provided
  e3 = swiki.place_in_container('div', '', 'Div with no id')

  assert e1 == '<h1 id="my-id">this is an h1</h1>'
  assert e2 == '<h2 id="my-id2">this is an h2</h2>'
  assert e3 == '<div>Div with no id</div>'
