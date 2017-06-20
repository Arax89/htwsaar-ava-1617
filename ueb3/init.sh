#!/usr/bin/env bash

konsole -e python3 lamportNode.py 1 4 &
sleep 1
konsole -e python3 lamportNode.py 2 4 &
sleep 1
konsole -e python3 lamportNode.py 3 4 &
sleep 1
konsole -e python3 lamportNode.py 4 4 &
