#!/usr/bin/env bash

konsole --hold -e python3 lamportMain.py 1 endpoints &
konsole --hold -e python3 lamportMain.py 2 endpoints &
konsole --hold -e python3 lamportMain.py 3 endpoints &
konsole --hold -e python3 lamportMain.py 4 endpoints &

