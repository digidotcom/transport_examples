############################################################################
#                                                                          #
# This Source Code Form is subject to the terms of the Mozilla Public      #
# License, v. 2.0. If a copy of the MPL was not distributed with this      #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.                 #
#                                                                          #
# Copyright (c)2017 Digi International Inc. All Rights Reserved.           #
#                                                                          #
############################################################################

"""
CLI approach to reading Voltage input on a WR31 router.
The following script assumes a 681K 1% resistor tied between
Power In (Vin) and the Analog Input (ain).

Flow:       Read the active SIM on boot to determine if it is different from
            the previous boot. On first boot, it will report that it is the
            first boot up and tracked the current SIM by ICCID.

Options:    Configurable options are found below in "User-configurable Variables"
            readInterval:           Time between readings in seconds
            resistorVal:            Value of resistor tied between Vin and Ain
            inputImpedance:         WR31 Analog Input Impedance
            conditionalReporting:   Default = False. Set to True if you want to
                                    send up reports only when voltage has
                                    changed by the specified threshold
            reportingThreshold:     Set to desired voltage threshold level
            voltageDecimal:         Change to desired voltage decimal accuracy
            streamName:             Data Stream name in Remote Manager

Usage:      The script should be uploaded and then can be run manually via the
            command-line (CLI), as:
            > python wr31Vin.py
            Or it can be set to run on boot.
"""

import sarcli
import idigidata
import time
import thread
import sys

# User-configurable Variables
readInterval = 60  # Time between readings in seconds
resistorVal = 681000  # Value of resistor tied between Vin and Ain
inputImpedance = 291000  # WR31 Analog Input Impedance
conditionalReporting = False  # Default = False
reportingThreshold = 0.01  # Set to desired voltage threshold level
voltageDecimal = 3  # Change to desired voltage decimal accuracy
streamName = 'wr31ain'  # Data Stream name in Remote Manager

# System Variables
lastReading = 0.0  # Initialize last reading variable


def convert_voltage(rawV):
    return rawV / (float(inputImpedance)/(float(resistorVal)+float(inputImpedance)))


def read_gpio():
    s = sarcli.open()
    s.write('gpio ain')
    resp = s.read()
    s.close()  # Close sarcli session
    i = resp.find('voltage=')
    j = resp.find('V')
    vdc = float(resp[i+8:j-1])
    calc_vdc = float(round(convert_voltage(vdc), voltageDecimal))
    return vdc, calc_vdc


def send_up_data():
    """Adam's stock function for uploading datapoints with mods by Brad"""
    global lastReading

    # Replace 'wr31ain' with the data stream to which you want to upload
    # Change the xml filename as needed
    path = 'DataPoint/{}.xml'.format(streamName)
    # Define datapoint(s)
    xml = '''<list>
    <DataPoint>
      <data>%s</data>
      <dataType>float</dataType>
      <units>V</units>
      <description>Raw voltage reading</description>
      <streamId>wr31ain</streamId>
    </DataPoint>
    <DataPoint>
      <data>%s</data>
      <dataType>float</dataType>
      <units>V</units>
      <description>Calculated voltage reading</description>
      <streamId>wr31vin</streamId>
    </DataPoint>
    </list>'''
    vdc, calc_vdc = read_gpio()

    z = xml % (vdc, calc_vdc)
    print "\n----------------------"
    print " Analog in: %s" % vdc
    print "Voltage in: %s" % calc_vdc

    # Only send to Remote Manager if conditionalReporting is set to false OR if
    # the reportingThreshold has been matched or exceeded
    if conditionalReporting is False or
        (round(calc_vdc - lastReading, voltageDecimal) >= reportingThreshold or
                round(lastReading - calc_vdc, voltageDecimal) >= reportingThreshold):
        print "Sending to Remote Manager..."
        idigidata.send_to_idigi(z, path)

    # Update the last reading to track for threashold changes
    lastReading = calc_vdc

if __name__ == '__main__':
    print "Starting Vin Reading Application"

    # spin forever
    while True:
        send_up_data()
        time.sleep(readInterval)
