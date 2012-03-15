#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: ukanga

import csv

DEBUG = False
translation_file = 'Final_French_translation.csv'
not_translated_file = 'Not_Translated.csv'
po_file = 'django.po'
tmp_po_file = 'translated_django.po'
pattern = "(?P<key>%\([a-z_]*\)s)|(?P<nokey>%s)"


def play(pattern, text):
    import re
    regex = re.compile(pattern)
    r = regex.search(text)
    '''print r
    print regex.match(text)
    print r.groups()
    print r.groupdict()'''
    stuff = regex.findall(text)
    items = []
    for x, y in stuff:
        if x != '' and x != y:
            items.append(x)
        if y != '' and x != y:
            items.append(y)
    # if items.__len__() > 0: print items, items.__len__()
    return items


def validate_vars(msgid, msgstr, line=None):
    v1 = play(pattern, msgid)
    v2 = play(pattern, msgstr)
    if v1.__len__() == 0:
        return False
    # print '______________\n'
    if v1.__len__() == v2.__len__():
        for val in v1:
            if val not in v2:
                print val, v2
                print "Line:", line, "NOT VALID"
                return False
        return True
    else:
        print "Line:", line, "DO NOT MATCH"
        return False
    return True


def validate_po():
    handler = open(tmp_po_file)
    match = None
    msgid = msgstr = ""
    s = c = lc = 0
    for line in handler:
        lc += 1
        line = line.decode('utf-8')
        if line.startswith('msgid '):
            msgid = line.replace('msgid ', '').strip('\n').strip('"')
        if line.startswith('msgstr '):
            msgstr = line.replace('msgstr ', '').strip('\n').strip('"')
            # print msgid, msgstr, line
            if msgstr.__len__() > 0 and validate_vars(msgid, msgstr, lc):
                s += 1
            c += 1
    print s, "of ", c, "valid"
    handler.close()


def main():
    handler = open(po_file)
    tmphandler = open(tmp_po_file, 'w')
    msgid = msgstr = ""
    for line in handler:
        line = line.decode('utf-8')
        if line.startswith('msgid '):
            msgid = line.replace('msgid ', '').strip('\n').strip('"')
        if line.startswith('msgstr '):
            msgstr = line.replace('msgstr ', '').strip('\n').strip('"')
            translation = lookup_translation(msgid)
            print translation
            if translation is not None:
                line = u'%s"%s"\n' % ('msgstr ', translation)
        tmphandler.write(line.encode('utf-8'))
    handler.close()
    tmphandler.close()


def lookup_in_po(term='',translation=''):
    handler = open(po_file)
    match = None
    msgid = hashtag = tmphashtag = msgstr = ""
    for line in handler:
        if line == '':
            continue
        line = line.decode('utf-8')
        if line.startswith('#') or len(line.strip()) == 0:
            hashtag += line
            continue
        if line.startswith('msgid '):
            msgid = line.replace('msgid ', '').strip('\n').strip('"')
            match = False
        if match == False and line.startswith('msgstr '):
            msgstr = line.replace('msgstr ', '').strip('\n').strip('"')
            match = True
            tmphashtag = hashtag
            hashtag = ""
        if match:
            if term == msgid:
                print tmphashtag
                print msgid
                print msgstr
                print translation
                print '________________________________________\n'
                return True
        # print len(line), line


def lookup_translation(term):
    handler = csv.reader(open(translation_file), delimiter=',', quotechar='"')
    # nhandler = open(not_translated_file, 'w')
    c = 0
    success = 0
    for row in handler:
        c += 1
        line = ','.join(row)
        line.decode('utf-8')
        if row.__len__() > 1:
            if len(row[0]) == 0 or len(row[1]) == 0:
                # nhandler.write(line + "\n")
                continue
                #print line.decode('utf-8')
            msgid = row[0].decode('utf-8').strip('"')
            msgstr = row[1].decode('utf-8').strip('"')
            if msgid == term:
                return msgstr
    return None


def _main():
    handler = csv.reader(open(translation_file), delimiter=',', quotechar='"')
    nhandler = open(not_translated_file, 'w')
    c = 0
    success = 0
    for row in handler:
        c += 1
        line = ','.join(row)
        line.decode('utf-8')
        if row.__len__() > 1:
            if len(row[0]) == 0 or len(row[1]) == 0:
                nhandler.write(line + "\n")
                continue
            #print line.decode('utf-8')
            msgid = row[0].decode('utf-8').strip('"')
            msgstr = row[1].decode('utf-8').strip('"')
            # print msgid + '\n\n'
            if lookup_in_po(msgid, msgstr):
                success += 1
            else:
                print msgid + '\n'
        if DEBUG and c == 10:
            break
    print "%d of %d translated" % (success, c)


if __name__ == '__main__':
    # main()
    # play("(?P<key>%\([a-z_]*\)s)|(?P<nokey>%s)", \
    #    "%(patient)s has %(msg)s %(msg)s %s %(danger_signs)s %s .%(meds)s %(referral)s %(chw)s %(mobile)s.")
    validate_po()