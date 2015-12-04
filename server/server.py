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

DATA_BUFFER= lambda x:x
stdscr = curses.initscr()
x,y=stdscr.getmaxyx()
f = open("chat history.txt","a")
sys.stdout.write("\x1b]2;PyChat\x07")
i=0

# THREADED CLASS FOR RECEIVING
class server_receive(threading.Thread):
    def __init__(self,conn,client_name):
        threading.Thread.__init__(self)
        self.conn = conn
        self.stop=False
        server_receive.client_name = client_name

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
                stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
                stdscr.addstr(x-2,0," >>>  ")
                stdscr.refresh()
            try:
            	message = self.message_receive()
            except IOError:
            	print "Client has closed PyChat window ! Press ctrl +c to exit"
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
            stdscr.addstr(i,0,server_receive.client_name + " : " +message,curses.color_pair(2))
            log=time.ctime()
            try:
            	f.write(log + " || " + server_receive.client_name + " : " +message + "\n")
            except ValueError:
            	print "Client has closed PyChat window ! Press ctrl +c to exit"
            	f.close()
            	sys.exit(1)
            stdscr.refresh()
            stdscr.addstr(x-2,0," >>>  ")
            i+=1
            if(i==x-8):
                i=0
                stdscr.clear()
                stdscr.addstr(x-4,0,"_"*y)
                stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
                stdscr.addstr(x-2,0," >>>  ")
                stdscr.refresh()
            if(len(message)>y-len(server_receive.client_name)-5):
                i+=(len(message)+len(server_receive.client_name)+5)/y
            stdscr.refresh()

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
def message_send(conn,server_name,msg):
    global i
    x,y=stdscr.getmaxyx()
    if(i==x-8):
        i=0
        stdscr.clear()
        stdscr.addstr(x-4,0,"_"*y)
        stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
        stdscr.addstr(x-2,0," >>>  ")
        stdscr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.addstr(i,0,server_name+" : "+msg,curses.color_pair(1))
    log=time.ctime()
    f.write(log + " || " + server_name+" : "+msg + "\n")
    stdscr.refresh()
    if(len(msg)>y-len(server_name)-5):
        i+=(len(msg)+len(server_name)+5)/y
    i+=1
    if(i==x-8):
        i=0
        stdscr.clear()
        stdscr.addstr(x-4,0,"_"*y)
        stdscr.addstr(x-5,0,"Press ctrl + c to quit chat safely")
        stdscr.addstr(x-2,0," >>>  ")
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
def server_initialize():
    x,y=stdscr.getmaxyx()
    stdscr.addstr(0,13,"PyChat")
    stdscr.addstr(1,0,"A P2P chat application based on sockets")
    stdscr.addstr(2,0,"Connected to HOST: "+str(HOST))
    stdscr.addstr(3,0,"Listening on PORT: "+str(PORT))
    a=curses_initialize()
    server_name = a.my_raw_input(stdscr,4,0,"Enter your nickname: ")
    stdscr.addstr(5,0,"Enjoy chatting on PyChat " + server_name + " !")
    stdscr.addstr(6,0,"Waiting for a connection...")
    return server_name

def main():
    x,y=stdscr.getmaxyx()
    server_name=server_initialize()
    stdscr.refresh()

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
    stdscr.addstr(7,0,"Connection Established !You are now connnected to " + client_name)
    stdscr.refresh()
    receive = server_receive(connect['recv'],client_name)
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
        message_send(connect['send'],server_name,send_data)
        stdscr.addstr(x-1,0," "*(y-1))
        stdscr.addstr(x-2,0," "*(y-1))

if __name__ == '__main__':
	try:
		main()
	except IOError:
		print "Input Output Error occured !"
	except SystemError:
		print "Encountered a python interpretter error !"
	except EnvironmentError:
		print "Encountered a python environment error !"
	except Exception:
		print "Exception occured !"
	except ValueError:
		print "Value Error occured !"
	except RuntimeError:
		print "PyChat encountered a run-time error !"
	except StandardError:
		print "Standard Error occured"
	except KeyboardInterrupt:
		print "Keyboard Interrupt occured (ctrl+c)"
   	finally:
   		print "PyChat is closing due to technical error. Reopen PyChat and try again :)"
		f.close()
   		curses.endwin()
   		sys.exit(1)