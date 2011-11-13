#!/usr/bin/env python

import sys
import json
import urllib

from xml.etree import ElementTree as et

class WorksVenn:

    def __init__(self, *isbns):
        self.isbns = isbns
        self.oclc = set()
        self.librarything = set()
        self.openlibrary = set()
        for isbn in self.isbns:
            self._add(isbn)

    def _add(self, isbn):
        self.oclc.update(xisbn(isbn))
        self.librarything.update(thingisbn(isbn))
        self.openlibrary.update(openlibrary(isbn))

    def chart_url(self):
        max_size = float(max(len(self.oclc), len(self.librarything), len(self.openlibrary)))
        max_size = float(len(self.oclc.union(self.librarything).union(self.openlibrary)))
        chd = [
            len(self.oclc) / max_size * 100,
            len(self.librarything) / max_size * 100, 
            len(self.openlibrary) / max_size * 100, 
            len(self.oclc.intersection(self.librarything)),
            len(self.oclc.intersection(self.openlibrary)), 
            len(self.librarything.intersection(self.openlibrary)),
            len(self.oclc.intersection(self.librarything).intersection(self.openlibrary))
        ]
        return "https://chart.googleapis.com/chart?chs=300x300&cht=v&chd=t:%s&chco=77FF77,7777FF,FF7777&chdl=ThingISBN|xISBN|OpenLibrary" % ",".join([str(d) for d in chd])

def thingisbn(isbn):
    url = "http://www.librarything.com/api/thingISBN/%s" % isbn
    doc = et.parse(urllib.urlopen(url))
    return set([e.text for e in doc.findall('.//isbn')])

def xisbn(isbn):
    url = "http://xisbn.worldcat.org/webservices/xid/isbn/%s?method=getEditions&format=xml" % isbn
    doc = et.parse(urllib.urlopen(url))
    return set([e.text for e in doc.findall('.//{http://worldcat.org/xid/isbn/}isbn')])

def openlibrary(isbn):
    try:
        url = 'http://openlibrary.org/api/books?bibkeys=ISBN:%s&jscmd=details&format=json' % isbn
        j = json.loads(urllib.urlopen(url).read())
        work_id = j['ISBN:%s' % isbn]['details']['works'][0]['key']

        isbns = set()
        offset = 0
        while True:
            url = "http://openlibrary.org" + work_id + "/editions.json?limit=50&offset=" + str(offset)
            print url
            j = json.loads(urllib.urlopen(url).read())
            for edition in j['entries']:
                for isbn in edition.get('isbn_10', []):
                    isbns.add(isbn)
            offset += 50
            if offset > int(j['size']):
                break

        return isbns

    except Exception, e:
        print e 
        print "error when looking up %s at openlibrary" % isbn
        return set()

def c(a):
    return ",".join(map(str, a))

if __name__ == "__main__":
    isbns = sys.argv[1:]
    v = WorksVenn(*isbns)
    print "oclc: %s" % c(v.oclc)
    print "librarything: %s" % c(v.librarything)
    print "openlibrary: %s" % c(v.openlibrary)
    print "oclc \\ librarything: " + c(v.oclc - v.librarything)
    print "oclc \\ openlibrary: " + c(v.oclc - v.openlibrary)
    print "librarything \\ oclc: ", c(v.librarything - v.oclc)
    print "librarything \\ openlibrary: ", c(v.librarything - v.openlibrary)
    print "openlibrary \\ oclc: ", c(v.openlibrary - v.oclc)
    print "openlibrary \\ librarything: ", c(v.openlibrary - v.librarything)
    print "chart: ", v.chart_url()


