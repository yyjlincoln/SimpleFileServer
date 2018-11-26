#Created by Lincoln Yan - https://github.com/yyjlincoln
#Date: 20181103

#imports
from socket import socket
from threading import Thread
from _thread import start_new,exit_thread
from errors import StatusMonitor
from errors import printlog as print
import hashlib, base64, random
import string
from urllib import parse
import os

PermissionCallback=None
NotFoundCallback=None
ExceptionCallback=None
Redirect={}


SaltPool={}

@StatusMonitor(allow_error=True)
class Handle(Thread): # Handles requests
    @StatusMonitor(allow_error=True)
    def __init__(self,sx,addr):
        Thread.__init__(self)
        self.sx=sx
        self.addr=addr

    @StatusMonitor(allow_error=True)
    def run(self):
        sx=self.sx
        addr=self.addr
        #处理事件
        ConnectionEstablished(sx,addr)

class InvalidRequest(Exception):
    pass

class InvalidToken(Exception):
    pass

class BadRequest(Exception):
    pass

class RequestFailed(Exception):
    pass
    
@StatusMonitor()
def generatefilelist(sx,Folder):
    start='''<html>
<head>
<meta charset='utf-8'>
<title>File Center - UFAS</title>
</head>
<body>
<div id="header">
<b><font size="5pt">Lincoln Yan's File Server.</font></b>
</div>
<hr>
<div id="message">
<p>Files available ('''+'/'+Folder[1:]+'):</p></div><div id="files">\n'
    Tmp=Folder.split('/')
    if len(Tmp)!=0:
        Tmp.pop(-1)
    UpperFolder='/'+'/'.join(Tmp)
    if UpperFolder[:2]=='//':
        UpperFolder=UpperFolder[1:]
    start=start+'<p><a href='+parse.quote(UpperFolder)+'>'+'..'+'</a></p>\n'
    TempDir=os.listdir(os.path.join(os.getcwd(),Folder[1:]))
    for x in TempDir:
        start=start+'<p><a href='+parse.quote(Folder)+'/'+parse.quote(x)+'>'+x+'</a></p>\n'
    start=start+'</div></body></html>'
    header='HTTP/1.1 200 OK\r\n\r\n'
    sx.send(str(header+start).encode())
    sx.close()

@StatusMonitor(allow_error=False,print_error=True)
def ConnectionEstablished(sx,addr): # Analyse Request
    rawdata=sx.recv(2048)
    try:
        httptry=rawdata.decode().split(' ')
        if httptry[0] == 'GET':
            #HTTP
            Address=parse.unquote(httptry[1])
        else:
            sx.close()
    
        if Address in Redirect:
            Address=Redirect[Address]
            print(Address)
        Rq=Address
        ContentType='auto'
        if Address[-4:]=='.mp3':
            ContentType='audio/mpeg'
        if Address[-4:]=='.wav':
            ContentType='audio/mpeg'
        if Address[-4:]=='.mp4':
            ContentType='video/mp4'
        try:
            if Address[:2]=='//':
                raise PermissionError
            if Rq=='/':
                generatefilelist(sx,'')
                return
            if os.path.isdir(os.path.join(os.getcwd(),Rq[1:])):
                generatefilelist(sx,Rq)
                return
        except PermissionError:
            if PermissionCallback:
                PermissionCallback(sx)
            else:
                sx.send('HTTP/1.1 403 Forbidden by system\r\n\r\n'.encode())
                sx.close()
        except FileNotFoundError:
            if NotFoundCallback:
                NotFoundCallback(sx)
            else:
                sx.send('HTTP/1.1 404 Error\r\n\r\n'.encode())
                sx.close()
        try:
            with open(Address[1:],'r',encoding='utf-8') as f:
                #print('file')
                sx.send(str('HTTP/1.1 200 OK\nContent-Type:%s\r\n\r\n'%ContentType).encode())
                sx.send(f.read().encode())
            sx.close()
        except PermissionError:
            if PermissionCallback:
                PermissionCallback(sx)
            else:
                sx.send('HTTP/1.1 403 Forbidden by system\r\n\r\n'.encode())
                sx.close()
        except FileNotFoundError:
            if NotFoundCallback:
                NotFoundCallback(sx)
            else:
                sx.send('HTTP/1.1 404 Error\r\n\r\n'.encode())
                sx.close()
        except:
            print('rb')
            with open(Address[1:],'rb') as f:
                #print('file')
                sx.send(f.read())
            sx.close()
    except Exception as r:
        sx.send('HTTP/1.1 404 Error\r\n\r\n'.encode())
        sx.close()
        raise r
