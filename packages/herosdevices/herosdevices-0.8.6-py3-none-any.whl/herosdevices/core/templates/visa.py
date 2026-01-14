"""Templates for devices connected via a visa interface."""

from herosdevices.core.bus.visa import VisaConnection


class VisaDeviceTemplate:
    """Template (base class) for devices which are controlled or read out through a visa interface.

    The interface must be accessible by pyvisa via TCP/IP.

    Inheriting your device driver from this class allows to use `herosdevices.core.DeviceCommandQuantity` to define
    the serial commands within your device driver class.
    """

    def __init__(
        self,
        resource: str,
        keep_alive: bool = True,
        **kwargs,
    ) -> None:
        self.resource = resource
        self.connection = VisaConnection(
            resource,
            keep_alive=keep_alive,
            **kwargs,
        )
