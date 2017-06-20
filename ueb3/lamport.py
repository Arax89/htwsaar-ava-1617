import sys
import argparse
import socket
import threading
import time
from queue import PriorityQueue

from LamportMessage import MsgTypes, LamportMessage


class Lamport:
    def __init__(self, nid: int):
        self.lock = threading.Lock
        self.host = 'localhost'
        self.port = 5000 + nid
        self.pendingRequest = False
        self.nid = nid
        self.pendingReplies = []
        self.requestQueue = PriorityQueue()
        self.running = True
        self.zeroesRead = 0
        self.time = 0
        self.time_stamp = 0

        if nid % 2 == 1:
            self.even = False
            self.partner = nid + 1
        else:
            self.even = True
            self.partner = nid - 1

    def handle_client_connection(self, client_socket):
        msg = client_socket.recv(1024)
        client_socket.close()
        self.interpret_message(msg)

    def increase_time(self, msg_timestamp):
        self.time = max(msg_timestamp, self.time) + 1

    def interpret_message(self, msg):
        lmsg = LamportMessage(jsonMsg=msg.decode())
        lmsg.decodeLamport()
        if lmsg.msgtype == MsgTypes.Request:
            self.increase_time(lmsg.time_stamp)
            self.requestQueue.put((lmsg.time_stamp, lmsg.sender))
            self.reply(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Reply:
            self.increase_time(lmsg.time_stamp)
            if self.time_stamp < lmsg.time_stamp:
                self.replies.add(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Release:
            self.increase_time(lmsg.time_stamp)
            self.requestQueue.queue.remove((lmsg.request_timestamp, lmsg.sender))
        elif lmsg.msgtype == MsgTypes.Terminate:
            self.terminate()

    def terminate(self):
        self.running = False
        exit(0)

    def release(self, request):
        self.time += 1
        self.time_stamp = self.time
        releaseMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Release, timestamp=self.time_stamp,
                                    request_timestamp=request[0])
        self.send(releaseMsg)
        self.pendingRequest = False

    def enterCS(self):
        print("Entered CS")
        print(self.nid, "RequestQueue:", self.requestQueue.queue)
        f = open('x', 'r+')
        ch = f.read(1)
        x = int(ch)
        if x == 0:
            self.zeroesRead += 1
        if self.even:
            x -= 1
        else:
            x += 1
        f.seek(0)
        f.write(str(x))
        f.seek(0, 2)
        f.write('\n' + str(self.nid))
        f.close()

        request = self.requestQueue.get()
        self.release(request)

    def server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def client(self):
        pass

    def run(self):
        serverthread = threading.Thread(target=self.server)
        clientthread = threading.Thread(target=self.client)
        serverthread.start()
        clientthread.start()

