
import json
import subprocess

import matplotlib.pyplot as plt

from topology.network import LINKS, HOSTS
from ctr_iface.install_rules import add_flow
from app.allocator import Allocator
from pathlib import Path

# Save matplot graphs in the /images directory
RESULTS_DIR = Path(__file__).resolve().parent.parent / "images"
RESULTS_DIR.mkdir(exist_ok=True)

# Declare scr_host and dst_host on which to perform measurments
SRC, DST = "pc1", "pc2"
# Requested rate for every measurment
RATES = [2, 4, 5, 6, 8, 10, 12]   
# Duration of measurment
DURATION = 5                     

# Function to define which kathara command to execute. 
def kathara_exec(host: str, *command: str) -> str:
    
    # The subprocess module allows to spawn processes and capture their outputs
    result = subprocess.run(["kathara", "exec", "-d", "lab", host, "--", *command],
                            capture_output=True, text=True)
    return result.stdout


def measure(rate: int, with_app: bool):
    
    # Initializing an allocator clears all flow tables in the network
    allocator = Allocator(LINKS, with_app=with_app)   
    try:
        path, cookie = allocator.request(SRC, DST, rate)
    except RuntimeError:
        # No route found with the requested rate
        return None
    add_flow(path, cookie=cookie)

    # Run a iperf3 server on the receiving host on port 5201. -s=server -d=daemon
    kathara_exec(DST, "iperf3", "-s", "-1", "-D")
    # Run a iperf3 client on the sender host. -u=udp -b=bitrate -t=test_duration -J=JSON output
    output = kathara_exec(SRC, "iperf3", "-c", HOSTS[DST]["ip"], "-u",
                          "-b", f"{rate}M", "-t", str(DURATION), "-J")
    # Save the JSON output of the test
    received = json.loads(output[output.index("{"):])["end"]["sum_received"]
    return path, received["bits_per_second"] / 1e6, received["lost_percent"]


def main():

    results = {True: [], False: []}   

    # Print the tests output in JSON format with added text formatting for a better terminal view
    for with_app, mode in ((True, "WITH ALGORITHM"), (False, "ALWAYS YES")):
        print(f"\n### {mode}: {SRC} -> {DST}")
        print(f"{'requested':>9}  {'received':>8}  {'loss %':>6}  path")
        for rate in RATES:
            result = measure(rate, with_app)
            if result is None:
                print(f"{rate:>9}  {'REJECTED':>8}")
                results[with_app].append(None)
            else:
                path, mbps, loss = result
                print(f"{rate:>9}  {mbps:>8.2f}  {loss:>6.1f}  {' -> '.join(path)}")
                results[with_app].append(mbps)


    # Create the plot and save it in the /images directory. Name of file is measurment_src_to_dst.png
    plt.figure(figsize=(7, 5))
    plt.plot(RATES, RATES, "--", color="gray", label="Requested")
    plt.plot(RATES, results[True], "o-", color="tab:blue", label="With admission algorithm")
    plt.plot(RATES, results[False], "s-", color="tab:red", label="Always yes")
    rejected = [r for r, v in zip(RATES, results[True]) if v is None]
    plt.plot(rejected, [0] * len(rejected), "x", color="tab:blue", markersize=10,
             label="Rejected (no route possible)")
    plt.xlabel("Requested rate (Mbps)")
    plt.ylabel("Received rate (Mbps)")
    plt.title(f"{SRC} -> {DST}: received vs requested")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.savefig( RESULTS_DIR / f"measurment_{SRC}_to_{DST}", dpi=120)
    print("\nSaved Graph in /images")


if __name__ == "__main__":
    main()