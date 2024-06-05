#!/usr/bin/env python3
import struct
from tqdm import tqdm
from spi import SPI
spi = SPI(0)
print("speed:",spi.getSpeed())
spi.setSpeed(8000000)
print("speed:",spi.getSpeed())
#print("delay:",spi.get_delay())
#spi.put(b"\x9e" + b"\x00"*20)

allret = []
for addr in range(0, 0x100000, 0x1000):
    print(struct.pack(">I", addr)[1:])
    ret = spi.put(b"\x03" + struct.pack(">I", addr)[1:], fSelEnd=0)
    ret = spi.get(0x1000, fSelEnd=1)
    allret.append(ret)

out = b''.join(allret)
with open("dump", "wb") as f:
    f.write(out)

del spi

