#!/usr/bin/env bash

konsole -e python3 lamport.py 1 4 &
konsole -e python3 lamport.py 2 4 &
konsole -e python3 lamport.py 3 4 &
konsole -e python3 lamport.py 4 4 &
