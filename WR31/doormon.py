"""
Monitor the WR31 door enclosure
"""
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

import time
import sys
import sarcli
import idigidata


def millisecond_timestamp():
    """
    Return a timestamp, in milliseconds
    :return ms_timestamp: int, Timestamp in milliseconds
    """
    ms_timestamp = int(time.time() * 1000)
    return ms_timestamp


def cli_command(cmd):
    """
    Send a command to the SarOS CLI and receive the response
    :param cmd: str, Command to run
    :return response: str, Response to cmd
    """
    cli = sarcli.open()
    cli.write(cmd)
    response = cli.read()
    cli.close()
    return response


class SmsAlert(object):
    """
    Send an SMS alert
    """
    def __init__(self, destination, custom_text):
        self.destination = destination
        self.custom_text = custom_text

    def send_alert(self, message):
        """
        Send an SMS alert
        :param message: str, Content of SMS message
        :return response: str, Response to sendsms command
        """
        message = "{0}: {1}".format(self.custom_text, message)
        command = 'sendsms ' + self.destination + ' "' + message + '" '
        response = cli_command(command)
        return response


class DatapointAlert(object):
    """
    Send a Datapoint alert
    """
    def __init__(self, destination):
        self.destination = destination

    def send_alert(self, message):
        """
        Send a Datapoint alert
        :param message: str, Datapoint content
        :return response: tuple, Result code of datapoint upload attempt
        """
        timestamp = millisecond_timestamp()
        dpoint = """\
        <DataPoint>
            <dataType>STRING</dataType>
            <data>{0}</data>
            <timestamp>{1}</timestamp>
            <streamId>{2}</streamId>
        </DataPoint>""".format(message, timestamp, self.destination)
        response = idigidata.send_to_idigi(dpoint, "DataPoint/stream.xml")
        return response


class DoorMonitor(object):
    """
    Provides methods to monitor the enclosure door status
    """
    def __init__(self, alert_list):
        self.d1_status = ""
        self.alert_list = alert_list

    @classmethod
    def switch_status(cls):
        """
        Reads line status and sends an alert if the status is different
        """
        response = cli_command("gpio dio")
        if "D1: DOUT=OFF, DIN=LOW" in response:
            if not "D0: DOUT=ON" in response:
                # Door is closed
                return "CLOSED"
        else:
            # Door is open
            return "OPEN"

    def send_alert(self, text):
        """
        :param text: str, Alert content
        :return:
        """
        for alert in self.alert_list:
            alert.send_alert(text)

    def monitor_switch(self):
        """
        Runs line monitoring and alerting in a loop
        :return:
        """
        while True:
            status = self.switch_status()
            if status != self.d1_status:
                print "WR31 door is: {0}".format(status)
                self.send_alert(status)
                self.d1_status = status
            time.sleep(.5)


if __name__ == '__main__':
    ALERT_FUNCTIONS = [DatapointAlert("WR31_door")]
    if len(sys.argv) >= 3:
        CUSTOM_TEXT = sys.argv[2]
    else:
        CUSTOM_TEXT = "WR31 Door"
    if len(sys.argv) >= 2:
        ALERT_FUNCTIONS.append(SmsAlert(sys.argv[1], CUSTOM_TEXT))
    MONITOR = DoorMonitor(ALERT_FUNCTIONS)
    MONITOR.monitor_switch()
