import threading
import socket
from queue import Queue
from LamportMessage import LamportMessage


class LamportListener(threading.Thread):
    '''Listener, which puts received messages in a given fifo message queue'''
    def __init__(self, nid: int, port: int, messagequeue: Queue):
        threading.Thread.__init__(self)
        self.nid = nid
        self.port = port
        self.host = socket.gethostname()
        self.running = True
        self.listenSocket = None
        self.msgqueue = messagequeue

    def run(self):
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenSocket.bind((self.host, self.port))
        self.listenSocket.listen(5)
        print(self.nid, ":Listening on port", self.port)
        while self.running:
            try:
                conn, adr = self.listenSocket.accept()
                msg = conn.recv(4096)
                # print("Recvd:", msg, "at:", datetime.datetime.utcnow())
                sendMsg = "Ok from " + str(self.nid)
                self.addToMsgQ(msg)
                conn.send(sendMsg.encode())
                conn.close()
            except KeyboardInterrupt:
                break
        print("stopping listener")
        self.listenSocket.shutdown(socket.SHUT_RDWR)
        self.listenSocket.close()

    def stop(self):
        self.running = False

    def addToMsgQ(self, msg):
        lmsg = LamportMessage(jsonMsg=msg.decode())
        self.msgqueue.put(lmsg)
