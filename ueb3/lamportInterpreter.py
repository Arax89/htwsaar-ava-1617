import threading
import socket
from LamportMessage import LamportMessage, MsgTypes
from queue import Queue, PriorityQueue
from lamportClock import LamportClock

test = set()

class LamportInterpreter(threading.Thread):
    def __init__(self, nid, messagequeue: Queue, neighbourNodes: set, priorityQueue: PriorityQueue,
                 lclock: LamportClock, allowed: threading.Condition):
        threading.Thread.__init__(self)
        self.nid = nid
        self.msgqueue = messagequeue
        self.running = True
        self.requestQueue = priorityQueue
        self.zeroesRead = 0
        self.lclock = lclock
        self.neighbours = neighbourNodes
        self.allowed = allowed
        self.replies = set()

        if nid % 2 == 0:
            self.even = True
            self.partnerID = nid - 1
        else:
            self.even = False
            self.partnerID = nid + 1

    def run(self):
        while self.running:
            if self.msgqueue.empty():
                pass
            else:
                msg = self.msgqueue.get()
                self.interpret(msg)
                print(self.replies)
                if len(self.replies) == (len(self.neighbours) - 1):
                    print("Got all replies, entering cs...")
                    self.allowed.notifyAll()

    def stop(self):
        self.running = False

    def interpret(self, lmsg: LamportMessage):
        lmsg.decodeLamport()
        if lmsg.msgtype == MsgTypes.Request:
            self.lclock.increaseTimeAfterRecv(lmsg.time_stamp)
            self.requestQueue.put((int(lmsg.time_stamp), int(lmsg.sender)))
            print("Got request:", self.requestQueue.queue)
            self.reply(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Reply:
            print("Got reply from :", lmsg.sender)
            print(lmsg)
            print("Lclock time:", self.lclock.getTime())
            self.replies.add(lmsg.sender)
            self.lclock.increaseTimeAfterRecv(lmsg.time_stamp)
        elif lmsg.msgtype == MsgTypes.Release:
            self.lclock.increaseTimeAfterRecv(lmsg.sender)
            self.requestQueue.queue.remove((int(lmsg.request_timestamp), int(lmsg.sender)))
        elif lmsg.msgtype == MsgTypes.Terminate:
            self.terminate()
        elif lmsg.msgtype == MsgTypes.Remove:
            pass
            # self.removeFromOtherNodes(lmsg.sender)
        else:
            pass

    def reply(self, target):
        port = target + 5000
        self.lclock.increaseTimeBeforeSend()
        replyMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Reply,
                                  timestamp=self.lclock.getTime()).encodeLamport()
        self.send(port, replyMsg)

    def send(self, target: int, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostname(), target))
        s.send(msg)

    def terminate(self):
        # self.removeMe()
        self.running = False

        # def removeMe(self):
        #     print("Send remove message. Waiting for acknowledge")
        #     removeMessage = LamportMessage(self.nid, MsgTypes.Remove)
        #     self.sendToAllWithAcknowledge(removeMessage.encodeLamport())
        #     while len(self.acknowledgeSet) > 0:
        #         pass
