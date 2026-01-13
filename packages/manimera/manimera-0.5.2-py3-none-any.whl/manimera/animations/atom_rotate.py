# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

# STANDARD IMPORTS =====================================================================================================

from typing import *

# THIRD PARTY IMPORTS ==================================================================================================

from manim import *

# MANIMERA IMPORTS =====================================================================================================

from manimera.components.bohr_atom import BohrAtom

# ======================================================================================================================
# ATOM ROTATE CLASS
# ======================================================================================================================


class AtomRotate(Animation):
    """
    Animation class for rotating a BohrAtom.
    """

    # INITIALIZATION ===================================================================================================

    def __init__(self, atom: BohrAtom, orbital_speed: float = 0.2, decay: float = 0.6, reverse: bool = False, **kwargs):
        """
        Initialize the AtomRotate animation.

        Args:
            atom (BohrAtom): The BohrAtom to rotate.
            orbital_speed (float): The orbital speed of the atom.
            decay (float): The decay of the atom.
            reverse (bool): Whether to rotate the atom in reverse.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(atom, **kwargs)

        # Instance variables
        self._orbital_speed = orbital_speed
        self._decay = decay
        self._reverse = reverse

        # Return
        return

    # UPDATE MOBJECT ===================================================================================================

    def update_mobjects(self, dt: float) -> None:
        """
        Update the mobjects.

        Args:
            dt (float): The time elapsed since the last frame.

        Returns:
            None

        Raises:
            None
        """

        # Get electrons
        electrons = self.mobject.electrons

        # Get number of shells
        num_shells = len(electrons)

        # Direction
        direction = -1 if self._reverse else 1

        # Rotate electrons
        for i, electron in enumerate(electrons):
            electron.rotate(
                direction * self._orbital_speed * TAU * dt * self._decay**i,
                about_point=self.mobject.nucleus.get_center(),
            )

        # Return
        return


# ======================================================================================================================
# ATOM ROTATE CLASS END
# ======================================================================================================================
