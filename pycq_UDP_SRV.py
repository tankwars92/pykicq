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

import string,re
from pycq_def import *

server_packets="""

UDP_SRV_PACKET_V3
        03 00           VERSION         ICQ protocol version
        xx xx           COMMAND         Code for service the server should provide
        xx xx           SEQ1            First sequence number
        xx xx           SEQ2            Second sequence number
        xx xx xx xx		MY_UIN		    UIN
        xx xx xx xx		CHECKCODE       Checksum


UDP_SRV_PACKET

        05 00           VERSION Protocol version 
        00              ZERO Unknown 
        xx xx xx xx	    SESSION Same as in your login packet. 
        xx xx		    COMMAND  
        xx xx		    SEQ1 Sequence 1 
        xx xx           SEQ2 Sequence 2 
        xx xx xx xx     MY_UIN Your (the client's) UIN 
        xx xx xx xx     CHECKCODE  


UDP_SRV_ACK
 

UDP_SRV_GO_AWAY


UDP_SRV_NEW_UIN


UDP_SRV_LOGIN_REPLY

         8C 00 00 00     X1 Unknown (dec: 140) 
         F0 00           X2 Unknown (dec: 240) 
         0A 00           X3 Unknown (dec: 10) 
         0A 00           X4 Unknown (dec: 10) 
         05 00           X5 Unknown (dec: 5, version?) 
         IP IP IP IP     MY_IP Your IP 
         xx xx xx xx     X6 Unknown 
 

UDP_SRV_BAD_PASS


UDP_SRV_USER_ONLINE

         xx xx xx xx     UIN UIN of the user who changed status 
         IP IP IP IP     IP The user's IP address 
         xx xx xx xx     PORT The port the user is listening for connections on 
         IP IP IP IP     REAL_IP
         xx              USE_TCP 
         xx xx           STATUS
         xx xx           X4
         xx xx xx xx     X1
         xx xx xx xx     X2
         xx xx xx xx     X3
 
UDP_SRV_STATUS_UPDATE
         xx xx xx xx     UIN UIN of the sender 
         xx xx           STATUS
         xx xx           X1

UDP_SRV_USER_OFFLINE

         xx xx xx xx     UIN UIN of the user who changed status 
 

UDP_SRV_QUERY


UDP_SRV_USER_FOUND

         xx xx xx xx     UIN UIN of the user found 
         LL LL xx .. 00  NICK User's nickname 
         LL LL xx .. 00  FIRST User's first name 
         LL LL xx .. 00  LAST User's last name 
         LL LL xx .. 00  EMAIL User's email address 
         xx              AUTHORIZE User's authorization status, see below 


UDP_SRV_END_OF_SEARCH

         xx              TOO_MANY The search genarated too many hits 


UDP_SRV_OFFLINE_MESSAGE

         xx xx xx xx     UIN UIN of the sender 
         xx xx           YEAR The year the message was sent 
         xx              MONTH The month the message was sent 
         xx              DAY Day of month 
         xx              HOUR Hour the message was sent 
         xx              MINUTE Minutes 
         xx xx           MESSAGE_TYPE What kind of message it is (see below) 
         LL LL xx .. 00  MESSAGE_TEXT Message text 


UDP_SRV_ONLINE_MESSAGE

         xx xx xx xx     UIN UIN of the sender 
         xx xx           MESSAGE_TYPE
         LL LL xx .. 00  MESSAGE_TEXT Message text 


UDP_SRV_UPDATE_SUCCESS


UDP_SRV_UPDATE_FAIL


UDP_SRV_META_USER

         xx xx           META_COMMAND Subcommand, see below for explanation 
         xx              RESULT Result of the function, success or failure. See below 
                         {0x0A:'success',0x32:'Failure'}


UDP_SRV_INFO_REPLY

         xx xx xx xx     UIN UIN of the user
         LL LL xx .. 00  NICK User's nickname 
         LL LL xx .. 00  FIRST User's first name 
         LL LL xx .. 00  LAST User's last name 
         LL LL xx .. 00  EMAIL User's email address 
         xx              AUTHORIZE User's authorization status, see below 


UDP_SRV_EXT_INFO_REPLY

         xx xx xx xx     UIN UIN of the user
         LL LL xx .. 00  CITY
         xx xx           COUNTRY_CODE
         xx              COUNTRY_STAT
         LL LL xx .. 00  STATE
         xx xx           AGE
         xx              GENDER
         LL LL xx .. 00  PHONE
         LL LL xx .. 00  HOMEPAGE
         LL LL xx .. 00  ABOUT


UDP_SRV_X1


UDP_SRV_X2


UDP_SRV_FORCE_DISCONNECT


UDP_SRV_MULTI_PACKET_
         xx              NUM_PACKETS             Number of packets 


META_SRV_USER_FOUND

         xx xx xx xx     UIN The user's UIN 
         LL LL xx .. 00  NICK Nickname 
         LL LL xx .. 00  FIRST First name 
         LL LL xx .. 00  LAST Last name 
         LL LL xx .. 00  EMAIL Email 
         xx              AUTHORIZE Authorization status 
         xx xx           X2 Unknown 
         xx xx xx xx     X3 Unknown 

META_SRV_USER_WORK         

         LL LL xx .. 00  WCITY 
         LL LL xx .. 00  WSTATE
         LL LL xx .. 00  WPHONE
         LL LL xx .. 00  WFAX 
         LL LL xx .. 00  WADDRESS
         xx xx xx xx     WZIP
         xx xx           WCOUNTRY
         LL LL xx .. 00  COMPANY 
         LL LL xx .. 00  DEPARTMENT
         LL LL xx .. 00  JOB 
         xx xx           OCCUPATION 
         LL LL xx .. 00  WHOMEPAGE 


META_SRV_USER_MORE         

         xx xx           AGE 
         xx              GENDER 
         LL LL xx .. 00  HOMEPAGE 
         xx              BYEAR 
         xx              BMONTH 
         xx              BDAY 
         xx              LANG1 
         xx              LANG2 
         xx              LANG3 


META_SRV_USER_INTERESTS    
         NN {INTEREST}           INTERESTS

INTEREST
         xx xx                   ICATEGORY
         LL LL xx .. 00          INTERESTS

META_SRV_USER_AFFILIATIONS 


META_SRV_USER_HPCATEGORY   


META_SRV_USER_ABOUT

         LL LL xx .. 00  ABOUT About string 


META_SRV_USER_INFO

         LL LL xx .. 00   NICK Nickname 
         LL LL xx .. 00   FIRST First name 
         LL LL xx .. 00   LAST Last name 
         LL LL xx .. 00   PRIMARY_EMAIL Primary email address 
         LL LL xx .. 00   SECONDARY_EMAIL Secondary email address 
         LL LL xx .. 00   OLD_EMAIL Old email address 
         LL LL xx .. 00   CITY City 
         LL LL xx .. 00   STATE State 
         LL LL xx .. 00   PHONE Phone number 
         LL LL xx .. 00   FAX Fax number 
         LL LL xx .. 00   STREET Street address 
         LL LL xx .. 00   CELLULAR Cellular phone number 
         xx xx xx xx      ZIPCODE Zip (postal) code.  
         xx xx            COUNTRY Country code 
         xx               TIMEZONE Time zone 
         xx               AUTHORIZE Authorization status 1 - no auth required, 0 - required
         xx               WEBAWARE Show the user's online status on the web 
         xx               HIDE_IP Don't show the user's IP 

"""

#####################################################################################################

def __U32(s,offset=0):
  return offset+4, (ord(s[offset+3])<<24) + (ord(s[offset+2])<<16) + (ord(s[offset+1])<<8) + (ord(s[offset+0]))

def __U16(s,offset=0):
  return offset+2, (ord(s[offset+1])<<8) + (ord(s[offset+0]))

def __U8(s,offset=0):
  return offset+1, ord(s[offset])

def __STR(s,offset=0):
  offset+=2
  start=offset
  while ord(s[offset]):
    offset += 1
  return offset+1,s[start:offset]

def __IP(s,offset=0):
  return offset+4, "%d"%ord(s[offset]) + ".%d"%ord(s[offset+1]) + ".%d"%ord(s[offset+2]) + ".%d"%ord(s[offset+3])
  
def __LOOP(s,offset,func):
  offset,nbr = __U8(s,offset)
  L=[]
  for x in range(nbr):
    d={}
    offset+=apply(func,(s[offset:],d))
    L.append(d)
  return offset,L

#####################################################################################################

def make_functions():
  reg_exps = [
               [ re.compile(r'^\s+NN\s+\{(.*)\}'),'__LOOP' ],
               [ re.compile(r'^\s+IP\s+IP\s+IP\s+IP\s+'),'__IP' ],
               [ re.compile(r'^\s+LL\s+LL\s+xx\s+\.\.\s+00'),'__STR'],     
               [ re.compile(r'^\s+\w\w\s+\w\w\s+\w\w\s+\w\w\s+'),'__U32' ],
               [ re.compile(r'^\s+\w\w\s+\w\w\s+'),'__U16' ],
               [ re.compile(r'^\s+\w\w\s+'),'__U8' ],
             ]


  eval_string=''
  first_func=0
  for x in server_packets.splitlines():
    if len(x) and not x[0] in string.whitespace:
      if first_func:
        eval_string+='  return offset\n'
      first_func=1
      eval_string+='\n'
      eval_string += "def parse_"+x+"(p,d):\n"
      eval_string += "  offset=0\n"
    else:
      for y in reg_exps:
        mo=y[0].search(x)
        if mo:
          name= x[mo.end():].split()[0].lower()
          if y[1]!='__LOOP':
            eval_string += "  offset,d['%s']=%s(p,offset)\n"%(name,y[1])
          else:
            eval_string += "  offset,d['%s']=%s(p,offset,%s)\n"%(name,y[1],'parse_'+mo.group(1))
          break
  eval_string+='  return offset\n'
  #print eval_string
  return eval_string


exec(make_functions())
#no need to keep this big string in memory
del server_packets
del make_functions


#######################################################################################

def UDP_SRV(p,o=None):
  d={}

  if ord(p[0])==5:
    offset = parse_UDP_SRV_PACKET(p,d)
    d['command_nbr']=d['command']
    d['command']  =  m_UDP_SRV[d['command']]
    function_name='parse_'+d['command']
    if globals().has_key(function_name):
      if o: o.dprint(6,"calling handler function for UDP server packet "+d['command'])
      offset += apply(globals()[function_name],(p[offset:],d))
    else:
      if o: o.dprint(2,"No handler function for UDP server packet "+d['command'])
  
  if ord(p[0])==3:
    offset = parse_UDP_SRV_PACKET_V3(p,d)
    d['command_nbr']=d['command']
    d['command']  =  "0x%X"%d['command']
  
  if d['command_nbr']==UDP_SRV_META_USER:
    d['meta_command_nbr']=d['meta_command']
    d['meta_command']=m_META[d['meta_command']]
    meta_function_name='parse_'+d['meta_command']
    if globals().has_key(meta_function_name):
      if o: o.dprint(6,"calling handler function for UDP meta server packet "+d['meta_command'])
      offset = apply(globals()[meta_function_name],(p[offset:],d))
    else:
      if o: o.dprint(2,"No handler function for UDP server meta packet "+d['meta_command'])

  return d


def parse_UDP_SRV_MULTI_PACKET(p,d):
  offset=parse_UDP_SRV_MULTI_PACKET_(p,d)
  c=[]
  for x in range(d['num_packets']):
    offset,size=__U16(p,offset)
    c.append(UDP_SRV(p[offset:]))
    offset+=size
  d['packets']=c
  return offset


      