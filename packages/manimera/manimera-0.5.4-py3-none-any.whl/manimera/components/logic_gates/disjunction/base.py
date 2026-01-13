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
# DISJUNCTION BASE CLASS
# ======================================================================================================================


class DisjunctionBase(BaseGate):
    def __init__(self, exclusive: bool = False, **kwargs) -> None:
        self.exclusive = exclusive
        super().__init__(**kwargs)

    def _create_gate(self) -> None:
        """
        Creates the disjunction gate.
        """
        vobj = VMobject()

        arc = Arc(start_angle=PI / 6, angle=-PI / 3, radius=1, arc_center=LEFT * 3**0.5 / 2, num_components=20)
        exclusive_arc = None

        lower_arc = ArcBetweenPoints(DOWN * 0.5, RIGHT, angle=PI / 6, num_components=20)
        upper_arc = ArcBetweenPoints(RIGHT, UP * 0.5, angle=PI / 6, num_components=20)

        vobj.start_new_path(UP * 0.5)
        vobj.add_points_as_corners(arc.get_points())
        vobj.add_points_as_corners(lower_arc.get_points())
        vobj.add_points_as_corners(upper_arc.get_points())
        vobj.close_path()

        if self.exclusive:
            exclusive_arc = Arc(
                start_angle=-PI / 6, angle=PI / 3, radius=1, arc_center=LEFT * (3**0.5 / 2 + 0.2), num_components=20
            )
            vobj.add(exclusive_arc)

        vobj.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
        )

        # Input and Output Ports
        for i in range(self.input_ports_count):
            # Create Dot
            dot = Dot(radius=self.port_radius, color=self.stroke_color)
            # Move Dot
            factor = (2 * i + 1) / (2 * self.input_ports_count)

            if self.exclusive:
                dot.move_to(exclusive_arc.point_from_proportion(1 - factor))
            else:
                dot.move_to(arc.point_from_proportion(factor))

            # Add Dot to Input Ports
            self.input_ports.add(dot)

        # Create Output Port
        self.output_port = Dot(radius=self.port_radius, color=self.stroke_color).move_to(RIGHT)

        # Return
        return vobj


# ==================================================================================================================
# DISJUNCTION BASE CLASS END
# ==================================================================================================================
