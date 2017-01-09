#!/bin/env python2
# -*- coding: utf8 -*-

import json
import requests
import codecs
import pprint
import sys
from HTMLParser import HTMLParser
import datetime

class PostTemplate():
    def __init__(self):
        self.Id = 0
        self.Stamp = datetime.datetime.today()
        self.LastModified = datetime.datetime.today()

class TagsChanger(HTMLParser):
    def __init__(self):
        self.reset()
        self.allowappend = False
        self.openedtable = False
        self.fed = []

    def handle_data(self, d):
        if self.openedtable:
            self.fed.append(d)
        else:
            self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    def handle_starttag(self, tag, attrs):
        """ Handle start tag """
        tag = tag.upper()
        if tag == 'B':
            self.fed.append('**')
        if tag == 'I':
            self.fed.append('//')
        if tag == 'S':
            self.fed.append('--')
        if tag == 'A':
            print 'A ATTRS %s'%attrs
            for attrpair in attrs:
                (attr,value) = attrpair
                if attr == 'href':
                    self.fed.append('[[%s '%value)
        if tag == 'CODE':
            self.fed.append('<code>')
        if tag == 'BR':
            self.fed.append('\n')
        if tag == 'TABLE':
            self.fed.append('-----')
            self.openedtable = True
        if tag == 'TD':
            self.fed.append('|')

    def handle_endtag(self, tag):
        """ Handle end tag """
        tag = tag.upper()
        if tag == 'B':
            self.fed.append('**')
        if tag == 'I':
            self.fed.append('//')
        if tag == 'S':
            self.fed.append('--')
        if tag == 'A':
            self.fed.append(']]')
        if tag == 'CODE':
            self.fed.append('</code>')
#        if tag == 'BR':
#            self.fed.append('\n')
        if tag == 'TABLE':
            self.fed.append('-----\n')
            self.openedtable = False
        if tag == 'TR':
            self.fed.append('|')

def ReformatBody(body):
    sbody = TagsChanger()
    sbody.feed(body.replace(u'&nbsp;', ' '))
    print sbody.get_data()

def ParsePost(post):
    CurrentPost = PostTemplate()
    if 'id' in post:
        print 'PostID: %s'%post['id']
        CurrentPost.Id = post['id']
    if 'date' in post:
        print 'Post Date %s'%datetime.datetime.strptime(post['date'],'%Y-%m-%d %H:%M:%S')
        CurrentPost.Stamp = datetime.datetime.strptime(post['date'],'%Y-%m-%d %H:%M:%S')
    if 'eventtime' in post:
        print 'LastModified %s'%datetime.datetime.strptime(post['eventtime'],'%Y-%m-%d %H:%M:%S')
        CurrentPost.LastModified = datetime.datetime.strptime(post['eventtime'],'%Y-%m-%d %H:%M:%S')
    if 'body' in post:
        ReformatBody(post['body'])
#    for item in post:
#        print item.encode(),'---->',post[item]
    

def main():
    if len(sys.argv) < 1:
        sys.exit(1)
    with codecs.open(sys.argv[1], encoding='cp1251') as fh:
        JSONedPosts = json.loads(fh.read())
	if 'post' in JSONedPosts:
	    ParsePost(JSONedPosts['post'])
        else:		
            for post in JSONedPosts:
                ParsePost(post)
    
if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    main()