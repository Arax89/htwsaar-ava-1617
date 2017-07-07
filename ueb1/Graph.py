import sys


class Graph:
    path = None
    nodes = set()
    edges = []

    def __init__(self, path):
        self.path = path
        self.parse_graph()

    def parse_graph(self):
        f = open(self.path, 'r')

        for line in f:
            if '{' not in line and '}' not in line:
                try:
                    l = line.replace(";", "")
                    l = l.split("--")
                    left = int(l[0].strip())
                    right = int(l[1].strip())
                    edge = (left, right)
                    self.edges.append(edge)
                    self.nodes.add(left)
                    self.nodes.add(right)
                except (ValueError, SyntaxError, IndexError) as err:
                    print("Couldn't read graphfile", file=sys.stderr)
                    exit(err)
        f.close()

    def id_in_set(self, nid):
        if nid in self.nodes:
            return True
        else:
            return False

    def find_neighbours(self,nid):
        neighbours = set()
        for edge in self.edges:
            if nid in edge:
                if edge[0] == nid:
                    neighbours.add(edge[1])
                else:
                    neighbours.add(edge[0])
        return neighbours

    def count_nodes(self):
        return len(self.nodes)

    def count_edges(self):
        return len(self.edges)

