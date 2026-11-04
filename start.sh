#!/bin/bash
kathara wipe -f
source /home/omarp/Scrivania/NGN_project/SDN_slicing/.venv/bin/activate
python3 -m topology.initlab
