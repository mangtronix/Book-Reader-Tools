#!/usr/bin/env python

#    Launchpad helper
#    Written by Michael Ang <http://github.com/mangtronix>
#
#    A bit of a mish-mash: could be refactored.
#
#    This file is part of Internet Archive BookReader Tools
#
#    BookReader Tools is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BookReader Tools is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with BookReader Tools.  If not, see <http://www.gnu.org/licenses/>.

from launchpadlib.launchpad import Launchpad, STAGING_SERVICE_ROOT, EDGE_SERVICE_ROOT
from launchpadlib.credentials import Credentials

import launchpadlib

import os.path
import string
import commands
import optparse

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

  def migrate(self, oldProjectName, newProjectName):
    oldProject = self.launchpad.projects[oldProjectName]
    newProject = self.launchpad.projects[newProjectName]
    
    # Find open milestones
    #  Create milestone in new project
    
    # Find open tasks
    tasks = oldProject.searchTasks() # All open tasks
    
    # For each bug
    for oldTask in tasks:
        bug = oldTask.bug
        print "Processing %s - %s" % (bug, bug.title)
        
        #  Also affects new project
        if not newProject.self_link in [task.target.self_link for task in bug.bug_tasks]:
            newTask = bug.addTask(target = newProject)
            
            #  Status
            newTask.status = oldTask.status
            
            #  Importance
            newTask.importance = oldTask.importance
            
            #  Assigned to
            newTask.assignee = oldTask.assignee
            
            #  Milestone
            if oldTask.milestone:
                milestoneName = oldTask.milestone.self_link.split('/')[-1] # Yuck
                newMilestone = newProject.getMilestone(name = milestoneName)
                if not newMilestone:
                    raise Exception("Couldn't find milestone %s" % milestoneName)
                else:
                    newTask.milestone = newMilestone
            
            newTask.lp_save()
        
  def getProject(self, projectName):
    return self.launchpad.projects[projectName]
    
  def getMilestone(self, project, milestoneName):
    return project.getMilestone(name = milestoneName)
    
  def getOpenTasks(self, project):
    return project.searchTasks(status = ['New','Confirmed','Triaged','In Progress','Unknown'])
    
  def changeMilestone(self, projectName, oldMilestoneName, newMilestoneName):
    """Change tasks from old milestone to new milestone"""
    project = self.getProject(projectName)
    newMilestone = self.getMilestone(project, newMilestoneName)
    if not newMilestone:
        raise Exception("Couldn't fine milestone %s" % newMilestoneName)
    tasks = self.tasksForMilestone(projectName, oldMilestoneName)
    suffix = ''
    for task in tasks:
        task.milestone = newMilestone
        task.lp_save()
    
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
    # lph = getLphStaging()
    lph = getLphEdge()
    
    # playAround(lph)
    
    # dumpMilestoneTasks(lph, "gnubook", "0.9.11")    
    # transitionToReleased(lph, "gnubook", "0.9.10")
    # dumpMilestoneTasks(lph, "gnubook", "0.9.10")
    # lph.changeMilestone('bookreader', 'r25', 'r26')

if __name__ == "__main__":
    main()
