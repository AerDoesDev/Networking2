"""
networking 2 ripng distance-vector mini-simulation work

has a periodic table exchange (one "tick" = 30 s in real life)
-hop-count increment
-infinity rule (metric 16 = unreachable)
-link-failure demo test after tick 5 currently
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

# maximum hop count before a route is considered unreachable
INFINITY = 16
# number of simulation iterations
MAX_TICKS = 10

@dataclass
class Route:
    gateway: str    # the next hop router to reach destination
    cost: int       # numberr of hops to the destination
@dataclass
class Router:
    identifier: str                                     # router name/id
    route_cache: Dict[str, Route] = field(default_factory=dict)  # routing table
    neighbours: List["Router"] = field(default_factory=list)     # adjacent routers

    def __post_init__(self) -> None:
        # add the route to self (0 cost, no gateway needed)
        self.route_cache[self.identifier] = Route("-", 0)

    def broadcast_routes(self) -> None:
        # send routing information to each connected router
        for peer in self.neighbours:
            peer.receive_update(self.identifier, self.route_cache)

    def receive_update(self, advertiser: str, foreign_routes: Dict[str, Route]) -> None:
        # check each destination in the received routing table
        for destination, path_info in foreign_routes.items():
            # add 1 to cost (one more hop), but cap at INFINITY
            augmented_cost = min(path_info.cost + 1, INFINITY)

            # if this is a new route or better than existing one, update our table
            if destination not in self.route_cache or augmented_cost < self.route_cache[destination].cost: self.route_cache[destination] = Route(advertiser, augmented_cost)

    def dump(self) -> str:
        # format the routing table for console display
        heading = f"Routing table for {self.identifier}"
        output = [heading, "-" * len(heading), "Dest   Gateway  Cost"]
        for dest, path_info in sorted(self.route_cache.items()):
            output.append(f"{dest:<6} {path_info.gateway:<8} {path_info.cost:>6}")
        return "\n".join(output) + "\n"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Router):
            return NotImplemented
        return self.route_cache == other.route_cache

def construct_network() -> List[Router]:
    # create three routers
    node1, node2, node3 = Router("R1"), Router("R2"), Router("R3")
    # connect them in a triangle sim topology
    node1.neighbours = [node2, node3]
    node2.neighbours = [node1, node3]
    node3.neighbours = [node1, node2]
    return [node1, node2, node3]

def run_simulation() -> None:
    # build the initial network topology
    network = construct_network()
    # keep track of previous state to detect convergence
    previous_state = [None, None, None]  

    # run through each simulation tick
    for tick in range(1, MAX_TICKS + 1):
        print(f"\n===== Tick {tick} =====")

        # simulate a link failure at tick 5
        if tick == 5:
            print("[Test] Link Rw-R3 has failed")
            node1, node2, node3 = network
            # remove the direct connection between r1 and r3
            node1.neighbours.remove(node3)
            node3.neighbours.remove(node1)

        # exchange routing tables between neighbours
        for node in network:
            node.broadcast_routes()

        # display current routing tables
        for node in network:
            print(node.dump())

        # check if the network has converged (no changes since last tick)
        if all(prev == current for prev, current in zip(previous_state, network)) and tick > 5:
            print(f"Network converged after {tick} ticks.")
            break
        # store current state for next iteration's comparison
        previous_state = [Router(node.identifier, dict(node.route_cache)) for node in network]  


if __name__ == "__main__":
    run_simulation()
