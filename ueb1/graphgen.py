import argparse
import random

# Adding commandline arguments'
parser = argparse.ArgumentParser()
parser.add_argument("n", help="The number of nodes", type=int)
parser.add_argument("m", help='The number of edges. m has to be greater than n. If m > (n*n-1)/2, the max possible '
                              'number of edges will be set', type=int)

# Parsing commandline arguments
parser.add_argument("savepath", help="The path, where the graphviz file will be saved", type=str)
args = parser.parse_args()

n = args.n
m = args.m
spath = args.savepath
edges = set()

if not spath.endswith('.gv', len(spath)-3):
    spath += '.gv'

if m > n:
    max_edges = (n * (n-1))/2
    nodes = range(1, n+1)
    if m > max_edges:
        m = int(max_edges)
    while m is not len(edges):
        for i in nodes:
            if i is not 1:
                j = random.randrange(i-1)
                length = len(edges)
                if m is not length:
                    edges.add((i, nodes[j]))
    # print(edges)
    f = open(spath, 'w')
    f.write('graph G {\n')
    for edge in edges:
        line = str(edge[0]) + ' -- ' + str(edge[1]) + ';\n'
        f.write(line)
    f.write('}')
    f.close()
    print("Graph is saved to", spath)
else:
    exit("m has to be greater than n")
