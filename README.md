# PyChat
A LAN based P2P chat server, developed using Python Network Programming (SOCKETS)<br/>
Project by: Aditya Thiruvengadam, IIIT Bangalore

![Alt text](https://github.com/adityathiru/PyChat/blob/master/images/logo.png "PyChat Logo")


<b>KEY FEATURES:</b><br/>
	-> Enables simultaneous chat thru multi-threading <br/>
	-> Connects over LAN / WLAN using IP Address and Port<br/>
	-> Reads out messages as and when you receive a message<br/>
	-> User can create chat nicknames<br/>
	-> WhatsApp style chat window layout implemented over ncurses<br/>
	-> Stores entire user chat history with proper logging<br/>

<b>INSTALLATION PROCEDURE:</b></br>
	-> Open Terminal with your system connected to the internet<br/>
	-> INSTALL.sh will install the pre-requisites needed for PyChat <br/>
	-> Hence, run the following command in PyChat folder,<br/>
	   chmod a+x INSTALL.sh<br/>
	   ./INSTALL.sh<br/>
	-> Follow the instructions displayed on the terminal and you are good to go ! <br/>

<b>RUNNING PYCHAT:</b><br/>
	-> Since PyChat is a P2P chat application, one person has to be a server (the one who hosts the chat) and the other should be the client<br/>
	-> Note that the client should always be created only after the server has been hosted<br/>
	-> Since, the chat uses TTS module espeak, which reads out the messages, it's advisable to keep the speaker volumes up<br/>

	-> If you are the server, open the folder named server and open a terminal window here
	-> Run server.py as follows,
	   Usage: python server.py <HOST> <PORT>")
       Ex. python server.py localhost 8000")
   	   Ex. python server.py 172.16.82.169 8000")
   	   You can obtain your HOST by doing ifconfig on your terminal window and any PORT which isn't a dedicated port, PORT >=0 and PORT<=65535 (excluding dedicated port values) is preferable.
   	   Advisable value >= 8000

   	-> If you are the client, open the folder named client and open a terminal window here, AFTER A SERVER HAS BEEN CREATED
	-> Run client.py as follows,
	   Usage: python client.py <HOST> <PORT>")
       Ex. python client.py localhost 8000")
   	   Ex. python client.py 172.16.82.169 8000")
   	   You can obtain your HOST by doing ifconfig on your terminal window and any PORT which isn't a dedicated port, PORT >=8000 is preferable

   	-> Once you've opened your chat window, Enter your nickname (the name which will be displayed on the other end of the chat application)
   	-> Use ctrl+c to safely quit the program
   	-> Enjoy chatting on PyChat

<b>NOTE:</b><br/>
	-> Since the program depends on ncurses, RESIZING the chat window will cause the program to close abruptly<br/>
	-> ctrl + c closes the program safely, closing the program safely is essential for the chat framework to store the chat history<br/>
	-> Closing the program abruptly by force closing the terminal window results in loss of chat history and loss of connection with the server/client<br/>
	<h3>Enjoy chatting on PyChat !</h3>
