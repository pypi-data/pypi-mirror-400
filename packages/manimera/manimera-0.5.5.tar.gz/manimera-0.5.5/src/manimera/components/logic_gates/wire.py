# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *

# THIRD PARTY IMPORTS ==================================================================================================

from manim import *

# MANIMERA IMPORTS =====================================================================================================

# <None>


# ======================================================================================================================
# WIRE CLASS
# ======================================================================================================================


class WIRE(VMobject):
    # def __init__(self, src_port, dst_port, color=DARK_GRAY, stroke_width=4, alpha=0.5, **kwargs):
    def __init__(self, src, dst, color=DARK_GRAY, stroke_width=4, alpha=0.5, **kwargs):
        super().__init__(**kwargs)

        self.src_port = src.get_output_port()
        self.dst_port, self.dst_port_index = dst.get_input_port()

        self.src_gate = src
        self.dst_gate = dst

        # Instance variables
        self.alpha = ValueTracker(alpha)
        self.signal_value = ValueTracker(self.src_gate._evaluate())
        self.stroke_width = stroke_width

        self.set_stroke(width=self.stroke_width, color=color)
        self.set_z_index(-1)
        self.update_path()

        self.add_updater(lambda w: w.update_path())

    def update_path(self):
        p0 = self.src_port.get_center()
        p1 = self.dst_port.get_center()

        # Read from cached output (all wires read from previous frame's values)
        cached_output = self.src_gate.output_value_cache.get_value()
        self.signal_value.set_value(cached_output)

        # Update cache for next frame (after reading)
        current_output = self.src_gate._evaluate()
        self.src_gate.output_value_cache.set_value(current_output)

        # Propagate to destination gate
        self.dst_gate.input_port_signal_values[self.dst_port_index].set_value(self.signal_value.get_value())

        self.set_stroke(width=self.stroke_width, color=interpolate(DARK_GRAY, YELLOW, self.signal_value.get_value()))

        mid_x = interpolate(p0[0], p1[0], self.alpha.get_value())

        self.set_points_as_corners(
            [
                p0,
                np.array([mid_x, p0[1], 0]),
                np.array([mid_x, p1[1], 0]),
                p1,
            ]
        )

    def set_signal_value(self, value):
        self.signal_value.set_value(value)

    def set_alpha(self, alpha):
        self.alpha.set_value(alpha)

    def set_stroke_width(self, stroke_width):
        self.stroke_width.set_value(stroke_width)


# ======================================================================================================================
# WIRE CLASS END
# ======================================================================================================================
