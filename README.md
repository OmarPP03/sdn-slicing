# Network Slicing in SDN

SDN Slicing project for Next Generation Networks course. A user requests a flow between two hosts with a given rate, then the program looks for a path where every link still has enough residual capacity: if it finds one, it reserves the capacity and install the OpenFlow rules along that path; if not, it rejects the request with an error.

The network is emulated with [Kathara](https://www.kathara.org/) via Docker containers: every switch is virtualized through Open vSwitch and are controlled by a Ryu controller.

The project has been developed with this configuration:

- 'Arch Linux' 7.2.9
- 'Python3' 3.14.8
- 'Kathara' 3.8.3
- 'Docker' 29.9.2
- 'Open vSwitch' 3.1.0 ('kathara/sdn' image)
- 'Ryu' 4.34 ('kathara/pox' image) 


# Demo topology

- 4 switches in a full mesh configuration, one host per switch
- Link capacities are expressed in Mbps: s1-s2 = 20, s1-s3 = 7, s1-s4 = 5, s2-s3 = 5, s2-s4 = 10, s3-s4 = 10. Host links are set to unlimited
- Every switch is connected to the Ryu controller via a separate management network

The topology can be modified via the 'topology/network.py' script:

- To add a host to a switch, simply add an entry to the 'HOSTS' dictionary, specifing name,  IP, MAC and connected switch
- To add a switch, add an entry to the 'SWITCHES' dictionary, specifing name, IP, and 'dpid' (used by OpenFlow to identify a switch). Also fill out the 'LINKS' dictionary with dedicated capacity for each link.

# Setup

To create the python virtual environment and install the needed dependencies execute on a Bash shell the following commands:

```bash
git clone <this-repository-url>
cd sdn-slicing
 
# Python dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
 
# Ryu controller image built from the Dockerfile in this repository
docker build -t kathara/ryu .
 
# Open vSwitch Linux kernel module 
sudo modprobe openvswitch
```

# Running the demo

```bash
./start.sh
```
'start.sh' removes any previous Kathara labs, builds and deploys the network ('topology/initlab.py'), waits until all switches are connected to the Ryu controller, and opens the CLI app ('app/main.py').



