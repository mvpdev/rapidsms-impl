#!/usr/bin/env python
# encoding=utf-8

import random
import hashlib
from datetime import datetime

from database import *


def update_deadperson_details():
    # alter table cc_dead_person modify id varchar(20);
    cursor = conn.cursor()
    cursor.execute("alter table cc_dead_person modify id varchar(20)")
    cursor.execute("SELECT ccp.id, r.dead_id, research_id, days, dob FROM "
                    "research_deadperson r JOIN cc_dead_person ccp ON "
                    "ccp.id=r.dead_id;")
    while(1):
        item = cursor.fetchone()
        if item == None:
            break
        id = item[0]
        dead_id = item[1]
        res_id = item[2]
        delta_days = item[3]
        dob = item[4]
        if id == None:
            continue
        info = {'res_id': res_id, 'id': id, 'delta_days': delta_days,
                'dead_id': dead_id}
        # dob, first_name, last_name, health_id
        sql = ("UPDATE cc_dead_person SET first_name='%(res_id)s', "
                "last_name='%(res_id)s', "
                                "id='%(res_id)s', "
                                "dob=(SELECT DATE_ADD(dob,  INTERVAL %(delta_days)s DAY)), "
                                "dod=(SELECT DATE_ADD(dod,  INTERVAL %(delta_days)s DAY)) "
                                "WHERE id='%(id)s';" \
                                % info)
        conn.cursor().execute(sql)


def update_patient_details():
    # alter table cc_patient modify health_id varchar(20);
    cursor = conn.cursor()
    cursor.execute("alter table cc_patient modify health_id varchar(20);")
    cursor.execute("SELECT ccp.id, r.health_id, research_id, days, dob FROM "
                    "research_patient r JOIN cc_patient ccp ON "
                    "ccp.health_id=r.health_id;")
    while(1):
        item = cursor.fetchone()
        if item == None:
            break
        id = item[0]
        health_id = item[1]
        res_id = item[2]
        delta_days = item[3]
        dob = item[4]
        if id == None:
            continue
        info = {'res_id': res_id, 'id': id, 'delta_days': delta_days,
                'health_id': health_id}
        # dob, first_name, last_name, health_id
        sql = ("UPDATE cc_patient SET first_name='%(res_id)s', "
                "last_name='%(res_id)s', "
                                "health_id='%(res_id)s', "
                                "dob=(SELECT DATE_ADD(dob,  INTERVAL %(delta_days)s DAY)) "
                                "WHERE id=%(id)s;" \
                                % info)
        conn.cursor().execute(sql)
        # encounter_date, 
        sql = ("UPDATE cc_encounter SET encounter_date=(SELECT "
                "DATE_ADD(encounter_date,  INTERVAL %(delta_days)s DAY)) "
                "WHERE patient_id=%(id)s;" % info)
        conn.cursor().execute(sql)
        # death_rpt
        sql = ("UPDATE cc_deathrpt SET death_date=(SELECT "
                "DATE_ADD(death_date,  INTERVAL %(delta_days)s DAY)) "
                "WHERE ccreport_ptr_id=(SELECT rpt.id rpt_id FROM "
                "cc_encounter e , cc_ccrpt rpt WHERE "
                "rpt.encounter_id=e.id AND cc_deathrpt.ccreport_ptr_id=rpt.id AND  "
                "e.patient_id=%(id)s);" % info)
        conn.cursor().execute(sql)
        # cc_sbmcrpt
        sql = ("UPDATE cc_sbmcrpt SET incident_date=(SELECT "
                "DATE_ADD(incident_date,  INTERVAL %(delta_days)s DAY)) "
                "WHERE ccreport_ptr_id=(SELECT rpt.id rpt_id FROM "
                "cc_encounter e , cc_ccrpt rpt WHERE "
                "rpt.encounter_id=e.id AND cc_sbmcrpt.ccreport_ptr_id=rpt.id AND  "
                "e.patient_id=%(id)s);" % info)
        conn.cursor().execute(sql)


def update_location_details():
    cursor = conn.cursor()
    cursor.execute("SELECT location_id, research_id, name FROM "
                    "research_location LEFT JOIN locations_location ON "
                    "research_location.location_id = locations_location.id;")
    while(1):
        item = cursor.fetchone()
        if item == None:
            break
        id = item[0]
        location = item[1]
        conn.cursor().execute("UPDATE locations_location SET name='%(loc)s' "
                                "WHERE id=%(id)s;" \
                                % {'loc': location, 'id': id})


def update_chw_details():
    cursor = conn.cursor()
    cursor.execute("SELECT chw_id, research_id, first_name, last_name "
                    "FROM research_chw LEFT JOIN auth_user ON "
                    "research_chw.chw_id = auth_user.id;")
    while(1):
        item = cursor.fetchone()
        if item == None:
            break
        chw_id = item[0]
        research_chw = item[1]
        conn.cursor().execute("UPDATE auth_user SET first_name='%(chw)s', "
                                "last_name='%(chw)s' WHERE id=%(chw_id)s;" \
                                % {'chw': research_chw, 'chw_id': chw_id})

def main():
    update_chw_details()
    update_location_details()
    update_patient_details()
    update_deadperson_details()
    # release mysql
    conn.close()

if __name__ == '__main__':
    main()
