############################################################################
#                                                                          #
# Copyright (c)2015, Digi International (Digi). All Rights Reserved.       #
#                                                                          #
# Permission to use, copy, modify, and distribute this software and its    #
# documentation, without fee and without a signed licensing agreement, is  #
# hereby granted, provided that the software is used on Digi products only #
# and that the software contain this copyright notice,  and the following  #
# two paragraphs appear in all copies, modifications, and distributions as #
# well. Contact Product Management, Digi International, Inc., 11001 Bren   #
# Road East, Minnetonka, MN, +1 952-912-3444, for commercial licensing     #
# opportunities for non-Digi products.                                     #
#                                                                          #
# DIGI SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED   #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A          #
# PARTICULAR PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, #
# PROVIDED HEREUNDER IS PROVIDED "AS IS" AND WITHOUT WARRANTY OF ANY KIND. #
# DIGI HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,         #
# ENHANCEMENTS, OR MODIFICATIONS.                                          #
#                                                                          #
# IN NO EVENT SHALL DIGI BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,      #
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS,   #
# ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF   #
# DIGI HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.                #
#                                                                          #
############################################################################

import sys
import sarcli
from time import sleep


# Number of display loops
LOOPS = 10
WAIT = 2  # seconds

# Your python code can detect when it is running on a Transport product by
# importing the 'sys' module, then testing the sys.platform variable like this:
if sys.platform == 'digiSarOS':
    print "\nRunning on Digi Transport"

ANALOG_CHANNEL_CONTROLS = ['current', 'voltage']
DIGITAL_CHANNELS = ['D0', 'D1']
DIGITAL_IO_OPTIONS = ['on', 'off']
ANALOG_CHANNEL = 'voltage'


def cli(command="gpio"):
    clidata = ""
    cli = sarcli.open()
    cli.write(command)
    while True:
        tmpdata = cli.read(-1)
        if not tmpdata:
            break
        clidata += tmpdata
    cli.close()
    return clidata


def parse_gpio_response(response_str):
    lines = response_str.strip().splitlines()
    lines.remove('OK')
    i = 0
    for line in lines:
        newline = line.split(": ")
        del lines[i]
        lines.insert(i, newline)
        i += 1
    return lines


# Validate the requested analong control is a valid analong control for
# the WR31
def check_analog_control(control):
    if control not in ANALOG_CHANNEL_CONTROLS:
        print 'controls: ' + str(ANALOG_CHANNEL_CONTROLS)
        sys.exit(1)
    return True


# Validate the requested digital channel is a valid digital channel for
# the WR31
def check_digital_channel(channel):
    if channel not in DIGITAL_CHANNELS:
        print 'Channels: ' + str(DIGITAL_CHANNELS)
        sys.exit(1)
    return True


# Get Digital Channel Response
def get_digital_io():
    # $ gpio dio
    #
    # D0: DOUT=OFF, DIN=HIGH (Inactive)
    # D1: DOUT=OFF, DIN=HIGH (Inactive)
    # OK
    print "Get All Digital Channels"
    command = "gpio dio"
    return parse_gpio_response(cli(command))


# Turn the requested digital channel on or off
def set_digital_io(channel, value):
    # $
    #
    print "Set Digital: " + str(channel) + ", value: " + str(value)
    command = "gpio dio -" + channel + " " + value
    return cli(command)


def get_analog_io(io_type):
    # $ gpio ain [current|voltage]    - analogue input control
    #
    # A0: current=0.0173 mA
    # OK
    out = ''
    if check_analog_control(io_type):
        print "Get Analog: " + str(io_type)
        command = "gpio ain " + io_type
        out = parse_gpio_response(cli(command))
    return out


def calibrate_analog_io(low_high, mA):
    # gpio aincal low|high <mA>     - calibrate analogue input
    command = "gpio aincal " + low_high + " " + mA
    return cli(command)


def get_analog_in_calibration():
    # gpio aincal show      - show analogue input calibration data
    command = "gpio aincal show"
    return cli(command)


def reset_analog_calibration():
    # gpio aincal reset     - wipe all analogue input calibration data
    command = "gpio aincal reset"
    return cli(command)


def string_to_cli_out(lines):
    if len(lines):
        for line in lines:
            print line
    else:
        print ''


if __name__ == "__main__":
    args = sys.argv
    for arg in args:
        if arg.startswith('-H') or arg.startswith('-?'):
            print """
Usage: python ex_gpio.py
Args (optional):
-[H|?] prints help
-A[voltage|current]
-L<number of loops>
-W<wait seconds between loops>"""
            sys.exit(0)
        elif arg.startswith('-A'):
            ANALOG_CHANNEL = arg[2:]
        elif arg.startswith('-L'):
            LOOPS = int(arg[2:])
        elif arg.startswith('-W'):
            WAIT = int(arg[2:])

    print "Setup:"
    print "Analog Channel: " + ANALOG_CHANNEL
    print "Number of loops: " + str(LOOPS)
    print "Wait time (secs): " + str(WAIT)

    for loop in range(LOOPS):
        print "======================"
        print "Loop: " + str(loop)
        print "----------------------"
        string_to_cli_out(get_analog_io(ANALOG_CHANNEL))
        print "----------------------"
        string_to_cli_out(get_digital_io())
        sleep(WAIT)

    sys.exit(0)
