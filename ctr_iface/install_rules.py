import requests
from topology.network import HOSTS, SWITCHES
from topology.initlab import get_ports

URL_ADD = "http://localhost:8080/stats/flowentry/add"
URL_DEL = "http://localhost:8080/stats/flowentry/delete"
URL_CLEAR = "http://localhost:8080/stats/flowentry/clear"
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
    response = requests.post(URL_ADD, json=rule)
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

        # print("Added " + "".join(path) + " flow with cookie " + str(cookie) + " succesfully.")


def delete_rule(dpid : int, cookie : int) -> None:

    rule = {
        "dpid": dpid,
        "cookie": cookie,
        "cookie_mask": 0xFFFFFFFFFFFFFFFF # Compare all 64 bits
    }
    response = requests.post(URL_DEL, json=rule)
    if response.status_code != 200:
        raise RuntimeError(f"{dpid}: {response.status_code} {response.text}")

def delete_flow(cookie : int) -> None:

    for switches in SWITCHES.values():
        delete_rule(switches["dpid"], cookie)

    print("Deleted path associated with " + str(cookie) + " cookie succesfully.")

def clear_flow_table(dpid: int) -> None:

    response = requests.delete(f"{URL_CLEAR}/{dpid}", timeout=5)
    if response.status_code != 200:
        raise RuntimeError(f"Could not clear flow table of switch {dpid}: {response.status_code} {response.text}")

# Probably not its place
def clear_all_tables() -> None:

    for i in SWITCHES.values():
        clear_flow_table(i["dpid"])


def main():
    path1 = ["pc1", "s1", "s4", "pc4"]
    path2 = ["pc2", "s2", "s3", "pc3"]
    add_flow(path1, 1)
    add_flow(path2, 2)
    delete_flow(1)
    delete_flow(2)

if __name__ == '__main__':
    main()