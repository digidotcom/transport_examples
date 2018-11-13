import idigidata
import time
import thread
import sarcli
import sys


def cli_parse(strData, strName, gps=False):
    try:
        pos1 = strData.find(strName)
        pos2 = strData.find('\n', pos1)
        if (gps):
            pos3 = strData.find('=', pos1)
        else:
            pos3 = strData.find(':', pos1)
        if pos2 > pos1 and pos2 > 0 and pos2 > pos3 and pos3 > 0:
            name = strData[pos3 + 2:pos2 - 1]
        else:
            name = ""
        return name
    except Exception, ex:
        return ""


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


def get_gps_lat_long(at_mibs_gps):
    stats_dict = {}
    stats_dict["gps_longitude"] = parse(answer, "gps.0.stats.longitude", True)
    stats_dict["gps_latitude"] = parse(answer, "gps.0.stats.latitude", True)
    stats_dict["gps_satellites"] = parse(answer, "gps.0.stats.satellites", True)
    stats_dict["gps_course"] = parse(answer, "gps.0.stats.course", True)
    stats_dict["gps_utctime"] = parse(answer, "gps.0.stats.utctime", True)
    stats_dict["gps_altitude"] = parse(answer, "gps.0.stats.altitude", True)
    speedknots = float(parse(answer, "gps.0.stats.speedknots", True))
    lat = float(stats_dict["gps_latitude"].strip(' NSEW'))
    lon = float(stats_dict["gps_longitude"].strip(' NSEW'))
    return [lat, lon]


def report(target, data):
    # ignore target and data for this example, but data is the content of the request
    # and can be parse at this point

    # push up geolocation in a separate thread, since the DataPoint upload gets blocked
    # by the in-progress device_request if you try to do it in the same thread
    thread.start_new_thread(send_up_data, ())

    # return the contents to be returned in the device request. This will show up
    # as the XML response in SCI. Not needed here so just returning and empty string ''
    return ''


def send_up_data():
    # Replace 'geolocation' with the data stream you want to upload to
    path = '/DataPoint/geolocation.xml'
    # report current location in geojson. Replace the literals ('-100.3046875', etc) with
    # your lat long and you're good to go
    xml = '''<DataPoint>
      <data>{"type": "Point", "coordinates": {0}</data>
      <streamId>geolocation</streamId>
    </DataPoint>'''.format(get_gps_lat_long(cli_command("at\mibs=gps")))

    idigidata.send_to_idigi(xml, path)


if __name__ == "__main__":
    args = sys.argv
    print(args)
    sleep_time = int(args[1]) if args[1] else 180

    at_mibs_gps = cli_command("at\mibs=gps")
    lat_long = get_gps_lat_long(cli_command("at\mibs=gps"))
    print(lat_long)

    ret = idigidata.register_callback("reportgps", report)

    # now spin forever so the callback stays active
    while True:
        send_up_data()
        time.sleep(sleep_time)
