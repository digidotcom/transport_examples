# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2016 Digi International Inc. All Rights Reserved.

"""
Monitor the WR31 door enclosure
"""

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
        :return status: str, Door status, "OPEN" or "CLOSED"
        """
        response = cli_command("gpio dio")
        if "D1: DOUT=OFF, DIN=LOW" in response:
            if not "D0: DOUT=ON" in response:
                # Door is closed
                status = "CLOSED"
        else:
            # Door is open
            status = "OPEN"
        return status

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
