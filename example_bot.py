# -*- coding: utf-8 -*-
from pycq import *

_uin = 1111
_password = "..."

c = pycq()
c.connect()
c.login(_uin, _password, 0, 1)
c.change_status(32) # Статус "Готов поболтать" (Free for Chat)

while True:
    p = c.main(10)
    print p
    
    if p and isinstance(p, list) and len(p) > 0 and isinstance(p[0], dict):
        if 'uin' in p[0] and 'message_text' in p[0]:
            if p[0]['message_text'] == "!logout":
                c.send_message_server(p[0]['uin'], "Goodbye!")
                c.logout()
                break
            else:
                c.send_message_server(p[0]['uin'], p[0]['message_text'])
