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
# ATOMIC CLOCK CLASS
# ======================================================================================================================


class AtomicClock(VGroup):
    """
    AtomicClock class.
    """

    # INITIALIZATION ===================================================================================================

    def __init__(self, side_length: int = 1, **kwargs):
        """
        Initialize the AtomicClock.

        Args:
            side_length: The side length of the atomic clock.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        # Instance variables
        self._side_length = side_length

        # Create Atomic Clock
        self._create_atomic_clock()

        # Return
        return

    # CREATE METHOD ====================================================================================================

    def _create_atomic_clock(self) -> None:
        """
        Create the atomic clock.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        # Create rods
        self._rods = self._create_rods()

        # Create internal body
        self._body = self._create_internal_body()

        # Create glow body
        self._glow_body = self._create_glow_body()

        # Add rods and internal body
        self.add(self._rods, self._body, self._glow_body)

        # Return
        return

    # INTERNAL METHODS =================================================================================================

    def _create_rods(self) -> VGroup:
        """
        Create the rods of the atomic clock.

        Args:
            None

        Returns:
            VGroup: The rods of the atomic clock.

        Raises:
            None
        """

        # Base disk for rods
        base_disk = Circle(radius=self._side_length * 1.5, stroke_width=0, color=YELLOW_A, fill_opacity=0.4)

        # Create base rectangle
        base_rect = Rectangle(
            height=self._side_length * 4.5,
            width=self._side_length * 0.8,
            fill_opacity=1,
            stroke_color=DARK_GRAY,
            stroke_width=4,
            color=interpolate_color(DARK_GRAY, BLACK, 0.3),
        )

        # Create rods
        rods = VGroup(base_disk, base_rect)

        for i in [-1, 1, 0]:
            rod = Rectangle(
                height=self._side_length / 3,
                width=self._side_length * 4,
                color=GREY if i == 0 else DARK_GRAY,
                stroke_width=0,
                fill_opacity=1,
            )
            rod.rotate(i * PI / 6)
            rods.add(rod)

        # Return
        return rods

    def _create_internal_body(self) -> VGroup:
        """
        Create the internal body of the atomic clock.

        Args:
            None

        Returns:
            VGroup: The internal body of the atomic clock.

        Raises:
            None
        """
        # Create square
        square = Square(side_length=self._side_length, color=GREY, fill_opacity=1)
        square.set_stroke(width=2, color=WHITE)

        # Create disk
        disk = Circle(radius=self._side_length * 0.4, fill_opacity=0)
        disk.set_stroke(width=15 * self._side_length, color=DARK_GRAY)

        bolts = VGroup()
        bolt_radius = self._side_length * 0.4  # Matches the disk radius

        for i in range(6):
            # 1. Create the hexagon shape
            bolt = RegularPolygon(n=6, color=WHITE, fill_opacity=1)
            bolt.set_stroke(width=0)
            bolt.scale_to_fit_width(self._side_length * 0.1)

            # 2. Calculate position: Angle * Radius
            angle = i * (TAU / 6)  # TAU is 2*PI
            position = np.array([np.cos(angle) * bolt_radius, np.sin(angle) * bolt_radius, 0])

            # 3. Move bolt to position relative to disk center
            bolt.move_to(disk.get_center() + position)
            bolts.add(bolt)

        # Return
        return VGroup(square, disk, bolts)

    def _create_glow_body(self) -> Circle:
        """
        Create the glow body of the atomic clock.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        glow_body = Circle(radius=self._side_length * 0.275, stroke_width=0, color=YELLOW, fill_opacity=1)
        return glow_body

    # REPRESENTATION ===================================================================================================

    def __str__(self) -> str:
        """Return a string representation of the atom."""
        return f"AtomicClock()"

    def __repr__(self) -> str:
        """Return a string representation of the atom."""
        return f"AtomicClock()"

    # PUBLIC METHODS =======================================================================================================

    def get_name(self) -> Text:
        """Return the name of the atom."""
        return Tex("Atomic Clock")

    # PROPERTIES =======================================================================================================

    @property
    def glow_body(self) -> Circle:
        return self._glow_body

    @property
    def body(self) -> VGroup:
        return self._body

    @property
    def rods(self) -> VGroup:
        return self._rods


# ======================================================================================================================
# ATOMIC CLOCK CLASS END
# ======================================================================================================================
