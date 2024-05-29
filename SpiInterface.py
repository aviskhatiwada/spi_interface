#!/usr/bin/python3

import struct
import sys
import usb1
context=usb1.USBContext() 

def listinfo():
	for d in dev.getDeviceList():
		print(f"{d.getVendorID():04x} || {d.getProductID():04x} || {d.getSerialNumber()}")
#10c4:ea60

'''
64 bit 
DSPI (serial) functions:
getspeed

        s[8] = 3;
        s[9] = 6;
        s[10] = 4;
        s[11] = DVT::PrtActive(v6);
        v5 = pfrqCur;
        s[80] = 4;
        s[72] = 1;

setspeed
        s[8] = 7;
        s[9] = 6;
        s[10] = 3;
        s[11] = DVT::PrtActive(v10);
        v6 = v12;
        v9 = v11;
        v8 = 4;
        v7 = 1;

gs:  3 6 4 P  . . . . (4,1) 
ss:  7 6 3 P 

ex: 3 6 0 P (enables port)

dis: s[]: 3 6 1 P
pb: 10 6 7 P [0 1 1]
'''

ENABLE=0	
DISABLE=1
GETSPEED=4
SETSPEED=3

class SPI_INTERFACE(object):
	# (1) - write endpoint, (2) - read endpoint
	def __init__(self, port):
		self.port=port
		self.context=usb1.USBContext()
		self.handle=self.context.openByVendorIDAndProductID(0x1443, 0x0007)
		try:
			self.handle.claimInterface(0)
		except:
			self.handle.detachKernelDriver(0) 
			self.handle.claimInterface(0)
			self.handle.setConfiguration(1)
		self.enable()
	def enable(self):
		self.handle.bulkWrite(1, struct.pack('BBBB', 3, 6, ENABLE, self.port))
	def getSpeed(self):
		self.handle.bulkWrite(1, struct.pack('BBBB', 3, 6, GETSPEED, self.port))
		return int.from_bytes(self.handle.bulkRead(2, 0x10, 1000)[2:], "little")
	def setSpeed(self, set_to):
		self.handle.bulkWrite(1, struct.pack('BBBBI', 7, 6, SETSPEED, self.port, set_to))
	def disable(self):
		self.handle.bulkWrite(1, struct.pack('BBBB', 3, 6, DISABLE, self.port))
	def sendByte(self, byte):
		self.handle.bulkWrite(1, struct.pack('BBBBBBB', 10,6,7,self.port,1,1,byte))
	def __del__(self):
		self.disable()
		self.handle.close()
		

s=SPI_INTERFACE(0)
print(s.getSpeed())
s.setSpeed(10000)
#s.sendByte(0xff)
