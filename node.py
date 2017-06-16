"""Definition of node class"""

import argparse
import sys
import socket
import random
from multiprocessing import Process


# class Node(Process):
class Node:
    'Local node process'
    node_id = 0
    filepath = ''
    nodelist = []
    neighbours = []
    host = ''
    port = 0
    running = True

    def __init__(self, filepath, node_id):
        # super(Node, self).__init__()
        'Constructor for local node'
        self.node_id = int(node_id)
        self.filepath = filepath

    def __str__(self):
        return "Node:"+ str(self.node_id) +', ' +  self.host + ', ' + str(self.port)

    def run(self):
        self.nodelist = self.getendpoints()
        print(self.nodelist)
        print(self)
        self.listen_on_port()
        self.get_rnd_neighbours()
        print(self.neighbours)

    # Reading the file from commandline argument and parsing the lines
    def getendpoints(self):
        # print(self.filepath)
        node_list = []
        f = open(self.filepath, 'r')
        for i, line in enumerate(f,1):
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
    def findIDinNodeList(self, nid):
        for n in self.nodelist:
            if n[0] == nid:
                return n
        raise IndexError('Node not found')

    def interpret_message(self, message):
        print(message)

    # Open port to listen on
    def listen_on_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.host, self.port))
        print("Listening on port", self.port)
        while self.running:
            break


    # Get random neighbours from nodelist
    def get_rnd_neighbours(self):
        for i in range(0,3):
            rnd_index = random.randrange(len(self.nodelist))
            neighbour = self.nodelist[rnd_index]
            self.neighbours.append(neighbour)
            self.nodelist.remove(neighbour)


# Adding commandline arguments'
parser = argparse.ArgumentParser()
parser.add_argument("endpointfile", help="Path to the endpoint file")
parser.add_argument("nodeid", help="Desired id from the endpoint file", type=int)

# Parsing commandline arguments'
args = parser.parse_args()

# Instantiating node process'
n = Node(filepath=args.endpointfile, node_id=args.nodeid)
# n.start()
n.run()