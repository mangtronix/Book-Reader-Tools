#!/usr/bin/env python

#    Create links from petabox CVS tree to git working copy
#    Will probably not work *and* eat your babies.
#
#    Written by Michael Ang <mang chez archive.org>
#
#    This file is part of Bookreader Tools.
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

import pipes
import commands
import re
import os

# Map of git dirs -> CVS dirs
gitToCVS = {
    'GnuBook': 'sf/bookreader',
    'GnuBookIA/inc': 'common',
    'GnuBookIA/www': 'sf/bookreader',
    'GnuBookIA/datanode': 'datanode/GnuBook'
}

gitRoot = '~/bookreader'
cvsRoot = '~/petabox/www'

# Returns true if file is up to date with CVS
def isClean(filename):
    quotedFilename = pipes.quote(filename)
    cmd = 'cvs status %s' % quotedFilename
    output = commands.getoutput(cmd)
    # print "%s => %s" % (cmd, output)
    if (re.search(r'Status: Up-to-date', output, re.MULTILINE)):
        return True
    else:
        return False

# Symlink src to dest if dest is clean
def linkFile(src, dest):
    if (os.path.islink(dest) and os.path.realpath(src) == os.path.realpath(dest)):
	# already linked
	return

    if (not isClean(dest)):
        raise 'Destination %s is not up to date' % dest
        
    os.remove(dest)
    os.symlink(src, dest)

def linkDirectory(src, dest):
    print "Linking files in %s to %s" % (src, dest)

    for file in os.listdir(src):
        # Recursively handle sub-directories
        if os.path.isdir(os.path.join(src, file)):
            linkDirectory(os.path.join(src, file), os.path.join(dest, file))
            continue
            
        srcFile = os.path.join(src, file)
        destFile = os.path.join(dest, file)
        print "  %s -> %s" % (srcFile, destFile)
        linkFile(srcFile, destFile)
        
def raiseError(message):
    print "ERROR: %s" % message
    raise message


def main():
    global gitToCVS, gitRoot, cvsRoot
    
    #gitDir = os.path.expanduser(gitRoot)
    #cvsDir = os.path.expanduser(cvsRoot)
    
    for srcDir, destDir in gitToCVS.items():
        srcDir = os.path.join(gitRoot, srcDir)
        destDir = os.path.join(cvsRoot, destDir)
        
        srcDir = os.path.expanduser(srcDir)
        destDir = os.path.expanduser(destDir)
        
        linkDirectory(srcDir, destDir)


if __name__ == "__main__":
    main()
