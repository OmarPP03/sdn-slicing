from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara

from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent / "lab"
LAB_DIR.mkdir(exist_ok=True)

def create_scenario() -> Lab:

    # Create scenario
    lab = Lab(None, path=str(LAB_DIR))

    # Create user nodes: assign static ip, MAC, ARP table and create their collision domain with the switch.
    pc1 = lab.new_machine("pc1")
    lab.connect_machine_to_link(pc1.name, "X", mac_address="02:00:00:00:00:01")
    lab.create_file_from_list(
            [
                "ip address add 10.0.3.1/16 dev eth0",
                "ip neigh add 10.0.3.2 lladdr 02:00:00:00:00:02 dev eth0 nud permanent",
                "ip neigh add 10.0.3.3 lladdr 02:00:00:00:00:03 dev eth0 nud permanent",
                "ip neigh add 10.0.3.4 lladdr 02:00:00:00:00:04 dev eth0 nud permanent"
            ],
            "pc1.startup"
        )

    pc2 = lab.new_machine("pc2")
    lab.connect_machine_to_link(pc2.name, "Y", mac_address="02:00:00:00:00:02")
    lab.create_file_from_list(
            [
                "ip address add 10.0.3.2/16 dev eth0",
                "ip neigh add 10.0.3.1 lladdr 02:00:00:00:00:01 dev eth0 nud permanent",
                "ip neigh add 10.0.3.3 lladdr 02:00:00:00:00:03 dev eth0 nud permanent",
                "ip neigh add 10.0.3.4 lladdr 02:00:00:00:00:04 dev eth0 nud permanent"
            ],
            "pc2.startup"
        )

    pc3 = lab.new_machine("pc3")
    lab.connect_machine_to_link(pc3.name, "W", mac_address="02:00:00:00:00:03")
    lab.create_file_from_list(
            [
                "ip address add 10.0.3.3/16 dev eth0",
                "ip neigh add 10.0.3.1 lladdr 02:00:00:00:00:01 dev eth0 nud permanent",
                "ip neigh add 10.0.3.2 lladdr 02:00:00:00:00:02 dev eth0 nud permanent",
                "ip neigh add 10.0.3.4 lladdr 02:00:00:00:00:04 dev eth0 nud permanent"
            ],
            "pc3.startup"
        )

    pc4 = lab.new_machine("pc4")
    lab.connect_machine_to_link(pc4.name, "Z", mac_address="02:00:00:00:00:04")
    lab.create_file_from_list(
            [
                "ip address add 10.0.3.4/16 dev eth0",
                "ip neigh add 10.0.3.1 lladdr 02:00:00:00:00:01 dev eth0 nud permanent",
                "ip neigh add 10.0.3.2 lladdr 02:00:00:00:00:02 dev eth0 nud permanent",
                "ip neigh add 10.0.3.3 lladdr 02:00:00:00:00:03 dev eth0 nud permanent"
            ],
            "pc4.startup"
        )

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

    s2 = lab.new_machine("s2", image="kathara/sdn")
    lab.connect_machine_to_link(s2.name, "Y")   # eth0 is connected to pc2
    lab.connect_machine_to_link(s2.name, "B")   # eth1 is connected to s1
    lab.connect_machine_to_link(s2.name, "C")   # eth2 is connected to s3
    lab.connect_machine_to_link(s2.name, "F")   # eth3 is connected to s4
    lab.connect_machine_to_link(s2.name, "S") 
    lab.create_file_from_list(
        [
            "ip address add 20.0.1.2/24 dev eth4",
            "/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start",
            "ovs-vsctl add-br s2",
            "ovs-vsctl set-fail-mode s2 secure", 
            "ovs-vsctl add-port s2 eth0",
            "ovs-vsctl add-port s2 eth1",
            "ovs-vsctl add-port s2 eth2",
            "ovs-vsctl add-port s2 eth3",
            "tc qdisc add dev eth1 root tbf rate 20mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth2 root tbf rate 5mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth3 root tbf rate 10mbit burst 32kb latency 50ms",
            "ovs-vsctl set bridge s2 protocols=[OpenFlow13]",
            "ovs-vsctl set bridge s2 other-config:datapath-id=0000000000000002",
            "ovs-vsctl set-controller s2 tcp:20.0.1.100"
        ],
        "s2.startup"
    )

    s3 = lab.new_machine("s3", image="kathara/sdn")
    lab.connect_machine_to_link(s3.name, "W")   # eth0 is connected to pc3
    lab.connect_machine_to_link(s3.name, "E")   # eth1 is connected to s1
    lab.connect_machine_to_link(s3.name, "C")   # eth2 is connected to s2
    lab.connect_machine_to_link(s3.name, "D")   # eth3 is connected to s4
    lab.connect_machine_to_link(s3.name, "S") 
    lab.create_file_from_list(
        [
            "ip address add 20.0.1.3/24 dev eth4",
            "/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start",
            "ovs-vsctl add-br s3",
            "ovs-vsctl set-fail-mode s3 secure", 
            "ovs-vsctl add-port s3 eth0",
            "ovs-vsctl add-port s3 eth1",
            "ovs-vsctl add-port s3 eth2",
            "ovs-vsctl add-port s3 eth3",
            "tc qdisc add dev eth1 root tbf rate 7mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth2 root tbf rate 5mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth3 root tbf rate 10mbit burst 32kb latency 50ms",
            "ovs-vsctl set bridge s3 protocols=[OpenFlow13]",
            "ovs-vsctl set bridge s3 other-config:datapath-id=0000000000000003",
            "ovs-vsctl set-controller s3 tcp:20.0.1.100"
        ],
        "s3.startup"
    )

    s4 = lab.new_machine("s4", image="kathara/sdn")
    lab.connect_machine_to_link(s4.name, "Z")   # eth0 is connected to pc4
    lab.connect_machine_to_link(s4.name, "A")   # eth1 is connected to s1
    lab.connect_machine_to_link(s4.name, "F")   # eth2 is connected to s2
    lab.connect_machine_to_link(s4.name, "D")   # eth3 is connected to s3
    lab.connect_machine_to_link(s4.name, "S") 
    lab.create_file_from_list(
        [
            "ip address add 20.0.1.4/24 dev eth4",
            "/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start",
            "ovs-vsctl add-br s4",
            "ovs-vsctl set-fail-mode s4 secure", 
            "ovs-vsctl add-port s4 eth0",
            "ovs-vsctl add-port s4 eth1",
            "ovs-vsctl add-port s4 eth2",
            "ovs-vsctl add-port s4 eth3",
            "tc qdisc add dev eth1 root tbf rate 5mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth2 root tbf rate 10mbit burst 32kb latency 50ms",
            "tc qdisc add dev eth3 root tbf rate 10mbit burst 32kb latency 50ms",
            "ovs-vsctl set bridge s4 protocols=[OpenFlow13]",
            "ovs-vsctl set bridge s4 other-config:datapath-id=0000000000000004",
            "ovs-vsctl set-controller s4 tcp:20.0.1.100"
        ],
        "s4.startup"
    )


    # Create ryu controller. Its port connects to all other switches in the network
    ctr = lab.new_machine(
        "ctr",
        image="kathara/ryu",
        bridged=True,
        ports=["8080:8080/tcp"]
    )
    lab.connect_machine_to_link(ctr.name, "S")
    lab.create_file_from_list(
            [
                "ip address add 20.0.1.100/24 dev eth0",
                # Send ryu stderr to log for debugging
                "ryu-manager ryu.app.ofctl_rest > /var/log/ryu.log 2>&1 &"
            ],
            "ctr.startup"
        )

    # Declare wireshark device for packet sniffing on switches/controller collision domain
    wsh = lab.new_machine(
        "wsh", 
        image="lscr.io/linuxserver/wireshark",
        bridged=True,
        ports=["3000:3000/tcp"])
    lab.connect_machine_to_link(wsh.name, "S")

    return lab
    
# Deploy lab 
def deploy_scenario(lab: Lab) -> None:
    Kathara.get_instance().deploy_lab(lab=lab)
    print("Lab scenario created successfully!")

def main():
    deploy_scenario(create_scenario())

if __name__ == '__main__':
    main()