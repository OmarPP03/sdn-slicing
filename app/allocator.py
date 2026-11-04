from ctr_iface.install_rules import add_flow

# Use a class to keep the network state consistent with flow table changes, cookies, ecc..
class Allocator:
    
    def __init__(self, links):
                 
        self.flows = {}             # associate cookie with flow inserted
        self.current_cookie = 1     # variable indicating n of flows inserted in this scenario
        self.graph = {}
        
        # Build the graph using dict instead of networkx to use our own allocation algorithm
        for sw1, sw2, cap in links:
            edge = {"capacity": cap, "residual": cap}
            self.graph.setdefault(sw1, {})[sw2] = edge
            self.graph.setdefault(sw2, {})[sw1] = edge
    
        
    # Use inverse Edmonds-Karp? https://en.wikipedia.org/wiki/Edmonds%E2%80%93Karp_algorithm
    def find_path(graph: dict, src: str, dst: str, rate: int) -> list | None: 
        
        return None
        
    # Request the path and save best path, subtracting capacities. Return path and cookie.
    def request(self, src : str, dst : str, rate : int ) -> tuple[list, int]:
        
        path = find_path(self.graph, src, dst, rate)
        if path == None:
            exit(0)
        reutrn path, 1
        # 1.  Allocation algorithm: decide best path and allocate path = [src, ..., dst];
        # 1.1 If no allocation possibile: throw exception
        # 2.  Remove capacities at links, current cookie += 1;
    def release(self, cookie : int):
        print(".")