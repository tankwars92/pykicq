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

command_packets="""            

UDP_CMD

      05 00             VERSION Protocol version
      00 00 00 00       ZERO Just zeros, purpouse unknown
      xx xx xx xx       MY_UIN Your (the client's) UIN
      xx xx xx xx       UDP_SESSION Used to prevent 'spoofing'. See below.
      xx xx             COMMAND
      xx xx             UDP_SEQ1 Starts at a random number
      xx xx             UDP_SEQ2 Starts at 1
      xx xx xx xx       CHECKCODE


UDP_CMD_ACK

      xx xx xx xx       RANDOM Random number.


UDP_CMD_KEEP_ALIVE

      ## This command has to be sent to the server every two minutes. If has not 
      ## been sent within two minutes, the server will assume that you are offline. 
 
      xx xx xx xx       RANDOM          Random number.

      ## Note! SEQ_NUM2 in the header should be set to zero when sending this 
      ## command. 


UDP_CMD_SEND_MESSAGE

      xx xx xx xx       RECEIVER_UIN        UIN of the user the message is sent to
      xx xx             MESSAGE_TYPE        Type of message being sent
      {'MSG_TEXT':1,'MSG_URL':4,'MSG_AUTH_REQ':6,'MSG_AUTH':8,'MSG_USER_ADDED':12,'MSG_CONTACTS':19}
      LL LL xx .. 00    MESSAGE_TEXT        NULL terminated string


UDP_CMD_LOGIN

      xx xx xx xx       TIME
	  xx xx xx xx       TCP_PORT
	  LL LL xx .. 00    PASSWORD
      98 00 00 00       X1	     
      xx xx xx xx       MY_IP	     
      xx                USE_TCP
      xx xx xx xx       STATUS
      03 00 00 00       X2
      00 00 00 00       X3
      10 00 98 00       X4
         

UDP_CMD_REG_NEW_USER

      ## This command is sent to the server without logging in. The UIN field of 
      ## header is set to NULL. The server will acknowledge this packet and reply 
      ## with a SRV_NEW_USER packet. This packet contains your new UIN, which you 
      ## must log in with immediately (send a CMD_LOGIN with your new UIN and the 
      ## password you have chosen). When you have logged in successfully 
      ## (SRV_LOGIN_REPLY) you should use the CMD_NEW_USER_INFO command to set up 
      ## basic info such as your nickname. 
   
      LL LL xx .. 00    PASSWORD        A password you want to use for the new account.
      A0 00 00 00       UNKNOWN1        Unknown.
      61 24 00 00       UNKNOWN2        Unknown.
      00 00 A0 00       UNKNOWN3        Unknown.
      00 00 00 00       UNKNOWN4        Unknown.

UDP_CMD_NEW_USER_INFO

      ## Send basic information about a new user being registered. This command is 
      ## sent when you log in the first time using a newly obtained UIN. See UDP_CMD_REG_NEW_USER. Parameters
      LL LL xx .. 00    NICK            Nickname, NULL terminated
      LL LL xx .. 00    FIRST           First name, NULL terminated
      LL LL xx .. 00    LAST            Last name, NULL terminated
      LL LL xx .. 00    EMAIL           Email address, NULL terminated
      01                UNKNOWN1        Unknown
      01                UNKNOWN2        Unknown
      01                UNKNOWN3        Unknown


UDP_CMD_CONTACT_LIST

      ## This command is used to inform the server of which users you wish to 
      ## recieve online/offline events for. Parameters

      NN xx xx xx xx    LIST_OF_UIN     contact list.
      
      ## Note! The maximum number of users is limited to about 120 because of ICQ's 
      ## maximum packet length of 450 bytes, if your contact list consists of more 
      ## users, you have to send this packet multiple times.


UDP_CMD_ADD_TO_LIST

      ## Add a user to contact list. After issuing this command you will recieve 
      ## user status changes for this user in addition to those on your contact 
      ## list. Parameters
      xx xx xx xx       UIN_TO_ADD       User to add


UDP_CMD_SEARCH_UIN

      ## This command is used to search for a user using his/her UIN. 

      xx xx             SEARCH_SEQ      See below.
      xx xx xx xx       SEARCH_UIN      The UIN to search for.


UDP_CMD_SEARCH_USER

      ## Search for a user. The server responds with SRV_USER_FOUND for every user 
      ## it finds and SRV_END_OF_SEARCH.

      LL LL xx .. 00    NICK            Nickname, NULL terminated
      LL LL xx .. 00    FIRST           First name, NULL terminated
      LL LL xx .. 00    LAST            Last name, NULL terminated
      LL LL xx .. 00    EMAIL           Email address, NULL terminated


UDP_CMD_SEND_TEXT_CODE

      ## This packet is used to send special commands to the server as text. 
      
      LL LL xx .. 00    TEXT_CODE       NULL terminated string containing of the 
      05 00             X1              Unknown, usually 05 00

      ## These are the different TEXT_CODEs available:
      ##      B_USER_DISCONNECTED Disconnect from the server
      ##      B_MESSAGE_ACK Tells the server to respond immediately, used when you  have trouble connecting.
      ##      B_KEEPALIVE_ACK Unknown, probably similar to B_MESSAGE_ACK
      ##
      ## Note! SEQ_NUM2 in the header should be set to zero when sending this 
      ## command. 


UDP_CMD_ACK_MESSAGES

      ## Remove old messages from server. Usually sent when SRV_X2 is recieved. 
      xx xx xx xx      RANDOM           Random number.

       
UDP_CMD_INFO_REQ 

      ## Request basic information about a user. Parameters
      xx xx xx xx       UIN             The UIN of the user you are requesting info about.

      ## The server will respond with SRV_INFO_REPLY. 


UDP_CMD_EXT_INFO_REQ

      ## Request extended information about a user. Parameters
      xx xx xx xx       UIN             The UIN of the user you are requesting info about.
      
      ## The server will respond with SRV_EXT_INFO_REPLY. 


UDP_CMD_UPDATE_EXT_INFO

       
UDP_CMD_QUERY_SERVERS

      ## Query the server about adresses to other servers.


UDP_CMD_QUERY_ADDONS

      ## Query the server about globally defined add-ons.

      
UDP_CMD_STATUS_CHANGE

      ## Change users online status. (Away, invisible etc.) Parameters
      xx xx xx xx       STATUS      The new status. See below


UDP_CMD_NEW_USER_1


UDP_CMD_UPDATE_INFO

      ## Update your info in the servers user database.
      LL LL xx .. 00    NICK        Nickname, NULL terminated
      LL LL xx .. 00    FIRST       First name, NULL terminated
      LL LL xx .. 00    LAST        Last name, NULL terminated
      LL LL xx .. 00    EMAIL       Email address, NULL terminated
 

UDP_CMD_AUTH_UPDATE

      ## Update you authorization status. (i.e. do you want users to require your 
      ## permission to add you to their contact lists?) Note that this does only 
      ## concern the Mirabilis client, most clones allow their users to override 
      ## this setting.
      xx xx xx xx       AUTHORIZE       TRUE => no authorization required, FALSE => authorization required.


UDP_CMD_META_USER 
      ## Set or get user information. Parameters
      xx xx             META_COMMAND

      
META_CMD_REQ_INFO

      ## Ask meta info about a user
      xx xx xx xx       UIN             The UIN of the user you are requesting info about.      
     

META_CMD_SET_INFO 
      LL LL xx .. 00    NICK        Nickname
      LL LL xx .. 00    FIRST       First name
      LL LL xx .. 00    LAST        Last name
      LL LL xx .. 00    PRIMARY_EMAIL   Primary email address
      LL LL xx .. 00    SECONDARY_EMAIL Secondary email address
      LL LL xx .. 00    OLD_EMAIL   Old email address
      LL LL xx .. 00    CITY        City
      LL LL xx .. 00    STATE       State
      LL LL xx .. 00    PHONE       Phone number
      LL LL xx .. 00    FAX         Fax number
      LL LL xx .. 00    STREET      Street address
      LL LL xx .. 00    CELLULAR    Cellular phone number
      xx xx xx xx       ZIPCODE     Zip (postal) code. 
      xx xx             COUNTRY     Country code
      xx                TIMEZONE    Time zone
      xx                EMAIL_HIDE   


META_CMD_SET_HOMEPAGE
      xx xx             AGE         Age, ff ff = not entered.
      xx                GENDER      1 = female, 2 = male
      LL LL xx .. 00    HOMEPAGE    URL to personal homepage, NULL terminated
      xx                BYEAR       Year of birth (from 1900).
      xx                BMONTH      Month of birth (13 here would be fun... ;)).
      xx                BDAY        Day of birth.
      xx                LANG1       Spoken language #1.
      xx                LANG2       Spoken language #2.
      xx                LANG3       Spoken language #3.

META_CMD_SET_WORK_INFO
      LL LL xx .. 00    WCITY       City, NULL terminated
      LL LL xx .. 00    WSTATE      State, NULL terminated
      LL LL xx .. 00    WPHONE      Phone number, NULL terminated
      LL LL xx .. 00    WFAX        Fax number, NULL terminated
      LL LL xx .. 00    WADDRESS    Address, NULL terminated
      xx xx xx xx       WZIP        Unknown
      xx xx             WCOUNTRY    Unknown
      LL LL xx .. 00    COMPANY     Name of the company, NULL terminated
      LL LL xx .. 00    DEPARTMENT  Name of departement, NULL terminated
      LL LL xx .. 00    JOB         Position, NULL terminated
      xx xx             OCCUPATION  Unknown
      LL LL xx .. 00    WHOMEPAGE   URL to corporate homepage, NULL terminated

      

META_CMD_SET_ABOUT         
      LL LL xx .. 00    ABOUT       Text string, NULL terminated

META_CMD_SET_SECURE        


"""


#####################################################################################################

def _U8(u8):
  return chr(u8)

def _U32(u32):
  if u32 >=0:
    return chr(u32 & 0xff)+chr((u32 & 0xff00)>>8)+chr((u32 & 0xff0000)>>16)+chr((u32 & 0xff000000)>>24)
  else:
    u32 &= 0x7fffffff
    return chr(u32 & 0xff)+chr((u32 & 0xff00)>>8)+chr((u32 & 0xff0000)>>16)+chr(((u32 & 0xff000000)>>24)+0x80)

def _U16(u32):
  return chr(u32 & 0xff)+chr((u32 & 0xff00)>>8)

def _STR(str):
  return _U16(len(str)+1) + str + chr(0)

def _U8_LIST_U32(L):
  s=_U8(len(L))
  for x in L:
    s+=_U32(x)
  return s



#####################################################################################################


def make_functions():
  reg_exps = [
               [ re.compile(r'^\s*(NN xx xx xx xx)'),'_U8_LIST_U32'],
               [ re.compile(r'^\s*(LL)\s+LL\s+xx\s+..\s+00'),'_STR'],
               [ re.compile(r'^\s*(\w\w\s+\w\w\s+\w\w\s+\w\w)\s+'),'_U32' ],
               [ re.compile(r'^\s*(\w\w\s+\w\w)\s+'),'_U16' ],
               [ re.compile(r'^\s*(\w\w)\s+'),'_U8' ],
             ]

  re_hexa = re.compile(r'\s*([0-9a-fA-F][0-9a-fA-F]\s*)+')
  eval_string=''
  first_func=0
  for x in command_packets.splitlines():
    if x[0:7]=='UDP_CMD' or x[0:8]=='META_CMD':
      if first_func:
        eval_string+='  return p\n'
      first_func=1
      eval_string+='\n'
      eval_string += "def c_"+x+"(p,d):\n"
    else:
      for y in reg_exps:
        mo=y[0].search(x)
        if mo:
          mo2=re_hexa.match(mo.group(1))
          if mo2:
            l=mo2.string[mo2.start():mo2.end()].split()
            l.reverse()
            number='0x'+string.join(l,'')
            eval_string += "  p=p+%s(%s)\n"%(y[1],number)
          else:
            name= x[mo.end():].split()[0].lower()
            eval_string += "  p=p+%s(d['%s'])\n"%(y[1],name)
          break
  eval_string+='  return offset\n'
  #print eval_string
  return eval_string

exec(make_functions())


## no need to keep in memory
del command_packets

