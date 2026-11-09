
#FULL MESH network configuration with one switch per node

# Declare nodes with their name, ip, mac address and connected switch
HOSTS = {
    "pc1" : { "ip" : "10.0.3.1", "mac" : "02:00:00:00:00:01", "switch" : "s1"},
    "pc2" : { "ip" : "10.0.3.2", "mac" : "02:00:00:00:00:02", "switch" : "s2"},
    "pc3" : { "ip" : "10.0.3.3", "mac" : "02:00:00:00:00:03", "switch" : "s3"},
    "pc4" : { "ip" : "10.0.3.4", "mac" : "02:00:00:00:00:04", "switch" : "s4"},
    "pc5" : { "ip" : "10.0.3.5", "mac" : "02:00:00:00:00:05", "switch" : "s3"}
}

# Declare switches with their own ip and datapath_id (used to interact with OpenFlow REST API)
SWITCHES = {
    "s1" : { "ip" : "20.0.1.1", "dpid" : 1 },
    "s2" : { "ip" : "20.0.1.2", "dpid" : 2 },
    "s3" : { "ip" : "20.0.1.3", "dpid" : 3 },
    "s4" : { "ip" : "20.0.1.4", "dpid" : 4 }
}

# Declare links and capacity, used in initlab.py with the Linux tc command
LINKS = [
    ("s1", "s2", 20),
    ("s1", "s3", 7),
    ("s1", "s4", 5),
    ("s2", "s3", 5),
    ("s2", "s4", 10),
    ("s3", "s4", 10) 
]