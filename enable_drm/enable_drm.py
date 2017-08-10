############################################################################
#                                                                          #
# This Source Code Form is subject to the terms of the Mozilla Public      #
# License, v. 2.0. If a copy of the MPL was not distributed with this      #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.                 #
#                                                                          #
# Copyright (c)2017 Digi International Inc. All Rights Reserved.           #
#                                                                          #
############################################################################

import csv
import fileinput
import logging
import os.path
import paramiko
import re
import socket
import sys
import traceback

from time import gmtime, localtime, strftime


CSV_FIELDNAMES = ['devId', 'installCode']
DEVID = '00000000-00000000-00000000-00000000'
DRM_HOSTNAME = "my.devicecloud.com"
HR = "----------------------------------------------------------------"
IP_FILENAME = "iplist.txt"
PASSWORD = "password"
SSH_TIMEOUT = 20  # seconds
USERNAME = "username"

CMD_ENABLE_DRM = "cloud 0 clientconn ON"
CMD_SET_SERVER = "cloud 0 server %s" % DRM_HOSTNAME
CMD_SAVEALL = "config 0 save"
CMD_HW_INFO = "hw ?"
CMD_REBOOT = "reboot"

# Global IP List
ip_addrs = []
csvwriter = None
csvfile = None


def config_logging(filename, console_level, file_level):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=file_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S%p',
                        filename='./{0}.log'.format(filename),
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(console_level)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def connect_to_router(ip_addr):
    logging.info("Connecting to %s..." % ip_addr)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_addr, username=USERNAME, password=PASSWORD, timeout=SSH_TIMEOUT)
    return ssh


def config_router(ip_addr, reboot=True):
    ssh_connection = connect_to_router(ip_addr)

    logging.info("Enabling Device Cloud Client for %s..." % ip_addr)
    stdin, stdout, stderr = ssh_connection.exec_command(CMD_ENABLE_DRM)

    logging.info("Setting Device Cloud hostname for %s..." % ip_addr)
    stdin, stdout, stderr = ssh_connection.exec_command(CMD_SET_SERVER)

    logging.info("Saving config to flash for %s..." % ip_addr)
    stdin, stdout, stderr = ssh_connection.exec_command(CMD_SAVEALL)

    logging.info("Getting hardware information for %s..." % ip_addr)
    stdin, stdout, stderr = ssh_connection.exec_command(CMD_HW_INFO)
    hw_info = stdout.readlines()

    if reboot:
        logging.info("Rebooting %s..." % ip_addr)
        stdin, stdout, stderr = ssh_connection.exec_command(CMD_REBOOT)

    return hw_info


def add_devices_from_file(fileName):
    ip_list = []
    if os.path.isfile(os.path.join(os.getcwd(), fileName)):
        for line in fileinput.input(fileName):
            if line[0] == '#':
                continue
            ip_list.append(line[0:len(line)-1])
    else:
        raise Exception("File not found, %s" % fileName)
    return ip_list


def format_mac_as_devId(mac):
    mac = re.sub('[-: ]', '', mac).upper()
    return '00000000-00000000-' + mac[:6] + 'FF-FF' + mac[6:]


def parse_hw_info(hw_info):
    logging.debug("HW INFO: %s" % hw_info)
    string_match = "MAC 0:"
    devId = DEVID
    for line in hw_info:
        # logging.debug(line)
        if string_match in line:
            line = line.replace(string_match, '').strip('\r\n').strip().upper()
            logging.info("MAC: %s" % line)
            devId = format_mac_as_devId(line)
            break
    logging.info("DevId: %s" % devId)
    return devId


def open_csv_file(filename):
    file = open(filename, 'wb+')
    writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
    # writer.writeheader() # headers not supported in Bulk Add DRM feature
    return writer, file


def log_to_csv(filename, devId, installCode=''):
    global csvwriter, csvfile

    if csvwriter is None:
        csvwriter, csvfile = open_csv_file(filename)

    logging.debug("Logging to CSV %s" % locals())
    row = {
        'devId': devId,
        'installCode': installCode,
    }
    logging.debug("ROW: %s" % row)
    csvwriter.writerow(row)


def log_status(ip_addr, devId, status='Success', error_msg=None):
    pass


if __name__ == "__main__":
    now = strftime("%Y%m%d_%H%M%S", localtime())
    logfile = 'results_{}_{}'.format(sys.argv[0].replace('.py', ''), now)
    config_logging(filename=logfile, console_level=logging.INFO, file_level=logging.INFO)

    csv_filename = "bulkadd_results_%s.csv" % now

    logging.info(HR)
    logging.info("| Starting Application to Enable Digi Remote Manager")
    logging.info(HR)

    try:
        reboot = True
        if len(sys.argv) > 1:
            ip_addrs.append(sys.argv[1])
        else:
            ip_addrs = add_devices_from_file(IP_FILENAME)

        if len(sys.argv) > 2 and sys.argv[2] == 'noreboot':
            reboot = False

        first = True
        for ip in ip_addrs:
            if not first:
                logging.info(HR)
            try:
                first = False
                cmd_resp = config_router(ip, reboot)
                devId = parse_hw_info(cmd_resp)
                log_to_csv(csv_filename, devId)
            except socket.error as msg:
                if str(msg) == 'timed out':
                    msg = "SSH connection timed out"
                logging.error(msg + ' for %s' % ip)
                continue
            except paramiko.ssh_exception.AuthenticationException as auth_err:
                logging.error(auth_err + ' for %s' % ip)
                continue
    except Exception as err:
        csvfile.close()
        logging.error(traceback.print_exc())

    logging.info(HR)
    logging.info("| Application Complete")
    logging.info(HR)
