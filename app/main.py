from topology.network import LINKS
from app.allocator import Allocator
from ctr_iface.install_rules import add_flow, delete_flow, clear_all_tables


class App():
    
    def __init__(self, links):

        clear_all_tables()
        self.allocator = Allocator(links)

    def add(self, src: str, dst: str, rate: int) -> int:
        print(f"### ALLOCATING {rate} mbps ON ROUTE {src} to {dst} ###\n"
            "### SEARCHING FEASIBLE PATH ###")

        path, cookie = self.allocator.request(src, dst, rate)

        print(f"### FOUND FEASIBLE PATH {self.allocator.to_string_flow(cookie=cookie)}! ALLOCATING TO NETWORK ###")

        add_flow(path, cookie=cookie)

        print("### ALLOCATION TERMINATED SUCCESSFULLY!")

        return cookie

def main():

    
    a = App(LINKS)
    a.add("pc1", "pc4", 10)

    
if __name__ == "__main__":
    main()