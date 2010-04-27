#!/usr/bin/env python

import optparse
import simplejson as json
import urllib
import urllib2

def rawSearch(searchQuery):
    """Return search results as JSON string, including search result wrapper"""
    
    # We add to just search for scanned books
    searchUrl = "http://www.archive.org/advancedsearch.php?q=" + urllib.quote_plus(searchQuery) + "+AND+mediatype%3A%28texts%29+AND+format%3A%28Single+Page+Processed%29&fl%5B%5D=identifier&fl%5B%5D=title&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=50&page=1&output=json&save=yes"
    f = urllib2.urlopen(searchUrl)
    json = f.read()
    f.close()
    return json

def search(searchQuery):
    """Returns python array of search results"""
    raw = rawSearch(searchQuery)    
    wrappedResult = json.loads(raw) 
    return extractSearchResults(wrappedResult)
    
def extractSearchResults(wrappedResults):
    # Gee, some error checking would be nice
    return wrappedResults['response']['docs']
    
def getItemJson(itemId):
    url = "http://www.archive.org/details/%s?output=json" % itemId
    
    # print "Getting %s json from %s" % (itemId, url)
    f = urllib2.urlopen(url)
    json = f.read()
    f.close()
    return json
    
def getBookJson(itemId):
    itemInfo = json.loads(getItemJson(itemId))
    
    itemInfo['itemId'] = itemId
    itemInfo['bookId'] = itemId     # NB: doesn't work if the bookId and itemId are not the same
    
    # XXX using /~mang
    bookJsonUrl = "http://%(server)s/~mang/BookReader/BookReaderJSON.php?itemId=%(itemId)s&bookId=%(bookId)s&server=%(server)s&itemPath=%(dir)s" % itemInfo
    
    print "Getting %s book json from %s" % (itemId, bookJsonUrl) # XXX
    f = urllib2.urlopen(bookJsonUrl)    
    bookJson = f.read()
    f.close()
    return bookJson
    
def getBookInfo(itemId):
    return json.loads(getBookJson(itemId))
    
def getCoverUrls(bookInfo):
    if bookInfo.has_key('coverImages'):
        return bookInfo['coverImages']
    else:
        return []

def getTitleUrl(bookInfo):
    if bookInfo.has_key('titleImage'):
        return bookInfo['titleImage']
    else:
        return None
        
def getPreviewUrl(bookInfo):
    if bookInfo.has_key('previewImage'):
        return bookInfo['previewImage']
    else:
        return None
        
def retrieveUrl(url, destFilename):
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print "  WARNING: Error retrieving %s - %s" % (destFilename, e.msg)
        print "  url: %s" % url
        return e.code, e.headers
    
    chunkSize = 4 * 1024
    destFile = open(destFilename, 'wb')
    while True:
        chunk = response.read(chunkSize)
        if not chunk:
            break
        destFile.write(chunk)
    
    return response.code, response.headers
    
def main():
    searchResults = search('title:round')
    
    #searchResults = [{'title':'Manual test', 'identifier': 'permstestbook'}]
    
    print "Found %d search results" % len(searchResults)
    
    for searchResult in searchResults:
        identifier = searchResult['identifier']
        print "Book title from search results: %s" % searchResult['title'][:50]
        bookInfo = getBookInfo(identifier)
        print "Book title from book info: %s" % (bookInfo['title'][:50])
        coverUrls = getCoverUrls(bookInfo)
        titleUrl = getTitleUrl(bookInfo)
        previewUrl = getPreviewUrl(bookInfo)
        
        if previewUrl:
            print "  Preview: %s" % previewUrl
            # XXX need to check for 403 and other codes
            status, headers = retrieveUrl(previewUrl, "%s_preview.jpg" % identifier)
            print "    Status: %s" % status
            #print "    Headers:"
            #print headers
        
        if titleUrl:
            print "  Title: %s" % titleUrl
            status, headers = retrieveUrl(titleUrl, '%s_title.jpg' % identifier)
            # print "  Title Headers:"
            # print headers
        
        if len(coverUrls) > 0:
            for coverUrl in coverUrls:
                print "  Cover: %s" % coverUrl
            status, headers = retrieveUrl(coverUrls[0], '%s_cover.jpg' % identifier)        
            # print "  Cover Headers:"
            # print headers

if __name__ == "__main__":
    main()
