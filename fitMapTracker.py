#!/usr/bin/env python
"""
A mobile-device accesible web application that displays your current location 
on a map, and then allows you to select a fitocracy.com exercise task to start 
tracking (eg: walk, jog, hike, run, bike ride). Once the task is selected, the 
application keeps track of your speed/distance/path as you are exercising. 
As you are going along, display the path you've taken on the map. Start the map 
at max-zoom, then zoom out as the path taken goes past the viewport of the 
current-zoom-level. When the user ends the task, the relevant details 
(speed, distance, pace) are uploaded to fitocaracy.

ToDo List:
  sanitize all inputs, remember bobby tables!
  turn this into a class (this.user and this.pass would be helpful!)
  create python package (ie: __init__.py and config file for WSGI server opts)
  JSONify all data from fitocracy.com 
  figure out what constitues a run/walk/jog/hike based on speed/elevation  
  deal with user that disables cookies (ugh)...
"""

import os, pprint
import requests
from flask import Flask, abort, session, redirect, url_for, render_template, escape, request
app = Flask(__name__)

app.secret_key = os.urandom(24)
username, password = '', ''

@app.route('/')
def index():
  if 'username' in session:
    return redirect(url_for('user', user_name = session['username']))
  return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if validate_login(username, password): 
      session['username'] = username 
    
      ## <DEBUGGING>     
      response = fitocracy_request(username, password)
      msg = 'Sucessful login: '
      msg += username
      msg += pprint.saferepr(response.url)
      msg += pprint.saferepr(response.status_code)
      msg += pprint.saferepr(response.history)
      msg += pprint.saferepr(response.headers)
      msg += pprint.saferepr(response.text)
      return render_template('default.html', msg = msg)   
      ## </DEBUGGING>     
     
     
      return redirect(url_for('user', user_name = username))
    else: 
      msg = 'ERROR: Invalid username or password!' 
      return render_template('default.html', msg = msg)
  return render_template('default.html')

@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('index'))

@app.route('/user/<user_name>', methods=['GET', 'POST'])
def user(user_name):
  if 'username' in session:
    if request.method == 'POST':
      task = ''
      if request.form['_task']: task = request.form['_task']
      if request.form['_new_task']: task = request.form['_new_task'] 
      return redirect(url_for('map', task = task))
    return render_template('default.html', \
                           username = user_name, \
                           fitocracy_tasks = fitocracy_tasks())
  return redirect(url_for('login'))

@app.route('/map/')
@app.route('/map/<task>')
def map(task=False):
  if 'username' in session: 
    if task:
      username = session['username']
      map_div = google_map();
      return render_template('map.html', \
                             username = username, \
                             map_div = map_div, \
                             task = task)
    else: 
      msg = 'ERROR: No task selected, please pick one'
      return render_template('map.html', msg = msg)
  else:
    return redirect(url_for('login')) 
  # display map at 95% of fullscreen with start pin on current location
  # display 'pause, end, restart' buttons in bottom 5% of screen
  # display path + pace/speed continually (longpoll or eventsource?) 
  # if task paused, drop pin, if task unpaused more than 100 ft
  # from pause location, force starting new task or only unpause once
  # back within 100 ft range of paused-pin. 
  # if task ended/restarted, display time/distance/speed to user and
  # upload task to fitocracy.com after user confirms (allow user notes?)

# modify func prototype to: fitocracy_request(username, password, url=False)
# to allow the response object that this returns to be for an arbritrary
# URL, not just https://www.fitocracy.com/accounts/login/ ... but how? [[wip]]
def fitocracy_request(username, password):
  output = '' 
  req_session = requests.session()
  payload = {'csrfmiddlewaretoken': None, 
            'username': username, 
            'password': password, 
            'login': 'Log+in', 
            'next': ''}
  headers = {'referer': 'https://www.fitocracy.com/accounts/login/'}
  req_session.get('https://www.fitocracy.com/accounts/login/', headers=headers)
  # Test to see if we have captured the CSRF token from the cookies...
  if 'csrftoken' not in req_session.cookies:
    output += 'Unable to capture CSRF token, login failed.'
  else: 
    output += 'Captured CSRF Token! %s' % req_session.cookies['csrftoken']
  # Now that we have the CSRF token we can inject it into our POST payload.
  payload['csrfmiddlewaretoken'] = req_session.cookies['csrftoken']
  # Submit a POST request to the login url with our payload.
  response = req_session.post('https://www.fitocracy.com/accounts/login/', \
                              data=payload, \
                              headers=headers, \
                              allow_redirects = True)
  return response 

def validate_login(username, password):
  output = '' 
  response = fitocracy_request(username, password)
  """output += pprint.saferepr(response.url)
  output += pprint.saferepr(response.status_code)
  output += pprint.saferepr(response.history)
  output += pprint.saferepr(response.headers)
  output += pprint.saferepr(response.text)"""
  if response.url == 'https://www.fitocracy.com/accounts/login/':
    output += 'Username and or password are incorrect. Try again.'
    return False
  output += 'Login successful!'
  return True

def fitocracy_tasks():
  return ['Run', 'Jog', 'Hike', 'Bike Ride'] 
  # retrieve list of recent non-stationary outdoor tasks from fitocracy.com

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug = True)
