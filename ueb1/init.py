import argparse
import os
from Graph import Graph

parser = argparse.ArgumentParser()
parser.add_argument("nodepath", help="The path to the endpoint file", type=str)
parser.add_argument("graphpath", help="The path to the graphviz file", type=str)
parser.add_argument("--c", help="The believing threshold. Defaults to 1", default=1, type=int)
args = parser.parse_args()

if os.path.exists('result.tmp'):
    os.remove('result.tmp')

g = Graph(args.graphpath)

num_nodes = g.count_nodes()
num_edges = g.count_edges()
range_end = num_nodes + 1

with open('result.tmp', 'w') as f:
    f.write("N:" + str(num_nodes) + '\n' + 'M:' + str(num_edges) + '\n' + 'C:' + str(args.c) + '\n')

if args.c > 1:
    c = args.c
    for i in range(1, range_end):
        cmd = "konsole --hide-tabbar -e python3 node.py " + args.nodepath + " " \
              + str(i) + " " + args.graphpath + " " + " --c" + str(c) + '&'
        os.system(cmd)
else:
    for i in range(1, range_end):
        cmd = "konsole --hide-tabbar -e python3 node.py " + args.nodepath + " " + str(i) + " " \
              + args.graphpath + '&'
        os.system(cmd)
