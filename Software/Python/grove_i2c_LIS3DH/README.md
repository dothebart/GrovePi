# python-lis3dh
Python library for using a [LIS3DH triple-axis accelerometer](https://www.adafruit.com/products/2809) on a Raspberry Pi

This is not a complete implementation of all the features of the LIS3DH - if you can help add more functionality then please contribute!


# Wiring 
we need to connect the wires of the groove plugs to the LIS3DH

I2C Groove pins:
------------------------
- Black - gnd 
- Red - 5V
- White - SDA
- Yellow - SCL - clock

LIS3DH Board
---------------------
https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/pinouts
- Vin VCC 5V / 3V   -> Red
- 3V out - if you need the convertet 3v - not needed.
- GND                    -> Black
- I2C SCL               -> Yellow
- I2C SDA               -> White
- SD0     - not needed
- CS       - not needed
- INT      - no interrupt connected yet



## Requirements
Requires the Adafruit I2C library which can be found at https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

## Useful reading
 * https://www.adafruit.com/datasheets/LIS3DH.pdf
 * https://github.com/adafruit/Adafruit_LIS3DH/blob/master/Adafruit_LIS3DH.cpp
 * https://github.com/adafruit/Adafruit_LIS3DH/blob/master/Adafruit_LIS3DH.h
 * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
 
## Credits
 * [Matt Dyson](http://mattdyson.org) - Original implementation
 * [Mal Smalley](https://github.com/MalSmalley) - Implementation of 'click' functionality 
 * [Wilfried Goesgens](https://github.com/dothebart/) - adopt to groove pi
