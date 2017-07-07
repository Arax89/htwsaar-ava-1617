import argparse
import socket
import sys

from NodeMessage import MsgTypes
from NodeMessage import NodeMessage

parser = argparse.ArgumentParser()
parser.add_argument("endpoints", help="Path to the endpoint file", type=str)
parser.add_argument("nid", help="The id of receiver node", type=int)
parser.add_argument("msg", help="The message you want to send")

args = parser.parse_args()


def getendpoints():
    # print(self.filepath)
    node_list = []
    f = open(args.endpoints, 'r')
    for i, line in enumerate(f, 1):
        try:
            l = line.split()
            nid = int(l[0])
            ip_port = l[1].split(':')
            endpoint = (nid, ip_port[0], int(ip_port[1]))
            node_list.append(endpoint)
        except (ValueError, SyntaxError, IndexError) as err:
            print("Couldn't read file. Error in line " + str(i), file=sys.stderr)
            exit(err)
    f.close()
    return node_list


def findIDinNodeList(nid: int, nodelist):
    for n in nodelist:
        if n[0] == nid:
            return n
    raise IndexError('Node not found')


def send(id: int, msg: str):
    nodelist = getendpoints()
    node = findIDinNodeList(args.nid, nodelist)
    print(node)
    host = node[1]
    port = node[2]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    nmsg = NodeMessage(MsgTypes.Control, msg, 0, node[0], None)
    s.sendto(nmsg.encode(), (host, port))
    # print("Send:", nmsg)
    s.close()


send(args.nid, args.msg)
