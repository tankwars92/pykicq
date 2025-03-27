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

import string


ICQ_UDP_VER             = 0x0005
ICQ_TCP_VER             = 0x0003

## TCP Packet Commands 
ICQ_TCP_HELLO            = 0xFF
ICQ_TCP_CANCEL           = 0x07D0
ICQ_TCP_ACK              = 0x07DA
ICQ_TCP_MESSAGE          = 0x07EE

## TCP Message Types 
ICQ_TCP_MSG_MSG          = 0x0001
ICQ_TCP_MSG_CHAT         = 0x0002
ICQ_TCP_MSG_FILE         = 0x0003
ICQ_TCP_MSG_URL          = 0x0004
ICQ_TCP_MSG_CONTACTLIST  = 0x0013
ICQ_TCP_MSG_READAWAY     = 0x03E8
ICQ_TCP_MSG_READOCCUPIED = 0x03E9
ICQ_TCP_MSG_READNA       = 0x03EA
ICQ_TCP_MSG_READDND      = 0x03EB
ICQ_TCP_MSG_READFFC      = 0x03EC
ICQ_TCP_MASS_MASK        = 0x8000

## TCP Message Command Types 
ICQ_TCP_MSG_ACK          = 0x0000
ICQ_TCP_MSG_AUTO         = 0x0000
ICQ_TCP_MSG_REAL         = 0x0010
ICQ_TCP_MSG_LIST         = 0x0020
ICQ_TCP_MSG_URGENT       = 0x0040
ICQ_TCP_MSG_INVISIBLE    = 0x0090
ICQ_TCP_MSG_UNK_1        = 0x00A0
ICQ_TCP_MSG_AWAY         = 0x0110
ICQ_TCP_MSG_OCCUPIED     = 0x0210
ICQ_TCP_MSG_UNK_2        = 0x0802
ICQ_TCP_MSG_NA           = 0x0810
ICQ_TCP_MSG_NA_2         = 0x0820
ICQ_TCP_MSG_DND          = 0x1010

## TCP Message Statuses 
ICQ_TCP_STATUS_ONLINE      = 0x0000
ICQ_TCP_STATUS_REFUSE      = 0x0001
ICQ_TCP_STATUS_AWAY        = 0x0004
ICQ_TCP_STATUS_OCCUPIED    = 0x0009
ICQ_TCP_STATUS_DND         = 0x000A
ICQ_TCP_STATUS_NA          = 0x000E
ICQ_TCP_STATUS_FREE_CHAT   = ICQ_TCP_STATUS_ONLINE
ICQ_TCP_STATUS_INVISIBLE   = ICQ_TCP_STATUS_ONLINE

###############################################################################

UDP_CMD_ACK                = 0x000A 
UDP_CMD_SEND_MESSAGE       = 0x010E
UDP_CMD_LOGIN              = 0x03E8
UDP_CMD_CONTACT_LIST       = 0x0406
UDP_CMD_SEARCH_UIN         = 0x041A
UDP_CMD_SEARCH_USER        = 0x0424
UDP_CMD_KEEP_ALIVE         = 0x042E
UDP_CMD_KEEP_ALIVE2        = 0x051E
UDP_CMD_SEND_TEXT_CODE     = 0x0438
UDP_CMD_LOGIN_1            = 0x044C
UDP_CMD_INFO_REQ           = 0x0460
UDP_CMD_EXT_INFO_REQ       = 0x046A
UDP_CMD_CHANGE_PW          = 0x049C
UDP_CMD_STATUS_CHANGE      = 0x04D8
UDP_CMD_LOGIN_2            = 0x0528
UDP_CMD_UPDATE_INFO        = 0x050A
UDP_CMD_UPDATE_AUTH        = 0x0514
UDP_CMD_UPDATE_EXT_INFO    = 0x04B0
UDP_CMD_ADD_TO_LIST        = 0x053C
UDP_CMD_REQ_ADD_LIST       = 0x0456
UDP_CMD_QUERY_SERVERS      = 0x04BA
UDP_CMD_QUERY_ADDONS       = 0x04C4
UDP_CMD_NEW_USER_1         = 0x04EC
UDP_CMD_NEW_USER_INFO      = 0x04A6
UDP_CMD_ACK_MESSAGES       = 0x0442
UDP_CMD_MSG_TO_NEW_USER    = 0x0456
UDP_CMD_REG_NEW_USER       = 0x03FC
UDP_CMD_VIS_LIST           = 0x06AE
UDP_CMD_INVIS_LIST         = 0x06A4
UDP_CMD_META_USER          = 0x064A
UDP_CMD_RAND_SEARCH        = 0x056E
UDP_CMD_RAND_SET           = 0x0564
UDP_CMD_REVERSE_TCP_CONN   = 0x015E

m_UDP_CMD={}
for x,y in globals().items():
  if x[0:8]=='UDP_CMD_':
    m_UDP_CMD[y]=x

UDP_SRV_ACK                = 0x000A
UDP_SRV_LOGIN_REPLY        = 0x005A
UDP_SRV_USER_ONLINE        = 0x006E
UDP_SRV_USER_OFFLINE       = 0x0078
UDP_SRV_USER_FOUND         = 0x008C
UDP_SRV_OFFLINE_MESSAGE    = 0x00DC
UDP_SRV_END_OF_SEARCH      = 0x00A0
UDP_SRV_INFO_REPLY         = 0x0118
UDP_SRV_EXT_INFO_REPLY     = 0x0122
UDP_SRV_STATUS_UPDATE      = 0x01A4
UDP_SRV_X1                 = 0x021C
UDP_SRV_X2                 = 0x00E6
UDP_SRV_UPDATE             = 0x01E0
UDP_SRV_UPDATE_EXT         = 0x00C8
UDP_SRV_NEW_UIN            = 0x0046
UDP_SRV_NEW_USER           = 0x00B4
UDP_SRV_QUERY              = 0x0082
UDP_SRV_SYSTEM_MESSAGE     = 0x01C2
UDP_SRV_ONLINE_MESSAGE     = 0x0104
UDP_SRV_GO_AWAY            = 0x00F0
UDP_SRV_TRY_AGAIN          = 0x00FA
UDP_SRV_FORCE_DISCONNECT   = 0x0028
UDP_SRV_MULTI_PACKET       = 0x0212
UDP_SRV_WRONG_PASSWORD     = 0x0064
UDP_SRV_INVALID_UIN        = 0x012C
UDP_SRV_META_USER          = 0x03DE
UDP_SRV_RAND_USER          = 0x024E
UDP_SRV_AUTH_UPDATE        = 0x01F4

m_UDP_SRV={}
for x,y in globals().items():
  if x[0:8]=='UDP_SRV_':
    m_UDP_SRV[y]=x

META_CMD_SET_INFO          = 1000
META_CMD_SET_WORK_INFO     = 1010
META_CMD_SET_HOMEPAGE      = 1020
META_CMD_SET_ABOUT         = 1030
META_CMD_SET_SECURE        = 1060
META_CMD_SET_PASS          = 1070
META_CMD_REQ_INFO          = 1200
META_SRV_RES_INFO          = 100
META_SRV_RES_WORK_INFO     = 110
META_SRV_RES_HOMEPAGE      = 120
META_SRV_RES_ABOUT         = 130
META_SRV_RES_SECURE        = 160
META_SRV_RES_PASS          = 170
META_SRV_USER_INFO         = 200
META_SRV_USER_WORK         = 210
META_SRV_USER_MORE         = 220
META_SRV_USER_ABOUT        = 230
META_SRV_USER_INTERESTS    = 240
META_SRV_USER_AFFILIATIONS = 250
META_SRV_USER_HPCATEGORY   = 270
META_SRV_USER_FOUND        = 410

META_SRV_SUCCESS       = 10
META_SRV_FAILURE       = 50

m_META={}
for x,y in globals().items():
  if x[0:5]=='META_':
    m_META[y]=x


TYPE_MSG               = 0x0001
TYPE_CHAT              = 0x0002
TYPE_FILE              = 0x0003
TYPE_URL               = 0x0004
TYPE_AUTH_REQ          = 0x0006
TYPE_AUTH              = 0x0008
TYPE_ADDED             = 0x000C
TYPE_WEBPAGER          = 0x000D
TYPE_EXPRESS           = 0x000E
TYPE_CONTACT           = 0x0013
TYPE_MASS_MASK         = 0x8000
