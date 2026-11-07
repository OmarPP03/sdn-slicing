import json
import subprocess

import matplotlib.pyplot as plt

from topology.network import LINKS, HOSTS
from ctr_iface.install_rules import add_flow, delete_flow
from app.allocator import Allocator

MEASUREMENTS = [
    ("pc1", "pc4", 8),
    ("pc2", "pc4", 5),
    ("pc1", "pc3", 6),
    ("pc3", "pc4", 8),
    ("pc2", "pc3", 5),
    ("pc1", "pc2", 10)
]

# Run a command in the lab and return its output
def kathara_exec(host: str, *command: str) -> str:

    result = subprocess.run(["kathara", "exec", "-d", "lab", host, "--", *command],
                            capture_output=True, text=True)
    return result.stdout


def run_measurements(allocator: Allocator) -> list:
    # Return allocated and received mbps + loss
    results = []

    for src, dst, cap in MEASUREMENTS:
        
        # If path is not possible
        try:
            path, cookie = allocator.request(src, dst, cap)
        except RuntimeError as e:
            print(f"{src} -> {dst} ({cap} Mbps): REJECTED ({e})")
            results.append((0, 0.0, 0.0))
            continue

        # Try installing the rules if possible 
        try:
            add_flow(path, cookie=cookie)
        except Exception:
            try:
                delete_flow(cookie)
            except Exception:
                pass
            allocator.release(cookie)
            raise

        # iperf3 server on dst host
        kathara_exec(dst, "iperf3", "-s", "-1", "-D")
        # iperf3 server on src host
        output = kathara_exec(src, "iperf3", "-c", HOSTS[dst]["ip"], "-u",
                              "-b", f"{cap}M", "-t", "10", "-J")

        # iperf3 server output for the src host
        received = json.loads(output[output.index("{"):])["end"]["sum_received"]
        mbps, loss = received["bits_per_second"] / 1e6, received["lost_percent"]
        print(f"{src} -> {dst} ({cap} Mbps) via {' -> '.join(path)}: "
              f"received {mbps:.2f} Mbps, loss {loss:.1f}%")
        results.append((cap, mbps, loss))

    return results


def main():
    print("### RUNNING TEST WITH BFS + CAPACITY CONSTRAINT ROUTING")
    with_algo = run_measurements(Allocator(LINKS, with_app=True))      

    print("\n### RUNNING TEST WITHOUT ADMISSION CONTROL (ALWAYS YES)")
    without_algo = run_measurements(Allocator(LINKS, with_app=False))  

    # Build graph 
    for i, (src, dst, cap) in enumerate(MEASUREMENTS):
        plt.figure()
        plt.bar(["requested", "with admission", "always yes"],
                [cap, with_algo[i][1], without_algo[i][1]], color=["gray", "tab:blue", "tab:red"])
        plt.ylabel("Throughput (Mbps)")
        plt.title(f"Flow {i + 1}: {src} -> {dst}")
        plt.savefig(f"flow{i + 1}.png")
        plt.close()


if __name__ == "__main__":
    main()