import sys
import argparse
import socket
import threading
import time
from queue import PriorityQueue

from LamportMessage import MsgTypes, LamportMessage


class LamportNode:
    host = None
    port = None
    time = None
    time_stamp = None
    nid = None
    partner = None
    count = None
    requestQueue = None
    zeroesRead = None
    file = None

    def __init__(self, nid: int, count: int):
        self.host = 'localhost'
        self.is_ready = False
        self.ready_set = set()
        self.running = True
        self.time = 0
        self.time_stamp = 0
        self.nid = nid
        self.port = 5000 + nid
        self.zeroesRead = 0
        self.replies = set()
        self.requestQueue = PriorityQueue()
        self.pendingRequest = False

        if nid % 2 == 1:
            self.even = False
            self.partner = nid + 1
        else:
            self.even = True
            self.partner = nid - 1

        if nid > count or count % 2 == 1:
            print("NodeID > count of other nodes or count is not even", file=sys.stderr)
            exit(1)
        else:
            self.count = count

    def send(self, msg: LamportMessage):
        print("Sender:", self.nid, msg)
        for i in range(1, self.count + 1):
            if i != self.nid:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, 5000 + i))
                s.send(msg.encodeLamport())
                s.close()

    def request(self):
        self.pendingRequest = True
        self.time += 1
        self.time_stamp = self.time
        requestMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Request, timestamp=self.time_stamp)
        self.requestQueue.put((self.time_stamp, requestMsg.sender))
        self.send(requestMsg)
        while len(self.replies) < self.count - 1:
            pass
        print("Got all replies", len(self.replies))
        self.checkQueue()
        self.replies.clear()
        print(len(self.replies))

    def reply(self, nid):
        self.time += 1
        self.time_stamp = self.time
        lmsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Reply, timestamp=self.time_stamp)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, 5000 + nid))
        s.send(lmsg.encodeLamport())
        s.close()

    def checkQueue(self):
        head = self.requestQueue.queue[0]
        print("Check Queuehead of", self.nid, ":", head)
        requestID = head[1]
        if requestID == self.nid:
            self.enterCS()

    def release(self, request):
        self.time += 1
        self.time_stamp = self.time
        releaseMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Release, timestamp=self.time_stamp,
                                    request_timestamp=request[0])
        self.send(releaseMsg)
        self.pendingRequest = False

    def remove(self):
        removeMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Remove)
        self.send(removeMsg)

    def terminate(self):
        self.running = False
        print("Terminating")
        terminateMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Terminate)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, 5000 + self.partner))
        s.send(terminateMsg.encodeLamport())
        s.close()
        exit(0)

    def receive(self, msg):
        lmsg = LamportMessage(jsonMsg=msg.decode())
        lmsg.decodeLamport()
        print(self.requestQueue.queue)
        print(self.nid, lmsg)
        if lmsg.msgtype == MsgTypes.Ready:
            self.ready_set.add(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Request:
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
        elif lmsg.msgtype == MsgTypes.Remove:
            self.count -= 1
        elif lmsg.msgtype == MsgTypes.Terminate:
            self.terminate()

    def increase_time(self, msg_timestamp):
        self.time = max(msg_timestamp, self.time) + 1

    def listening(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        print("Listening on port", self.port)

        while self.running:
            conn, addr = s.accept()
            print("Connection from:", addr)
            msg = conn.recv(1024)
            self.receive(msg)
            conn.close()
        print("stopping")

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

    def run(self):
        listenthread = threading.Thread(target=self.listening)
        listenthread.start()
        print("Started with ID", self.nid, "Partner:", self.partner)
        time.sleep(4)
        # while not self.is_ready:
        #     self.ready()
        #     print(self.ready_set)
        #     if len(self.ready_set) == self.count:
        #         self.is_ready = True
        while self.zeroesRead < 3:
            if not self.pendingRequest:
                self.request()
        self.terminate()
        print("End")


parser = argparse.ArgumentParser()
parser.add_argument("nodeid", help="id for the node", type=int)
parser.add_argument("count", help="Count of all nodes", type=int)

# Parsing commandline arguments'
args = parser.parse_args()

# Instantiating node process'
n = LamportNode(nid=args.nodeid, count=args.count)
# n.start()
n.run()
