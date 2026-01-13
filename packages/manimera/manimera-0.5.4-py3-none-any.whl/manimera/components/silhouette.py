# ============================================================
# IMPORTS
# ============================================================

# Import all Manim primitives (VGroup, Dot, ORIGIN, etc.)
from manim import *

# Literal is used to restrict valid string values
# for parameters like `cover_area`
from typing import Literal

# Pillow is used to load and process image files
from PIL import Image

# NumPy is used for numerical operations and randomness
import numpy as np


# ============================================================
# Silhouette CLASS
# ============================================================


class Silhouette(VGroup):
    """
    A Manim VGroup that generates a silhouette made of dots
    sampled from an image.

    The image is converted to grayscale, and dots are randomly
    placed over either the dark or light regions of the image.
    The dots can optionally be shuffled to randomize animation
    order.
    """

    def __init__(
        self,
        image_path,
        dot_radius=0.03,
        dot_color=WHITE,
        dot_shuffle=True,
        target_height=6,
        target_width=6,
        probability=0.002,
        cover_area: Literal["white", "black"] = "black",
    ):
        """
        Parameters
        ----------
        image_path : str
            Path to the image file used to generate the silhouette.
        dot_radius : float
            Radius of each dot.
        dot_color : Color
            Color of the dots.
        dot_shuffle : bool
            Whether to randomize the order of dots (useful for animation).
        target_height : float
            Height of the silhouette in Manim units.
        target_width : float
            Width of the silhouette in Manim units.
        probability : float
            Probability that a valid pixel produces a dot.
        cover_area : Literal["white", "black"]
            Determines whether dots cover light or dark regions of the image.
        """

        # Initialize the base VGroup
        super().__init__()

        # Store configuration parameters
        self.image_path = image_path
        self.probability = probability
        self.target_width = target_width
        self.target_height = target_height
        self.dot_radius = dot_radius
        self.cover_area = cover_area
        self.dot_color = dot_color
        self.dot_shuffle = dot_shuffle

        # Build the silhouette
        self.__create()

    # ------------------------------------------------------------
    # Silhouette construction
    # ------------------------------------------------------------

    def __create(self):
        """
        Creates the dot-based silhouette and adds it to the group.
        """

        # Fix the random seed for reproducible results
        np.random.seed(7)

        # Generate dot positions from the image
        points = self.__get_points()

        # Create dots at the generated positions
        dots = VGroup(*[Dot(radius=self.dot_radius, color=self.dot_color).move_to(p) for p in points])

        # Randomize dot order if enabled (affects animation order)
        if self.dot_shuffle:
            dots.shuffle_submobjects()

        # Add dots to the group and center them
        self.add(dots)
        self.move_to(ORIGIN)

    # ------------------------------------------------------------
    # Image sampling
    # ------------------------------------------------------------

    def __get_points(self):
        """
        Samples points from the image based on brightness and probability.

        Returns
        -------
        list[np.ndarray]
            A list of 3D points in Manim coordinates.
        """

        # Load image and convert to grayscale
        img = Image.open(self.image_path).convert("L")
        arr = np.array(img)

        h, w = arr.shape
        points = []

        # Iterate over all pixels
        for y in range(h):
            for x in range(w):

                # Decide whether this pixel belongs to the target area
                use_point = arr[y, x] > 128 if self.cover_area == "white" else arr[y, x] < 128

                # Randomly sample points from valid pixels
                if use_point and np.random.rand() < self.probability:

                    # Normalize pixel coordinates to Manim space
                    nx = (x / w - 0.5) * self.target_width
                    ny = (0.5 - y / h) * self.target_height

                    points.append(np.array([nx, ny, 0]))

        return points
