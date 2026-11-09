#!/bin/bash

# Stop at the first failed command
set -e

#Run from project root always
cd "$(dirname "$0")"

# Wipe all existing kathara instances
echo "### REMOVING OLD KATHARA INSTANCES ###" 
kathara wipe -f

echo "### ACTIVATING VIRTUAL ENVIRONMENT"
source .venv/bin/activate

echo "### BUILDING AND DEPLOYING THE LAB ###"
python3 -m topology.initlab

# Expected switches 
expected=$(python3 -c "from topology.network import SWITCHES; print(len(SWITCHES))")

echo "### WAITING FOR THE SWITCHES TO RESPOND ###"
waited=0
while true; do
    connected=$(curl -s http://localhost:8080/stats/switches | grep -o '[0-9]\+' | wc -l)
    if [ "$connected" -ge "$expected" ]; then
        echo "## ALL $expected SWITCHES CONNECTED AFTER ${waited}s"
        break
    fi
    sleep 1
    waited=$((waited + 1))
done
 
echo "### Starting the CLI"
exec python3 -m app.main "$@"


