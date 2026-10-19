from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara


lab = Lab("Lab")

device_par = { "pc1" : "A", "pc2" : "A", "pc3": "A" }
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


Kathara.get_instance().deploy_lab(lab)

