#!/usr/bin/python3

from hexdump import hexdump
import array
import struct
import sys
import usb1
import usb.core
import usb.util
import binascii
'''
# DspiEnableEx:   3 6 0 <1: port request>
# DspiDisable:    3 6 1 <1: port request>
# DspiSetSpeed:   7 6 3 <1: active port> <4: speed>
# DspiGetSpeed:   3 6 4 <1: active port>
# DspiSetSpiMode: 4 6 5 <1: active port> <1: mode?>
# DspiSetSelect:  4 6 6 <1: active port> <1: select state>
# DspiPut:       10 6 7 <1: active port> <1: fSelStart> <1: fSelEnd>
#                       <1: should receive?> <4: number of bytes>
# (fSelStart, fSelEnd, rgbSnd, rgbRcv, cbSend, fOverlap)

self.ep_cmdout  = usb.util.find_descriptor(intf, bEndpointAddress = 1)
self.ep_cmdin   = usb.util.find_descriptor(intf, bEndpointAddress = 0x82)
self.ep_dataout = usb.util.find_descriptor(intf, bEndpointAddress = 3)
self.ep_datain  = usb.util.find_descriptor(intf, bEndpointAddress = 0x84)
'''

ENABLE=0    
DISABLE=1
GETSPEED=4
SETSPEED=3

STAT_BUSY = 0x1
STAT_WEL = 0x2

CMD_GET_STATUS = 0x05
CMD_WRITE_ENABLE = 0x6
CMD_READ_ID = 0x9F
CMD_WAKEUP = 0xAB
CMD_CHIP_ERASE = 0xC7
CMD_PAGE_PROGRAM = 0x02
CMD_FAST_READ = 0xB
CMD_RFSR=0x70
#flash protocols
class SPI_INTERFACE(object):

    STAT_BUSY=1
    def __init__(self, port):
        self.port=port
        self.dev = usb.core.find(idVendor=0x1443, idProduct=0x0007)
        self.dev.reset()
        self.dev.set_configuration()


        cfg = self.dev.get_active_configuration()
        intf = usb.util.find_descriptor(cfg)


        self.ep_cmdout  = usb.util.find_descriptor(intf, bEndpointAddress = 1)
        self.ep_cmdin   = usb.util.find_descriptor(intf, bEndpointAddress = 0x82)
        self.ep_dataout = usb.util.find_descriptor(intf, bEndpointAddress = 3)
        self.ep_datain  = usb.util.find_descriptor(intf, bEndpointAddress = 0x84)

        self.ENABLED=0

    def __return_bytes(self, num=16):
        return bytes(self.ep_cmdin.read(num)) 

    def enable(self):
        self.ep_cmdout.write(struct.pack('BBBB', 3, 6, 0, self.port))
        self.ENABLED=1
        return self.__return_bytes()[1:]
    #talk to flash through spi protocols
    #talk to flash through spi protocols

    def setSpeed(self, speed):
        self.ep_cmdout.write(struct.pack('BBBBI', 7,6,3,0, speed))
        return self.__return_bytes()[1:]

    def getSpeed(self):
        self.ep_cmdout.write(struct.pack('BBBB', 3, 6, 4, self.port))
        return self.__return_bytes()[2:]

    def setMode(self, mode,sh=False):
        self.ep_cmdout.write(struct.pack('BBBBBB', 4,6,5,self.port,mode,sh))
        return self.__return_bytes()
        

    def io(self, write_bytes, read_byte_count=0):
        write_bytes=list(write_bytes)
        if len(write_bytes) < read_byte_count:
            write_bytes.extend([0]*(read_byte_count-len(write_bytes)))
        write_b_count=len(write_bytes)
        read_bytes=[]


            # Do the IO
        while write_bytes or len(read_bytes) < read_byte_count:
            if write_bytes:
                self.ep_dataout.write(write_bytes[:64])
                write_bytes = write_bytes[64:]

            if read_byte_count:
                to_read = min(64, read_byte_count)
                read_bytes.extend(self.ep_datain.read(to_read))
        return read_bytes
        

    def put(self, b, fSelStart=0, fSelEnd=1):
        rcv = 1
        self.ep_cmdout.write(struct.pack("BBBBBBBI", 10, 6, 7, 0, fSelStart, fSelEnd, rcv, len(b)))
        self.ep_dataout.write(b)
        #hexdump(self.ep_cmdin.read(0x10))
    def get(self, nbytes, fSelStart=0, fSelEnd=1, bfill=1):
        rcv=1
        self.ep_cmdout.write(struct.pack("BBBBBBBB", 10,6,8,0,fSelStart, fSelEnd, rcv, nbytes))
        
        hexdump(self.ep_datain.read(100))

    def bulk_erase(self):
        self.put(b'\x06',16)

        self.put(b'\x70',16)
        hexdump(self.ep_datain.read(0x10))
        self.put(b'\x05',16)
        hexdump(self.ep_datain.read(0x10))

        self.put(b'\xc7', 16)
         

        self.put(b'\x70',16)
        hexdump(self.ep_datain.read(0x10))

        #self.waitDone()

    def write_to(self,fn_):
        data=fn_.read()
        for addr in range(0, len(data), 256):
            buf=data[addr:addr+256]
            pageProgram(addr, buf)
        
    def pageProgram(self,addr,buf):
        assert len(buf) <= 256
        assert addr & 0xff==0
        #self.io([0x02, (addr>>16) & 0xFF, (addr>>8)&0xff, addr&0xff] + list(buf))

    def getStatus(self):
        return self.io(b'/0x05',2)[1]

    def read(self, addr):
        inp=bytearray([CMD_FAST_READ, (addr>>16)&0xff, (addr>>8)& 0xFF, addr&0xff])
        self.put(inp)
        return hexdump(self.ep_cmdin.read(100))

    def waitDone(self):
        while self.getStatus() & self.STAT_BUSY:
            pass

s=SPI_INTERFACE(0)
s.enable()
s.setMode(0)
s.bulk_erase()
s.read(0xffffff)
#  06 WREN p88 BULK ERASE c7 p79 

