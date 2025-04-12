# -*- coding: utf-8 -*-
import Tkinter as tk
import tkMessageBox
from pycq import pycq
import threading
import Queue
import time

class ICQClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ICQ")
        self.root.iconbitmap('ICQ.ico')
        self.root.option_add('*Button.background', 'SystemButtonFace')
        self.root.option_add('*Button.foreground', 'SystemButtonText')
        self.root.option_add('*Label.background', 'SystemButtonFace')
        self.root.option_add('*Label.foreground', 'SystemButtonText')
        self.root.option_add('*Entry.background', 'SystemWindow')
        self.root.option_add('*Entry.foreground', 'SystemWindowText')
        self.root.option_add('*Text.background', 'SystemWindow')
        self.root.option_add('*Text.foreground', 'SystemWindowText')
        
        self.message_queue = Queue.Queue()
        self.setup_login_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_login_window(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        tk.Label(self.login_frame, text="ICQ", font=('MS Sans Serif', 10, 'bold')).pack(pady=(0, 10))
        
        input_frame = tk.Frame(self.login_frame)
        input_frame.pack()
        
        uin_frame = tk.Frame(input_frame)
        uin_frame.pack(fill=tk.X, pady=2)
        tk.Label(uin_frame, text="UIN:", width=8, anchor='e').pack(side=tk.LEFT)
        self.uin_entry = tk.Entry(uin_frame, width=20)
        self.uin_entry.pack(side=tk.LEFT, padx=5)
        
        pass_frame = tk.Frame(input_frame)
        pass_frame.pack(fill=tk.X, pady=2)
        tk.Label(pass_frame, text="Password:", width=8, anchor='e').pack(side=tk.LEFT)
        self.password_entry = tk.Entry(pass_frame, show="*", width=20)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login, width=15)
        self.login_button.pack(pady=10)
        
    def setup_chat_window(self):
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(self.chat_frame, text="ICQ", font=('MS Sans Serif', 10, 'bold')).pack(pady=(0, 10))
        
        recipient_frame = tk.Frame(self.chat_frame)
        recipient_frame.pack(fill=tk.X, pady=2)
        tk.Label(recipient_frame, text="To:", width=8, anchor='e').pack(side=tk.LEFT)
        self.recipient_entry = tk.Entry(recipient_frame, width=20)
        self.recipient_entry.pack(side=tk.LEFT, padx=5)
        
        self.chat_text = tk.Text(self.chat_frame, height=15, width=40, wrap=tk.WORD, state='disabled')
        self.chat_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        message_frame = tk.Frame(self.chat_frame)
        message_frame.pack(fill=tk.X, pady=2)
        tk.Label(message_frame, text="Message:", width=8, anchor='e').pack(side=tk.LEFT)
        self.message_entry = tk.Entry(message_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', self.send_message)
        
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message, width=15)
        self.send_button.pack(pady=5)
        
    def login(self):
        try:
            uin = int(self.uin_entry.get())
            password = self.password_entry.get()
            
            self.icq = pycq()
            self.icq.connect()
            self.icq.set_debug_level(0)
            
            result = self.icq.login(uin, password, 0, 1)
            
            if self.icq.logged:
                self.login_frame.destroy()
                self.setup_chat_window()
                self.receiver_thread = threading.Thread(target=self.message_receiver)
                self.receiver_thread.daemon = True
                self.receiver_thread.start()
                self.check_message_queue()
            else:
                tkMessageBox.showerror("Error", "Failed to login")
        except Exception, e:
            tkMessageBox.showerror("Error", str(e))
            
    def message_receiver(self):
        while True:
            try:
                packets = self.icq.main(1)
                if packets:
                    for packet in packets:
                        if isinstance(packet, dict) and 'uin' in packet and 'message_text' in packet:
                            message_text = packet['message_text']
                            if isinstance(message_text, str):
                                try:
                                    message_text = message_text.decode('cp1251')
                                except UnicodeDecodeError:
                                    pass
                            message = u"From %s: %s\n" % (packet['uin'], message_text)
                            self.message_queue.put(message)
            except:
                break
                
    def check_message_queue(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.chat_text.config(state='normal')  
                self.chat_text.insert(tk.END, message)
                self.chat_text.see(tk.END)
                self.chat_text.config(state='disabled')
        except Queue.Empty:
            pass
        self.root.after(100, self.check_message_queue)
            
    def send_message(self, event=None):
        try:
            recipient = int(self.recipient_entry.get())
            message = self.message_entry.get()
            message_ = message
            if message:
                if isinstance(message, unicode):
                    message = message.encode('cp1251')
                self.icq.send_message_server(recipient, message)
                self.chat_text.config(state='normal') 
                self.chat_text.insert(tk.END, u"Me -> %s: %s\n" % (recipient, message_))
                self.chat_text.see(tk.END)
                self.chat_text.config(state='disabled') 
                self.message_entry.delete(0, tk.END)
        except Exception, e:
            tkMessageBox.showerror("Error", str(e))
            
    def on_closing(self):
        if hasattr(self, 'icq') and self.icq.logged:
            self.icq.logout()
        self.root.destroy()
            
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    client = ICQClient()
    client.run() 
