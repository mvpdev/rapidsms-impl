#!/usr/bin/env python
# encoding=utf-8

import random
import hashlib
from datetime import datetime

from database import *


def generate_patient_ids():
    print("Generating PATIENT IDs")
    generate_research_ids('health_id', 'cc_patient', 'health_id', \
                        'research_patient', add_days=True, prefix=SITE_ABBR)


def generate_deadperson_ids():
    print("Generating DEAD PERSON IDs")
    generate_research_ids('id', 'cc_dead_person', 'dead_id', \
                        'research_deadperson', add_days=True,prefix=SITE_ABBR)


def generate_location_ids():
    print("Generating LOCATION IDs")
    generate_research_ids('id', 'locations_location', 'location_id', \
                        'research_location', add_days=False, prefix=SITE_ABBR)


def generate_clinic_ids():
    """ no need for clinic as those are locations """
    pass


def generate_chw_ids():
    print("Generating CHW IDs")
    generate_research_ids('reporter_ptr_id', 'cc_chw', 'chw_id', \
                          'research_chw', add_days=False, prefix=SITE_ABBR)


def generate_research_ids(field, table, research_field, \
                          research_table, add_days=False, prefix=''):
    cursor = conn.cursor()
    cursor.execute("SELECT tbl.%(field)s FROM %(table)s as tbl WHERE " \
                   "tbl.%(field)s NOT IN (SELECT rtbl.%(research_field)s " \
                   "FROM %(research_table)s as rtbl);" \
                   % {'field': field, 'table': table, \
                      'research_field': research_field, \
                      'research_table': research_table})
    # looping on patients like
    while (1):
        item = cursor.fetchone()
        if item == None:
            break
        item_id = item[0]
        research_id = '%s-%s-%s' % (SITE, item_id, \
                                    datetime.now().strftime('%s%f'))
        research_id = hashlib.md5(research_id).hexdigest()[:10]
        research_id ='%s%s' % (prefix, research_id.upper())
        if add_days:
            days = random.randint(-30, -1)
        else:
            days = 0
        print "RESEARCH ITEM: %s | %s" % (item_id, research_id)
        if add_days:
            insert = "INSERT INTO %(research_table)s " \
                     "(%(research_field)s, research_id, days) " \
                     % {'research_table': research_table, \
                        'research_field': research_field}
            conn.cursor().execute(insert + "VALUES (%s, %s, %s);", \
                                  (item_id, research_id, days))
        else:
            insert = "INSERT INTO %(research_table)s " \
                     "(%(research_field)s, research_id) " \
                     % {'research_table': research_table, \
                        'research_field': research_field}
            conn.cursor().execute(insert + "VALUES (%s, %s);", \
                                  (item_id, research_id))
    print "Number of new items: %d" % cursor.rowcount
    cursor.close()


def main():
    if not SITE:
        print("DIE: SITE variable is not configured.\nAdd site name in it.")
        exit(1)
    if not SITE_ABBR:
        print ("DIE: SITE_ABBR variable is not configured."\
               "\nAdd site abbreviation in it.")
        exit(1)
    generate_patient_ids()
    generate_location_ids()
    generate_clinic_ids()
    generate_deadperson_ids()
    generate_chw_ids()

    # release mysql
    conn.close()

if __name__ == '__main__':
    main()
