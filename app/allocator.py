
from topology.network import HOSTS

# Use a class to keep the network state consistent with flow table changes, cookies, ecc..
class Allocator:
    
    def __init__(self, links):
                 
        self.flows = {}          # associate cookie with flow inserted. { 1 : {}}
        self.next_cookie = 1     # variable indicating n of flows inserted in this scenario
        self.graph = {}          # weighted network graph
        
        # Build the graph using dict instead of networkx to use our own allocation algorithm
        for sw1, sw2, cap in links:
            edge = {"capacity": cap, "residual": cap}
            self.graph.setdefault(sw1, {})[sw2] = edge
            self.graph.setdefault(sw2, {})[sw1] = edge
    
        
    # Check if src -> dst already exists as dst -> src in flows dict
    def check_path(self, src: str, dst: str) -> None:
        for cookie, f in self.flows.items():
            if {f["src"], f["dst"]} == {src, dst}:
                raise RuntimeError(f"A flow between {src} and {dst} already exists (cookie {cookie}). Delete it first.")

    # Request the path and save best path, subtracting capacities. Return path and cookie.
    def request(self, src : str, dst : str, rate : int ) -> tuple[list, int]:

        self.check_path(src, dst)
        
        src_switch = HOSTS[src]["switch"]
        dst_switch = HOSTS[dst]["switch"]

        path = find_path(self.graph, src_switch, dst_switch, rate)

        cookie = self.next_cookie
        
        for sw1, sw2 in zip(path, path[1:]):
            # bfr = self.graph[sw1][sw2]["residual"]
            self.graph[sw1][sw2]["residual"] -= rate 
            # print(f"{sw1} --> {sw2}: Capacity is now {self.graph[sw1][sw2]['residual']} from {bfr}.")

        full_path = [src] + path + [dst]
        self.flows[cookie] = {"src": src, "dst": dst, "rate": rate, "path": full_path}
    
        self.next_cookie += 1
        return full_path, cookie
    
    def release(self, cookie : int) -> dict:
        
        if cookie not in self.flows:
            raise RuntimeError("No flow associated with that cookie.")

        full_path = self.flows[cookie]["path"]
        path_list = full_path[1:-1]
        rate = self.flows[cookie]["rate"]

        print(f"\nEliminating flow {full_path} with rate {rate}.")
        for sw1, sw2 in zip(path_list, path_list[1:]):
            bfr = self.graph[sw1][sw2]["residual"]
            self.graph[sw1][sw2]["residual"] += rate
            print(f"{sw1} --> {sw2}: Capacity is now {str(self.graph[sw1][sw2]['residual'])} from {str(bfr)}.")

        return self.flows.pop(cookie)

    def to_string_flow(self, cookie: int):
        print(f"{self.flows[cookie]['path']}")



# Pseudo BFS. Uses src as sender hosts switch and dst as receiver hosts switch, host managign is left to request()
def find_path(graph: dict, src: str, dst: str, rate: int) -> list | None: 
    
    # Only source is visited
    visited = {src}
    # Create a queue for bfs starting from source 
    queue = []
    queue.append(src)

    # Keep a list of previous switches in the path, to build the src -> dst best path
    prev = {}

    while queue:
        s = queue.pop(0)

        # Found dst in best path, build the path and return it
        if s == dst:
            path = [dst]
            while path[-1] != src:
                path.append(prev[path[-1]])
            path.reverse()
            return path

        for i in graph[s]:
            if graph[s][i]["residual"] < rate or i in visited:
                continue
            else:
                prev[i] = s
                visited.add(i)
                queue.append(i)
    return None


from topology.network import LINKS

def main():
    a = Allocator(LINKS)
    a.request("pc1", "pc4", 10)
    a.release(1)
    a.request("pc4", "pc1", 10)

if __name__ == "__main__":
    main()