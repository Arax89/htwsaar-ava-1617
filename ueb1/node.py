"""Definition of node class"""

import argparse
import datetime
import random
import socket
import sys
import threading
import portalocker

from Graph import Graph

from NodeMessage import MsgTypes
from NodeMessage import NodeMessage


# class Node(Process):
class Node:
    """Local node process"""
    node_id = 0
    filepath = ''
    graphpath = ''
    nodelist = []
    neighbours = []
    host = ''
    port = 0
    running = True
    HasSendID = False
    rumor = None
    counter = 0
    threshold = 0
    believing = False
    hasSpreadRumor = False
    graph = None

    def __init__(self, filepath, node_id, graphpath, c):
        # super(Node, self).__init__()
        """Constructor for local node"""
        self.node_id = int(node_id)
        self.filepath = filepath
        self.graphpath = graphpath
        self.threshold = c
        self.graph = Graph(graphpath)

    def __str__(self):
        return "Node:" + str(self.node_id) + ', ' + self.host + ', ' + str(self.port)

    def run(self):
        self.nodelist = self.getendpoints()
        self.get_neighbours_from_graph()
        self.listen_on_port()
        if self.believing:
            self.write_to_file()
            # self.get_rnd_neighbours()

    def print_message(self, nmsg: NodeMessage, send: bool):
        if send:
            print('Send:', nmsg, datetime.datetime.utcnow())
        else:
            print('Recv:', nmsg, datetime.datetime.utcnow())

    # Reading the file from commandline argument and parsing the lines
    def getendpoints(self):
        # print(self.filepath)
        node_list = []
        f = open(self.filepath, 'r')
        for i, line in enumerate(f, 1):
            try:
                l = line.split()
                nid = int(l[0])
                ip_port = l[1].split(':')
                if self.node_id == nid:
                    self.host = ip_port[0]
                    self.port = int(ip_port[1])
                else:
                    endpoint = (nid, ip_port[0], int(ip_port[1]))
                    node_list.append(endpoint)
            except (ValueError, SyntaxError, IndexError) as err:
                print("Couldn't read file. Error in line " + str(i), file=sys.stderr)
                exit(err)
        f.close()
        return node_list

    # Finds the endpoint with the given ID in list
    def findIDinNodeList(self, nid: int):
        for n in self.nodelist:
            if n[0] == nid:
                return n
        raise IndexError('Node not found')

    def interpret_message(self, message):
        # print(message)
        nmsg = NodeMessage(jsonmsg=message.decode())
        msg = nmsg.getMessage()
        self.print_message(nmsg, False)
        if nmsg.msgtype == MsgTypes.Control:
            if msg == "stop":
                self.running = False
                print("stopping")
            if msg == "stopall":
                self.running = False
                self.send_to_neighbours("stopall", MsgTypes.Control)
                print("stopped")
            if msg == "start":
                if not self.HasSendID:
                    self.HasSendID = True
                    self.send_to_neighbours(self.node_id, MsgTypes.Application)
            else:
                self.send_to_neighbours(msg, MsgTypes.Application)
        elif nmsg.msgtype == MsgTypes.Application:
            if not self.HasSendID:
                self.HasSendID = True
                self.send_to_neighbours(self.node_id, MsgTypes.Application)
            else:
                if not nmsg.getSender() == msg:
                    self.believe_rumor(msg)
                    if not self.hasSpreadRumor:
                        self.hasSpreadRumor = True
                        self.spread_rumor(msg, nmsg.getSender())

    def believe_rumor(self, msg):
        if self.rumor is None:
            self.rumor = msg
        if self.rumor == msg:
            self.counter += 1
            if self.counter >= self.threshold and not self.believing:
                self.believing = True
                print("Believing...")

    def spread_rumor(self, msg, origin: int):
        recList = self.neighbours
        recList.remove(self.findIDinNodeList(origin))
        for rec in recList:
            self.send_message(rec, msg, MsgTypes.Application)

    # Open port to listen on
    def listen_on_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.host, self.port))
        print(self, "Listening on port", self.port)
        while self.running:
            msg, addr = s.recvfrom(1024)
            interpretthread = threading.Thread(target=Node.interpret_message(self, msg))
            interpretthread.start()
        print("stopping")

    def send_message(self, receiver, msg, msgtype):
        host = receiver[1]
        port = receiver[2]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nmsg = NodeMessage(msgtype, msg, self.node_id, receiver[0])
        s.sendto(nmsg.encode(), (host, port))
        # print("Send:", nmsg)
        s.close()
        self.print_message(nmsg, True)

    def send_to_neighbours(self, msg, msgtype):
        for n in self.neighbours:
            self.send_message(n, msg, msgtype)

    # Get random neighbours from nodelist
    def get_rnd_neighbours(self):
        for i in range(0, 3):
            rnd_index = random.randrange(len(self.nodelist))
            neighbour = self.nodelist[rnd_index]
            self.neighbours.append(neighbour)
            self.nodelist.remove(neighbour)

    def get_neighbours_from_graph(self):
        tempNeighbours = []
        neighbour_ids = self.graph.find_neighbours(self.node_id)
        for i in neighbour_ids:
            tempNeighbours.append(self.findIDinNodeList(i))
        self.neighbours = tempNeighbours

    def write_to_file(self):
        f = open('result.tmp', 'a+')
        portalocker.lock(f, portalocker.LOCK_UN)
        f.write(str(self.node_id) + ':believed\n')
        portalocker.unlock(f)
        f.close()


# Adding commandline arguments'
parser = argparse.ArgumentParser()
parser.add_argument("endpointfile", help="Path to the endpoint file")
parser.add_argument("nodeid", help="Desired id from the endpoint file", type=int)
parser.add_argument("--c", help="C is the believe rumor threshold", default=1, type=int)
parser.add_argument("graphpath", help="Path to graph file")

# Parsing commandline arguments'
args = parser.parse_args()

# Instantiating node process'
n = Node(filepath=args.endpointfile, node_id=args.nodeid, graphpath=args.graphpath, c=args.c)
# n.start()
n.run()
