import requests

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
    response = requests.post(f"{URL}", json=rule)
    if response.status_code != 200:
        raise RuntimeError(f"{dpid}: {response.status_code} {response.text}")


def main():
    match_pc1_to_s4 = {"in_port": 1, "eth_type": 2048, "ipv4_src": "10.0.3.1", "ipv4_dst": "10.0.3.4"}
    match_s4_to_pc4 = {"in_port": 2, "eth_type": 2048, "ipv4_src": "10.0.3.1", "ipv4_dst": "10.0.3.4"}
    match_pc4_to_s1 = {"in_port": 1, "eth_type": 2048, "ipv4_src": "10.0.3.4", "ipv4_dst": "10.0.3.1"}
    match_s1_to_pc1 = {"in_port": 4, "eth_type": 2048, "ipv4_src": "10.0.3.4", "ipv4_dst": "10.0.3.1"}
    add_rule(1, match_pc1_to_s4, 4, cookie=1)
    add_rule(4, match_s4_to_pc4, 1, cookie=1)
    add_rule(4, match_pc4_to_s1, 2, cookie=1)
    add_rule(1, match_s1_to_pc1, 1, cookie=1)


if __name__ == '__main__':
    main()