import curses
import socket
import threading
import time
import sys
import subprocess
import ctypes

from Tkinter import *
import tkMessageBox,Tkinter
import util

DATA_BUFFER= lambda x:x
f = open("chat history.txt","a")
i=0

# THREADED CLASS FOR RECEIVING
class server_receive(threading.Thread):
    def __init__(self,conn,client_name, m):
        threading.Thread.__init__(self)
        self.conn = conn
        self.stop=False
        self.m = m
        server_receive.client_name = client_name

    def message_receive(self):
        data = self.conn.recv(DATA_BUFFER(1024))
        self.conn.send('OK')
        return self.conn.recv(DATA_BUFFER(1024))
        raise IOError

    def run(self):
        while not self.stop:
            global i
            try:
            	message = self.message_receive()
            except IOError:
            	print "Client has closed PyChat window ! Press ctrl +c to exit"
                f.close()
            	sys.exit()
            frame = self.m.mframe
            subFrame = Frame(frame, height = 20, width = 460)
            subFrame.grid(row=i,column=0)
            Label(subFrame,text=server_receive.client_name+" : "+str(message)).place(x=5,y=0)
            i+=1

# CONNECTS THE SOCKETS TO THE CORRESPONDING SEND AND RECEIVE CONNECTIONS
def SetConnection(conn1,conn2):
    connect={}
    state = conn1.recv(9)
    conn2.recv(9)
    if state =='WILL RECV':
        connect['send'] = conn1 # server will send data to reciever
        connect['recv'] = conn2
    else:
        connect['recv'] = conn1 # server will recieve data from sender
        connect['send'] = conn2
    return connect

# FUNCTION WHICH HELPS IN SENDING THE MESSAGE
def message_send(conn,server_name,msg,slf):
    global i
    frame = slf.mframe
    subFrame = Frame(frame, height = 20, width = 460)
    subFrame.grid(row=i,column=0)
    Label(subFrame,text=server_name+" : "+str(msg)).place(x=5,y=0)
    i+=1

    if len(msg)<=999 and len(msg)>0:
        conn.send(str(len(msg)))
        if conn.recv(2) == 'OK':
            stdscr.refresh()
            conn.send(msg)
    else:
        conn.send(str(999))
        if conn.recv(2) == 'OK':
            conn.send(msg[:999])
            message_send(conn,msg[1000:]) # calling recursive

# INITIAL SPLASH SCREEN
def server_initialize():
    # Init
    l = []
    class loading(util.window):
        def __init__(self):
            # Init
            util.window.__init__(self,"PyChat | Welcome",width = 500, height=600)   

            # image
            canvas = Canvas(width = 500, height = 600, bg = 'white')
            canvas.pack(expand = YES, fill = BOTH)
            gif1 = PhotoImage(file = './data/1.gif')
            canvas.create_image(0, 0, image = gif1, anchor = NW)

            # Login frame
            login_frame = Frame(self.root, height = 180, width = 400, relief = FLAT, bd = 1)
            login_frame.place(x=40,y=350)

            x,y = 70,20

            Label(login_frame, text="Please enter your details to start chatting").place(x=x, y = y+0)

            Label(login_frame, text="Host    : ").place(x=x+0, y = y+30)
            Label(login_frame, text="Port    : ").place(x=x+0, y = y+60)
            Label(login_frame, text="Name    : ").place(x=x+0, y = y+90)

            entry_host = Entry(login_frame)
            entry_port = Entry(login_frame)
            entry_name = Entry(login_frame)
            entry_host.place(x=x+80, y = y+30)
            entry_port.place(x=x+80, y = y+60)
            entry_name.place(x=x+80, y = y+90)

            Button(login_frame, text ="Start Chat", command=(lambda: self.start(entry_host.get(),entry_port.get(),entry_name.get()))).place(x=x+80, y = y+120)

            # run
            self.root.mainloop()
        def start(self, host, port, name):
            self.root.destroy()
            l.append(host)
            l.append(int(port))
            l.append(name)
    loading()
    return l

def main():
    #x,y=stdscr.getmaxyx()
    HOST, PORT, server_name = server_initialize()
    #stdscr.refresh()

    class mainw(util.window):
        def __init__(self):
            self.con = None
            self.sname = None
            # Init
            util.window.__init__(self,"PyChat",width = 500, height=600)   

            main_frame = Frame(self.root, height = 500, width = 500, relief = RAISED, bd = 0)
            main_frame.place(x=10,y=20)

            def myfunction(event):
                canvas.configure(scrollregion=canvas.bbox("all"),width=457,height=500)

            canvas=Canvas(main_frame)
            frame=Frame(canvas)
            myscrollbar=Scrollbar(main_frame,orient="vertical",command=canvas.yview)
            canvas.configure(yscrollcommand=myscrollbar.set)

            myscrollbar.pack(side="right",fill="y")
            canvas.pack(side="left")
            canvas.create_window((0,0),window=frame,anchor='nw')
            frame.bind("<Configure>",myfunction)

            self.mframe = frame

            x,y = 20,550

            entry_msg = Entry(self.root, width=43)
            entry_msg.place(x=x, y = y)

            Button(self.root, text ="Send", command=(lambda: self.sendd(entry_msg.get()))).place(x=x+400, y = y)

        def sendd(self, msg):
            message_send(self.con,self.sname,msg,self)
    m = mainw()

	# SOCKET OBJECT INITIALIZATION
    socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_object.bind((HOST, PORT))
    socket_object.listen(1)

    # WAITING FOR CONNECTION ...
    (conn1,addr1) = socket_object.accept()
    (conn2,addr2) = socket_object.accept()
    # CONNECTION ESTABLISHED !

    #INITIALIZING SEND AND RECEIVE
    connect = SetConnection(conn1,conn2)

    # INITIALIZING SERVER AND CLIENT NAMES
    conn2.send(server_name)
    client_name = conn1.recv(DATA_BUFFER(1024))
    receive = server_receive(connect['recv'],client_name,m)
    receive.start()

    m.con = connect['send']
    m.sname = server_name
    
    m.root.mainloop()

if __name__ == '__main__':
    main()