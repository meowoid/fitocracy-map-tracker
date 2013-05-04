#!/usr/bin/env python

""" [[toDo]]
clean up code: 
  sanitize all inputs (remember bobby tables!)
    flask docs claim jinja (underlying template engine) sanitizes inputs
create a package 'fitMapTracker/fmt{Flask, Selenium}' 
  'fitMapTracker/__init__.py' should launch Xvfb and Firefox  
  setup global logging for entire package 
add a 'self.fmtLoggedIn' bool to fmtFlask/__init__() to track logged in state
"""

import fmtSelenium 
import os, re, pprint
from flask import Flask, session, redirect, url_for, render_template, request

class fmtFlask(object):
  def __init__(self):
    self.fmtSel = fmtSelenium.fmtSelenium() 
    self.app = Flask(__name__.split('.')[0])
    self.app.secret_key = os.urandom(24)
    self.errorMsg = ''
    #self.tasks = ['Running', 'Jogging', 'Hiking', 'Cycling']
    self.tasks = ['Jogging', 'Hiking', 'Cycling']
    #self.session, self.request = request, session
    # http://flask.pocoo.org/docs/api/#sessions
    # http://flask.pocoo.org/docs/reqcontext/#notes-on-proxies
    # how do context local proxy objects work? why are they 'thread safe'?

    @self.app.route('/')
    def index():
      if 'username' in session:
        return redirect(url_for('user', username = session['username']))
      return redirect(url_for('login'))

    @self.app.route('/login', methods=['GET', 'POST'])
    def login():
      if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if validate_login(u, p): 
          session['username'] = u 
          return redirect(url_for('user'))
        else: 
          msg = 'ERROR: There was a problem logging in: %s' % self.errorMsg 
          return render_template('default.html', msg = msg) 
      return render_template('default.html')

    @self.app.route('/logout')
    def logout():
      session.pop('username', None)
      self.fmtSel.fitocracy_logout()
      return redirect(url_for('index'))

    @self.app.route('/user', methods=['GET', 'POST'])
    def user():
      if 'username' in session:
        if request.method == 'POST':
          session['task'] = ''
          if request.form['_task']: 
            session['task'] = request.form['_task']
          if request.form['_new_task']: 
            session['task'] = request.form['_new_task']
          session['task'] = validate_task(session['task']) 
          return redirect(url_for('map'))
        return render_template('default.html', \
                               username = session['username'], \
                               fitocracy_tasks = fitocracy_tasks())
      return redirect(url_for('login'))

    @self.app.route('/map')
    def map():
      if 'username' in session: 
        if 'task' in session: 
          # HTML5 geolocation obj passed to google by JS inside map.html 
          return render_template('map.html', username = session['username'], \
            task = session['task'])
        else: return redirect(url_for('user')) # ie: force user to pick a task
      else:
        return redirect(url_for('login')) 

    def validate_login(username, password):
      fmtLoggedIn = self.fmtSel.fitocracy_login(username, password)
      if fmtLoggedIn:
        self.errorMsg += 'Login sucessful!'
        return True
      else:
        self.errorMsg += "Login Faliure - check user/pass: %s / %s" % (username, password)
        return False

    def fitocracy_tasks():
      recordedActivities = self.fmtSel.getActivities()
      if not recordedActivities: 
        self.errorMsg = "ERROR retrieving activities: %s" % (pprint.saferepr(recordedActivities))
        return self.tasks  
      for activity in self.fmtSel.getActivities():
        activity = re.split('\n', activity)[1].rstrip(':')
        if not activity in self.tasks: self.tasks.append(activity)
        # should check if activity is also 'outdoor' too; how? [[toDo]]
      return self.tasks 
    
    def validate_task(task=None):
      if task: return task
      else: pass
      #if self.fmtSel.validate_workout(task=task): return True  
      # write a func in fmtSel to validate a type of workout

if __name__ == '__main__':
  fmtFlaskApp = fmtFlask()
  fmtFlaskApp.app.run(host='0.0.0.0', port=5000, debug=True)
