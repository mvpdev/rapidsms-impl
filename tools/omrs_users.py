#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin, rgaudin

LOGIN_URL = 'loginServlet'
USER_FORM_URL = 'admin/users/user.form'

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9090)
socket.socket = socks.socksocket
import random, string
from re import search as re_match
from cookielib import CookieJar
from urllib import urlencode
from urllib2 import Request, HTTPCookieProcessor, urlopen, build_opener

class CreateUserException(Exception):
    pass

class OmrsBot(object):
    def __init__(self, host, port, base_dir, username, password):
        self.base = "http://%(host)s:%(port)d/" % \
                    {'host': host, 'port': port }
        self.cookiejar = CookieJar()
        self.username = username
        self.password = password
        self.opener = build_opener(HTTPCookieProcessor(self.cookiejar))

        if base_dir:
            self.base = "%(base)s%(dir)s/" % \
                        {'base': self.base, 'dir': base_dir.strip('/')}

    def login(self):
        data = urlencode({'uname': self.username, 'pw': self.password})
        url = self.base + LOGIN_URL
        response = self.opener.open(url, data).read()
        if response.find('userLoggedInAs') == -1:
            raise Exception("Error logging in")

    def create_user(self, first, last, gender='M',
                    username=None, password=None, role='Provider'):
        url = self.base + USER_FORM_URL

        if not first:
            raise CreateUserException("Given name can't be blank")
        first_names = first.split()

        if not last:
            raise CreateUserException("Family name can't be blank")

        if not username:
            username = ''.join([c[0] for c in first_names] + [last]).lower()

        if not password:
            password = []
            for i in range(0,3):
                password += [random.choice(string.digits), \
                             random.choice(string.lowercase)]
            random.shuffle(password)
            password = ''.join(password)
        else:
            if len(password) < 6 or \
               not (re_match('\d', password) and \
                    re_match('[a-zA-Z]', password)) or \
               re_match('\s', password):
                raise CreateUserException("Password must be at least six " \
                                          "characters and contain at least " \
                                          "one letter and number")

        params = {}
        if len(first_names) > 1:
            params.update({'names[0].middleName': first_names.pop().title()})

        params.update({'names[0].givenName': ' '.join(first_names).title(),
                       'names[0].familyName': last.title(),
                       'gender': gender,
                       'username': username.lower(),
                       'userFormPassword': password,
                       'confirm': password,
                       'roleStrings': role})

        data = urlencode(params)
        response = self.opener.open(url, data).read()
        if response.find('Username or System Id taken') != -1:
            raise CreateUserException("Username taken")
        #print response


def create_omrs(csv_file, password=u"cc2010", host='192.168.5.202', \
                port=8080, base_url_dir='openmrs', omrs_username='admin', \
                omrs_password='test'):

    ''' create OpenMRS user accounts from CSV file

    FORMAT of CSV:
    | Last Name | First Name | GENDER

    GENDER: M/F '''

    bot = OmrsBot(host, port, base_url_dir, omrs_username, omrs_password)
    bot.login()

    try:
        fhandler = open(csv_file)
    except IOError:
        print "Unable to open file %s" % csv_file
        exit(1)

    cptr = 1

    for line in fhandler:

        data = line.strip().split(',')
        first_name = data[1].strip().title()
        last_name = data[0].strip().title()
        gender = data[2].strip().upper()

        # username
        first_names = first_name.split()
        username = ''.join([c[0] for c in first_names] + [last_name]).lower()

        print "%s %s, %s" % (first_name, last_name, gender)

        try:
            bot.create_user(first_name, last_name, username=username, \
                            password=password, gender=gender)
        except CreateUserException, e:
            if e.message == u"Username taken":
                username = '%s%s' % (username, cptr)
                bot.create_user(first_name, last_name, username=username, \
                                password=password, gender=gender)
                cptr += 1             
            else:
                raise
