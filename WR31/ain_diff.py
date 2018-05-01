import digihw
import sarcli
from time import sleep

GPIO_CLI = 'gpio ain'


def cli(cmd):
    s = sarcli.open()
    s.write(cmd)
    resp = s.read()
    s.close()
    return resp.strip('\r\n').strip('\r\nOK')


def python_ain():
    return digihw.wr31_ain_get_value()

if __name__ == "__main__":
    for x in range(20):
        ain = python_ain()
        print "Loop %s" % x
        print "DIGIHW Value: %s" % (ain,)
        resp = cli(GPIO_CLI)
        print "CLI Value: %s" % (resp,)
        sleep(2)
