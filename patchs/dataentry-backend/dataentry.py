#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' WIP: do not use. '''

import BaseHTTPServer, SocketServer
import select
import BaseHTTPServer
import random
import re
import urllib
from datetime import datetime

import rapidsms


def _uni(str):
    try:
        return unicode(str)
    except:
        return unicode(str,'utf-8')

def _str(uni):
    try:
        return str(uni)
    except:
        return uni.encode('utf-8')

class HttpServer (BaseHTTPServer.HTTPServer, SocketServer.ThreadingMixIn):
    
    def handle_request (self, timeout=1.0):
        # don't block on handle_request
        reads, writes, errors = (self,), (), ()
        reads, writes, errors = select.select(reads, writes, errors, timeout)
        if reads:
            BaseHTTPServer.HTTPServer.handle_request(self)

class DEHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    ''' '''

    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_str(msg))

    msg_store = {}
    
    def do_GET(self):
        # if the path is just "/" then start a new session
        # and redirect to that session's URL
        if self.path == "/":
            session_id = random.randint(100000, 999999)
            self.send_response(301)
            self.send_header("Location", "/%d/" % session_id)
            self.end_headers()
            return
        
        # if the path is of the form /integer/blah 
        # send a new message from integer with content blah
        send_regex = re.compile(r"^/(\d+)/(.*)")
        match = send_regex.match(self.path)
        if match:
            # send the message
            session_id = match.group(1)
            text = _str(match.group(2))
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if DEHttpHandler.msg_store.has_key(session_id) and DEHttpHandler.msg_store[session_id]:
                    message = DEHttpHandler.msg_store[session_id].pop(0)
                    resp=_str("{'phone':'%s', 'message':'%s', 'status': '%s'}" % (session_id, message.text.replace("'", r"\'"), message.status))
                    self.wfile.write(resp)
                return
            
            # get time
            received = datetime.utcnow()
            # leave Naive!
            # received.replace(tzinfo=pytz.utc)
            
            msg = self.server.backend.message(
                session_id, 
                urllib.unquote(text),
                date=received
                )

            self.server.backend.route(msg)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_str("{'phone':'%s', 'message':'%s'}" % (session_id, urllib.unquote(text).replace("'", r"\'"))))
            return
            
        return
        
    def do_POST(self):
        return
    
    @classmethod
    def outgoing(klass, msg):
        '''Used to send outgoing messages through this interface.'''
        #self.log_message("http outgoing message: %s" % message)
        # the default http backend just stores outgoing messages in
        # a store and provides access to them via the JSON/AJAX 
        # interface
        if not DEHttpHandler.msg_store.has_key(msg.connection.identity):
            DEHttpHandler.msg_store[msg.connection.identity] = []
        msg.text = _str(msg.text)
        DEHttpHandler.msg_store[msg.connection.identity].append(msg)

class Backend(rapidsms.backends.Backend):
    def configure(self, host="localhost", port=8080):
        
        self.server = HttpServer((host, int(port)), DEHttpHandler)
        self.type = "dataentry"
        # set this backend in the server instance so it 
        # can callback when a message is received
        self.server.backend = self

    def run (self):
        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                DEHttpHandler.outgoing(msg)
            self.server.handle_request()
