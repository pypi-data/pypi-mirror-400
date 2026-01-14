"""Device driver for ThorLabs MDT69XB Piezo Controllers."""

import time

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import SerialDeviceTemplate as SerialDevice
from herosdevices.helper import limits, mark_driver
from herosdevices.interfaces.atomiq import VoltageSource

MDT69XB_CHANNELS = {0: "x", 1: "y", 2: "z"}


def _remove_brackets(raw_str: str) -> str:
    """Remove brackets from piezo controller voltage return values."""
    return raw_str.strip("[]\r")


@mark_driver(
    info="Single Channel, Open-Loop Piezo Controller",
    product_page="https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=1191",
    state="beta",
)
class MDT694B(SerialDevice):
    """Device driver for the MDT694B Single Channel, Open-Loop Piezo Controller.

    Args:
        address: Serial address of the device. Example: "/dev/ttyUSB0"
        timeout: timeout for read operations.
    """

    voltage_x: float = DeviceCommandQuantity(
        command_set="xvoltage={}",
        command_get="xvoltage?",
        dtype=float,
        value_check_fun=limits(0, 150),
        unit="V",
        format_fun=_remove_brackets,
    )
    min_voltage_x: float = DeviceCommandQuantity(
        command_set="xmin={}", command_get="xmin?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )
    max_voltage_x: float = DeviceCommandQuantity(
        command_set="xmax={}", command_get="xmax?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )

    def __init__(self, address: str, timeout: float = 1.0) -> None:
        SerialDevice.__init__(
            self,
            address,
            baudrate=115200,
            timeout=timeout,
            delays={"read_echo": 0.05},
            read_line_termination=b"\r",
            write_line_termination=b"\r",
        )
        self.connection.write("echo=0")

    def initial_piezo_loop(self, voltage_start: float, voltage_stop: float, channel: int | str = 0) -> None:
        """Perform a piezo voltage loop to compensate for hysteresis effects.

        This function executes a voltage cycle (start -> stop -> start) on the specified piezo axis. Doing this
        before setting the target value helps compensate for the hysteresis behavior inherent in piezo actuators.

        Args:
            channel: The piezo axis to control. Can be either:
                  - Integer (0, 1, 2) corresponding to x, y, z axes respectively
                  - String ('x', 'y', 'z') directly specifying the axis
                  For the one channel MDT694B, only x or 0 is valid.
            voltage_start: Starting voltage in volts for the hysteresis compensation loop
            voltage_stop: Stop voltage in volts for the hysteresis compensation loop

        Raises:
            ValueError: If channel is not a valid channel for the device
        """
        channel_str: str = f"voltage_{MDT69XB_CHANNELS[channel] if isinstance(channel, int) else channel}"
        if not hasattr(self, channel_str):
            raise ValueError("Channel %s is not a valid channel for %s", channel, self)

        for voltage in [voltage_start, voltage_stop, voltage_start]:
            setattr(self, channel_str, voltage)
            time.sleep(2e-3)  # 2ms delay between voltage changes to allow for settling time


@mark_driver(
    info="3-Channel, Open-Loop Piezo Controller",
    product_page="https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=1191",
    state="beta",
)
class MDT693B(MDT694B):
    """Device driver for the MDT693B 3-Channel, Open-Loop Piezo Controller."""

    voltage_y: float = DeviceCommandQuantity(
        command_set="yvoltage={}",
        command_get="yvoltage?",
        dtype=float,
        value_check_fun=limits(0, 150),
        unit="V",
        format_fun=_remove_brackets,
    )
    min_voltage_y: float = DeviceCommandQuantity(
        command_set="ymin={}", command_get="ymin?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )
    max_voltage_y: float = DeviceCommandQuantity(
        command_set="ymax={}", command_get="ymax?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )
    voltage_z: float = DeviceCommandQuantity(
        command_set="zvoltage={}",
        command_get="zvoltage?",
        dtype=float,
        value_check_fun=limits(0, 150),
        unit="V",
        format_fun=_remove_brackets,
    )
    min_voltage_z: float = DeviceCommandQuantity(
        command_set="zmin={}", command_get="zmin?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )
    max_voltage_z: float = DeviceCommandQuantity(
        command_set="zmax={}", command_get="zmax?", dtype=float, value_check_fun=limits(0, 150), unit="V"
    )


@mark_driver(
    name="MDR69xB Channel",
    info="Single Channel Representation of a MDT69xB Piezo Driver",
    product_page="https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=1191",
    state="beta",
)
class MDT69xBChannel(VoltageSource):
    """A single channel of a MDT69xB piezo driver.

    This class provides an :py:class:`herosdevices.interfaces.atomiq.VoltageSource` compatible interface to control a
    single channel of a MDT69xB piezo driver.

    Note:
        This class does not directly connect to the hardware but to another object given by the host_device argument
        which can also be a HERO running on another machine. It can be used to provide a universal interface which does
        not require setting a channel for every operation.

    Args:
        host_device: The host MDT69xB device (MDT693B or MDT694B).
        channel: The channel to control (can be int 0-2 or str 'x', 'y', 'z', depending on host_device)

    Raises:
        ValueError: If the channel is not valid for the host device
    """

    def __init__(self, host_device: MDT693B | MDT694B, channel: int | str = "x") -> None:
        super().__init__()
        self.host_device = host_device
        self.channel: str = MDT69XB_CHANNELS[channel] if isinstance(channel, int) else channel
        if not hasattr(self.host_device, f"voltage_{self.channel}"):
            raise ValueError("Channel %s is not a valid channel for %s", channel, host_device)

    def _set_voltage(self, value: float) -> None:
        self.voltage = value

    @property
    def voltage(self) -> float:
        """Get or set the current voltage of the channel.

        Returns:
            The current voltage in volts
        """
        return getattr(self.host_device, f"voltage_{self.channel}")

    @voltage.setter
    def voltage(self, value: float) -> None:
        """Set the current voltage of the channel.

        Args:
            value: The voltage to set in volts
        """
        setattr(self.host_device, f"voltage_{self.channel}", value)

    @property
    def max_voltage(self) -> float:
        """Get or set the maximum voltage limit for the channel.

        Returns:
            The maximum voltage limit in volts
        """
        return getattr(self.host_device, f"max_voltage_{self.channel}")

    @max_voltage.setter
    def max_voltage(self, value: float) -> None:
        """Set the maximum voltage limit for the channel.

        Args:
            value: The maximum voltage limit to set in volts
        """
        setattr(self.host_device, f"max_voltage_{self.channel}", value)

    @property
    def min_voltage(self) -> float:
        """Get or set the minimum voltage limit for the channel.

        Returns:
            The minimum voltage limit in volts
        """
        return getattr(self.host_device, f"min_voltage_{self.channel}")

    @min_voltage.setter
    def min_voltage(self, value: float) -> None:
        """Set the minimum voltage limit for the channel.

        Args:
            value: The minimum voltage limit to set in volts
        """
        setattr(self.host_device, f"min_voltage_{self.channel}", value)

    def initial_piezo_loop(self, voltage_start: float, voltage_stop: float) -> None:
        """Perform a piezo voltage loop to compensate for hysteresis effects.

        This function executes a voltage cycle (start -> stop -> start) on the specified piezo axis. Doing this
        before setting the target value helps compensate for the hysteresis behavior inherent in piezo actuators.

        Args:
            voltage_start: Starting voltage in volts for the hysteresis compensation loop
            voltage_stop: Stop voltage in volts for the hysteresis compensation loop

        Raises:
            ValueError: If channel is not a valid channel for the device
        """
        self.host_device.initial_piezo_loop(
            voltage_start=voltage_start, voltage_stop=voltage_stop, channel=self.channel
        )
