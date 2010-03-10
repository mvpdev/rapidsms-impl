#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' DataEntry Backend

Simple HTTP backend which respond JSON to POST requests.
WIP: do not use. '''

import BaseHTTPServer
import SocketServer
import select
import random
import re
import urllib
import json
from datetime import datetime
from urlparse import parse_qs

import rapidsms


def _uni(str):
    try:
        return unicode(str)
    except:
        return unicode(str, 'utf-8')


def _str(uni):
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

    def log_error(self, format, *args):
        self.server.backend.error(format, *args)

    def log_message(self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_str(msg))

    def respond_json(self, msg):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(_str(msg))

    msg_store = {}

    def do_GET(self):

        self.respond(200, u"Hey, nothing there pal. Try POST.")
        return

    def do_POST(self):

        # retrieve and parse HTTP POST data
        content_length = int(self.headers['Content-Length'])
        encoded_data = self.rfile.read(content_length)
        decoded_data = parse_qs(encoded_data)

        try:
            identity = _uni(decoded_data['identity'][0])
        except (KeyError, TypeError):
            identity = None

        try:
            message = _uni(decoded_data['message'][0])
        except (KeyError, TypeError):
            message = None

        try:
            action = _uni(decoded_data['action'][0])
        except (KeyError, TypeError):
            action = None

        if action == "list":

            if identity in DEHttpHandler.msg_store \
               and DEHttpHandler.msg_store[identity]:
                message = DEHttpHandler.msg_store[identity].pop(0)
                json_msg = {'phone': identity, 'message': message.text, \
                            'status': message.status}
                self.respond_json(json.dumps(json_msg, indent=4))
            else:
                self.respond_json({})
            return

        # get time
        received = datetime.utcnow()

        # create message object
        msg = self.server.backend.message(identity, message, date=received)

        # route the message
        self.server.backend.route(msg)

        # json response
        json_msg = {'phone': identity, 'message': message}

        self.respond_json(json.dumps(json_msg, indent=4))
        return

    @classmethod
    def outgoing(klass, msg):
        '''Used to send outgoing messages through this interface.'''

        # store outgoing message in a dictionary.
        if not msg.connection.identity in DEHttpHandler.msg_store:
            DEHttpHandler.msg_store[msg.connection.identity] = []
        msg.text = _str(msg.text)
        DEHttpHandler.msg_store[msg.connection.identity].append(msg)


class Backend(rapidsms.backends.Backend):

    def configure(self, host="localhost", port=8080):

        self.server = HttpServer((host, int(port)), DEHttpHandler)
        self.type = "dataentry"

        # reference backend in HTTP server
        self.server.backend = self

    def run(self):
        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                DEHttpHandler.outgoing(msg)
            self.server.handle_request()
