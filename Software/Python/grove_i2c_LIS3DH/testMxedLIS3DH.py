#!/usr/bin/python
import mxI2C
from LIS3DH import LIS3DH
from time import sleep

def clickcallback(channel):
    # interrupt handler callback   
    print "Interrupt detected"
    click = sensor.getClick()
    print "Click detected (0x%2X)" % (click)
    if (click & 0x10): print " single click"
    if (click & 0x20): print " double click"


if __name__ == '__main__':
    mxEdI2C = [None, None, None, None, None, None, None, None] 
    mx = mxI2C.MXtca9548aDevice()
    mxEdI2C[0] = mx.GetSubDevice(0)
    print(dir(mxEdI2C))
    print()
    sensors[0] = LIS3DH(debug=True, bus=1, i2c=mxEdI2C[0])
    sensors[0].setRange(LIS3DH.RANGE_2G)
    sensors[0].setClick(LIS3DH.CLK_SINGLE,80,mycallback=clickcallback)

    print "Starting stream"
    while True:
	   
        x = sensors[0].getX()
        y = sensors[0].getY()
        z = sensors[0].getZ()

# raw values
        print "\rX: %.6f\tY: %.6f\tZ: %.6f" % (x,y,z)
        sleep(0.1)
		
# click sensor if polling & not using interrupt		
#        click = sensor.getClick()
#        if (click & 0x30) :
#            print "Click detected (0x%2X)" % (click)
#            if (click & 0x10): print " single click"
#            if (click & 0x20): print " double click"
