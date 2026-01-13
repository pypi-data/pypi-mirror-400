# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *

# THIRD PARTY IMPORTS ==================================================================================================

from manim import *

# MANIMERA IMPORTS =====================================================================================================

from manimera.components.logic_gates.base import BaseGate

# ======================================================================================================================
# VOID CLASS
# ======================================================================================================================


class VOID(BaseGate):
    def __init__(self, **kwargs):
        super().__init__(input_ports=1, negated=False)

    def _create_gate(self) -> None:
        """
        Creates the VOID gate.
        """
        dot = Dot(radius=self.port_radius, color=self.stroke_color)

        # Input and Output Ports
        self.input_ports.add(dot.copy())

        # Create Output Port
        self.output_port = dot.copy()

        return dot

    def _evaluate(self) -> float:
        """
        Abstract method to evaluate the gate.
        """
        return self.input_port_signal_values[0].get_value()

    def toggle(self, run=1):
        return Succession(
            self.input_port_signal_values[0].animate.set_value(1 - self.input_port_signal_values[0].get_value()),
            Wait(run / 2),
            run_time=run / 2,
        )


# ==================================================================================================================
# VOID CLASS END
# ==================================================================================================================
