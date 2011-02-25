#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: rgaudin

import re

try:
    from childcount.models import HealthId
except ImportError as e:
    print e


DEBUG=False

# URL
URL = "http://%s:%s" % ('localhost', '1338')

# stores last date from CSV.
last_date = None

# stores data from previous row
last_data = {}

TOYA_CHW_MAP = {
            1: 3,
            2: 2,
            3: 10,
            4: 5,
            5: 6,
            6: 7,
            7: 13,
            8: 8,
            9: 9,
            10: 4,
            11: 11,
            12: 12,
        }

def data_reset():
    """ remove all values in last_data """
    global last_data
    last_data = {}

def data_change(field, value):
    """ update value for field on last_data """
    global last_data
    last_data[field] = value

def data_update(all_values):
    """ replace last_data with passed dictionnary """
    if not all_values.__class__ == dict:
        raise ValueError(u"must be a %s" % dict)
    global last_data
    last_data = all_values

def data_get(field):
    """ return value in last_data for requested field """
    global last_data
    try:
        return last_data[field]
    except IndexError:
        return None

def data_all():
    """ return the whole last_data container """
    global last_data
    return last_data

def set_date(new_date):
    """ store new value (from form) into global variable """
    global last_date
    if re.match(r'\d{4}\-\d{2}\-\d{2}', new_date):
        data = new_date.split('-')
        nd = "%s%s%s" % (data[0], data[1], data[2])
        last_date = nd
    else:
        data = new_date.split('-')
        nd = "%s%s%s" % (data[2], data[1], data[0])
        last_date = nd
    return last_date


def get_date():
    """ retrieve global variable last_date """
    global last_date
    return last_date
    

def http_request(url, data):
    """ Sends POST call to URL with DATA and return result """
    import urllib
    import urllib2

    req = urllib2.Request(url, urllib.urlencode(data))
    stream = urllib2.urlopen(req)
    content = stream.read()

    return content

def get_response(identity):
    """ Requests new CC+ debackend message for IDENTITY """

    import json
    import time

    data = {}
    tries = 0
    while not 'text' in data and tries < 12:
        resp = http_request(URL, {'identity': identity, 'action': 'list'})
        data = json.loads(resp)
        tries += 1
        time.sleep(0.3)
    if 'text' in data:
        return (data['text'], data['status'])
    else:
        return (u"No answer from server. Probably malformed message", 'error')
    

def send_sms(text, identity, date, chw_id):
    """ Sends CC+ debackend message TEXT fron IDENTITY on DATE as CHW """

    http_request(URL, {'identity': identity, 'message': text, \
                       'encounter_date': date, 'chw': chw_id})

    return get_response(identity)

class FormA(object):
    """ ChildCount+ A Form for Patient Registration """

    def __init__(self, text=None):

        self.map = {}

        self.chw_id = None
     
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
        self.clean_mobile()

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

    def clean_mobile(self):
        if self.mobile:
            self.mobile = re.sub(r'\D*', '', self.mobile.strip())

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

class FormB(object):
    """ ChildCount+ B Form for HouseHold Visits """

    def __init__(self, text=None):

        self.map = {}

        self.chw_id = None
        self.date = None

        self.health_id = None
        # +V
        self.hh_member_avail = None
        self.under_5 = None
        self.advices = None
        # +E
        self.sick_members = None
        self.sick_rdt = None
        self.sick_rdtpos = None
        self.sick_malarial = None
        # +L
        self.women_bcp = None
        # +K
        self.women = None
        self.women_fp = None
        self.fp_methods = None

        self.init_map()

        if text:
            self.parse_line(text)
            self.post_process()

    def init_map(self):

        self.map = {
            0: 'chw_id',
            1: 'date',
            2: 'health_id',
            3: None, # +V
            4: 'hh_member_avail',
            5: 'under_5',
            6: 'advices',
            7: None, # +E
            8: 'sick_members',
            9: 'sick_rdt',
            10: 'sick_rdtpos',
            11: 'sick_malarial',
            12: None, # +L
            13: 'women_bcp',
            14: None, #+K
            15: 'women',
            16: 'women_fp',
            17: 'fp_methods',
        }

    def post_process(self):
        pass

    def has_v(self):
        return self.hh_member_avail

    def has_e(self):
        return self.sick_members

    def has_l(self):
        return self.women_bcp

    def has_k(self):
        return self.women

    def parse_line(self, text):
        data = text.split(',')
        for index, field in self.map.items():
            try:
                setattr(self, field, data[index].strip())
            except (IndexError, TypeError):
                # not in map
                pass

    def to_sms(self):
        sms = u"%(hid)s" % {'hid': self.health_id}
        if self.has_v():
            v = {'hh_memb': self.hh_member_avail, 'und5': self.under_5, \
                 'advi': self.advices}
            sms += u" +V %(hh_memb)s %(und5)s %(advi)s" % v
        if self.has_e():
            e = {'sick': self.sick_members, 'sick_rdt': self.sick_rdt, \
                 'sick_pos': self.sick_rdtpos, 'sick_mal': self.sick_malarial}
            sms += u" +E %(sick)s %(sick_rdt)s %(sick_pos)s %(sick_mal)s" % e
        if self.has_l():
            l = {'bcp': self.women_bcp}
            sms += u" +L %(bcp)s" % l
        if self.has_k():
            k = {'women': self.women, 'women_fp': self.women_fp, \
                 'methods': self.fp_methods}
            sms += u" +K %(women)s %(women_fp)s %(methods)s" % k
        return sms

class FormC(object):
    """ ChildCount+ C Form for Individual Visits """

    def __init__(self, text=None):

        self.map = {}

        self.chw_id = None
        self.date = None

        self.health_id = None
        # +U
        self.improved = None
        self.clinic_visit = None
        # +S
        self.danger_sign = None
        # +P
        self.preg_month = None
        self.preg_num_visits = None
        self.preg_last_visit = None
        # +N
        self.neo_visits = None
        # +T
        self.breast_feed = None
        self.immun = None
        # +M
        self.muac = None
        self.oedema = None
        self.weight = None
        # +F
        self.rdtpos = None
        # +G
        self.meds = None
        # +R
        self.referral = None

        self.init_map()

        if text:
            self.parse_line(text)
            self.post_process()

    def init_map(self):

        self.map = {
            0: 'chw_id',
            1: 'date',
            2: 'health_id',
            3: None, # +U
            4: 'improved',
            5: 'clinic_visit',
            6: None, # +S
            7: 'danger_sign',
            8: None, # +P
            9: 'preg_month',
            10: 'preg_num_visits',
            11: 'preg_last_visit',
            12: None, # +N
            13: 'neo_visits',
            14: None, #+T
            15: 'breast_feed',
            16: 'immun',
            17: None, # +M
            18: 'muac',
            19: 'oedema',
            20: 'weight',
            21: None, # +F
            22: 'rdtpos',
            23: None, # +G
            24: 'meds',
            25: None, # +R
            26: 'referral',
        }

    def post_process(self):
        pass

    def has_u(self):
        return self.improved + self.clinic_visit

    def has_s(self):
        return self.danger_sign

    def has_p(self):
        return self.preg_month + self.preg_num_visits + self.preg_last_visit

    def has_n(self):
        return self.neo_visits

    def has_t(self):
        return self.breast_feed + self.immun

    def has_m(self):
        return self.muac + self.oedema + self.weight

    def has_f(self):
        return self.rdtpos

    def has_g(self):
        return self.meds

    def has_r(self):
        return self.referral

    def parse_line(self, text):
        data = text.split(',')
        for index, field in self.map.items():
            try:
                setattr(self, field, data[index].strip())
            except (IndexError, TypeError):
                # not in map
                pass

    def to_sms(self):
        sms = u"%(hid)s" % {'hid': self.health_id}
        if self.has_u():
            u = {'improved': self.improved, 'clinic': self.clinic_visit}
            sms += u" +U %(improved)s %(clinic)s" % u
        if self.has_s():
            s = {'sign': self.danger_sign}
            sms += u" +S %(sign)s" % s
        if self.has_p():
            p = {'month': self.preg_month, 'num_vis': self.preg_num_visits, 'last_vis': self.preg_last_visit}
            sms += u" +P %(month)s %(num_vis)s %(last_vis)s" % p
        if self.has_n():
            n = {'visits': self.neo_visits}
            sms += u" +N %(visits)s" % n
        if self.has_t():
            t = {'breast': self.breast_feed, 'immun': self.immun}
            sms += u" +T %(breast)s %(immun)s" % t
        if self.has_m():
            m = {'muac': self.muac, 'oedema': self.oedema, 'weight': self.weight}
            sms += u" +M %(muac)s %(oedema)s %(weight)s" % m
        if self.has_f():
            f = {'rdt': self.rdtpos}
            sms += u" +F %(rdt)s" % f
        if self.has_g():
            g = {'meds': self.meds}
            sms += u" +G %(meds)s" % g
        if self.has_r():
            r = {'ref': self.referral}
            sms += u" +R %(ref)s" % r
        return sms

# TOYA
class ToyaFormA(FormA):
    """ Toya specificities on FormA """

    def init_map(self):

        self.map = {
            0: 'date',
            1: 'health_id',
            2: None, # +NEW
            3: 'location_code',
            4: 'last_name',
            5: 'first_name',
            6: 'gender',
            7: 'dob',
            8: 'hohh',
            9: 'mother_hid',
            10: None, #+BIR
            11: 'delivery',
            12: 'weight',
            13: None, # +MOB
            14: 'mobile',
            15: 'chw_id',
        }

    def post_process(self):

        self.map_chw_id()
        self.date_get_last()
        self.date_add_0month()
        self.date_add_year()
        self.convert_date()
        self.same_hohh()
        self.dob_add_unit()
        self.dob_5digits()
        self.dob_year_only()
        self.clean_mobile()
        self.mob_spaces()
        self.mob_prefix_mali()

    def map_chw_id(self):
        """ convert Toya Team CHW ID to CC+ ID """
        if self.chw_id:
            self.chw_id = TOYA_CHW_MAP[int(self.chw_id)].__str__()

    def date_get_last(self):
        """ if date missing, use LAST_DATE """
        if not self.date:
            self.date = get_date()

    def date_add_0month(self):
        """ replace date dmm to ddmm """
        if self.date.__len__() == 3:
            self.date = '0%s' % self.date

    def date_add_year(self):
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
        if self.dob.__len__() <= 3 and self.dob.isdigit():
            self.dob = '%s%s' % (self.dob, 'a')

    def mob_spaces(self):
        if self.mobile:
            self.mobile = self.mobile.replace(' ', '')

    def mob_prefix_mali(self):
        if self.mobile:
            self.mobile = '223%s' % self.mobile.strip().replace(' ','')

    def dob_year_only(self):
        """ converts DOB YYYY to 0101YYYY """
        if self.date.__len__() == 4:
            self.date = '0101%s' % self.date

class ToyaFormB(FormB):
    """ Toya specificities on FormB """

    def init_map(self):

        self.map = {
            0: 'chw_id',
            1: 'date',
            2: 'health_id',
            3: None, # +V
            4: 'hh_member_avail',
            5: 'under_5',
            6: 'advices',
            7: None, # +E
            8: 'sick_members',
            9: 'sick_rdt',
            10: 'sick_rdtpos',
            11: 'sick_malarial',
            12: None, #+K
            13: 'women',
            14: 'women_fp',
            15: 'fp_methods',
        }

    def date_get_last(self):
        """ if date missing, use LAST_DATE """
        if not self.date:
            self.date = get_date()

    def date_add_0month(self):
        """ replace date dmm to ddmm """
        if self.date.__len__() == 3:
            self.date = '0%s' % self.date

    def date_add_year(self):
        """ Add 4-digit year at end of date """
        if self.date.__len__() == 4:
            self.date = '%s%s' % (self.date, '2010')

    def convert_date(self):
        """ convert date from ddmmYYYY to YYYY-mm-dd """
        self.date = '%s-%s-%s' % (self.date[4:8], self.date[2:4], \
                                  self.date[0:2])

    def zero2o_hh_avail(self):
        """ replace 0 (zero) to O in HH member available field """
        if self.hh_member_avail.lower() == '0':
            self.hh_member_avail = 'o'

    def k_default_value(self):
        """ consider non-filled #of women using FPM 0 if blank """
        if self.women and not self.women_fp:
            self.women_fp = '0'

    def v_default_value(self):
        """ consider non-filled #of under5 0 if blank """
        if self.hh_member_avail.lower() in ('o','y') and not self.under_5:
            self.under_5 = '0'

    def e_default_value(self):
        """ consider non-filled +E 0 if blank """
        if self.sick_members:
            if not self.sick_rdt:
                self.sick_rdt = '0'
            if not self.sick_rdtpos:
                self.sick_rdtpos = '0'
            if not self.sick_malarial:
                self.sick_malarial = '0'

    def e_niszero(self):
        """ replace N by 0 on +E """
        if self.sick_members and self.sick_members.lower() == 'n':
            self.sick_members = '0'
        if self.sick_rdt and self.sick_rdt.lower() == 'n':
            self.sick_rdt = '0'
        if self.sick_rdtpos and self.sick_rdtpos.lower() == 'n':
            self.sick_rdtpos = '0'
        if self.sick_malarial and self.sick_malarial.lower() == 'n':
            self.sick_malarial = '0'

    def k_niszero(self):
        """ replace N by 0 on +K """
        if self.women and self.women.lower() == 'n':
            self.women = '0'
        if self.women_fp and self.women_fp.lower() == 'n':
            self.women_fp = '0'
        if self.fp_methods and self.fp_methods.lower() == 'n':
            self.fp_methods = None

    def fp_multi_methods(self):
        """ copy FP methods by number of women """
        if not self.has_k():
            return

        try:
            if int(self.women_fp) > 1 \
            and self.fp_methods.strip().split(' ').__len__() == 1:
                meth = self.fp_methods.strip()
                meths = [meth for i in range(0, int(self.women_fp))]
                self.fp_methods = ' '.join(meths)
        except:
            pass

    def adv_codes(self):
        """ convert +V advices codes to correct ones """
        if self.advices:
            self.advices = self.advices.upper().replace('PL', 'PF')

    def map_chw_id(self):
        """ convert Toya Team CHW ID to CC+ ID """

        self.chw_id = TOYA_CHW_MAP[int(self.chw_id)].__str__()

    def post_process(self):

        self.map_chw_id()

        self.date_get_last()
        self.date_add_0month()
        self.date_add_year()
        self.convert_date()

        self.zero2o_hh_avail()

        self.e_niszero()
        self.k_niszero()

        self.k_default_value()
        self.v_default_value()
        self.e_default_value()

        self.fp_multi_methods()
        #self.fp_codes()
        self.adv_codes()

class ToyaFormC(FormC):
    """ Toya specificities on FormC """

    def date_get_last(self):
        """ if date missing, use LAST_DATE """
        if not self.date:
            self.date = get_date()

    def date_add_0month(self):
        """ replace date dmm to ddmm """
        if self.date.__len__() == 3:
            self.date = '0%s' % self.date

    def date_add_year(self):
        """ Add 4-digit year at end of date """
        if self.date.__len__() == 4:
            self.date = '%s%s' % (self.date, '2010')

    def convert_date(self):
        """ convert date from ddmmYYYY to YYYY-mm-dd """
        self.date = '%s-%s-%s' % (self.date[4:8], self.date[2:4], \
                                  self.date[0:2])

    def danger_sign_flag(self):
        """ removes O or N as danger sign code """
        if self.danger_sign.lower() in ('o','n','0'):
            self.danger_sign = None

    def g_zerofornone(self):
        """ replace 0 by blank on +G """
        if self.meds.lower() == '0':
            self.meds = None

    def r_zerofornone(self):
        """ replace 0 by blank on +R """
        if self.referral.lower() == '0':
            self.referral = None

    def map_chw_id(self):
        """ convert Toya Team CHW ID to CC+ ID """

        self.chw_id = TOYA_CHW_MAP[int(self.chw_id)].__str__()

    def post_process(self):

        self.map_chw_id()

        self.date_get_last()
        self.date_add_0month()
        self.date_add_year()
        self.convert_date()

        self.danger_sign_flag()
        self.g_zerofornone()
        self.r_zerofornone()

# KORARO
class KoraroFormA(FormA):
    """ Koraro specificities on FormA """

    MOTHER = 0
    FATHER = 1
    CHILD = 2

    def init_map(self):

        self.person_type = self.CHILD

        self.map = {
            0: 'hh_number',
            1: 'date',
            2: 'health_id',
            3: None,  # +NEW
            4: 'location_code',
            5: 'first_name',
            6: 'last_name',
            7: 'gender',
            8: 'dob',
            9: 'hohh',
            10: 'mother_id',
            11: None, #+BIR
            12: 'delivery',
            13: 'weight',
            14: None, # +MOB
            15: 'mobile',
        }

    def post_process(self):

        self.date_assign()
        self.health_id_set()
        self.gender_harmonize()
        self.dob_reformat()
        self.store_person_type()
        self.guess_hohh()
        self.guess_mother_id()
        self.clean_mobile()
        self.mob_spaces()
        self.mob_prefix_ethiopia()

    def has_bir(self):
        return self.delivery

    def date_assign(self):
        """ Assign March 21st, 2010 as encounter date """
        if not self.date:
            self.date = '2010-03-21'

    def health_id_set(self):
        """ gets the first available HealthId from DB """
        self.health_id = HealthId.objects \
               .filter(status__in=(HealthId.STATUS_PRINTED, \
               HealthId.STATUS_GENERATED))[0].health_id

    def gender_harmonize(self):
        """ replace male/female with appropriate abbreviations """
        if self.gender:
            gender = self.gender.strip().lower()
            if gender == 'female':
                self.gender = 'F'
            elif gender == 'male':
                self.gender = 'M'

    def dob_reformat(self):
        """ convert dob from mm/dd/yyyy to yyyy-mm-dd """
        if self.dob and self.dob.count('/') == 2:
            dob = self.dob.split('/')
            self.dob = u"%(day)s-%(month)s-%(year)s" \
                       % {'year': dob[2], \
                          'month': dob[0] if dob[0].__len__() == 2 \
                                          else '0%s' % dob[0], \
                          'day': dob[1] if dob[1].__len__() == 2 \
                                        else '0%s' % dob[1]}

    def store_person_type(self):
        """ set an harmonized person type based on hohh field """
        if self.hohh:
            if self.hohh.lower() == 'mother':
                self.person_type = self.MOTHER
            elif self.hohh.lower() == 'father':
                self.person_type = self.FATHER
            else:
                self.person_type = self.CHILD
        
    def guess_hohh(self):
        """ fills HoHH based on last rows and person type """
        if self.hh_number:
            # new HH
            data_change('hh_number', self.health_id)
            self.hohh = 'H'
        else:
            self.hohh = data_get('hh_number')

    def guess_mother_id(self):
        """ filles mother_id based on last rows and person type """
        if self.person_type == self.MOTHER:
            data_change('mother_id', self.health_id)
        if self.person_type == self.CHILD:
            self.mother_id = data_get('mother_id')

    def mob_spaces(self):
        if self.mobile:
            self.mobile = self.mobile.replace(' ', '')

    def mob_prefix_ethiopia(self):
        if self.mobile:
            self.mobile = '251%s' % self.mobile.strip().replace(' ','')

def import_csv(csv_file, form, handler, username, chw_id):

    # select handler
    try:
        FormClass = eval('%sForm%s' % (handler.title(), form.title()))
    except:
        raise

    try:
        common_fname = csv_file.split('.csv')[0]
        fhandler = open(csv_file)
        ehandler = open('%s_error.csv' % common_fname, 'w')
        shandler = open('%s_success.csv' % common_fname, 'w')
    except IOError, e:
        print "Unable to open file: %s" % e
        return None

    linecptr = 0
    for line in fhandler:

        line = line.decode('utf-8')

        linecptr += 1

        # debug
        if DEBUG and linecptr > 10:
            return

        # instanciate form
        form = FormClass(line)

        if hasattr(form, 'chw_id') and form.chw_id:
            chw_id = form.chw_id

        sms_text = form.to_sms()
        print ">>> %s" % sms_text
        response, status = send_sms(sms_text.encode('utf-8'), \
                                    identity=username, date=form.date, \
                                    chw_id=chw_id)

        # set last_date variable
        set_date(form.date)

        # mark as success if only +BIR failed due to overaged patient
        if status == 'warning' \
           and response.count(u"Echec d'un terme., Réussi:  +BIR failed:") \
           and response.count(u"Vous ne pouvez pas soumettre un compte-rendu de naissance pour les patients de plus de 28 jours., +NEW Traité avec succès"):
            status = 'success'

        mline = '"%s",%s' % (response, line)
        mline = mline.encode('utf-8')

        if status == 'success':
            print "<<< SUCCESS"

            # write log to success file
            shandler.write(mline)

        else:
            print "<<< (%s) %s" % (status, response)

            # write log to error file
            ehandler.write(mline)

    fhandler.close()
    ehandler.close()
    shandler.close()
