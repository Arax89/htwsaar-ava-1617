#!/usr/bin/env bash

konsole -e python3 lamportTest.py 1 4 &
konsole -e python3 lamportTest.py 2 4 &
konsole -e python3 lamportTest.py 3 4 &
konsole -e python3 lamportTest.py 4 4 &
