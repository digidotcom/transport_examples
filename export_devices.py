#!/usr/bin/env python

############################################################################
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2018 Digi International Inc. All Rights Reserved.
#
############################################################################

VERSION = {
    'major': 0,
    'minor': 1,
    'patch': 0
}

import sys
import csv
import json

from devicecloud import DeviceCloud
from devicecloud.version import __version__
from devicecloud.examples.example_helpers import get_authenticated_dc
from devicecloud.conditions import Attribute


DEBUG = False


def disp_help():
    print("""Usage: python {} export_file_path [--debug] [--help]

This script exports registered devices within a Digi Remote Manager (Device Cloud) account to a CSV file.

Required:
export_file_path: the output CSV file name and path

Optional:
--debug, -d: Debug, display registered devices
--help, -h -?: Help, display help
""".format(sys.argv[0]))
    sys.exit()


def parse_args(argv):
    global DEBUG

    if '--help' in sys.argv or '-h' in sys.argv or '-?' in sys.argv:
        disp_help()

    if '--debug' in sys.argv or '-d' in sys.argv:
        DEBUG = True

    if len(sys.argv) < 2:
        # print sys.argv
        disp_help()

    return sys.argv


if __name__ == "__main__":
    print("Device Exporter - version {major}.{minor}.{patch}".format(**VERSION))
    args = parse_args(sys.argv)

    print("Opening {}".format(args[1]))

    dc = get_authenticated_dc()
    devices = dc.devicecore.get_devices()

    fieldnames = ['devMac', 'devCellularModemId', 'devConnectwareId', 'xpExtAddr', 'dpLastKnownIp',
                  'dpGlobalIp', 'dpDeviceType', 'dpDescription', 'dpConnectionStatus', 'dpRestrictedStatus',
                  'dpFirmwareLevelDesc', 'dpLastConnectTime', 'dpContact', 'dpLocation', 'dpMapLat', 'dpMapLong',
                  'dpCapabilities', 'dvVendorId', 'dpUserMetaData', 'dpTags', 'dpLastDisconnectTime',
                  'dpLastUpdateTime', 'dpHealthStatus', 'grpPath', 'dpPanId', 'dpFirmwareLevel',
                  'devTerminated', 'devEffectiveStartDate', 'grpId', 'cstId', 'devRecordStartDate', 'id',
                  'dpZigbeeCapabilities']

    with open(args[1], 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        csv_devices = []
        for device in devices:
            if DEBUG:
                print(json.dumps(device.get_device_json(), indent=4, sort_keys=True))
            dvc = device.get_device_json()
            csv_devices.append(dvc)

        writer.writerows(csv_devices)

    print("DONE! Device export complete. Open {} to verify file complete.".format(args[1]))
