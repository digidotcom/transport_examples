#!/usr/local/bin/python

############################################################################
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2017 Digi International Inc. All Rights Reserved.
#
############################################################################

"""
Application prints if current, active SIM ICCID is the same as the previous.

Flow:       Read the active SIM on boot to determine if it is different from
            the previous boot. On first boot, it will report that it is the
            first boot up and tracked the current SIM by ICCID.

Options:    When a non-matching ICCID is found, an alert, data point or some
            other action should be added. The placeholder is marked as:
            ---- DO SOMETHING HERE ---

Usage:      The script can be run manually via the command-line (CLI), as:
            > python read_sim.py
            It should updated with an appropriate action and then set to run
            on boot.
"""

import os
import sarcli
import sys

SIM_FILE = "iccid.txt"
MODEM_STAT = "modemstat ?"


def cli(command):
    cli = sarcli.open()
    cli.write(command)
    response = cli.read()
    cli.close()
    return response


def parse_modemStat(modemstat):
    iccid = ""
    string_match = "ICCID:"
    lines = modemstat.split('\r\n')
    for line in lines:
        if string_match in line:
            iccid = line.strip('\r\n').replace(string_match, '').strip()
            break
    return iccid


def get_iccid():
    resp = cli(MODEM_STAT)
    return parse_modemStat(resp)


def sim_file_exists():
    return os.path.isfile(SIM_FILE)


def read_sim_file():
    """Opens the SIM_FILE and return the ICCID"""
    sim = ""
    if sim_file_exists():
        with(open(SIM_FILE, 'r')) as f:
            sim = f.read()
            sim = sim.strip()
    return sim


def write_sim_file(iccid):
    with(open(SIM_FILE, 'w')) as f:
        f.write(iccid)


if __name__ == "__main__":
    if not sim_file_exists():
        print "First run, no SIM file exists"
        write_sim_file(get_iccid())
    else:
        print "Checking SIM information"
        modem_stat = cli(MODEM_STAT)
        current_sim = parse_modemStat(modem_stat)
        print "SIM number %s" % (current_sim,)
        sim = read_sim_file()
        print "Previous SIM %s" % (sim,)
        if sim != current_sim:
            print "SIM is different than previous!"
            # ---- DO SOMETHING HERE ----
            # send datapoint here
        else:
            print "SIM ICCIDs match"
        write_sim_file(current_sim)
    sys.exit()
