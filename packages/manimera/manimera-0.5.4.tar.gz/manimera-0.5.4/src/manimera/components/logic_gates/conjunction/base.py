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
# CONJUNCTION BASE CLASS
# ======================================================================================================================


class ConjunctionBase(BaseGate):
    def _create_gate(self) -> None:
        """
        Creates the conjunction gate.
        """
        vobj = VMobject()

        arc = Arc(start_angle=-PI / 2, angle=PI, radius=0.5, arc_center=RIGHT * 0.5, num_components=20)
        POINTS = 15
        vobj.start_new_path(UP * 0.5)

        for i in range(POINTS):
            vobj.add_line_to(DOWN * interpolate(-0.5, 0.5, (i + 1) / POINTS))

        for i in range(POINTS // 2):
            vobj.add_line_to(DOWN * 0.5 + RIGHT * interpolate(0, 0.5, (i + 1) / (POINTS // 2)))

        vobj.add_points_as_corners(arc.get_points())

        for i in range(POINTS // 2):
            vobj.add_line_to(UP * 0.5 + RIGHT * interpolate(0.5, 0, (i + 1) / (POINTS // 2)))

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
        self.output_port = Dot(radius=self.port_radius, color=self.stroke_color).move_to(RIGHT)

        # Return
        return vobj


# ==================================================================================================================
# CONJUNCTION BASE CLASS END
# ==================================================================================================================
