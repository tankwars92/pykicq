# -*- coding: utf-8 -*-
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
#
#
#
# Acknowledgment : this module would not have been possible without
# the example of icqlib (by Denis V. Dmitrienko, Bill Soudan and others)
# and the ICQ v5 protocol document by Henrik Isaksson.
#

### !!! PASTE YOUR UIN AND PASSWORD HERE !!! ###
_uin = 1111111   # must be int (number)
_password = 'password' # must be string


import socket,whrandom,time,select,types
import random
from pycq_encode import * 

rnd=whrandom.whrandom()

##############################################################################

class timer:
  def __init__(self,seconds):
    self.reset(seconds)
  def reset(self,seconds=None):
    if seconds:
      self.seconds=seconds
    self.end_time=time.time()+self.seconds
  def rings(self):
    if self.end_time<time.time():
      self.reset()
      return 1
    return 0

##############################################################################

class user:
  def __init__(self):
    self.on_contact_list=0
    self.status = 0xff00   # set offline


##############################################################################

class pycq:
  
  #############################################################################

  def dprint(self,level,*args):
    if level<=self.debug_level:
      s=string.join(args,' ')
      print "<%d><%d><%d> %s"%(self.udp_fileno,self.udp_port,level,s)

  ##############################################################################
  
  class _args:
    def __init__(self,dict=None):
      if dict:
        for x,y in dict.items():
          setattr(self,x,y)
    pass

  def args(self,dict=None):
    self.A=self._args(dict)
    return self.A

  class cmd_packet:
    def __init__(self,pycq_instance,cmd):
      for (x,y) in pycq_instance.A.__dict__.items():
        setattr(self, x, y) 
      self.command=cmd
      self.my_uin = _uin
      self.udp_session = pycq_instance.udp_session
      self.seq1 = pycq_instance.udp_seq1
      self.seq2 = pycq_instance.udp_seq2
      self.udp_seq1 = pycq_instance.udp_seq1
      self.udp_seq2 = pycq_instance.udp_seq2
      pycq_instance.udp_seq1 += 1
      pycq_instance.udp_seq2 += 1
      self.checkcode = 0
      self.tries = 0
      if not pycq_instance.A.__dict__.has_key('expect_ack'):
        self.expect_ack = 1
      self.time=int(time.time())
      self.random=rnd.randint(0,0x3ffffff)
      pycq_instance.args()

  def UDP_send(self,packet,defer_if_not_logged=0):
    #UDP_print_packet(packet)
    if defer_if_not_logged and not self.logged:
      self.dprint(3,'!!! UDP cmd packet %s (%d,%d) defered until client has logged in'%(packet.command,packet.seq1,packet.seq2))
      self.udp_defered.append(packet)
    raw_packet=packet.raw_packet
    if packet.expect_ack:
      packet.time=time.time()
      packet.tries+=1
      seq2=packet.seq2
      self.UDP_waiting_for_ack[seq2]=packet
    raw_packet = UDP_encode(raw_packet)
    self.dprint(4,'>>> UDP cmd packet %s (%d,%d) try: %d'%(packet.command,packet.seq1,packet.seq2,packet.tries))
    self.udp_socket.send(raw_packet)

  def UDP_CMD(self, cmd=0):
    packet = self.cmd_packet(self,cmd)
    packet.raw_packet = c_UDP_CMD('',packet.__dict__)
    if cmd:
      cmd_string=m_UDP_CMD[cmd]
      packet.raw_packet = apply(globals()['c_'+cmd_string],(packet.raw_packet,packet.__dict__))
      packet.command=cmd_string
    return packet
  
  def UDP_CMD_META(self, meta_command=0):
    self.A.meta_command=meta_command
    p=self.UDP_CMD(UDP_CMD_META_USER)
    meta_cmd_string=m_META[meta_command]
    p.raw_packet = apply(globals()['c_'+meta_cmd_string],(p.raw_packet,p.__dict__))
    return p


  ##############################################################################

  def got_ack(self,packet):
    seq2=packet['seq2']
    if self.UDP_waiting_for_ack.has_key(seq2):
      del self.UDP_waiting_for_ack[seq2]
      self.dprint(5,"    Removing %d from self.UDP_waiting_for_ack ( %d elements left )"%(seq2,len(self.UDP_waiting_for_ack)))
    else:
      self.dprint(4,"  %d not found in self.UDP_waiting_for_ack"%seq2)

  def send_ack(self,in_packet):
    # don't ack an ack
    if in_packet['command_nbr']==UDP_SRV_ACK:
      self.got_ack(in_packet)
      return
    self.dprint(5,"Sending UDP_SRV_ACK for server packet %s, seq = (%d,%d)"%(in_packet['command'],in_packet['seq1'],in_packet['seq2']))
    save = self.udp_seq1,self.udp_seq2             # save the seq numbers
    self.udp_seq1,self.udp_seq2=in_packet['seq1'],0
    packet = self.UDP_CMD(UDP_CMD_ACK)
    self.udp_seq1,self.udp_seq2=save               # restore the seq numbers
    packet.expect_ack=0
    self.UDP_send(packet)

  def send_keep_alive(self):
    #self.dprint(4,"Sending UDP_CMD_KEEP_ALIVE")
    packet = self.UDP_CMD(UDP_CMD_KEEP_ALIVE)
    self.UDP_send(packet)
 
  def check_timeouts(self):
    # 
    #  resend packets that have not been acked within 10 seconds
    # 
    now = time.time()
    for x,y in self.UDP_waiting_for_ack.items():
      if now-y.time > 10:
        seq2=y.seq2
        if y.tries>=7:
          # give up after 7 tries
          self.dprint(2,"!!! UDP packet %d got no ack after 7 retries, giving up on it"%seq2)
          del(self.UDP_waiting_for_ack[x])
        else:
          self.dprint(3,"!!! resending UDP packet (%d,%d)"%(y.seq1,seq2))
          self.UDP_send(y)

  def _get_user(self,uin):
    if not self.users.has_key(uin):
      self.users[uin]=user()
    return self.users[uin]

  ##############################################################################
  #
  #  handler functions for incoming UDP packets
  #
  def h_UDP_SRV_GO_AWAY(self,packet):
    self.UDP_waiting_for_ack={}

  def h_UDP_SRV_FORCE_DISCONNECT(self,packet):
    self.logged=0
    if self.auto_relogin:
      self.login(self.my_uin,self.password,self.status)

  def h_UDP_SRV_LOGIN_REPLY(self,packet):
    self.logged=1
    self.dprint(2,"logged in succesfully")
    for x in self.udp_defered:
      self.UDP_send(x)
    self.udp_defered=[]

  def h_UDP_SRV_OFFLINE_MESSAGE(self,packet):
    packet = self.UDP_CMD(UDP_CMD_ACK_MESSAGES)
    self.UDP_send(packet)
    
  def h_UDP_SRV_USER_ONLINE(self,packet):
    self._get_user(packet['uin']).status=packet['status']

  def h_UDP_SRV_STATUS_UPDATE(self,packet):
    self._get_user(packet['uin']).status=packet['status']

  def h_UDP_SRV_USER_OFFLINE(self,packet):
    self._get_user(packet['uin']).status=0xff00

  def h_UDP_SRV_NEW_UIN(self,packet):
    self.my_uin=packet['my_uin']
    self.dprint(3,'<<< new UIN : %d'%self.my_uin)

  ##############################################################################
  #
  #  public functions
  #

  def __init__(self):
    self.default_hostname='195.66.114.37'
    self.default_port=4000
    self.my_uin=_uin
    self.debug_level=255
    self.users={}
    self.udp_socket=0
    self.udp_port=0
    self.udp_fileno=0
    self.logged=0
    self.udp_srv_received={}
    self.udp_defered=[]
    self.args()

  def __del__(self):
    if self.logged:
      self.logout()
    if self.udp_socket:
      self.udp_socket.close()
    pass

  #
  #  set debug level. The higher the number, the more
  #  debug info on your screen. (between 0 and 5)
  #
  def set_debug_level(self,level):
    self.debug_level=level

  def connect(self,hostname='',port=0):
    if not port: port=self.default_port
    if not hostname: hostname=self.default_hostname
    self.udp_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp_socket.connect((hostname,port))
    self.udp_fileno=self.udp_socket.fileno()
    self.udp_port=self.udp_socket.getsockname()[1]
    self.udp_session=rnd.randint(0,0x3fffffff)
    self.udp_seq1=rnd.randint(0,0xffff)
    self.udp_seq2=1
    self.tcp_port=0
    self.my_ip=socket.inet_aton(socket.gethostbyname(socket.gethostname()))
    self.my_ip=(ord(self.my_ip[0])<<24)+(ord(self.my_ip[1])<<16)+(ord(self.my_ip[2])<<8)+(ord(self.my_ip[3]))
    self.UDP_waiting_for_ack={}
    self.keep_alive_timer=timer(100)

  def login(self,my_uin=0,password='',status=0,wait_for_result=0,use_tcp=0,auto_relogin=1):
    if my_uin: self.my_uin=my_uin
    if password: self.password=password
    self.status=status
    self.logged=0
    self.auto_relogin=auto_relogin
    if use_tcp: self.use_tcp=0x04
    else : self.use_tcp=0x06
    self.args({'password':self.password,'use_tcp':self.use_tcp,'status':status,'tcp_port':self.tcp_port,'my_ip':self.my_ip})
    packet = self.UDP_CMD(UDP_CMD_LOGIN)
    #UDP_print_packet(packet)
    self.UDP_send(packet)
    packets=[]
    if wait_for_result:
      t=timer(wait_for_result)
      while not ( self.logged or t.rings()):
        packets.extend(self.main(.5))
    return packets

  def change_status(self,new_status):
    self.args({'status':new_status})
    if self.status!=new_status:
      self.status=new_status
      self.UDP_send(self.UDP_CMD(UDP_CMD_STATUS_CHANGE))

  def logout(self):
    self.args({'text_code':'B_USER_DISCONNECTED'})
    packet = self.UDP_CMD(UDP_CMD_SEND_TEXT_CODE)
    packet.expect_ack=0
    self.UDP_send(packet) 
    self.logged=0

  ############################################################################

  def add_to_contact_list(self,list_or_nbr):
    if type(list_or_nbr) == types.ListType:
      self.A.list_of_uin = list_or_nbr
      packet = self.UDP_CMD(UDP_CMD_CONTACT_LIST)
      self.UDP_send(packet,1)
    else:
      self.A.uin_to_add=list_or_nbr
      packet = self.UDP_CMD(UDP_CMD_ADD_TO_LIST)
      self.UDP_send(packet,1)
      list_or_nbr=[list_or_nbr]
    for x in list_or_nbr:
      if not self.users.has_key(x):
        self.users[x]=user()
      self.users[x].on_contact_list=1

  ############################################################################

  def reg_new_user(self,password,wait_for_result=0):
    self.A.password = self.password = password
    #self.args('password':password)
    self.UDP_send(self.UDP_CMD(UDP_CMD_REG_NEW_USER))
    packets=[]
    if wait_for_result:
      t=timer(wait_for_result)
      while not ( self.my_uin or t.rings()): 
        packets.extend(self.main(1))
    return packets
      
  def new_user_info(self,nick,first,last,email):
    A=self.args()
    A.nick,A.first,A.last,A.email=nick,first,last,email
    self.UDP_send(self.UDP_CMD(UDP_CMD_NEW_USER_INFO))
  
  ############################################################################
  
  def send_message_server(self,receiver_uin,message):
    self.A.receiver_uin=receiver_uin
    self.A.message_type=1
    self.A.message_text=message
    self.UDP_send(self.UDP_CMD(UDP_CMD_SEND_MESSAGE))

  ############################################################################

  def send_info_req(self, uin):
    self.A.uin=uin
    self.UDP_send(self.UDP_CMD(UDP_CMD_INFO_REQ))

  def send_ext_info_req(self, uin):
    self.A.uin=uin
    self.UDP_send(self.UDP_CMD(UDP_CMD_EXT_INFO_REQ))

  def send_meta_info_req(self, uin):
    self.A.uin=uin
    self.UDP_send(self.UDP_CMD_META(META_CMD_REQ_INFO))

  ############################################################################

  def update_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD(UDP_CMD_UPDATE_INFO))
  
  def update_ext_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD(UDP_CMD_UPDATE_INFO))

  def meta_set_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD_META(META_CMD_SET_INFO))
  
  def meta_set_more_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD_META(META_CMD_SET_HOMEPAGE))

  def meta_set_work_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD_META(META_CMD_SET_WORK_INFO))

  def meta_set_about_info(self,dict):
    self.args(dict)
    self.UDP_send(self.UDP_CMD_META(META_CMD_SET_ABOUT))


  ############################################################################
    
  def main(self,timeout=None):
    packets=[]
    r, w, e = select.select([self.udp_socket], [], [], timeout)
    if len(r):
      raw_packet = self.udp_socket.recv(2048)
      #UDP_print_packet(raw_packet)
      packet = UDP_SRV(raw_packet,self)
      packet['raw_packet']=raw_packet
      self.dprint(4,"<<< UDP server packet %s (%d,%d)"%(packet['command'],packet['seq1'],packet['seq2']))

      # It is possible that we receive the same server packet more than once (if our ack
      # got lost in cyberspace). In this case, resend the ack, but otherwise ignore the packet.
      self.send_ack(packet)
      if self.udp_srv_received.has_key(packet['seq1']) and self.udp_srv_received[packet['seq1']]==packet['command']:
        self.dprint(4,"!!! UDP server packet %s (%d,%d) ignored"%(packet['command'],packet['seq1'],packet['seq2']))
      else:
        self.udp_srv_received[packet['seq1']]=packet['command']    # to do : limit the size of this dict by removing older packets
        #
        #  call the handler function if there is one 
        #
        if pycq.__dict__.has_key('h_'+packet['command']):
          apply(pycq.__dict__['h_'+packet['command']],(self,packet))
        #
      #  UDP_SRV_MULTI_PACKET 
      #
        if packet['command_nbr']==UDP_SRV_MULTI_PACKET:
          for x in packet['packets']:
            packets.append(x)
            if pycq.__dict__.has_key('h_'+x['command']):
              x['raw_packet']=raw_packet
              apply(pycq.__dict__['h_'+x['command']],(self,x))
        #  acks are not interesting for the user
        elif packet['command_nbr']!=UDP_SRV_ACK:
          packets.append(packet)

    if self.keep_alive_timer.rings():
      self.send_keep_alive()
    self.check_timeouts()

    return packets





if __name__=='__main__':
  
  c=pycq()
  
  c.connect()
  
  # set this line if you don't want all that debug crap on your screen 
  # c.set_debug_level(0)
  
  # Login, set status to 0 (=online) and wait for the result
  # Set your own uin and password here. ( login will fail if
  # you're already logged in with some other icq client)
  #
  c.login(_uin ,_password,0,1)
  
  # send a message to the author of pycq (through the icq-server)
  c.send_message_server(3739186,"Hey dude i'm using your fixed for KICQ pycq module.")

  # go in receive loop
  while True:
    p=c.main(10) # wait at most 10 seconds for some message from the server
    print p

    if p and isinstance(p, list) and len(p) > 0 and isinstance(p[0], dict):
      if 'uin' in p[0] and 'message_text' in p[0]:
        p_uin = p[0]['uin']
        p_message_text = p[0]['message_text']

        if p_message_text == "!test":
          c.send_message_server(p_uin, 'Hi. This is the pycqlibrary, corrected to work with the OSCAR "KICQ" server. Random number (1-100): ' + str(random.randint(1, 100)) + " :D. Send !logout message to logout gracefully. Russian message test: \xcf\xf0\xe8\xe2\xe5\xf2.")
        elif p_message_text == "!logout":
          c.send_message_server(p_uin, "Goodbye!")
          c.logout()
          break


