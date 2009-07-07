#!/usr/bin/env python

#    Launchpad helper
#    Written by Michael Ang <mang chez archive.org>
#
#    This file is part of Bookreader Tools
#
#    Bookreader Tools is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Bookreader Tools is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Bookreader Tools.  If not, see <http://www.gnu.org/licenses/>.

from launchpadlib.launchpad import Launchpad, STAGING_SERVICE_ROOT, EDGE_SERVICE_ROOT
from launchpadlib.credentials import Credentials

import launchpadlib

import os.path
import string
import commands

class LaunchpadHelper:

  def __init__(self, cacheDir, username, service = STAGING_SERVICE_ROOT):
    self.cacheDir = cacheDir
    self.service = service
    self.launchpad = None
    self.username = username
    self.credentialsFilename = os.path.join(cacheDir, 'credentials.txt')
    
  def login(self):
    self.launchpad = Launchpad.get_token_and_login(self.username, self.service, self.cacheDir)

  def saveAuthentication(self):
    self.launchpad.credentials.save(file(self.credentialsFilename, 'w'))
    
  def authenticateFromSaved(self):
    credentials = Credentials()
    credentials.load(file(self.credentialsFilename, 'r'))
    self.launchpad = Launchpad(credentials, self.service, self.cacheDir)

  def authenticate(self):
    if (os.path.exists(self.credentialsFilename)):
        try:
            self.authenticateFromSaved()
            return
        except launchpadlib.errors.HTTPError:
            pass

    self.login()
    self.saveAuthentication()
      
  def serviceRoot(self):
    return self.service
    
  def tasksForMilestone(self, projectName, milestoneName):
    project = self.launchpad.projects[projectName]
    milestone = project.getMilestone(name = milestoneName)
    milestoneTasks = project.searchTasks(milestone = milestone)
    return milestoneTasks
    
    
#### Some play functions
    
def helloWorld(lph):
    bug_one = lph.launchpad.bugs[1]
    print bug_one.title
    
def playAround(lph):
    gnubook = lph.launchpad.projects['gnubook']
    bookserver = lph.launchpad.projects['bookserver']
    milestone99 = gnubook.getMilestone(name='0.9.9')
    milestoneBugTasks = gnubook.searchTasks(milestone = milestone99)
    
    for bugTask in milestoneBugTasks:
      bug = bugTask.bug
      print bug.title
      print "  " + string.join([task.bug_target_name for task in bug.bug_tasks], ', ')
      
      hasBookServer = False
      for task in bug.bug_tasks:
        if task.target.self_link == bookserver.self_link:
          hasBookServer = True
      if not hasBookServer:
        print "  Adding target"
        # bug.addTask(target = bookserver)
        # bug.lp_refresh()
        # print "    " + string.join([task.bug_target_name for task in bug.bug_tasks], ', ')

def dumpMilestoneTasks(lph, projectName, milestoneName):
    tasks = lph.tasksForMilestone(projectName, milestoneName)
    for task in tasks:
      print "%s - %s - %s" % (task.milestone, task.status, task.title)


def transitionToReleased(lph, projectName, milestoneName):
    tasks = lph.tasksForMilestone(projectName, milestoneName)
    for task in tasks:
        task.transitionToStatus(status = 'Fix Released')
        
def addTags(lph, projectName, milestoneName, tags):
    tasks = lph.tasksForMilestone(projectName, milestoneName)
    for task in tasks:
        bug = task.bug
        newTags = {}
        for tag in tags:
            newTags[tag] = True
        for tag in bug.tags:
            newTags[tag] = True
        bug.tags = newTags.keys()            
        bug.lp_save()
                
# Get a live Launchpad Helper
def getLphEdge():
    cacheDir = os.path.expanduser('~/.lpcache_edge')
    user = commands.getoutput('whoami')
    lph = LaunchpadHelper(cacheDir, user, EDGE_SERVICE_ROOT)
    lph.authenticate()
    return lph
    
def getLphStaging():
    cacheDir = os.path.expanduser('~/.lpcache_staging')
    user = commands.getoutput('whoami')
    print '%s - %s' % (cacheDir, user)
    lph = LaunchpadHelper(cacheDir, user, STAGING_SERVICE_ROOT)
    lph.authenticate()
    return lph
     
#### Main

def main():
    lph = getLphStaging()
    # lph = getLphEdge()
    
    # playAround(lph)
    
    dumpMilestoneTasks(lph, "gnubook", "0.9.11")    
    # transitionToReleased(lph, "gnubook", "0.9.10")
    # dumpMilestoneTasks(lph, "gnubook", "0.9.10")

if __name__ == "__main__":
    main()
