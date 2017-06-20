#!/bin/bash

konsole -e python3 node.py endpoints 1 test.gv --c 3 &
konsole -e python3 node.py endpoints 2 test.gv --c 3 &
konsole -e python3 node.py endpoints 3 test.gv --c 3 &
konsole -e python3 node.py endpoints 4 test.gv --c 3 &
konsole -e python3 node.py endpoints 5 test.gv --c 3 &