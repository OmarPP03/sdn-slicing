SDN_IMAGE = "kathara/sdn"
RYU_IMAGE = "kathara/ryu"
WSH_IMAGE = "lscr.io/linuxserver/wireshark"

CTR_LINK = "S"
CTR_IP = "20.0.1.100"
OF_VERSION = "OpenFlow13"

HOST_PREFIX = "/16"
SWITCH_PREFIX = "/24"

TC_BURST = "32kb"
TC_LATENCY = "50ms"

HOSTS = {
    "pc1" : { "ip" : "10.0.3.1", "mac" : "02:00:00:00:00:01", "switch" : "s1"},
    "pc2" : { "ip" : "10.0.3.2", "mac" : "02:00:00:00:00:02", "switch" : "s2"},
    "pc3" : { "ip" : "10.0.3.3", "mac" : "02:00:00:00:00:03", "switch" : "s3"},
    "pc4" : { "ip" : "10.0.3.4", "mac" : "02:00:00:00:00:04", "switch" : "s4"}
}

SWITCHES = {
    "s1" : { "ip" : "20.0.1.1", "dpid" : 1 },
    "s2" : { "ip" : "20.0.1.2", "dpid" : 2 },
    "s3" : { "ip" : "20.0.1.3", "dpid" : 3 },
    "s4" : { "ip" : "20.0.1.4", "dpid" : 4 }
}

LINKS = [
    ("s1", "s2", 20),
    ("s1", "s3", 7),
    ("s1", "s4", 5),
    ("s2", "s3", 5),
    ("s2", "s4", 10),
    ("s3", "s4", 10) 
]