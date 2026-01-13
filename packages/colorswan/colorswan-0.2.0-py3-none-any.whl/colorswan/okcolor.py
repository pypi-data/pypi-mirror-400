import math
from dataclasses import dataclass

from .constants import M_RGB_XYZ, M_XYZ_LMS, M_LMS_OKLAB


@dataclass
class Oklab:
    """
    Represents a color in the Oklab color space (perceptually uniform).
    
    Attributes:
        L (float): Lightness (0.0 to 1.0).
        a (float): Green-Red component (approx -0.4 to 0.4).
        b (float): Blue-Yellow component (approx -0.4 to 0.4).
    """
    L: float
    a: float
    b: float


@dataclass
class Oklch:
    """
    Represents a color in the Oklch color space (cylindrical form of Oklab).

    Attributes:
        L (float): Lightness (0.0 to 1.0).
        C (float): Chroma (0.0 upwards).
        h (float): Hue (0.0 to 360.0 degrees).
    """
    L: float
    C: float
    h: float


class OkColor:
    """
    A precision converter for sRGB to Oklab/Oklch.
    """

    @staticmethod
    def _linearize_srgb(v):
        """
        Applies the EOTF to convert non-linear sRGB to linear light intensity.
        Formula constants defined in IEC 61966-2-1.
        """
        if v <= 0.04045:
            return v / 12.92
        else:
            return ((v + 0.055) / 1.055) ** 2.4

    @staticmethod
    def _multiply_matrix_vector(matrix, vector):
        """Helper for matrix multiplication (3x3 * 3x1)."""
        return [
            sum(matrix[i][j] * vector[j] for j in range(3))
            for i in range(3)
        ]

    @staticmethod
    def _cbrt(x):
        """
        Signed cube root function. 
        Necessary for handling negative values in wide-gamut scenarios.
        """
        return math.copysign(abs(x) ** (1 / 3), x)

    @staticmethod
    def _parse_hex(hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            raise ValueError("Hex string must be 6 characters (e.g., #FF0000)")
        return tuple(int(hex_str[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def convert(color_input, return_type="oklab"):
        """
        Main entry point. Accepts:
        - Hex String: "#ffffff" or "ffffff"
        - RGB Tuple (0-255): (255, 0, 0)
        - return_type: "oklab" (default), "oklch", or "all".

        Returns:
            - Oklab object (if return_type="oklab")
            - Oklch object (if return_type="oklch")
            - Dictionary {"oklab": ..., "oklch": ...} (if return_type="all")
        """
        valid_types = {"oklab", "oklch", "all"}
        if return_type not in valid_types:
            raise ValueError(f"Invalid return_type. Choose from {valid_types}")

        # 1. Parse Input & Normalize to 0-1
        if isinstance(color_input, str):
            r, g, b = OkColor._parse_hex(color_input)
        elif isinstance(color_input, (tuple, list)):
            r, g, b = [c / 255.0 for c in color_input]
        else:
            raise ValueError("Invalid input format. Use Hex string or RGB tuple.")

        # 2. Linearize sRGB (EOTF)
        r_lin = OkColor._linearize_srgb(r)
        g_lin = OkColor._linearize_srgb(g)
        b_lin = OkColor._linearize_srgb(b)
        rgb_lin_vector = [r_lin, g_lin, b_lin]

        # 3. Linear RGB -> XYZ
        xyz = OkColor._multiply_matrix_vector(M_RGB_XYZ, rgb_lin_vector)

        # 4. XYZ -> LMS (Cone Response)
        lms = OkColor._multiply_matrix_vector(M_XYZ_LMS, xyz)

        # 5. Non-Linear Compression (Cube Root)
        lms_prime = [OkColor._cbrt(c) for c in lms]

        # 6. LMS -> Oklab (Decorrelation)
        l_ok, a_ok, b_ok = OkColor._multiply_matrix_vector(M_LMS_OKLAB, lms_prime)

        # 7. Oklab -> Oklch (Polar conversion)
        chroma = math.sqrt(a_ok ** 2 + b_ok ** 2)
        hue = math.atan2(b_ok, a_ok) * (180 / math.pi)

        # Normalize hue to 0-360 range
        if hue < 0:
            hue += 360

        if return_type == "oklab":
            return Oklab(l_ok, a_ok, b_ok)
        elif return_type == "oklch":
            return Oklch(l_ok, chroma, hue)
        else:  # "all"
            return {
                "oklab": Oklab(l_ok, a_ok, b_ok),
                "oklch": Oklch(l_ok, chroma, hue)
            }

