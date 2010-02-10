#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' USBVBOX Backend

    detach and reattach USB modem to virtualbox host on start/stop
    '''

import os
import time
import subprocess

from rapidsms.backends import Backend
import backend


class Backend(Backend):

    def configure(self, vm='rsms', uuid):
        ''' set backend variables and open file descriptors '''
        self.vm = vm.strip()
        self.uuid = uuid.strip()

        self.usb_reload()

    def run(self):
        ''' does nothing '''
        pass

    def send(self, msg):
        ''' does nothing '''
        pass

    def usb_reload(self):
        ''' detach then attach usb device on host '''
        # calls host vbox manager to detach/attach
        c = subprocess.call(['/usr/bin/ssh', 'childcount@host', \
                  '"/usr/bin/VBoxManage controlvm %(vm)s usbdetach %(uuid)s"'])
        c = subprocess.call(['/usr/bin/ssh', 'childcount@host', \
                  '"/usr/bin/VBoxManage controlvm %(vm)s usbattach %(uuid)s"'])
