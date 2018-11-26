#Created by Lincoln Yan - https://github.com/yyjlincoln
#Date: 20181103

#imports
from socket import socket
from threading import Thread
from _thread import start_new,exit_thread
from handle import Handle
from errors import StatusMonitor
from errors import printlog as print

#Address+Port
SYS_ADDRESS=''
SYS_PORT=83

@StatusMonitor(allow_error=True)
def ConnectionHandler():
    Socket=socket()
    try:
        Socket.bind((SYS_ADDRESS,SYS_PORT))
        Socket.listen(10)
        print('Successfully launched.')
    except:
        raise Exception('Can not bind address: '+SYS_ADDRESS+':'+str(SYS_PORT))
    while True:
#        print('Waiting for connection...')
        sx,addr=Socket.accept()
#        print(addr[0]+':'+str(addr[1])+' Connected.')
        Handle(sx,addr).start()
#        print(addr[0]+':'+str(addr[1])+' Handle Started')

print('Initialized. Lauching server...')
ConnectionHandler()
