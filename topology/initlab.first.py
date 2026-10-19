'''
Very simple example of using Kathara for creating a network environment.
'''

from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara

# Create scenario
lab = Lab("Lab")

# Create example dictionary with device names and link as index
device_par = { "pc1" : "A", "pc2" : "A", "pc3": "A", "pc4" : "A"}

# Iterative cycle to create, connect and assign ip addresses to devices
count = 1
for d, n in device_par.items():
    lab.new_machine(d)
    lab.connect_machine_to_link(d, n)
    lab.create_file_from_list(
        [
            f"ip address add 193.10.11.{count}/24 dev eth0"
        ],
        f"pc{count}.startup"
    )
    count += 1

# Deploy lab
Kathara.get_instance().deploy_lab(lab)

