#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' PIPE Backend

    reads and writes messages from/to regular files.

    syntax: timestamp identity message

    identity *can not* contain spaces. '''

import os
import time
import re
from datetime import datetime

from rapidsms.backends import Backend
import backend
from rapidsms.message import Message


class Backend(Backend):

    def configure(self, interval=60, incoming='.pipe_backend_in', \
                  outgoing='/dev/null'):
        ''' set backend variables and open file descriptors '''
        self.interval = int(interval)
        self.incoming = incoming.strip()
        self.outgoing = outgoing.strip()
        for f in (self.incoming, self.outgoing):
            if not os.path.exists(f):
                open(f, 'w').close()

    def run(self):
        ''' reads incoming file and create message objects from it '''
        while self.running:

            # open file descriptor
            self.incoming_file = open(self.incoming, 'r+')
            try:
                all_lines = self.incoming_file.readlines()
                self.incoming_file.truncate(0)
            # just make sure we don't truncate if read failed
            except:
                pass
            self.incoming_file.close()

            for mtext in all_lines:

                mtext = mtext.strip()

                # check syntax
                if not re.match("^[0-9]{10} [a-zA-Z0-9\-\_]+ .*$", mtext):
                    continue

                try:
                    smsi = mtext.split(" ", 2)
                    mtime = datetime.utcfromtimestamp(int(smsi[0]))
                    identity = smsi[1]
                    text = smsi[2]
                except (AttributeError, IndexError, ValueError, TypeError):
                    # not a well formatted message. skipping.
                    continue

                # create message object
                msg = self.message(identity, text, mtime)
                self.route(msg)

            # wait a bit then poll file again
            time.sleep(self.interval)

    def send(self, msg):
        ''' append message as text to outgoing file '''
        mtext = "%(time)s %(identity)s %(text)s\n" \
                % {'time': datetime.now().strftime("%s"), 'text': msg.text, \
                   'identity': msg.connection.identity}

        self.outgoing_file = open(self.outgoing, 'a')
        self.outgoing_file.write(mtext)
        self.outgoing_file.close()

    def stop(self):
        # call superclass to terminate run loop
        backend.Backend.stop(self)

        # release descriptors
        if self.incoming_file is not None:
            self.incoming_file.close()

        if self.outgoing_file is not None:
            self.outgoing_file.close()
