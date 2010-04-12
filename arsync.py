#!/usr/bin/env python

# Creates links from petabox SVN tree to git working copy.
# Will probably not work *and* eat your babies.
#
# mang chez archive.org

import pipes
import commands
import re
import os
import shutil

from optparse import OptionParser

# Map of git dirs -> SVN dirs
gitToSVN = {
    'BookReader': 'sf/bookreader',
    'BookReaderIA/inc': 'common',
    'BookReaderIA/www': 'sf/bookreader',
    'BookReaderIA/datanode': 'datanode/BookReader'
}

gitRoot = '~/bookreader'
svnRoot = '~/petabox/www'

# Returns true if file is up to date
def isClean(filename):
    status = svnStatus(filename)
    if (re.search(r'^ ', status)):
        return True
    else:
        return False
        
def svnStatus(filename):
    quotedFilename = pipes.quote(filename)
    cmd = 'svn stat -v %s' % quotedFilename
    output = commands.getoutput(cmd)
    return output[0]

# Symlink src to dest 
def linkFile(src, dest, force=False):
    if (os.path.islink(dest) and os.path.realpath(src) == os.path.realpath(dest)):
	# already linked
	return

    if (not os.path.exists(dest)):
        os.symlink(src, dest)
    elif (force or isClean(dest)): # file exists
        os.remove(dest)
        os.symlink(src, dest)
    else:
        raise Exception('Destination %s is not up to date' % dest)

def linkDirectory(src, dest, force=False):

    for file in os.listdir(src):
        # Recursively handle sub-directories
        if os.path.isdir(os.path.join(src, file)):
            linkDirectory(os.path.join(src, file), os.path.join(dest, file), force)
            continue
            
        srcFile = os.path.join(src, file)
        destFile = os.path.join(dest, file)
        # print "  %s -> %s" % (srcFile, destFile)
        print "    %s" % (file)
        linkFile(srcFile, destFile, force)
        
def raiseError(message):
    print "ERROR: %s" % message
    raise Exception(message)
    

def linkSVNtoGit(gitRoot, svnRoot, force=False):
    global gitToSVN
    
    #gitDir = os.path.expanduser(gitRoot)
    #cvsDir = os.path.expanduser(cvsRoot)
    
    for srcDir, destDir in gitToSVN.items():
        srcDir = os.path.join(gitRoot, srcDir)
        destDir = os.path.join(svnRoot, destDir)
        
        print "Linking files in %s to %s" % (srcDir, destDir)
        srcDir = os.path.expanduser(srcDir)
        destDir = os.path.expanduser(destDir)
        
        linkDirectory(srcDir, destDir, force)
        
    print "Files in SVN working copy are now LINKS to git working copy"
        
def copyGitToSVN(gitRoot, svnRoot, force=False):
    global gitToSVN
    
    for srcDir, destDir in gitToSVN.items():
        srcDir = os.path.join(gitRoot, srcDir)
        destDir = os.path.join(svnRoot, destDir)
        
        print "Copying files in %s to %s" % (srcDir, destDir)
        srcDir = os.path.expanduser(srcDir)
        destDir = os.path.expanduser(destDir)
        
        copyFiles(srcDir, destDir, force)
        
    print "Files in SVN working copy are now REGULAR files ready for checkin"
    
def copySVNtoGit(gitRoot, svnRoot, force=False):
    """
    $$$ Not fully implemented.
    """
    global gitToSVN
    
    for gitDir, svnDir in gitToSVN.items():
        gitDir = os.path.join(gitRoot, gitDir)
        svnDir = os.path.join(svnRoot, svnDir)
        
        print "Copying files in %s to %s" % (svnDir, gitDir)
        gitDir = os.path.expanduser(gitDir)
        svnDir = os.path.expanduser(svnDir)
        
        for file in os.listdir(gitDir):
            srcFile = os.path.join(svnDir, file)
            destFile = os.path.join(gitDir, file)
            
            if (os.path.isdir(srcFile)):
                print "  Skipping directory %s" % srcFile
            else:
                # print "  Copying %s -> %s" % (srcFile, destFile)
                shutil.copy(srcFile, destFile)
        
    print "Files in SVN working copy are now REGULAR files ready for checkin"
        
def copyFiles(srcDir, destDir, force=False):
    for file in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, file)
        destFile = os.path.join(destDir, file)
        if os.path.isdir(srcFile):
            copyFiles(srcFile, destFile, force)
            continue
        
        # $$$ if the file does not exist we should copy then add to SVN
        
        if (force or os.path.islink(destFile) or isClean(destFile)):
            print "    %s" % (file)
            try:
                os.remove(destFile)
            except OSError:
                pass
            shutil.copy(srcFile, destFile)
        else:
            raise Exception("Destination file %s is not clean" % destFile)
        
def main():
    parser = OptionParser()
    parser.add_option('-l', '--link',
        help="Create symlinks in SVN working dir point to git working dir",
        action="store_true",
        default=False)
    parser.add_option('-g', '--git2svn',
        help="Copy files from git working dir to SVN working dir",
        action="store_true",
        default=False)
    parser.add_option('-s', '--svn2git',
        help="Copies files that exist in git from svn to git",
        action="store_true",
        default=False)
    parser.add_option('', '--gitroot', help="Git root dir (default %default)", default="~/bookreader")
    parser.add_option('', '--svnroot', help="SVN www dir (default %default)", default="~/petabox/www")
    parser.add_option('-f', '--force',
        help="Overide modification checks. (Ready, fire, aim!)",
        default=False,
        action="store_true")

    (options, args) = parser.parse_args()
    
    if (options.link):
        linkSVNtoGit(options.gitroot, options.svnroot, options.force)
        
    elif (options.git2svn):
        copyGitToSVN(options.gitroot, options.svnroot, options.force)
        
    elif (options.svn2git):
        copySVNtoGit(options.gitroot, options.svnroot, options.force)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
