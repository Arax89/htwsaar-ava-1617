from lamportListener import LamportListener
from lamportWorker import LamportWorker, LamportInterpreter
from lamportClock import LamportClock
from queue import Queue, PriorityQueue
import argparse
import threading
import time


def getEndpoints(f: str, nodeID):
    endpoints = set()
    with open(f, 'r') as file:
        for line in file:
            try:
                l = line.split()
                nid = int(l[0])
                port = int(l[1])
                if nodeID == nid:
                    pass
                else:
                    endpoints.add((nid, port))
            except (ValueError, SyntaxError, IndexError) as err:
                print("Couldn't read file.")
                exit(err)
    return endpoints


parser = argparse.ArgumentParser()
parser.add_argument("nid", help="The ID the node shall have", type=int)
parser.add_argument("endpointfile", help="The path to the endpointfile", type=str)
args = parser.parse_args()

nid = args.nid
port = 5000 + nid
endpointfile = args.endpointfile
q = Queue()
pq = PriorityQueue()
lclock = LamportClock()
endpoints = getEndpoints(endpointfile, nid)
allowed = threading.Condition()

listener = LamportListener(nid, port, q)
worker = LamportWorker(nid, endpoints, pq, lclock)
interpreter = LamportInterpreter(nid, q, endpoints, pq, lclock, worker)

listener.start()
time.sleep(1)
interpreter.start()
time.sleep(1)
worker.start()
worker.join()
listener.stop()
interpreter.stop()
