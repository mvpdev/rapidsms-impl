#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' DataEntry Backend

Simple HTTP backend which respond JSON to POST requests. '''

import BaseHTTPServer
import SocketServer
import select
import random
import json
from datetime import datetime
from urlparse import parse_qs

import rapidsms


def _uni(str_):
    ''' decode unicode/utf-8 string '''
    try:
        return unicode(str_)
    except:
        return unicode(str_, 'utf-8')


def _str(uni):
    ''' encode string as utf8 '''
    try:
        return str(uni)
    except:
        return uni.encode('utf-8')


class HttpServer (BaseHTTPServer.HTTPServer, SocketServer.ThreadingMixIn):

    def handle_request(self, timeout=1.0):
        # don't block on handle_request
        reads, writes, errors = (self,), (), ()
        reads, writes, errors = select.select(reads, writes, errors, timeout)
        if reads:
            BaseHTTPServer.HTTPServer.handle_request(self)


class DEHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    ''' HTTP Server handling incoming messages

    Only respond to HTTP POST request. '''

    msg_store = {}

    def log_error(self, format, *args):
        self.server.backend.error(format, *args)

    def log_message(self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        ''' sends according html string with according status code '''
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_str(msg))

    def respond_json(self, msg):
        ''' sends according string with JSON header '''
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(_str(msg))

    def do_GET(self):
        ''' responds empty content. '''

        self.respond(200, u"POST?")
        return

    def json_from_message(self, message):

        json = {'peer': message.peer, 'text': message.text, \
                'status': message.status}
        return json

    def do_POST(self):
        ''' Handles incoming message and list available ones

        retrieves parameters from HTTP POST dictionary

        A. creates message object from parameters
           sends the message to the router

        B. reads one message from the pool
           writes it to the client

        Parameters:
        - action: if 'list' then triggers B. workflow
        - identity (mandatory): the identity string of sender/requester
        - message: the text to send'''

        # retrieve and parse HTTP POST data
        content_length = int(self.headers['Content-Length'])
        encoded_data = self.rfile.read(content_length)
        decoded_data = parse_qs(encoded_data)

        incoming_msg = {}

        # sanitize (utf8) all input parameters
        for (key, data) in decoded_data.items():
            try:
                if decoded_data[key].__len__() == 1:
                    ddata = _uni(decoded_data[key][0])
                else:
                    ddata = []
                    for each in decoded_data[key]:
                        ddata.append(_uni(each))
                incoming_msg[key] = ddata
            except:
                pass

        # retrieve base & mandatory parameters
        action = incoming_msg['action'] if 'action' in incoming_msg else None
        identity = incoming_msg['identity'] if 'identity' in incoming_msg \
                                            else None
        message = incoming_msg['message'] if 'message' in incoming_msg \
                                          else None

        # request the list of messages sent to _identity_
        if action == "list":

            if identity in DEHttpHandler.msg_store \
               and DEHttpHandler.msg_store[identity]:

                message = DEHttpHandler.msg_store[identity].pop(0)
                json_msg = self.json_from_message(message)
                self.respond_json(json.dumps(json_msg, indent=4))

            else:
                self.respond_json({})
            return

        # get time
        received = datetime.utcnow()

        # create message object
        msg = self.server.backend.message(identity, message, date=received)

        # overload message object with parameters
        existing = msg.__dict__
        for (key, value) in incoming_msg.items():
            if not key in existing:
                try:
                    msg.__getattribute__(key)
                    continue
                except:
                    msg.__setattr__(key, value)

        # route the message
        self.server.backend.route(msg)

        # json response
        json_msg = {'ack': True}

        self.respond_json(json.dumps(json_msg, indent=4))
        return

    @classmethod
    def outgoing(klass, msg):
        ''' send message to backend client via HTTP

        stores message in the backend instance and wait for polling. '''

        # store outgoing message in a dictionary.
        if not msg.connection.identity in DEHttpHandler.msg_store:
            DEHttpHandler.msg_store[msg.connection.identity] = []
        DEHttpHandler.msg_store[msg.connection.identity].append(msg)


class Backend(rapidsms.backends.Backend):

    def configure(self, host="localhost", port=8080):
        ''' changes HTTP server parameters

        host: server host name
        port: server port '''

        self.server = HttpServer((host, int(port)), DEHttpHandler)
        self.type = "debackend"

        # reference backend in HTTP server
        self.server.backend = self

    def run(self):
        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                DEHttpHandler.outgoing(msg)
            self.server.handle_request()
