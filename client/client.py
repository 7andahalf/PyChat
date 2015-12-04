import curses
import socket
import threading
import time
import sys
import subprocess
import ctypes
from ncurses import curses_initialize

# COMMAND LINE ARGUMENTS FOR HOST AND PORT
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except:
    print("Incorrect parameters")
    print("Usage: python server.py <HOST> <PORT>")
    print("Ex. python server.py localhost 8000")
    print("Ex. python server.py 172.16.82.169 8000")
    sys.exit(1)

DATA_BUFFER = lambda x:x
stdscr = curses.initscr()
x,y=stdscr.getmaxyx()
f = open("chat history.txt","a")
sys.stdout.write("\x1b]2;PyChat\x07")
i=0

# THREADED CLASS FOR RECEIVING
class client_receive(threading.Thread):
    def __init__(self,conn,server_name):
        threading.Thread.__init__(self)
        self.conn = conn
        self.stop = False
        client_receive.server_name = server_name

    def message_receive(self):
        data = self.conn.recv(DATA_BUFFER(1024))
        self.conn.send('OK')
        return self.conn.recv(DATA_BUFFER(1024))
        raise IOError

    def run(self):
        while not self.stop:
            global i
            x,y=stdscr.getmaxyx()
            if(i==x-8):
                i=0
                stdscr.clear()
                stdscr.addstr(x-4,0,"_"*y)
                stdscr.addstr(x-2,0," >>>  ")
                stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
                stdscr.refresh()
            try:
                message = self.message_receive()
            except IOError:
                print "Server has closed PyChat window ! Press ctrl +c to exit"
                f.close()
                sys.exit()
            try:
            	speak = 'espeak -p 90 -s 120 "'+ message +'"';
                subprocess.call(speak,shell=True)
            	raise Exception
            except:
            	pass
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(2, curses.COLOR_BLACK,curses.COLOR_WHITE)
            stdscr.addstr(i,0,client_receive.server_name + " : " +message,curses.color_pair(2))
            log=time.ctime()
            try:
                f.write(log + " || " + client_receive.server_name + " : " +message + "\n")
            except ValueError:
                print "Server has closed PyChat window ! Press ctrl +c to exit"
                f.close()
                sys.exit(1)
            stdscr.refresh()
            stdscr.addstr(x-2,0," >>>  ")
            i+=1
            if(i==x-8):
                i=0
                stdscr.clear()
                stdscr.addstr(x-4,0,"_"*y)
                stdscr.addstr(x-2,0," >>>  ")
                stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
                stdscr.refresh()
            if(len(message)>y-len(client_receive.server_name)-5):
                i+=(len(message)+len(client_receive.server_name)+5)/y  
            stdscr.refresh()

# FUNCTION WHICH HELPS IN SENDING THE MESSAGE
def message_send(conn,client_name,msg):
    global i
    x,y=stdscr.getmaxyx()
    if(i==x-8):
        i=0
        stdscr.clear()
        stdscr.addstr(x-4,0,"_"*y)
        stdscr.addstr(x-2,0," >>>  ")
        stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
        stdscr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.addstr(i,0,client_name+" : "+msg,curses.color_pair(1))
    log=time.ctime()
    f.write(log + " || " + client_name+" : "+msg + "\n")
    stdscr.refresh()
    if(len(msg)>y-len(client_name)-5):
        i+=(len(msg)+len(client_name)+5)/y
    i+=1
    if(i==x-8):
        i=0
        stdscr.clear()
        stdscr.addstr(x-4,0,"_"*y)
        stdscr.addstr(x-2,0," >>>  ")
        stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
        stdscr.refresh()
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
def client_initialize():
    x,y=stdscr.getmaxyx()
    stdscr.addstr(0,13,"PyChat")
    stdscr.addstr(1,0,"A P2P chat application based on sockets")
    stdscr.addstr(2,0,"Connected to HOST: "+str(HOST))
    stdscr.addstr(3,0,"Listening on PORT: "+str(PORT))
    a=curses_initialize()
    client_name = a.my_raw_input(stdscr,4,0,"Enter your nickname: ")
    stdscr.addstr(5,0,"Enjoy chatting on PyChat " + client_name + " !")
    stdscr.addstr(6,0,"Waiting for a connection...")
    return client_name

def main():
    x,y=stdscr.getmaxyx()
    client_name=client_initialize()
    stdscr.refresh()

    # SOCKET OBJECT INITIALIZATION
    socket_object1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_object1.connect((HOST,PORT))

    # SELECTING SEND AND RECEIVE SOCKETS
    socket_object1.send("WILL SEND") # telling server we will send data from here
    socket_object2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_object2.connect((HOST,PORT))
    socket_object2.send("WILL RECV") # telling server we will recieve data from here
    # CONNECTION ESTABLISHED

    # INITIALIZING SERVER AND CLIENT NAMES
    socket_object1.send(client_name)
    server_name = socket_object2.recv(DATA_BUFFER(1024))
    stdscr.addstr(7,0,"Connection Established !You are now connnected to " + server_name)
    receive = client_receive(socket_object2,server_name)
    stdscr.refresh()
    stdscr.clear()
    stdscr.addstr(x/2,y/2-20," PRESS ANY KEY TO START CHATTING ")
    z=stdscr.getch()
    stdscr.clear()

    # RECEIVE THREAD STARTS HERE
    receive.start()
    a=curses_initialize()

    # SEND STARTS HERE
    while 1:
        x,y=stdscr.getmaxyx()
        stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
        stdscr.addstr(x-4,0,"_"*y)
        send_data=a.my_raw_input(stdscr,x-2,0," >>> ")
        while send_data=='':
            send_data=a.my_raw_input(stdscr,x-2,0," >>> ")
        message_send(socket_object1,client_name,send_data)
        stdscr.addstr(x-1,0," "*(y-1))
        stdscr.addstr(x-2,0," "*(y-1))

if __name__ == '__main__':
    try:
        main()
    except IOError as (errno, sterror):
        print "Input Output Error occured !"
    except SystemError:
        print "Encountered a python interpretter error !"
    except EnvironmentError:
        print "Encountered a python environment error !"
    except ValueError:
        print "Value Error occured !"
    except Exception:
        print "Exception occured !"
    except KeyboardInterrupt:
        print "Keyboard Interrupt occured (ctrl+c)"
    finally:
        print "PyChat is closing due to technical error. Reopen PyChatand try again :)"
        curses.endwin()
        f.close()
        sys.exit(1)