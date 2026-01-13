# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *
from abc import ABC, abstractmethod

# THIRD PARTY IMPORTS ==================================================================================================

from manim import *

# MANIMERA IMPORTS =====================================================================================================

# <None>

# ======================================================================================================================
# BASE GATE CLASS
# ======================================================================================================================


class BaseGate(VGroup, ABC):
    """
    BaseGate class.
    """

    # INITIALIZATION ===================================================================================================

    def __init__(self, input_ports: int = 2, negated: bool = False, port_radius: float = 0, **kwargs):
        """
        Initialize the BaseGate.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        # Negation
        self.negation = negated

        # Ports
        self.port_radius = port_radius

        # Port Counts
        self.input_ports_count = input_ports
        self.output_ports_count = 1

        # Port Position Tracker
        self.input_ports: VGroup[Dot] = VGroup()
        self.output_ports: VGroup[Dot] = VGroup()
        self.output_port: Dot = None

        # Instance variables
        self.gate = self._create_gate()

        # Negate Output
        self._negate_output()

        # Move to origin
        self.add(self.gate, self.input_ports, self.output_ports)
        self.move_to(ORIGIN)

        # Return
        return

    # INTERNAL METHODS =================================================================================================

    @abstractmethod
    def _create_gate(self) -> None:
        """
        Abstract method to create the gate.
        """
        ...

    # PRIVATE METHODS ==================================================================================================

    def _negate_output(self, offset: float = 0.02) -> None:
        """
        Negates the gate.
        """
        if not self.negation:
            return

        if self.output_port is not None:
            circle = Circle(radius=0.1, stroke_color=self.stroke_color, stroke_width=self.stroke_width)
            circle.next_to(self.output_port, RIGHT, aligned_edge=LEFT, buff=offset)
            self.add(circle)
            self.output_port.next_to(circle, RIGHT, aligned_edge=RIGHT, buff=0)
        else:
            raise ValueError("Gate has no output ports.")

        return

    # GETTERS ==========================================================================================================

    def get_input_port_position(self, index: int) -> tuple[float, float, float]:
        """
        Returns the input port at the given index.
        """
        return self.input_ports[index].get_center()

    def get_output_port_position(self) -> tuple[float, float, float]:
        """
        Returns the output port.
        """
        return self.output_port.get_center()


# ======================================================================================================================
# BASE GATE CLASS END
# ======================================================================================================================
