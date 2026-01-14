"""A collection of templates for device drivers.

If implementing new hardware, e.g. developing new device drivers, it is encouraged to use a template class from this
module.
"""

from .acq_device import AcquisitionDeviceTemplate
from .camera import CameraTemplate
from .display import DisplayDeviceTemplate
from .oscilloscope import OscilloscopeTemplate
from .serial import SerialDeviceTemplate
from .telnet import TelnetDeviceTemplate
from .visa import VisaDeviceTemplate

__all__ = [
    "AcquisitionDeviceTemplate",
    "CameraTemplate",
    "DisplayDeviceTemplate",
    "OscilloscopeTemplate",
    "SerialDeviceTemplate",
    "TelnetDeviceTemplate",
    "VisaDeviceTemplate",
]
