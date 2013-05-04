#!/usr/bin/env python

""" [[toDo]]
create formal selenium SiteObject and PageObject classes for use by fmtFlask
  make sure there is only ever one instance of Xvfb and Firefox!
  http://code.google.com/p/selenium/wiki/PageObjects
  http://fijiaaron.wordpress.com/2009/09/02/selenium-page-objects-site-objects-data-objects-high-level-navigation/
replace stupid time.sleep() calls with TimeoutException try/catch logic 
  research selenium.webdriver.support.wait.WebDriverWait()
  research selenium.webdriver.support.expected_conditions
setup 'fitMapTracker' package with modules (eg: fmtSelenium, fmtFlask)
setup global logging for entire package into single log file
"""

import time, logging
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# setup logging
if __file__: logFile = '%s.log' % __file__[:__file__.rfind('.')]
else: logFile = 'fmtSelenium.log'
#logging.basicConfig(filename=logFile,level=logging.INFO)
log = logging.getLogger('fmtSelenium')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logFile)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s::%(name)s::%(levelname)s: %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)
startTime = time.time()
def elapsed(): return (time.time() - startTime).__format__('.2f')

class fmtSelenium(object):
  def __init__(self):
    self.fmt_username, self.fmt_password = '', ''
    self.login_url = 'https://www.fitocracy.com/accounts/login'
    self.logout_url = 'https://www.fitocracy.com/accounts/logout/' 
    self.profile_url = '' # depends on username
    self.error_msg = '' # depends on error occuring
    self.display = Display(visible=0, size=(800, 600))
    log.info('Launching Xvfb display... %s sec', elapsed()) 
    self.display.start()
    log.info('Launching Firefox: %s sec', elapsed()) 
    self.driver = webdriver.Firefox()

  def fitocracy_login(self, username=None, password=None):
    if username: self.fmt_username = username
    if password: self.fmt_password = password
    self.profile_url = 'https://www.fitocracy.com/profile/%s' % self.fmt_username
    log.debug('username: %s', self.fmt_username)
    log.debug('password: %s', self.fmt_password)
    log.debug('login_url: %s', self.login_url) 
    log.debug('profile_url: %s', self.profile_url)
    log.info('Retrieving %s... %s sec', self.login_url, elapsed())
    self.driver.get(self.login_url)
    log.info('Clicking Login... %s sec', elapsed())
    loginButton = self.driver.find_element_by_class_name('login-button')
    loginButton.click()
    log.info('Clicking login-with-username... %s sec', elapsed()) 
    withUsernameLink = self.driver.find_element_by_class_name('login-username-link')
    withUsernameLink.click()
    log.info('Typing in username/password... %s sec', elapsed()) 
    loginUsername = self.driver.find_element_by_id('username-login-username')
    loginPassword = self.driver.find_element_by_id('username-login-password')
    loginUsername.send_keys(self.fmt_username)
    loginPassword.send_keys(self.fmt_password)
    log.info('Clicking Submit... %s sec', elapsed()) 
    withUsernameSubmit = self.driver.find_element_by_id('username-login-submit')
    withUsernameSubmit.click()
    log.info('Logging in... %s sec', elapsed())
    time.sleep(5)
    try: 
      self.driver.find_element_by_class_name('wrapper-logged-in').is_displayed()
    except NoSuchElementException:
      #self.error_msg += self.driver.find_element_by_class_name('error').text
      #log.info('Login Faliure %s... %s sec', self.error_msg, elapsed())
      #...research how to grab text inside error div on login faliure [[toDo]] 
      log.info('Login Faliure - check user/pass: %s / %s ... %s sec', \
                self.fmt_username, self.fmt_password, elapsed())
      return False
    except:
      log.info('Unknown Login Faliure... %s sec', elapsed())
      return False 
    log.info('Login Sucess... %s sec', elapsed())
    return True

  def getActivities(self, activity=None):
    if not activity: 
      activity = 'workout' # types: workout, status, levelup
      # this func should return activity tuple, not activities dict [[toDo]]
    log.info('Redirecting to user profile... %s sec', elapsed()) 
    self.driver.get(self.profile_url)
    time.sleep(2)
    fitEvents = self.driver.find_elements_by_class_name('stream_item')
    activities = {}
    log.info('Retrieving profile events... %s sec', elapsed())
    for event in fitEvents:   
      k = event.get_attribute('data-ag-type')
      v = event.text
      activities.setdefault(k, []).append(v)    
    #return activities # entire dict with types as key and activity tuple as val
    return activities.get(activity) 

  def fitocracy_logout(self):
    log.info('Logging out of fitocracy.com... %s sec', elapsed())
    self.driver.get(self.logout_url)
    return True

if __name__ == '__main__':
  """ Display activities for a fitocracy.com user """
  log.info('Launched %s from command line... %s sec', __file__, elapsed())
  username, password = 'YOUR-FITOCRACY-USERNAME', 'YOUR-FITOCRACY-PASSWORD'
  fmtActivities = fmtSelenium() # launch Xvfb and Firefox
  fmtLoggedIn = fmtActivities.fitocracy_login(username, password) 
  if fmtLoggedIn: 
    print fmtActivities.getActivities() 
  else: 
    print "Login Faliure - check user/pass: %s / %s" % (username, password)
