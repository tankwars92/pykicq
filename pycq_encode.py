# 
# pycq : a 100% python module for writing icq clients.
#
# Copyright (C) 2001, Michael Vanslembrouck <zmiczmic@hotmail.com>
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#


import time
from pycq_UDP_CMD import *
from pycq_UDP_SRV import *
from pycq_def import *

###############################################################################



def UDP_print_packet(packet):
  packet=packet.raw_packet
  l=''
  a=''
  print '=========================='
  print 'len',len(packet)
  print '=========================='
  for x in xrange(len(packet)):
    l=l+"%2x "%ord(packet[x])
    if ord(packet[x])>32:
      a=a+packet[x]
    else:
      a+='.'
    if x&3 == 3:
      print l,a
      l=''
      a=''
  if l:
    print l
  print '=========================='


def U32(u32):
  if u32 >=0:
    return chr(u32 & 0xff)+chr((u32 & 0xff00)>>8)+chr((u32 & 0xff0000)>>16)+chr((u32 & 0xff000000)>>24)
  else:
    u32 &= 0x7fffffff
    return chr(u32 & 0xff)+chr((u32 & 0xff00)>>8)+chr((u32 & 0xff0000)>>16)+chr(((u32 & 0xff000000)>>24)+0x80)

def _U32(s,offset=0):
  return (ord(s[offset+3])<<24) + (ord(s[offset+2])<<16) + (ord(s[offset+1])<<8) + (ord(s[offset+0]))


##############################################################################
#
#  python shift right propagates the sign bit. This is not wat we want
#
def SHR(i,n):
  if i>=0:
    return i>>n
  i >>= n
  i  &= ( 0x7fffffff >> (n-1) )
  return i

##############################################################################
#
#  python does not allow integer overflow, so we have to emulate it via
#  these ugly functions
#

def mult(i1,i2):
  i1=long(i1)
  i2=long(i2)
  m = (i1 * i2) & 0xffffffffL
  if m > 0x7fffffffL:
    m=m-0x100000000L
  return int(m)

def plus(i1,i2):
  i1=long(i1)
  i2=long(i2)
  m = (i1 + i2) & 0xffffffffL
  if m > 0x7fffffffL:
    m=m-0x100000000L
  return int(m)


###############################################################################
#
#  From this point, all code was taken over almost literally from 
#  icqlib by Denis V. Demitrienko and others.
#

UDP_table = (
  0x59, 0x60, 0x37, 0x6B, 0x65, 0x62, 0x46, 0x48, 0x53, 0x61, 0x4C, 0x59, 0x60, 0x57, 0x5B, 0x3D,
  0x5E, 0x34, 0x6D, 0x36, 0x50, 0x3F, 0x6F, 0x67, 0x53, 0x61, 0x4C, 0x59, 0x40, 0x47, 0x63, 0x39,
  0x50, 0x5F, 0x5F, 0x3F, 0x6F, 0x47, 0x43, 0x69, 0x48, 0x33, 0x31, 0x64, 0x35, 0x5A, 0x4A, 0x42,
  0x56, 0x40, 0x67, 0x53, 0x41, 0x07, 0x6C, 0x49, 0x58, 0x3B, 0x4D, 0x46, 0x68, 0x43, 0x69, 0x48,
  0x33, 0x31, 0x44, 0x65, 0x62, 0x46, 0x48, 0x53, 0x41, 0x07, 0x6C, 0x69, 0x48, 0x33, 0x51, 0x54,
  0x5D, 0x4E, 0x6C, 0x49, 0x38, 0x4B, 0x55, 0x4A, 0x62, 0x46, 0x48, 0x33, 0x51, 0x34, 0x6D, 0x36,
  0x50, 0x5F, 0x5F, 0x5F, 0x3F, 0x6F, 0x47, 0x63, 0x59, 0x40, 0x67, 0x33, 0x31, 0x64, 0x35, 0x5A,
  0x6A, 0x52, 0x6E, 0x3C, 0x51, 0x34, 0x6D, 0x36, 0x50, 0x5F, 0x5F, 0x3F, 0x4F, 0x37, 0x4B, 0x35,
  0x5A, 0x4A, 0x62, 0x66, 0x58, 0x3B, 0x4D, 0x66, 0x58, 0x5B, 0x5D, 0x4E, 0x6C, 0x49, 0x58, 0x3B,
  0x4D, 0x66, 0x58, 0x3B, 0x4D, 0x46, 0x48, 0x53, 0x61, 0x4C, 0x59, 0x40, 0x67, 0x33, 0x31, 0x64,
  0x55, 0x6A, 0x32, 0x3E, 0x44, 0x45, 0x52, 0x6E, 0x3C, 0x31, 0x64, 0x55, 0x6A, 0x52, 0x4E, 0x6C,
  0x69, 0x48, 0x53, 0x61, 0x4C, 0x39, 0x30, 0x6F, 0x47, 0x63, 0x59, 0x60, 0x57, 0x5B, 0x3D, 0x3E,
  0x64, 0x35, 0x3A, 0x3A, 0x5A, 0x6A, 0x52, 0x4E, 0x6C, 0x69, 0x48, 0x53, 0x61, 0x6C, 0x49, 0x58,
  0x3B, 0x4D, 0x46, 0x68, 0x63, 0x39, 0x50, 0x5F, 0x5F, 0x3F, 0x6F, 0x67, 0x53, 0x41, 0x25, 0x41,
  0x3C, 0x51, 0x54, 0x3D, 0x5E, 0x54, 0x5D, 0x4E, 0x4C, 0x39, 0x50, 0x5F, 0x5F, 0x5F, 0x3F, 0x6F,
  0x47, 0x43, 0x69, 0x48, 0x33, 0x51, 0x54, 0x5D, 0x6E, 0x3C, 0x31, 0x64, 0x35, 0x5A, 0x00, 0x00,
)


def UDP_calc_check_code(packet):
  num1   = ord(packet[8])
  num1 <<= 8
  num1  += ord(packet[4])
  num1 <<= 8
  num1  += ord(packet[2])
  num1 <<= 8
  num1  += ord(packet[6])

  #r1 = 0x18 + rnd.randint(len(packet)-0x19)
  #r2 = rnd.randint(0,255)
  r1  = 0x18
  r2  = 0x00

  num2   = r1
  num2 <<= 8
  num2  += ord(packet[r1])
  num2 <<= 8
  num2  += r2
  num2 <<= 8
  num2  += UDP_table[r2]
  num2  ^= 0x00ff00ff

  return num1 ^ num2


def UDP_scramble(cc):
  
  a0 = cc & 0x0000001F
  a1 = cc & 0x03E003E0
  a2 = cc & 0xF8000400
  a3 = cc & 0x0000F800
  a4 = cc & 0x041F0000

  a0 <<= 0x0C
  a1 <<= 0x01
  a2   = SHR(a2,0x0A)
  a3 <<= 0x10
  a4   = SHR(a4,0x0F)
  
  #print a0,a1,a2,a3,a4

  return a0 + a1 + a2 + a3 + a4;


##############################################################################

def UDP_encode(packet):
  #UDP_print_packet(packet)
  checkcode = UDP_calc_check_code(packet)
  #print "%X"%checkcode
  PL=len(packet)
  #print PL
  packet=packet+'extra'
  buffer = packet[0:0x0a]
  code1 = mult(PL,0x68656c6c)
  code2 = plus(code1,checkcode)
  #print "%X %X %X"%(checkcode,code1,code2)
  pos = 0x0a
  while pos < PL:
    data  = _U32(packet[pos:pos+4])
    code3 = code2 + UDP_table[pos & 0xff]
    data ^= code3
    buffer += U32(data)
    pos += 4
  checkcode = UDP_scramble(checkcode)
  buffer = buffer[:0x14]+U32(checkcode)+buffer[0x18:PL]
  #UDP_print_packet(buffer)
  return buffer






