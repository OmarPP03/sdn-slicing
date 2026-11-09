from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara

from pathlib import Path

from topology.network import SWITCHES, HOSTS, LINKS

# Docker images
HOST_IMAGE = "kathara/base"
SDN_IMAGE = "kathara/sdn"
RYU_IMAGE = "kathara/ryu"
WSH_IMAGE = "lscr.io/linuxserver/wireshark"

# Controller variables
CTR_LINK = "S"
CTR_IP = "20.0.1.100"
OF_VERSION = "OpenFlow13"

# Devices prefix 
HOST_PREFIX = "/16"
SWITCH_PREFIX = "/24"

# tc configuration 
TC_BURST = "32kb"
TC_LATENCY = "50ms"

# Path for lab directory (.startup files)
LAB_DIR = Path(__file__).resolve().parent.parent / "lab"
LAB_DIR.mkdir(exist_ok=True)

# Create the Lab object and port map
def create_scenario() -> Lab:

    # Create scenario
    lab = Lab(None, path=str(LAB_DIR))

    # ports[switch][neighbour_switch] = OpenFlow port number
    ports = {sw: {} for sw in SWITCHES}
    # tc[switch] = tc commands for each switch neighbour
    tc = {sw: [] for sw in SWITCHES}

    # Declare switches
    for sw in SWITCHES:
        # Populate network with SDN switches with their kathara image
        lab.new_machine(sw, image=SDN_IMAGE)


    # Create user nodes: assign static ip, MAC, ARP table and create their collision domain with the switch.
    for h, i in HOSTS.items():
        # Populate network with normal hosts, kathara/base image
        lab.new_machine(h, image=HOST_IMAGE)

        # Connect host and switch to the same link in eth0
        link = f"{h}-{i['switch']}"
        lab.connect_machine_to_link(h, link, mac_address=i['mac'])
        # connect_machine_to_link returns the interface on the second argument of the returning tuple
        _, ethface = lab.connect_machine_to_link(i['switch'], link)
        ports[i['switch']][h] = ethface.num + 1  # Linux interface = eth0, while OpenFlow interface is 1

        # Write the startup file for every host, ARP tables
        startup =  [f"ip address add {i['ip']}{HOST_PREFIX} dev eth0"]
        for h_other, i_other in HOSTS.items():
            if h_other != h:
                startup.append(f"ip neigh add {i_other['ip']} lladdr {i_other['mac']} dev eth0 nud permanent")
        lab.create_file_from_list(startup, f"{h}.startup")
    
    """ Static version

    pc1 = lab.new_machine("pc1")
    lab.connect_machine_to_link(pc1.name, "X", mac_address="02:00:00:00:00:01")
    lab.create_file_from_list(
            [
                "ip address add 10.0.3.1/16 dev eth0",

                # Write static ARP table 
                "ip neigh add 10.0.3.2 lladdr 02:00:00:00:00:02 dev eth0 nud permanent",
                "ip neigh add 10.0.3.3 lladdr 02:00:00:00:00:03 dev eth0 nud permanent",
                "ip neigh add 10.0.3.4 lladdr 02:00:00:00:00:04 dev eth0 nud permanent"
            ],
            "pc1.startup"
        )

    ecc...

    """

    # Switch to switch collision domains and tc entiers for every switch
    for sw1, sw2, cap in LINKS:
        for firstsw, secondsw in ((sw1, sw2), (sw2, sw1)):
            _, ethface = lab.connect_machine_to_link(firstsw, f"{sw1}-{sw2}")
            ports[firstsw][secondsw] = ethface.num + 1
            tc[firstsw].append(f"tc qdisc add dev eth{ethface.num} root tbf rate {cap}mbit burst {TC_BURST} latency {TC_LATENCY}")
        

    # Swtich configuaration
    for sw, i in SWITCHES.items():
        _, ctrlink = lab.connect_machine_to_link(sw, CTR_LINK)
        # Static switch entries, self_ip assign, install OpenFlow protocol
        startup = [
            f"ip address add {i['ip']}{SWITCH_PREFIX} dev eth{ctrlink.num}",
            "/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start",
            f"ovs-vsctl add-br {sw}",
            f"ovs-vsctl set-fail-mode {sw} secure",
        ]

        # Set up collision domains, datapath-id for OF, connect to Ryu controller
        for port in (ports[sw].values()):
            startup.append(f"ovs-vsctl add-port {sw} eth{port - 1}")
        startup += tc[sw]
        startup.append(f"ovs-vsctl set bridge {sw} protocols=[{OF_VERSION}]")
        # :016x = hex padded with zero to get to 16 digits
        startup.append(f"ovs-vsctl set bridge {sw} other-config:datapath-id={i['dpid']:016x}")
        startup.append(f"ovs-vsctl set-controller {sw} tcp:{CTR_IP}")
        lab.create_file_from_list(startup, f"{sw}.startup")


    """ Static version

    # Create switches and connect them to their device interface and between them. 
    # From eth0 to eth(X-1) we get the data links, ethX is the interface for the Ryu controller
    s1 = lab.new_machine("s1", image="kathara/sdn") 
    lab.connect_machine_to_link(s1.name, "X")   # eth0 is connected to pc1
    lab.connect_machine_to_link(s1.name, "B")   # eth1 is connected to s2
    lab.connect_machine_to_link(s1.name, "E")   # eth2 is connected to s3
    lab.connect_machine_to_link(s1.name, "A")   # eth3 is connected to s4
    # eth4 is the link to the Ryu controller, same for all the switches
    lab.connect_machine_to_link(s1.name, "S")   
    lab.create_file_from_list(
        [
            "ip address add 20.0.1.1/24 dev eth4",
            "/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start",
            "ovs-vsctl add-br s1",
            # Fail mode: what if i dont find a controller?
            # default: learn and install flows automatically (normal switch)
            # secure: # do not learn or install flows if there is no controller
            "ovs-vsctl set-fail-mode s1 secure", 
            "ovs-vsctl add-port s1 eth0",
            "ovs-vsctl add-port s1 eth1",
            "ovs-vsctl add-port s1 eth2",
            "ovs-vsctl add-port s1 eth3",
            # Add link capacities to each interface, after ovs takes over (otherwise ovs will remove them)
            "tc qdisc add dev eth1 root tbf rate 20mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth2 root tbf rate 7mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth3 root tbf rate 5mbit burst 32kb latency 50ms",
            "ovs-vsctl set bridge s1 protocols=[OpenFlow13]",
            # Add datapath id to each switch, so the controller assigns "1 -> s1, 2 -> s2, ecc...". Must be 16 hexadecimal digits.abs
            "ovs-vsctl set bridge s1 other-config:datapath-id=0000000000000001",
            "ovs-vsctl set-controller s1 tcp:20.0.1.100"
        ],
        "s1.startup"
    )

    """


    # Create ryu controller. Its port connects to all other switches in the network
    ctr = lab.new_machine(
        "ctr",
        image=RYU_IMAGE,
        bridged=True,
        ports=["8080:8080/tcp"]
    )
    lab.connect_machine_to_link(ctr.name, f"{CTR_LINK}")
    lab.create_file_from_list(
            [
                f"ip address add {CTR_IP}{SWITCH_PREFIX} dev eth0",
                # Use ryu.app.ofctl_rest to use the OF REST API. Send ryu stderr to log for debugging
                "ryu-manager ryu.app.ofctl_rest > /var/log/ryu.log 2>&1 &"
            ],
            "ctr.startup"
        )

    # Declare wireshark device for packet sniffing on switches/controller collision domain
    wsh = lab.new_machine(
        "wsh", 
        image=WSH_IMAGE,
        bridged=True,
        ports=["3000:3000/tcp"])
    lab.connect_machine_to_link(wsh.name, f"{CTR_LINK}")

    return lab
    
# Used by add_flow() in install_rules.py to get the port map in the whole network
def get_ports() -> dict:
    ports = {sw: {} for sw in SWITCHES}
    # First the host ports. If for 1 switch = 1 host, then it will always be port one.
    for hosts, i in HOSTS.items():
        switch = i["switch"]
        # len(ports[sw]) + 1 is the next free port on that switch
        ports[switch][hosts] = len(ports[switch]) + 1
    for sw1, sw2, cap in LINKS:
        ports[sw1][sw2] = len(ports[sw1]) + 1
        ports[sw2][sw1] = len(ports[sw2]) + 1
    return ports

# Deploy lab 
def deploy_scenario(lab: Lab) -> None:
    Kathara.get_instance().deploy_lab(lab=lab)
    # print("Lab scenario created successfully!")


def main():
    lab = create_scenario()
    deploy_scenario(lab)

if __name__ == '__main__':
    main()