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
        self.Subject = ''
        self.SubjectTransliterated = ''
        self.Body = ''
        self.isVisible = False

    def transliterate(self,string):
        ''' cut from https://gist.github.com/aruseni/1685068 '''
        capital_letters = {u'А':u'A', u'Б':u'B', u'В':u'V', u'Г':u'G', u'Д':u'D', 
        u'Е':u'E', u'Ё':u'E', u'З':u'Z', u'И':u'I', u'Й':u'Y', u'К':u'K', 
        u'Л':u'L', u'М':u'M', u'Н':u'N', u'О':u'O', u'П':u'P', u'Р':u'R', 
        u'С':u'S', u'Т':u'T', u'У':u'U', u'Ф':u'F', u'Х':u'H', u'Ъ':u'', 
        u'Ы':u'Y', u'Ь':u'', u'Э':u'E',}

        capital_letters_transliterated_to_multiple_letters = {u'Ж':u'Zh', u'Ц':u'Ts', 
                                                              u'Ч':u'Ch', u'Ш':u'Sh', 
                                                              u'Щ':u'Sch', u'Ю':u'Yu', 
                                                              u'Я':u'Ya',}


        lower_case_letters = {u'а':u'a', u'б':u'b', u'в':u'v', u'г':u'g', 
        u'д':u'd', u'е':u'e', u'ё':u'e', u'ж':u'zh', u'з':u'z', u'и':u'i', 
        u'й':u'y', u'к':u'k', u'л':u'l', u'м':u'm', u'н':u'n', u'о':u'o', 
        u'п':u'p', u'р':u'r', u'с':u's', u'т':u't', u'у':u'u', u'ф':u'f', 
        u'х':u'h', u'ц':u'ts', u'ч':u'ch', u'ш':u'sh', u'щ':u'sch', 
        u'ъ':u'', u'ы':u'y', u'ь':u'', u'э':u'e', u'ю':u'yu', u'я':u'ya',}

        capital_and_lower_case_letter_pairs = {}

        for capital_letter, capital_letter_translit in capital_letters_transliterated_to_multiple_letters.iteritems():
            for lowercase_letter, lowercase_letter_translit in lower_case_letters.iteritems():
                capital_and_lower_case_letter_pairs[u"%s%s" % (capital_letter, lowercase_letter)] = u"%s%s" % (capital_letter_translit, lowercase_letter_translit)

        for dictionary in (capital_and_lower_case_letter_pairs, capital_letters, lower_case_letters):

            for cyrillic_string, latin_string in dictionary.iteritems():
                string = string.replace(cyrillic_string, latin_string)

        for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
            string = string.replace(cyrillic_string, latin_string.upper())

        return string

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
            #print 'A ATTRS %s'%attrs
            for attrpair in attrs:
                (attr,value) = attrpair
                if attr == 'href':
                    self.fed.append('[[%s '%value)
        if tag == 'CODE' or tag == 'PRE':
            self.fed.append('<code>')
        if tag == 'BR':
            self.fed.append('\n')
        if tag == 'TABLE':
            self.fed.append('-----')
            self.openedtable = True
        if tag == 'TD':
            self.fed.append('|')
        if tag == 'IMG':
            for attrpair in attrs:
                (attr,value) = attrpair
                if attr == 'src':
                    self.fed.append('<img src=\"%s\">'%value)
            #print 'IMG %s'%attrs

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
        if tag == 'CODE' or tag == 'PRE':
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
    #print "="*50,"\n",sbody.get_data()
    #print "="*50,"\n",body
    return sbody.get_data()

def ParsePost(post):
    CurrentPost = PostTemplate()
    if 'id' in post:
        print 'PostID: %s'%post['id']
        CurrentPost.Id = post['id']
    if 'date' in post:
        CurrentPost.Stamp = datetime.datetime.strptime(post['date'],'%Y-%m-%d %H:%M:%S')
    if 'eventtime' in post:
        CurrentPost.LastModified = datetime.datetime.strptime(post['eventtime'],'%Y-%m-%d %H:%M:%S')
    if 'subject' in post:
        CurrentPost.Subject = post['subject']
        CurrentPost.SubjectTransliterated = CurrentPost.transliterate(post['subject']).replace(' ','-')[:64]
    if 'security' in post:
        CurrentPost.isVisible = 1 if post['security'] == 'public' else 0
    if 'body' in post:
        CurrentPost.Body = ReformatBody(post['body'])
#    for item in post:
#        print item.encode(),'---->',post[item]
    print 'Date: %s'%CurrentPost.Stamp
    print 'LastModified: %s'%CurrentPost.LastModified
    print 'Subject: %s'%CurrentPost.Subject
    print 'Subject_Trans: %s'%CurrentPost.SubjectTransliterated
    print 'Body',CurrentPost.Body
    print "="*50
    

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