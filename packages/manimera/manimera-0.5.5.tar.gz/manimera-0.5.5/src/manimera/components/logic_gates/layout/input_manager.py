# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *

# THIRD PARTY IMPORTS ==================================================================================================

# <None>

# MANIMERA IMPORTS =====================================================================================================

from manimera.components.logic_gates.base import BaseGate

# ======================================================================================================================
# INPUT MANAGER LAYOUT CLASS
# ======================================================================================================================


class InputManager:
    def __init__(self, graph: List[Tuple[str, BaseGate, List[str]]]):
        # String Data
        self.nodes = []
        self.edges = []

        # String to Gate Instance Map
        self.instance_map = {}

        # Input Data
        self.graph = graph

        # Build
        self._build(self.graph)

    def _build(self, graph: List[Tuple[str, BaseGate, List[str]]]):
        for entry in graph:
            gate_type = entry[1]
            self.instance_map[entry[0]] = gate_type()
            self.nodes.append(entry[0])

            for output in entry[2]:
                self.edges.append((entry[0], output))

    def get_instance(self, node: str):
        return self.instance_map[node]

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_graph(self):
        return self.graph


# ======================================================================================================================
# INPUT MANAGER LAYOUT CLASS END
# ======================================================================================================================
