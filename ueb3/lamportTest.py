import socket
import errno
import argparse
import threading
import time
import datetime
import sys
from queue import PriorityQueue

from LamportMessage import MsgTypes, LamportMessage


class Lamport():
    def __init__(self, nid, nodeCount):
        self.lock = threading.Lock()
        self.time = 0
        self.time_stamp = 0
        self.running = True
        self.setup = False
        self.allReady = False
        self.pendingRequest = False
        self.nid = nid
        self.nodeCount = nodeCount
        self.neighbourCount = nodeCount - 1
        self.host = socket.gethostname()
        self.port = 5000 + nid
        self.acknowledgeSet = set()
        self.otherNodes = set()
        self.readies = set()
        self.replies = set()
        self.requestQueue = PriorityQueue()
        self.listenSocket = None
        self.zeroesRead = 0
        if nid % 2 == 0:
            self.even = True
            self.partnerID = nid - 1
        else:
            self.even = False
            self.partnerID = nid + 1

    def checkQueue(self):
        head = self.requestQueue.queue[0]
        print("Check Queuehead of", self.nid, ":", head)
        requestID = head[1]
        if requestID == self.nid:
            self.enterCS()

    def request(self):
        self.lock.acquire()
        self.pendingRequest = True
        self.lock.release()
        self.time += 1
        self.time_stamp = self.time
        requestMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Request, timestamp=self.time_stamp)
        self.requestQueue.put((int(self.time_stamp), int(requestMsg.sender)))
        self.sendToAll(requestMsg.encodeLamport())
        while len(self.replies) < self.neighbourCount:
            pass
        print("Got all replies", len(self.replies))
        self.checkQueue()
        self.replies.clear()
        print(len(self.replies))

    def increase_time(self, msg_timestamp: int):
        self.time = max(msg_timestamp, self.time) + 1

    def listen(self):
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.bind((self.host, self.port))
        self.listenSocket.listen(5)
        print(self.nid, ":Listening on port", self.port)
        while self.running:
            try:
                conn, adr = self.listenSocket.accept()
                # msg = conn.recv(4096)
                # # print("Recvd:", msg, "at:", datetime.datetime.utcnow())
                # sendMsg = "Ok from " + str(self.nid)
                threading.Thread(target=self.interpret, args = (conn, adr)).start()
                # self.interpreting = True
                # self.interpret(msg)
                # conn.send(sendMsg.encode())
                # conn.close()
            except KeyboardInterrupt:
                break
        print("stopping listener")
        self.listenSocket.shutdown(socket.SHUT_RDWR)
        self.listenSocket.close()

    def interpret(self, conn, adr):
        msg = conn.recv(4096)
        sendMsg = "Ok from " + str(self.nid)
        conn.send(sendMsg.encode())
        conn.close()
        lmsg = LamportMessage(jsonMsg=msg.decode())
        lmsg.decodeLamport()
        if lmsg.msgtype == MsgTypes.Request:
            self.increase_time(lmsg.time_stamp)
            self.requestQueue.put((int(lmsg.time_stamp), int(lmsg.sender)))
            print("Got request:", self.requestQueue.queue)
            self.reply(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Reply:
            if self.time_stamp < lmsg.time_stamp:
                self.replies.add(lmsg.sender)
            self.increase_time(lmsg.time_stamp)
        elif lmsg.msgtype == MsgTypes.Acknowledge:
            self.confirmAcknowledge(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Release:
            self.increase_time(lmsg.time_stamp)
            self.requestQueue.queue.remove((lmsg.request_timestamp, lmsg.sender))
        elif lmsg.msgtype == MsgTypes.Terminate:
            self.terminate()
        elif lmsg.msgtype == MsgTypes.Remove:
            self.removeFromOtherNodes(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Register:
            self.addToOtherNodes(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Ready:
            self.addToReadies(lmsg.sender)
        else:
            pass
        self.interpreting = False

    def confirmAcknowledge(self, sender):
        self.acknowledgeSet.remove(sender)
        print("Acknowledge confirmed")

    def addToOtherNodes(self, sender):
        # print("Before add", self.otherNodes)
        self.otherNodes.add(sender)
        # print("After add", self.otherNodes)
        if len(self.otherNodes) == self.neighbourCount:
            readyMessage = LamportMessage(self.nid, MsgTypes.Ready)
            self.sendToAll(readyMessage.encodeLamport())

    def removeFromOtherNodes(self, sender):
        self.otherNodes.remove(sender)
        self.readies.remove(sender)
        print("Removed", sender, "from list")
        print("sending acknowledge")
        acknowledge = LamportMessage(self.nid, MsgTypes.Acknowledge)
        self.send(sender, acknowledge.encodeLamport())

    def addToReadies(self, sender):
        print("Add to readies", sender)
        self.readies.add(sender)

    def sendToAllWithAcknowledge(self, sendMsg):
        if self.otherNodes:
            for i in self.otherNodes:
                self.acknowledgeSet.add(i)
                self.send(i, sendMsg)

    def sendToAll(self, sendMsg):
        if self.otherNodes:
            for i in self.otherNodes:
                self.send(i, sendMsg)

    def sendRegister(self):
        registerMessage = LamportMessage(self.nid, MsgTypes.Register)
        for i in range(1, self.nodeCount + 1):
            if i is not self.nid and i not in self.readies:
                self.send(i, registerMessage.encodeLamport())

    def send(self, target, sendMsg):
        targetPort = int(target) + 5000
        senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            senderSocket.connect((self.host, targetPort))
            senderSocket.send(sendMsg)
            # print(sendMsg)
            # print("Send", sendMsg, "Wating for answer...")
            recvMsg = senderSocket.recv(4096)
            senderSocket.close()
            print(recvMsg.decode())
        except socket.error as serr:
            if serr == errno.ECONNREFUSED:
                print("Connection refused, try again...")
                self.send(target=target, sendMsg=sendMsg)
        finally:
            senderSocket.close()

    def removeMe(self):
        print("Send remove message. Waiting for acknowledge")
        removeMessage = LamportMessage(self.nid, MsgTypes.Remove)
        self.sendToAllWithAcknowledge(removeMessage.encodeLamport())
        while len(self.acknowledgeSet) > 0:
            pass

    def release(self, request):
        self.time += 1
        self.time_stamp = self.time
        releaseMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Release, timestamp=self.time_stamp,
                                    request_timestamp=request[0])
        self.sendToAll(releaseMsg.encodeLamport())
        self.lock.acquire()
        self.pendingRequest = False
        self.lock.release()

    def reply(self, nid):
        self.time += 1
        self.time_stamp = self.time
        lmsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Reply, timestamp=self.time_stamp)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, 5000 + nid))
        s.send(lmsg.encodeLamport())
        s.close()


    def enterCS(self):
        print("Entered CS")
        print(self.nid, "RequestQueue:", self.requestQueue.queue)
        f = open('x', 'r+')
        ch = f.read(1)
        if ch == '-':
            ch2 = f.read(2)
            x = int(ch + ch2)
        else:
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
        while len(self.readies) < self.neighbourCount:
            self.sendRegister()
            time.sleep(0.5)
        print("All nodes are ready:", self.readies)
        while self.zeroesRead < 3:
            if not self.pendingRequest:
                print(self.nid, ":Sending request...")
                self.request()
                time.sleep(0.5)
        self.terminate()
        if self.otherNodes:
            self.removeMe()
        self.lock.acquire()
        self.running = False
        self.lock.release()
        print("OtherNodes: ", self.otherNodes)
        print("Readies", self.readies)
        print("AcknowledgeSet", self.acknowledgeSet)
        print("Exit")
        sys.exit()

    def terminate(self):
        self.removeMe()
        self.running = False
        sys.exit()

    def start(self):
        try:
            listenThread = threading.Thread(target=self.listen)
            runThread = threading.Thread(target=self.run)
            listenThread.setDaemon(True)
            runThread.setDaemon(True)
            listenThread.start()
            runThread.start()
            runThread.join()
            sys.exit()

        except (KeyboardInterrupt, SystemExit):
            self.running = False
            self.listenSocket.shutdown(socket.SHUT_RDWR)
            self.listenSocket.close()
            sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument("nodeId", help="The id of the node", type=int)
parser.add_argument("nodeCount", help="The number of all nodes", type=int)
args = parser.parse_args()

lamport = Lamport(args.nodeId, args.nodeCount)
lamport.start()
