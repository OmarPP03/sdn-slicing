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

        print("### FOUND FEASIBLE PATH ! ALLOCATING TO NETWORK ###")

        # Error handling
        try:
            # POST requests may fail 
            add_flow(path, cookie=cookie)
        except Exception:
            # Delete partially installed rules 
            try:
                delete_flow(cookie)
            # In case Ryu is down
            except Exception:
                pass
            self.allocator.release(cookie)
            # Pass the error onto the caller
            raise

        print("### ALLOCATION TERMINATED SUCCESSFULLY!")

        return cookie

    def delete(self, cookie: int):

        print(f"### DELETING ROUTE ASSOCIATED WITH COOKIE NUMBER {cookie}:!")

        # First delete the rules on switches, so that if Ryu fails, capacity is not touched
        delete_flow(cookie)
        self.allocator.release(cookie)

        print("### DELETED ROUTE SUCCESFULLY! ###")

    def show(self) -> None:
        print("Active flows:")
        if not self.allocator.flows:
            print("  (none)")
        for cookie, f in self.allocator.flows.items():
            print(f"  [{cookie}] {f['src']} -> {f['dst']}  {f['rate']} Mbps  via {' -> '.join(f['path'])}")

        print("Links (residual / capacity):")
        for sw1, sw2, cap in LINKS:
            res = self.allocator.graph[sw1][sw2]["residual"]
            print(f"  {sw1}-{sw2}: {res:>3} / {cap} Mbps")

def run_cli(app: App):

    print("\nUsage: add [source_host] [dest_host] [rate_in_mbps] | delete [cookie] | show | quit ")

    while True:
        cmd = input(" > ").split()
        if not cmd:
            continue
        try:
            match cmd[0]:
                case "add":
                    cookie = app.add(cmd[1], cmd[2], int(cmd[3]))
                    print(f"Flow with cookie {cookie} added.")
                case "delete":
                    app.delete(int(cmd[1]))
                case "show":
                    app.show()
                case "exit":
                    break
                case _:
                    print("Command not recognized. Retry.")
        except RuntimeError as e:
            print(f"Error: {e}")
        except (IndexError,ValueError):
            print("Wrong arguments/order given.")
        except KeyError as e:
            print(f"Unknown host {e}")
        
def main():

    run_cli(App(LINKS))

    
if __name__ == "__main__":
    main()