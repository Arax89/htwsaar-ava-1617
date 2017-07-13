import threading
import socket
import time
from LamportMessage import LamportMessage, MsgTypes
from queue import Queue, PriorityQueue
from lamportClock import LamportClock

cv = threading.Condition()

class LamportWorker(threading.Thread):
    '''WorkerThread which wants to access the critical section'''
    def __init__(self, nid, neighbourNodes: set, prioQ: PriorityQueue, lclock: LamportClock):
        threading.Thread.__init__(self)
        self.lclock = lclock
        self.nid = nid
        self.running = True
        self.prioQ = prioQ
        self.zeroesRead = 0
        self.neighbours = neighbourNodes

        if nid % 2 == 0:
            self.even = True
            self.partner = nid - 1 + 5000
        else:
            self.even = False
            self.partner = nid + 1 + 5000

    def run(self):
        while self.zeroesRead < 3 and self.running:
            with cv: # CV = condition variable (Lock)
                self.requestAccess()
                print("ZeroesRead:", self.zeroesRead, "worker waiting")
                cv.wait() # Waits until LamportListener notifies for meeting the requirements for entering CS
                if self.running:
                    print("worker allowed")
                    self.enterCS()
        if self.running:
            terminateMsg = LamportMessage(self.nid, MsgTypes.Terminate).encodeLamport()
            self.send(self.partner, terminateMsg)
            print("Send terminate message to:", self.partner)
            removeMsg = LamportMessage(self.nid, MsgTypes.Remove, timestamp=self.lclock.getTime()).encodeLamport()
            self.sendToAll(removeMsg)
            print("Send remove message to all")
        print("Stopped workerthread...")

    def stop(self):
        self.running = False

    def requestAccess(self):
        self.lclock.increaseTimeBeforeSend()
        requestMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Request,
                                    timestamp=self.lclock.getTimeStamp()).encodeLamport()
        self.prioQ.put((self.lclock.getTimeStamp(), self.nid))
        self.sendToAll(requestMsg)

    def send(self, target: int, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((socket.gethostname(), target))
            s.send(msg)
            s.close()
        except:
            print("Worker: Connection refused to target", target)
            time.sleep(1)

    def sendToAll(self, msg):
        tmpNeighbours = self.neighbours.copy()
        for node in tmpNeighbours:
            self.send(node[1], msg)

    def release(self, RequestTimestamp):
        self.lclock.increaseTimeBeforeSend()
        releaseMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Release,
                                    timestamp=self.lclock.getTimeStamp(),
                                    request_timestamp=RequestTimestamp).encodeLamport()
        self.sendToAll(releaseMsg)
        print("Send release:", (RequestTimestamp, self.nid))

    def enterCS(self):
        '''Critical section'''
        print("Entered CS")
        print(self.nid, "PrioQ before cs:", self.prioQ.queue)
        f = open('x', 'r+')
        ch = f.read(1)
        if ch == '-':
            ch2 = f.read(1)
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

        # Follow Up
        request = self.prioQ.get()
        self.release(request[0])
        print(self.nid, "PrioQ after cs:", self.prioQ.queue)


class LamportInterpreter(threading.Thread):
    '''Interpretes messages received by LamportListener'''
    def __init__(self, nid, messagequeue: Queue, neighbourNodes: set, priorityQueue: PriorityQueue,
                 lclock: LamportClock, lworker : LamportWorker):
        threading.Thread.__init__(self)
        self.nid = nid
        self.msgqueue = messagequeue
        self.running = True
        self.requestQueue = priorityQueue
        self.zeroesRead = 0
        self.lclock = lclock
        self.neighbours = neighbourNodes
        self.msgsLaterOwnRequest = set()
        self.terminated = False
        self.lworker = lworker

    def run(self):
        while self.running:
            with cv: # Condition variable (Lock)
                if self.msgqueue.empty():
                    pass
                else:
                    msg = self.msgqueue.get()
                    self.interpret(msg)
                    # print("Replies:", self.msgsLaterOwnRequest)
                    if len(self.msgsLaterOwnRequest) == (len(self.neighbours)) and not self.terminated:
                        # print("Got msg from all later than own clock, entering cs...")
                        if self.isHead():
                            # print("Head of Q")
                            # print("Q Before cs:", self.requestQueue.queue)
                            cv.notify_all() # Notify worker to continue
                            self.msgsLaterOwnRequest.clear()

    def isHead(self):
        '''Check if this node's request is head of queue'''
        if not self.requestQueue.empty():
            head = self.requestQueue.queue[0]
            requestID = head[1]
            if requestID == self.nid:
                return True
            else:
                return False

    def stop(self):
        self.running = False

    def interpret(self, lmsg: LamportMessage):
        '''Interpreting messages from messagequeue. The messages are received by LamportListener.Thread'''
        lmsg.decodeLamport()
        # print("Message:", lmsg)
        requestTime = self.getOwnRequestTime()
        if not lmsg.msgtype == MsgTypes.Terminate and not lmsg.msgtype == MsgTypes.Remove and lmsg.time_stamp > requestTime:
            self.msgsLaterOwnRequest.add(lmsg.sender)
        if lmsg.msgtype == MsgTypes.Request:
            self.lclock.increaseTimeAfterRecv(lmsg.time_stamp)
            self.requestQueue.put((int(lmsg.time_stamp), int(lmsg.sender)))
            # print("Got request:", self.requestQueue.queue)
            self.reply(lmsg.sender)
        elif lmsg.msgtype == MsgTypes.Reply:
            # print("Got reply from :", lmsg.sender)
            # print(lmsg)
            # print("Lclock time:", self.lclock.getTime())
            self.lclock.increaseTimeAfterRecv(lmsg.time_stamp)
        elif lmsg.msgtype == MsgTypes.Release:
            self.lclock.increaseTimeAfterRecv(lmsg.sender)
            print("Got release msg from", lmsg.sender)
            print("To be removed", (lmsg.request_timestamp, lmsg.sender))
            print(self.nid, "PrioQ before release:", self.requestQueue.queue)
            self.requestQueue.queue.remove((int(lmsg.request_timestamp), int(lmsg.sender)))
            print(self.nid, "PrioQ after release:", self.requestQueue.queue)
            print("Removed request", (int(lmsg.request_timestamp), int(lmsg.sender)))
        elif lmsg.msgtype == MsgTypes.Terminate:
            print("Terminating...")
            self.removeFromNeighbours(lmsg.sender)
            self.terminate()
        elif lmsg.msgtype == MsgTypes.Remove:
            print("Got remove msg from:", lmsg.sender)
            self.removeFromNeighbours(lmsg.sender)
            self.removeFromRequestQueue(lmsg.sender)
        else:
            pass

    def reply(self, target):
        port = target + 5000
        self.lclock.increaseTimeBeforeSend()
        replyMsg = LamportMessage(sender=self.nid, msgtype=MsgTypes.Reply,
                                  timestamp=self.lclock.getTime()).encodeLamport()
        self.send(port, replyMsg)

    def send(self, target: int, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((socket.gethostname(), target))
            s.send(msg)
            # recv = s.recv(1024)
            # print(self.nid, recv)
        except:
            print("Interpreter: Connection refused to target", target)
            time.sleep(1)

    def getOwnRequestTime(self):
        time = 0
        for i in self.requestQueue.queue:
            if i[1] == self.nid:
                time = i[0]
        return time

    def terminate(self):
        self.removeMe()
        self.lworker.stop()
        cv.notify_all()
        self.running = False
        self.terminated = True

    def sendToAll(self, msg):
        for node in self.neighbours:
            self.send(node[1], msg)

    def removeMe(self):
        print("Send remove message.")
        removeMessage = LamportMessage(self.nid, MsgTypes.Remove)
        self.sendToAll(removeMessage.encodeLamport())

    def removeFromNeighbours(self, id):
        tmp = self.neighbours.copy()
        for node in tmp:
            if node[0] == id:
                self.neighbours.remove(node)

    def removeFromRequestQueue(self, id):
        tmp = self.requestQueue.queue
        for request in tmp:
            if request[1] == id:
                self.requestQueue.queue.remove(request)


