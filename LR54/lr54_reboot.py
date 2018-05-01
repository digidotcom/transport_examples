# ============================================
# LR54 Quick Reboot Script
# ============================================
# Update REBOOT_TIME (in seconds) to set the
# amount of time to wait before rebooting
# the router
# ============================================

import sys
from time import sleep
from datetime import datetime
from digidevice import cli

REBOOT_TIME = 86340
DEBUG = False


def usage():
    print("""Usage:
    python {} [--help | --debug | --time <seconds>]

Options:
    --help              Print this help and exit
    --debug             Output 'show tech-support' to tech_support_[timestamp].log file
    --time <seconds>    Reboot time in seconds [default: {}]

""".format(sys.argv[0], REBOOT_TIME))


if __name__ == "__main__":
    if "--help" in sys.argv:
        usage()
        exit()
    if "--debug" in sys.argv:
        DEBUG = True
        print("Debug option to output Tech Support before reboot enabled.")
    if "--time" in sys.argv:
        loc = sys.argv.index("--time")
        try:
            REBOOT_TIME = int(sys.argv[loc + 1])
        except:
            pass

    print("Running reboot script, timeout {0} seconds".format(REBOOT_TIME))
    while True:
        sleep(REBOOT_TIME)
        if DEBUG:
            log_name = "tech_support_{}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
            cli.execute("show tech-support {}".format(log_name))
        cli.execute("reboot")
