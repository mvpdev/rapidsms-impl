#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

''' USB VBOX backend helper

    rewrites local.ini with correct UUID for USB modem
    get from ssh connecting to host.

    Edit following variables to set Vendor and Product Id
    of the USB modem.

    Adds the following bash code to /etc/rc.local

    # execute rapidsms usb/vbox helper
    # requires:
    #    - 'host' in /etc/hosts to host' IP
    #    - root's pubkey in chilcount@host ssh auth
    /home/mvp/install/patches/usbvbox-backend/startup_localini.py

    logs as `usbvbox` on syslog daemon '''

import subprocess
import re
import logging
import logging.handlers

# define target HW identifiers
VENDOR_ID = '06e0'
PRODUCT_ID = 'f111'
LOCALINI = '/home/mvp/sms/local.ini'


def sanitize_hex(hex_):
    hex_ = hex_.lower()
    if hex_.startswith('0x'):
        return hex_[2:]
    else:
        return hex_


def get_uuid():
    ''' calls VBoxManage on host and parse response to return UUID '''

    # read usb list from host
    output = subprocess.Popen(['/usr/bin/ssh', 'childcount@host', \
                               '/usr/bin/VBoxManage list usbhost'], \
                               stdout=subprocess.PIPE).communicate()[0]

    # sanitize hex identifiers
    target_vendor = sanitize_hex(VENDOR_ID)
    target_product = sanitize_hex(PRODUCT_ID)

    uuid = None
    vendor_id = None
    product_id = None

    for line in output.split("\n"):

        # store UUID cause it comes first
        if line.startswith('UUID:'):
            uuid = re.match(r'^UUID:\s*([a-z0-9\-]*)$', line).groups()[0]

        # retrieve vendor & product
        if line.startswith('VendorId:'):
            vendor_id = re.match(\
                            r'VendorId:\s*0x[0-9a-f]{4}\s\(([A-Z0-9]{4})\)$', \
                            line).groups()[0].lower()

        if line.startswith('ProductId:'):
            product_id = re.match(\
                           r'ProductId:\s*0x[0-9a-f]{4}\s\(([A-Z0-9]{4})\)$', \
                           line).groups()[0].lower()

        # if both vendor and product matchs, return UUID
        if product_id == target_product and vendor_id == target_vendor:
            return uuid

    return None


def edit_localini(uuid):
    ''' read local.ini, change uuid and rewrites it '''

    # read source line by line to find UUID one
    # store each file into output
    output = []
    original = open(LOCALINI, 'r')
    for line in original:
        if line.startswith('usb_vbox_uuid='):
            line = 'usb_vbox_uuid=%s\n' % uuid
        output.append(line)
    original.close()

    # reopen file for writing
    # truncate and write output of previous replacement
    modified = open(LOCALINI, 'w')
    modified.truncate()
    modified.write(''.join(output))
    modified.close()


def main():

    # initialize logging
    name = 'usbvbox'
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.handlers.SysLogHandler(address='/dev/log', \
                                                     facility='daemon'))
    # retrieve UUID
    uuid = get_uuid()
    if uuid == None:
        logging.error("%s: Can't find your device. Script configured ?" % name)
        exit(1)
    else:
        logging.error("%s: Found USB UUID: %s" % (name, uuid))
    # UUID is found, edit local.ini
    edit_localini(uuid)
    logging.info("%s: Edited local.ini file (%s)" % (name, LOCALINI))


if __name__ == '__main__':
    main()
