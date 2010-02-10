#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' UPS Backend

    reads info from /proc/apci and delivers notification

    status only delivered on AC power change (off/on line)
    ability to request details by sending: ups now

    TODO: subclass with different types (battery, ups, etc) '''

import os
import time
import re
from datetime import datetime

from rapidsms.backends import Backend
import backend
from rapidsms.message import Message


def str2bool(str_):
    ''' converts an sms-received bool (string) to actual boolean '''
    return str_.lower().strip() in ('true', 'yes', 'y')


class Backend(Backend):

    STATE_ONLINE = 1
    STATE_OFFLINE = 0
    CAPACITY_UNKNOWN = -1
    STATES = {STATE_ONLINE: 'on-line', STATE_OFFLINE: 'off-line'}

    def configure(self, interval=60, kind='battery', \
                  device='BAT0', ac_device='ADP1'):
        ''' set backend variables and open file descriptors

        interval: delay in second to check battery state
        kind: kind of ups in use (battery only for now)
        device name/file of the ups '''

        self.interval = int(interval)
        if kind.lower().strip() in ('battery'):
            self.kind = kind.lower().strip()
        self.device = device.strip()
        self.ac_device = ac_device.strip()

    def start(self):
        # assumes we're online when starting
        self.state = self.STATE_ONLINE
        self.battery_capacity = self.CAPACITY_UNKNOWN
        self.battery_current_capacity = self.CAPACITY_UNKNOWN
        self.battery_present = False
        self.request_now = False

        backend.Backend.start(self)

    def dict_from_file(self, file_):
        ''' returns a dict from /proc-like string '''
        f = open(file_, 'r')
        lines = f.readlines()
        f.close()
        dict_ = {}
        for var in lines:
            key, value = var.split(':')
            key = key.strip()
            value = value.strip()
            dict_[key] = value.split(' ')[0]
        return dict_

    def send_text(self, text):
        ''' creates a message object from text and route it '''
        msg = self.message(self.device, text, datetime.now())
        self.route(msg)

    def run(self):
        ''' reads incoming file and create message objects from it '''

        # retrieve infos about capacity
        # for sake of performances, we get this once on startup
        # although use could exchange battery but not likely to happen.
        info = self.dict_from_file("/proc/acpi/battery/%(battery)s/info" \
                                   % {'battery': self.device})
        self.battery_capacity = int(info['last full capacity'])

        while self.running:

            # get AC state
            ac = self.dict_from_file("/proc/acpi/ac_adapter/%(device)s/state" \
                                     % {'device': self.ac_device})
            if ac['state'] == 'on-line':
                state = self.STATE_ONLINE
            else:
                state = self.STATE_OFFLINE

            # send text on state change
            # not sure if it's worth the load to always capture battery
            # and notify about battery removal.
            if state != self.state or self.request_now:
                # store new state
                self.state = state

                # get battery state (about 5-6s)
                batt = self.dict_from_file(\
                                       "/proc/acpi/battery/%(battery)s/state" \
                                       % {'battery': self.device})

                self.battery_present = (batt['present'] == 'yes')
                self.battery_current_capacity = int(batt['remaining capacity'])

                # build and send notification
                message = "%(state)s %(batt_pres)s %(full_cap)s " \
                          "%(cur_cap)s %(requested)s" \
                          % {'state': self.STATES[self.state],
                             'batt_pres': self.battery_present.__str__(),
                             'full_cap': self.battery_capacity,
                             'cur_cap': self.battery_current_capacity,
                             'requested': self.request_now.__str__()}
                self.send_text(message)

                # remove request
                self.request_now = False

            # wait a bit then poll file again
            time.sleep(self.interval)

    def send(self, msg):
        ''' records a request of update

        message must be: ups now '''
        if msg.connection.identity == self.device and msg.text == 'ups now':
            self.request_now = True
