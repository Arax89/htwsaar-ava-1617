import errno
import socket
import argparse
import threading
import time
import colorama
from _thread import allocate_lock

from LamportMessage import LamportMessage, MsgTypes


class Lamport:
    def __init__(self, nid: int, countNeighbours: int):
        self.lock = allocate_lock()
        self.countReady = 0
        self.running = True
        self.id = nid
        self.host = socket.gethostname()
        self.port = 5000 + nid
        self.countNodes = countNeighbours
        if nid % 2 == 0:
            self.even = True
            self.partnerID = nid - 1
        else:
            self.even = False
            self.partnerID = nid + 1

        self.neighbours = set()

    def interpret(self, msg):
        lmsg = LamportMessage(jsonMsg=msg.decode())
        lmsg.decodeLamport()
        if lmsg.msgtype == MsgTypes.Request:
            pass
        elif lmsg.msgtype == MsgTypes.Reply:
            pass
        elif lmsg.msgtype == MsgTypes.Release:
            pass
        elif lmsg.msgtype == MsgTypes.Terminate:
            pass
        elif lmsg.msgtype == MsgTypes.Remove:
            self.removeFromNeighbours(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Ready:
            self.addToNeighbours(lmsg.sender)
            self.lock.acquire()
            self.countReady += 1
            self.lock.release()

    def removeFromNeighbours(self, nid: int):
        self.neighbours.remove(nid)
        print("Neighbours:", self.neighbours)

    def addToNeighbours(self, nid: int):
        self.neighbours.add(nid)
        print("Neighbours:", self.neighbours)

    def listen(self):
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.bind((self.host, self.port))
        self.listenSocket.listen(0)
        try:
            while self.running:
                conn, addr = self.listenSocket.accept()
                msg = conn.recv(2048)
                sendMsg = "OK from " + str(self.id)
                conn.send(sendMsg.encode())
                print(colorama.Fore.CYAN, msg.decode())
                self.interpret(msg)
                conn.close()
            self.listenSocket.close()
        finally:
            self.listenSocket.close()

    def send(self, receiverPort: int, sendMsg):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sendSocket.connect((self.host, receiverPort))
            sendSocket.send(sendMsg)
            # print(sendMsg)
            recvMsg = sendSocket.recv(1024)
            sendSocket.close()
            print(colorama.Fore.GREEN, recvMsg.decode())
        except socket.error as serr:
            if serr == errno.ECONNREFUSED:
                print("Connection refused, try again...")
                self.send(receiverPort=receiverPort, sendMsg=sendMsg)
        finally:
            sendSocket.close()

    def ready(self):
        lmsg = LamportMessage(sender=self.id, msgtype=MsgTypes.Ready)
        sendMsg = lmsg.encodeLamport()
        for i in range(1, self.countNodes + 1):
            if i != self.id:
                receiverPort = 5000 + i
                self.send(receiverPort=receiverPort, sendMsg=sendMsg)

    def remove(self):
        lmsg = LamportMessage(sender=self.id, msgtype=MsgTypes.Remove)
        sendMsg = lmsg.encodeLamport()
        self.lock.acquire()
        for i in self.neighbours:
            receivePort = 5000 + i
            self.send(receiverPort=receivePort, sendMsg=sendMsg)
        self.lock.release()

    def run(self):
        self.listenthread = threading.Thread(target=self.listen)
        self.listenthread.start()
        time.sleep(2)
        self.ready()
        while self.countReady < self.countNodes - 1:
            time.sleep(1)
        self.remove()
        self.lock.acquire()
        print("in lock")
        self.running = False
        self.lock.release()
        print(self.running)
        print("Exit")
        if self.listenthread.is_alive():
            self.running = False


parser = argparse.ArgumentParser()
parser.add_argument("nodeid", help="id for the node", type=int)
parser.add_argument("countNeighbours", help="Count of all nodes", type=int)
# Parsing commandline arguments'
args = parser.parse_args()

# Instantiating node process'
n = Lamport(nid=args.nodeid, countNeighbours=args.countNeighbours)
# n.start()
n.run()
