import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("source", help="The path to the resultfile", type=str)
parser.add_argument("target", help="The path to the targetfile", type=str)
args = parser.parse_args()
n = 0
m = 0
c = 0
believers = 0

with open(args.source, 'r') as f:
    for line in f:
        if line.startswith('N'):
            n = int(line.split(':')[1])
        elif line.startswith('M'):
            m = int(line.split(':')[1])
        elif line.startswith('C'):
            c = int(line.split(':')[1])
        elif line.strip() == '':
            pass
        else:
            believers += 1
print('N:', n, 'M:', m, 'C:', c, 'Believer:', believers)

if not os.path.exists(args.target):
    with open(args.target, 'w') as f:
        f.write('| N | M | C | # |\n')
        f.write('|---|---|---|---|\n')
with open(args.target, 'a+') as f:
    f.write('| ' + str(n) + ' | ' + str(m) + ' | ' + str(c) + ' | ' + str(believers) + ' |\n')
