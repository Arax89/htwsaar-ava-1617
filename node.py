'Definition of node class'

import argparse

class Node:
    'Local node process'
    node_id = 0
    filepath = ''

    def __init__(self, filepath, node_id):
        'Constructor for local node'
        self.node_id = node_id
        self.filepath = filepath
        self.readfile()
        print(self.node_id)

    def readfile(self):
        print(self.filepath)

# Adding commandline arguments'
parser = argparse.ArgumentParser()
parser.add_argument("endpointfile", help="Path to the endpoint file")
parser.add_argument("nodeid", help="Desired id from the endpoint file")

# Parsing commandline arguments'
args = parser.parse_args()

# Instantiating node process'
Node(filepath=args.endpointfile, node_id=args.nodeid)
