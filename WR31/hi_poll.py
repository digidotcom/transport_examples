# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2016 Digi International Inc. All Rights Reserved.

"""
The purpose of this application is to show the maximum poll rate that can be
achieved on the IO ports, using the CLI commands.
"""

import sarcli
import time
import sys


CMD_DIO = 'gpio dio'
CMD_AIN = 'gpio ain'
ANALOG_CHANNEL_CONTROLS = ['current', 'voltage']
DIGITAL_CHANNELS = ['D0', 'D1']
DIGITAL_IO_OPTIONS = ['on', 'off']

VOLTAGE_DECIMAL = 3  # Change to desired voltage decimal accuracy
ANALOG_CHANNEL = 'voltage'
LOOPS = 10
WAIT = 200  # sleep in milliseconds (ms)
DEBUG = False


def display_help():
    print """
Usage: python {0}
Args (optional):
-[H|?] prints help, then exits
-A[voltage|current] # sets analog reading by voltage or current
-L<number of loops>
-W<wait milliseconds between loops>
--Ex. > python {0} -Avoltage -L100 -W250
""".format(sys.args[0])


def cli(command="gpio"):
    clidata = ''
    cli = sarcli.open()
    if DEBUG:
        print 'CLI> {0}'.format(command)
    cli.write(command)
    while True:
        tmpdata = cli.read(-1)
        if not tmpdata:
            break
        clidata += tmpdata
    cli.close()
    return clidata


def string_to_cli_out(lines):
    if len(lines):
        for line in lines:
            print line
    else:
        print ''


def check_analog_control(control):
    """
    Validate the requested analong control is a valid analong control for
    the WR31
    """
    if control not in ANALOG_CHANNEL_CONTROLS:
        print 'Invalid analog control type:'
        print 'controls: {0}'.format(ANALOG_CHANNEL_CONTROLS)
        return False
    return True


def check_digital_channel(channel):
    """
    Validate the requested digital channel is a valid digital channel for
    the WR31
    """
    if channel not in DIGITAL_CHANNELS:
        print 'Channels: ' + str(DIGITAL_CHANNELS)
        return False
    return True


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


def get_digital_io():
    """
    Get Digital Channel Response
    >gpio dio
    D0: DOUT=OFF, DIN=HIGH (Inactive)
    D1: DOUT=OFF, DIN=HIGH (Inactive)
    OK
    """
    return parse_gpio_response(cli(CMD_DIO))


def set_analog_io_type(io_type):
    command = '{0} {1}'.format(CMD_AIN, io_type)
    if check_analog_control(io_type):
        print parse_gpio_response(cli(command))
        print 'Analog set to {0}'.format(io_type)
        return True
    return False


def get_analog_io(io_type):
    """
    >gpio ain [current]
    A0: current=0.0173 mA
    OK
    ----
    >gpio ain [voltage]
    A0: voltage=0.0075 V
    OK
    """
    return parse_gpio_response(cli(CMD_AIN))


if __name__ == "__main__":
    print ''
    args = sys.argv
    if len(args) > 1:
        for arg in args:
            if arg.upper().startswith('-H') or arg.startswith('-?'):
                display_help()
                sys.exit(0)
            elif arg.upper().startswith('-A'):
                analog_type = arg[2:]
                if check_analog_control(analog_type):
                    set_analog_io_type(analog_type)
            elif arg.upper().startswith('-L'):
                LOOPS = int(arg[2:])
                if LOOPS > 10000:
                    print 'Too many loops, {0}'.format(LOOPS)
                    sys.exit(1)
            elif arg.upper().startswith('-W'):
                WAIT = int(arg[2:])
                if WAIT < 100:
                    print 'Poll rate too fast, {0}'.format(WAIT)
                    sys.exit(1)
            elif arg.upper().startswith('-D'):
                DEBUG = True

    print '======================'
    print 'Setup:'
    print 'Number of loops: {0}'.format(LOOPS)
    print 'Wait time (ms):  {0}'.format(WAIT)

    for x in range(LOOPS):
        print '======================'
        print 'Loop: %d' % (x+1)
        print '----------------------'
        string_to_cli_out(get_analog_io(ANALOG_CHANNEL))
        print '----------------------'
        string_to_cli_out(get_digital_io())
        time.sleep(WAIT/1000.0)

    print '======================'
    print 'Polling Complete'
    sys.exit(0)
