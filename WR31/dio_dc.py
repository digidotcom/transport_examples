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
import idigidata
import sarcli


def millisecond_timestamp():
    """
    Return a timestamp, in milliseconds
    :return ms_timestamp: int, Timestamp in milliseconds
    """
    ms_timestamp = int(time.time() * 1000)
    return ms_timestamp


def upload_datapoint(stream_id, data, timestamp=millisecond_timestamp()):
    """
    :param stream_id: str, Name of datapoint
    :param data: str, Datapoint content
    :param timestamp: int, Timestamp, must be in milliseconds
    :return result: tuple, Result code of datapoint upload attempt
    """
    dpoint = """\
    <DataPoint>
        <dataType>STRING</dataType>
        <data>{0}</data>
        <timestamp>{1}</timestamp>
        <streamId>{2}</streamId>
    </DataPoint>""".format(data, timestamp, stream_id)
    result = idigidata.send_to_idigi(dpoint, "DataPoint/stream.xml")
    return result


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


class SwitchMonitor(object):
    """
    Provides methods to monitor the enclosure door status
    """
    def __init__(self, destination):
        self.d1_status = ""
        self.destination = destination

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

    def send_alert(self, destination, text):
        """
        :param destination: str, Destination of alert
        :param text: str, Alert content
        :return:
        """
        raise NotImplementedError

    def monitor_switch(self):
        """
        Runs line monitoring and alerting in a loop
        :return:
        """
        while True:
            status = self.switch_status()
            if status != self.d1_status:
                print "WR31 door is: {0}".format(status)
                self.send_alert(self.destination, status)
                self.d1_status = status
            time.sleep(.5)


class SwitchMonitorDatapoint(SwitchMonitor):
    """
    Provides methods to monitor the enclosure door status, with an alert sent to a datapoint
    """
    def send_alert(self, destination, text):
        """
        :param destination: str, Destination of alert
        :param text: str, Alert content
        :return:
        """
        upload_datapoint(destination, text)


if __name__ == '__main__':
    DESTINATION = "WR31_door"
    MONITOR = SwitchMonitorDatapoint(DESTINATION)
    MONITOR.monitor_switch()
