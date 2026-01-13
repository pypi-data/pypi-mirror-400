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
# UNARY BASE CLASS
# ======================================================================================================================


class UnaryBase(BaseGate):
    def _create_gate(self) -> None:
        """
        Creates the Unary gate.
        """
        SHIFT_VAL = 3**0.5 / 2
        vobj = VMobject()

        vobj.start_new_path(UP * 0.5)
        vobj.add_line_to(DOWN * 0.5)
        vobj.add_line_to(RIGHT * SHIFT_VAL)
        vobj.add_line_to(UP * 0.5)
        vobj.close_path()

        vobj.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
        )

        # Input and Output Ports
        for i in range(self.input_ports_count):
            # Create Dot
            dot = Dot(radius=self.port_radius, color=self.stroke_color)
            dot.move_to(UP * interpolate(0.5, -0.5, (2 * i + 1) / (2 * self.input_ports_count)))

            # Add Dot to Input Ports
            self.input_ports.add(dot)

        # Create Output Port
        self.output_port = Dot(radius=self.port_radius, color=self.stroke_color).move_to(RIGHT * SHIFT_VAL)

        return vobj


# ==================================================================================================================
# UNARY BASE CLASS END
# ==================================================================================================================
