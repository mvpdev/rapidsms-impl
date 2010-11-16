#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: rgaudin

class FormA(object):

    def __init__(self, text=None):

        self.map = {}
     
        self.date = None

        self.health_id = None
        # +NEW
        self.location_code = None
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.dob = None
        self.hohh = None
        # +BIR
        self.mother_hid = None
        self.delivery = None
        self.weight = None
        # +MOB
        self.mobile = None

        self.init_map()

        if text:
            self.parse_line(text)
            self.post_process()

    def init_map(self):

        self.map = {
            0: 'date',
            1: 'health_id',
            2: None, # +NEW
            3: 'location_code',
            4: 'first_name',
            5: 'last_name',
            6: 'gender',
            7: 'dob',
            8: 'hohh',
            9: None, #+BIR
            10: 'mother_hid',
            11: 'delivery',
            12: 'weight',
            13: None, #+MOB
            14: 'mobile',
        }

    def post_process(self):
        pass

    def has_bir(self):
        return self.mother_hid + self.delivery

    def has_mob(self):
        return self.mobile

    def parse_line(self, text):
        data = text.split(',')
        for index, field in self.map.items():
            try:
                setattr(self, field, data[index].strip())
            except (IndexError, TypeError):
                # not in map
                pass 

    def to_sms(self):
        new = {'hid': self.health_id, 'loc': self.location_code, \
               'first': self.first_name, 'last': self.last_name, \
               'gender': self.gender, 'dob': self.dob, 'hohh': self.hohh}
        sms = u"%(hid)s +NEW %(loc)s %(first)s %(last)s %(gender)s %(dob)s " \
               "%(hohh)s" % new
        if self.has_bir():
            bir = {'mom': self.mother_hid, 'del': self.delivery, 'weight': self.weight}
            sms += u" +BIR %(mom)s %(del)s %(weight)s" % bir
        if self.has_mob():
            sms += u" +MOB %(mob)s" % {'mob': self.mobile}
        return sms

class ToyaFormA(FormA):

    def init_map(self):

        self.map = {
            0: 'date',
            1: 'health_id',
            2: None, # +NEW
            3: 'location_code',
            4: 'first_name',
            5: 'last_name',
            6: 'gender',
            7: 'dob',
            8: 'hohh',
            9: 'mother_hid',
            10: None, #+BIR
            11: 'delivery',
            12: 'weight',
            13: None, #+MOB
            14: 'mobile',
        }

    def post_process(self):

        self.add_date_year()
        self.convert_date()
        self.same_hohh()
        self.dob_add_unit()
        self.dob_5digits()
        self.mob_spaces()
        self.mob_prefix_mali()

    def add_date_year(self):
        """ Add 4-digit year at end of date """
        if self.date.__len__() == 4:
            self.date = '%s%s' % (self.date, '2010')

    def convert_date(self):
        """ convert date from ddmmYYYY to YYYY-mm-dd """
        self.date = '%s-%s-%s' % (self.date[4:8], self.date[2:4], self.date[0:2])

    def same_hohh(self):
        """ replace HoHH ID with H if same as HID """
        if self.health_id == self.hohh:
            self.hohh = 'H'

    def dob_5digits(self):
        """ replace DOB dmmYY with ddmmYY """
        if self.dob.__len__() == 5:
            self.dob = self.dob.zfill(6)

    def dob_add_unit(self):
        """ add `a` at end of DOB """
        if self.dob.__len__() <= 3:
            self.dob = '%s%s' % (self.dob, 'a')

    def mob_spaces(self):
        if self.mobile:
            self.mobile = self.mobile.replace(' ', '')

    def mob_prefix_mali(self):
        if self.mobile:
            self.mobile = '223%s' % self.mobile

URL = "http://%s:%s" % ('localhost', '1338')

def http_request(url, data):

    import urllib
    import urllib2

    req = urllib2.Request(url, urllib.urlencode(data))
    stream = urllib2.urlopen(req)
    content = stream.read()

    return content

def get_response(identity):

    import json
    import time

    data = {}
    while not 'text' in data:
        resp = http_request(URL, {'identity': identity, 'action': 'list'})
        data = json.loads(resp)
        time.sleep(0.3)
    return (data['text'], data['status'])

def send_sms(text, identity, date):

    http_request(URL, {'identity': identity, 'message': text, 'encounter_date': date, 'chw': '2'})

    return get_response(identity)


def import_csv(csv_file, handler=None):

    # select FormA class
    if handler == 'toya':
        FormClass = ToyaFormA
    else:
        FormClass = FormA

    try:
        fhandler = open(csv_file)
    except IOError:
        print "Unable to open file %s" % csv_file
        return None

    linecptr = 0
    for line in fhandler:
        linecptr += 1

        # debug
        if linecptr > 100:
            return

        # instanciate form
        form = FormClass(line)

        sms_text = form.to_sms()
        print ">>> %s" % sms_text
        response, status = send_sms(sms_text, 'mtoure', form.date)

        # mark as success if only +BIR failed due to overaged patient
        if status == 'warning' \
           and response.count(u"Echec d'un terme., Réussi:  +BIR failed:") \
           and response.count(u"Vous ne pouvez pas soumettre un compte-rendu de naissance pour les patients de plus de 28 jours., +NEW Traité avec succès"):
            status = 'success'

        if status == 'success':
            print "<<< SUCCESS"
        else:
            print "<<< (%s) %s" % (status, response)
        
