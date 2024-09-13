import socket
import re
import random



server = 'irc.chat.twitch.tv'
port  = 6667
nickname = 'Python'
token = 'oauth:fqvrfk5hxj947ed5w7rdpfy07uhrj3'
channel = '#amnyle'
viewer = "anonyme_younes"





sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))





while True:
    msg = sock.recv(2048).decode('utf-8')

    if msg.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))
    
    elif len(msg) > 0:
        print(msg)
        match = re.search(r':([^!]+)![^ ]+ PRIVMSG #[^ ]+ :(.+)', msg)
        if match:
            username = match.group(1).strip
            message = match.group(2).strip() 
            print("Username:", username)
            print("Message:", message)  
            

                
    
        









