import pytest
import os
import shutil
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

def test_css_copy():
  #Create path needed for CSS
  input_path = os.path.join(os.getcwd(), 'pytest_fixtures/input_dir')
  output_path = os.path.join(os.getcwd(), 'pytest_fixtures/output_dir')
  if not os.path.exists(input_path):
    os.makedirs(input_path + '/_swiki')
    os.makedirs(output_path)
    f = open(input_path + '/_swiki/frame.html', 'a')
    f.close()
    f = open(input_path + '/_swiki/test_css.css', 'a')
    f.close()

    swiki.copy_css_file(input_path, 'pytest_fixtures/output_dir')
    assert os.path.isfile(output_path + '/test_css.css') == True
    shutil.rmtree(os.path.join(os.getcwd(), 'pytest_fixtures'), ignore_errors=True)