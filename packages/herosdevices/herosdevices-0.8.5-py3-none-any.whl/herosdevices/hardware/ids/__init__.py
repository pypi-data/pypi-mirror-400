"""Module for IDS Imaging Development Systems hardware representations.

IDS is an industrial camera manufacturer and offers high-performance area scan cameras with USB or GigE interfaces
as well as 3D cameras with a wide range of sensors and variants.
"""

from .peak_camera import PeakCompatibleCamera

__all__ = ["PeakCompatibleCamera"]

__vendor_name__ = "IDS Imaging Development Systems"
