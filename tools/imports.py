#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin


def import_hid(hid_file):

    ''' create Health ID objects from Text File

    HHID must be on per line.
    Also creates appropriate reversion objects. '''

    from datetime import datetime

    import reversion
    from childcount.models.Patient import Patient
    from childcount.models.HealthId import HealthId

    print hid_file

    try:
        fhandler = open(hid_file)
    except IOError:
        print "Unable to open file %s" % hid_file
        return None

    for line in fhandler:

        textid = line.strip()
        print "Adding: %s" % textid
        hid = HealthId(health_id=textid, generated_on=datetime.now())
        with reversion.revision:
            hid.save()


def import_user(csv_file, full_name=False):

    ''' create CHW objects from CSV file

    FORMAT of CSV:
    | Last Name | First Name | Location ID | OpenMRS ID

    Alternatively, you can call function with full_name=True with:
    | Full Name | Location ID | OpenMRS ID '''

    from datetime import date, timedelta, datetime
    import re

    from django.contrib.auth.models import User, UserManager, Group
    from reporters.models import PersistantConnection, PersistantBackend
    from locations.models import Location
    from mgvmrs.models import User as OUser

    from childcount.models import Patient, CHW, Configuration, Clinic
    from childcount.utils import clean_names

    try:
        fhandler = open(csv_file)
    except IOError:
        print "Unable to open file %s" % csv_file
        return None

    for line in fhandler:

        data = line.strip().split(",")
        first_name = data[1]
        last_name = data[0]
        password = u"childcount"
        language = 'en'
        location = data[2]
        mobile = data[3] or None
        openmrs_id = data[4] or None

        print "F: %s - L: %s - P: %s - L: %s - LC: %s - M: %s - O: %s" \
              % (first_name, last_name, password, \
                 language, location, mobile, openmrs_id)

        # CHW creation
        chw = CHW()
        # names and alias
        surname, firstnames, alias = clean_names(u"%s %s" % \
                              (last_name, first_name), surname_first=True)
        orig_alias = alias[:20]
        alias = orig_alias.lower()
        if alias != chw.alias and not re.match(r'%s\d' % alias, chw.alias):
            n = 1
            while User.objects.filter(username__iexact=alias).count():
                alias = "%s%d" % (orig_alias.lower(), n)
                n += 1
            chw.alias = alias
        chw.first_name = firstnames
        chw.last_name = surname
        # properties
        chw.language = language
        chw.location = Location.objects.get(id=location)
        chw.mobile = mobile
        chw.save()

        # set password through User.s
        chw.set_password(password)
        chw.save()

        # Add CHW Group
        chw.groups.add(Group.objects.get(name__iexact='CHW'))

        # create dataentry connection
        c = PersistantConnection(backend=PersistantBackend.objects.get(\
                                               slug__iexact='debackend'), \
                                 identity=chw.username, \
                                 reporter=chw, \
                                 last_seen=datetime.now())
        c.save()

        # add mobile connection
        try:
            pygsm = PersistantBackend.objects.get(slug__iexact='pygsm')
        except:
            pygsm = PersistantBackend(slug='pygsm', title='pygsm')
            pygsm.save()

        if mobile:
            c = PersistantConnection(backend=pygsm, \
                                     identity=mobile, \
                                     reporter=chw, \
                                     last_seen=datetime.now())
            c.save()

        # add MGVMRS
        if openmrs_id:
            ouser = OUser()
            ouser.chw = chw
            ouser.openmrs_id = openmrs_id
            ouser.save()


def import_locations(csv_file):

    ''' create Location and Clinic objects from CSV file

    FORMAT of CSV:
    | Name | Code | TYPE | PARENT

    TYPES:
    - V: Village
    - Z: ZOne
    - H: Health Unit

    PARENT:
    Parent must be ID of another location '''

    from locations.models import Location, LocationType
    from childcount.models import Clinic

    try:
        fhandler = open(csv_file)
    except IOError:
        print "Unable to open file %s" % csv_file
        return None

    # maps character code to LocationType ID in fixtures
    TYPES_MAP = {'V': 1, 'Z': 3, 'H': 2}

    for line in fhandler:

        data = line.strip().split(",")
        name = data[0].strip()
        code = data[1].strip().lower()
        type_code = data[2].strip()
        parent_id = data[3].strip() or None

        type_ = LocationType.objects.get(id=TYPES_MAP[type_code])

        if parent_id:
            parent = Location.objects.get(id=parent_id)
        else:
            parent = None

        print "N: %s - C: %s - T: %s (%s) - P: %s (%s)" \
              % (name, code, type_code, type_, parent_id, parent)

        # Create Clinic object if Health Unit
        if type_.id in (2,):
            location = Clinic()
        else:
            location = Location()
        location.type = type_
        location.name = name
        location.code = code
        location.parent = parent
        location.save()
