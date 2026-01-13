# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *

# THIRD PARTY IMPORTS ==================================================================================================

from manim import *

# MANIMERA IMPORTS =====================================================================================================

from manimera.components.logic_gates.base import BaseGate
from manimera.components.logic_gates.layout.input_manager import InputManager
from manimera.components.logic_gates.wire import WIRE

# ======================================================================================================================
# SUGIYAMA LAYOUT CLASS
# ======================================================================================================================


class SugiyamaLayout:
    def __init__(self, graph: List[Tuple[str, BaseGate, List[str]]]):
        self.input_manager = InputManager(graph)
        self.nodes = self.input_manager.get_nodes()
        self.edges = self.input_manager.get_edges()

        # Results of decycling
        self.acyclic_edges = []
        self.reversed_edges = set()  # Store which ones we flipped to fix later

        self._decycle()
        self._assign_layers()
        self._normalize()
        self._reduce_crossings()
        print(self.normalized_edges)

    def _decycle(self):
        visited = set()  # Fully processed nodes
        visiting = set()  # Nodes in the current recursion stack

        # 1. Create adjacency list for easy traversal
        adj = {node: [] for node in self.nodes}
        for u, v in self.edges:
            adj[u].append(v)

        def dfs(u):
            visiting.add(u)
            for v in adj[u]:
                if v in visiting:
                    # Found a back-edge (Cycle)!
                    # Reverse it for the layout math
                    self.acyclic_edges.append((v, u))
                    self.reversed_edges.add((v, u))
                elif v not in visited:
                    self.acyclic_edges.append((u, v))
                    dfs(v)
                else:
                    # Edge to an already processed node (Forward/Cross edge)
                    self.acyclic_edges.append((u, v))

            visiting.remove(u)
            visited.add(u)

        # Start DFS from all nodes to cover disconnected components
        for node in self.nodes:
            if node not in visited:
                dfs(node)

    def _assign_layers(self):
        # Initialize ranks
        ranks = {node: 0 for node in self.nodes}

        # We use the acyclic edges generated in Step 1
        # We repeat the process until ranks stabilize (Max iterations = num_nodes)
        for _ in range(len(self.nodes)):
            changed = False
            for u, v in self.acyclic_edges:
                # If rank of destination is not at least 1 greater than source
                if ranks[v] <= ranks[u]:
                    ranks[v] = ranks[u] + 1
                    changed = True
            if not changed:
                break

        max_rank = max(ranks.values())
        ranks = {node: max_rank - r for node, r in ranks.items()}

        # Group nodes by their rank for easy access
        self.layers = {}
        for node, r in ranks.items():
            if r not in self.layers:
                self.layers[r] = []
            self.layers[r].append(node)

        self.ranks = ranks

    def _normalize(self):
        """
        Inserts dummy VOID nodes for edges that span multiple layers.
        Updates self.instance_map and creates a localized adjacency list.
        """
        self.final_layers = {r: list(nodes) for r, nodes in self.layers.items()}
        self.normalized_edges = []

        # We use a copy of edges because we might "split" them
        for u, v in self.acyclic_edges:
            u_rank = self.ranks[u]
            v_rank = self.ranks[v]
            span = v_rank - u_rank

            if span > 1:
                # Long edge detected: u -> [dummy1] -> [dummy2] -> v
                previous_node = u
                for i in range(1, span):
                    dummy_layer = u_rank + i
                    dummy_name = f"DUMMY_{u}_{v}_{dummy_layer}"

                    # 1. Create the VOID instance via your InputManager logic
                    # (Assuming VOID() is a valid constructor in your setup)
                    from manimera.components.logic_gates.base import VOID

                    self.input_manager.instance_map[dummy_name] = VOID()

                    # 2. Add to our layout tracking
                    if dummy_name not in self.ranks:
                        self.ranks[dummy_name] = dummy_layer
                        self.final_layers[dummy_layer].append(dummy_name)

                    # 3. Create the segment
                    self.normalized_edges.append((previous_node, dummy_name))
                    previous_node = dummy_name

                # Final segment to the actual destination
                self.normalized_edges.append((previous_node, v))
            else:
                # Standard edge: Layer n to n+1
                self.normalized_edges.append((u, v))

    def _reduce_crossings(self):
        """
        Orders nodes within each layer to minimize edge crossings
        using the Barycenter heuristic.
        """
        # 1. Initialize an order based on the initial parsing
        # self.final_layers is a dict: {layer_index: [node_names]}
        num_layers = max(self.final_layers.keys()) + 1

        # We create a mapping of node -> vertical_position
        # Initial vertical positions are just the index in the list
        v_pos = {node: i for layer in self.final_layers.values() for i, node in enumerate(layer)}

        # 2. Perform a forward sweep (Left to Right)
        for l in range(1, num_layers):
            current_layer = self.final_layers[l]

            # Calculate Barycenter for each node in current_layer
            barycenters = {}
            for node in current_layer:
                # Find all nodes in (l-1) that connect TO this node
                predecessors = [u for u, v in self.normalized_edges if v == node]

                if predecessors:
                    # Average of the vertical positions of all predecessors
                    avg = sum(v_pos[p] for p in predecessors) / len(predecessors)
                    barycenters[node] = avg
                else:
                    # If no predecessors (e.g., an input in a later layer), keep current pos
                    barycenters[node] = v_pos[node]

            # 3. Sort the current layer based on calculated barycenters
            current_layer.sort(key=lambda n: barycenters[n])

            # 4. Update vertical positions after sorting
            for i, node in enumerate(current_layer):
                v_pos[node] = i

    def _assign_final_positions(self, x_spacing=3.0, y_spacing=2.0):
        """
        Translates ranks and sorted orders into Manim coordinates.
        """
        grp = VGroup()
        for layer_idx, nodes in self.final_layers.items():
            for v_idx, node_name in enumerate(nodes):
                # Calculate X (Column)
                x = layer_idx * x_spacing

                # Calculate Y (Vertical centering)
                # Center the layer around Y=0
                layer_height = (len(nodes) - 1) * y_spacing
                y = (v_idx * y_spacing) - (layer_height / 2)

                # Move the actual Manim instance
                instance = self.input_manager.get_instance(node_name)
                instance.move_to([x, y, 0])
                grp.add(instance)
        grp.move_to(ORIGIN)

        return grp

    def get_layout(self, x_spacing=3.0, y_spacing=2.0):
        return self._assign_final_positions(x_spacing, y_spacing)

    def build_wires(self):
        """
        Creates WIRE objects for all normalized edges.
        Uses normalized_edges so all edges span exactly one layer.
        """
        wires = VGroup()

        seen = set()

        for u, v in self.normalized_edges:
            if u in seen:
                print(f"Found {u} -> {v}")
                seen.add(v)
            src = self.input_manager.get_instance(u)
            dst = self.input_manager.get_instance(v)

            wire = WIRE(src, dst)
            wires.add(wire)

        self.wires = wires
        return wires


# ======================================================================================================================
# SUGIYAMA LAYOUT CLASS END
# ======================================================================================================================
