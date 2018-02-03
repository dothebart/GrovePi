#!/usr/bin/python

# Author: Wilfried Goesgens

'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2015  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
'''      


'''
Gather several environmental gauges, and push it to the zabbix monitoring system


'''
''' import module '''
import protobix
import time
import grovepi
import atexit

# from grovepi import *
from grove_rgb_lcd import *
from math import isnan

atexit.register(grovepi.dust_sensor_dis)

# connect dust sensor to port D2
print("Reading from the dust sensor")
grovepi.dust_sensor_en()

dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# Connect the Grove Air Quality Sensor to analog port A0
# SIG,NC,VCC,GND
air_sensor = 0

grovepi.pinMode(air_sensor,"INPUT")

''' Add items one after the other '''

zabbix_host="192.168.3.111"


while True:
    try:
        # the PM comes at its own frequency, so we send it alone.
	[new_val,lowpulseoccupancy] = grovepi.dustSensorRead()
	if new_val:
	    print(lowpulseoccupancy)
            ''' create DataContainer, providing data_type, zabbix server and port '''
            zbx_container = protobix.DataContainer("items", zabbix_host, 10051)
            ''' set debug '''
            zbx_container.set_debug(True)
            zbx_container.set_verbosity(True)

            zbx_container.add_item("grooveberry", "my.zabbix.pm-count", lowpulseoccupancy)
		
	    ''' Send data to zabbix '''
	    ret = zbx_container.send(zbx_container)
	    ''' If returns False, then we got a problem '''
	    if not ret:
		print "Ooops. Something went wrong when sending data to Zabbix"
            else:
                zbx_container.item_list = []

        # get the temperature and Humidity from the DHT sensor
        [ temp,hum ] = grovepi.dht(dht_sensor_port,dht_sensor_type)
        print("temp =", temp, "C\thumidity =", hum,"%")

        # check if we have nans
        # if so, then raise a type error exception
        if isnan(temp) is True or isnan(hum) is True:
            raise TypeError('nan error')

        t = str(temp)
        h = str(hum)

        # Get the air quality sensor value
        sensor_value = grovepi.analogRead(air_sensor)[2]
        val = "Air fresh"
        if sensor_value > 700:
            val = "High pollution"
        elif sensor_value > 300:
            val = "Low pollution"

        print("sensor_value =", sensor_value)
        if 1:
            ''' create DataContainer, providing data_type, zabbix server and port '''
            zbx_container = protobix.DataContainer("items", zabbix_host, 10051)
            ''' set debug '''
            zbx_container.set_debug(True)
            zbx_container.set_verbosity(True)

	    zbx_container.add({
		"grooveberry": {
		    "my.zabbix.air_quality": sensor_value,
		    "my.zabbix.air_quality_level": val,
                    "my.zabbix.temperature": t,
                    "my.zabbix.humidity": h
                    
		}
	    })
		
	    ''' Send data to zabbix '''
	    ret = zbx_container.send(zbx_container)
	    ''' If returns False, then we got a problem '''
	    if not ret:
		print "Ooops. Something went wrong when sending data to Zabbix"
            else:
                zbx_container.item_list = []

	time.sleep(5) 
    except IOError:
        print ("Error")



print "Everything is OK"

