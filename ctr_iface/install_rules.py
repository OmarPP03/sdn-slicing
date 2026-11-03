import requests
from topology.network import HOSTS, SWITCHES
from topology.initlab import get_ports

URL = "http://localhost:8080/stats/flowentry/add"
DEF_PRIORITY = 100
IDLE_TIMEOUT = 0
HARD_TIMEOUT = 0
ETH_TYPE = 2048

def add_rule(dpid : int, match : dict, out_port : int, cookie : int) -> None:

    rule = {
        "dpid": dpid,
        "cookie": cookie,
        "priority": DEF_PRIORITY,
        "idle_timeout": IDLE_TIMEOUT,
        "hard_timeout": HARD_TIMEOUT,
        "match": match,
        "actions": [{"type": "OUTPUT", "port": out_port}],      
        }
    response = requests.post(URL, json=rule)
    if response.status_code != 200:
        raise RuntimeError(f"{dpid}: {response.status_code} {response.text}")

def add_flow(path : list, cookie : int) -> None:

    # Retrive ports list
    ports = get_ports()

    # path = [src_host, switch, ..., switch, dst_host]
    src, dst = path[0], path[-1]
    src_ip, dst_ip = HOSTS[src]["ip"], HOSTS[dst]["ip"]

    for i in range(1, len(path) - 1):
        curr, nxt, prev = path[i], path[i+1], path[i-1]
        # source to dest path
        add_rule(SWITCHES[curr]["dpid"], {
            "in_port": ports[curr][prev],
            "eth_type": ETH_TYPE,
            "ipv4_src": src_ip,
            "ipv4_dst": dst_ip
        }, ports[curr][nxt], cookie)
        # dest to source path
        add_rule(SWITCHES[curr]["dpid"], {
            "in_port": ports[curr][nxt],
            "eth_type": ETH_TYPE,
            "ipv4_src": dst_ip,
            "ipv4_dst": src_ip
        }, ports[curr][prev], cookie)



def main():
    path = ["pc1", "s1", "s4", "pc4"]
    add_flow(path, 1)

if __name__ == '__main__':
    main()