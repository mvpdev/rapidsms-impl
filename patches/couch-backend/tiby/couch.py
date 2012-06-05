#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin, ukanga

''' CouchDB Backend

    reads and writes messages from/to a CouchDB server.
    Depends on couchdb module (pip)

    See https://github.com/mvpdev/smpp2local '''

import time
import math
import re
from datetime import datetime

from rapidsms.backends import Backend
import backend
from rapidsms.message import Message
import couchdb

MSG_LIMITS = {
    # 'encoding', (max_normal, max_csm)
    'gsm': (160,152),
    'ucs2': (70,67)
}
MAX_CSM_SEGMENTS = 255
MAX_SMS_LENGTH = 160

def split_msg_ucs2(text):
    """
    Returns a list of text split by MSG_LIMITS['ucs2']
    """
    encoding = 'ucs2'
    encoded_text = text

    csm_max = MSG_LIMITS[encoding][1]
    if len(encoded_text)>(MAX_CSM_SEGMENTS*csm_max):
        raise ValueError('Message text too long')

    # see if we are under the single PDU limit
    if len(encoded_text)<=MSG_LIMITS[encoding][0]:
        return [text]

    # split the text
    num = int(math.ceil(len(encoded_text)/float(MSG_LIMITS[encoding][0])))
    rs = []
    for seq in range(num):
        i = seq*csm_max
        seg_txt = encoded_text[i:i+csm_max]
        rs.append(seg_txt)
    return rs

def sms_split(text):
    ''' Split SMS/Text proportianally 
        returns an array of strings
    '''

    sms_array = []
    num_sms = len(text)/MAX_SMS_LENGTH  + 1
    
    s_s = 0
    s_e = MAX_SMS_LENGTH
    
    for i in range(num_sms):
        sms = text[s_s:s_e]
        if i < num_sms - 1:
            s_e = s_s + sms.rfind(' ')
            sms =  text[s_s:s_e]
        s_s = s_e
        if i < num_sms - 1:
            s_e += MAX_SMS_LENGTH
        else:
            s_e = len(text)
        sms_array.append(sms)
    return sms_array


def document_from_sms(identity, text, date=datetime.now()):
    ''' returns dictionary matching CouchDB and RSMS backend format '''
    document = {'identity': identity,
                'datetime': date.isoformat(),
                'text': text,
                'direction': 'outgoing',
                'status': 'created'}
    return document


class Backend(Backend):

    def configure(self, server='http://localhost:5984', \
                  database='rapidsms', interval='1', view=False):
        ''' set backend variables and create DB connection '''

        self._slug = 'couch'
        self.type = 'couch'

        self.server = server.strip()
        self.database = database.strip()
        self.interval = int(interval.strip())
        self.couch_view = view

        # let's try to connect so we can blow up startup
        # if CouchDB isn't available.
        try:
            self._couch = couchdb.Server(self.server)
        except Exception as e:
            raise 
            #Exception(u"can't connect to Couch server %s" % self.server)
        try:
            self._database = self._couch[self.database]
        except couchdb.ResourceNotFound:
            raise Exception(u"DB %s missing on Couch server." % self.database)

    def run(self):
        ''' retrieves incoming sms from CouchDB and route '''
        while self.running:

            try:
                messages = self.get_messages_from_couch()
            except:
                raise Exception(u"can't retrieve view from Couch " \
                                 "server %s" % self.server)
                continue

            self.log('info', u"%d messages in CouchDB" % messages.__len__())

            for message in messages:
                # create message object
                message_date = datetime(*map(int, re.split('[^\d]', \
                                             message['datetime'])[:-1]))
                msg = self.message(message['identity'], message['text'], \
                                   message_date)
                self.route(msg)

                self.log('info', "rapidsms router message %s." % message['_id'])
                # message sent successfuly.
                # mark it as done in Couch
                doc = self._database[message['_id']]
                doc.update({'status': 'processed'})
                self._database.update([doc])
                self.log('info', "couch updated message %s." % message['_id'])

            # wait a bit then poll file again
            time.sleep(self.interval)

    def send(self, msg):
        ''' creates CouchDB documents for outgoing messages '''
        sms_date=datetime.now()
        identity = msg.connection.identity
        sms_list = split_msg_ucs2(msg.text)
        for text in sms_list:
            document = document_from_sms(identity, text, date=sms_date)

            try:
                doc = self.save_document_to_couch(document)
                self.log('info', "Added outgoing message %s to " \
                                 "CouchDB document %s" % (document, doc))
            except:
                # no f*cking error handling on rsms anyway.
                raise

    def save_document_to_couch(self, document):
        ''' saves an arbitrary document to CouchDB '''

        # create a Couch document and save it to DB.
        doc_id = self._database.create(document)
        doc = self._database[doc_id]
        return doc

    def get_messages_from_couch(self):
        ''' fecthes all pending outgoing messages in couch and return them '''
        messages = []

        # uses permanent view if defined
        # use a temporary view if not.
        if self.couch_view:
            results = self._database.view(self.couch_view)
        else:
            map_fun = '''function(doc) {
                if (doc.direction == 'incoming' && doc.status == 'created')
                    emit(doc, null);
                }'''
            results = self._database.query(map_fun)
        for row in results:
            messages.append(row.key)

        return messages
