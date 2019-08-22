import time
from datetime import datetime
#from PIL import ImageGrab as IG
#from PIL import ImageDraw as ID
import struct
from PIL import Image as Im
import socket

class Wallcomm:
  def __init__(self, offsets=(0,), base_addr="192.168.10.", port=5656, packsize=128, brightness=1):
    self.PIX_HEADER = b"\x00\x00"
    self.FLUSH_HEADER = b"\x10\x00"
    self.PACK_SIZE = packsize
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.offsets = offsets
    self.walls = []
    self.brightness = brightness
    # todo: check which walls are active
    for o in offsets:
      ip = base_addr + str(int(o)+100)
      self.walls.append({"active" : True, "ip" : ip })

  def sendFrame(self, im):
    # check size
    if im.size[1] != 32 or im.size[0] != 32*len(self.walls):
      print("wrong image size for %d walls!" % len(self.walls))
      return
    else:
      # send chunks
      for i in range(len(self.walls)):
        chunk = im.crop((i*32,0,i*32+32,32))
        self.sendPackets(chunk, self.walls[i]["ip"])
      # flush frame
      self.sock.sendto(self.FLUSH_HEADER, ("192.168.10.255", self.port))

  def sendPackets(self, im, ip):
    pxdata = im.load()
    #packets = []
    data = b""
    for y in range(32):
      for x in range(32):
        index = pxdata[x,y]
        data = data + struct.pack(">BBB",
                                  int(index[0]*self.brightness),
                                  int(index[1]*self.brightness),
                                  int(index[2]*self.brightness))
    #self.img.tostring()
    addr = 0
    while data:
      buf = data[0:3*self.PACK_SIZE]
      packet = self.PIX_HEADER + struct.pack("<H", len(buf)//3) + struct.pack("<H", addr) + buf
      addr += self.PACK_SIZE
      data = data[3*self.PACK_SIZE:]
      self.sock.sendto(packet, (ip, self.port))

