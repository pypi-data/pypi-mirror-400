"""Device driver for Rohde Schwarz NGX Power Supplies."""

from typing import Any

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import VisaDeviceTemplate
from herosdevices.helper import add_class_descriptor, get_or_create_dynamic_subclass, mark_driver


@mark_driver(
    info="Rohde Schwarz NGX Power Supply",
    product_page="https://www.rohde-schwarz.com/de/produkte/messtechnik/dc-netzgeraete_64067.html",
    state="beta",
)
class NGX(VisaDeviceTemplate):
    """A channel of a RS NGX PSU with TCP/IP connection."""

    _default_observables: tuple[tuple[str, str], ...] = (
        ("voltage", "V"),
        ("current", "A"),
        ("power", "W"),
        ("state", ""),
    )
    channels: tuple[tuple[int, str], ...] = ((1, "ch1"),)

    def __init__(
        self, resource: str, channels: tuple[tuple[int, str], ...] = ((1, "ch1"),), keep_alive: bool = True, **kwargs
    ) -> None:
        VisaDeviceTemplate.__init__(self, resource=resource, keep_alive=keep_alive, **kwargs)
        self.channels = channels

    def __new__(cls, channels: tuple[tuple[int, str], ...] = ((1, "ch1"),), *_args, **_kwargs) -> Any:
        """Create a new NGX instance."""
        # get new or cashed subclass
        new_cls = get_or_create_dynamic_subclass(cls, channels=channels)
        # global commands (affecting all channels)
        channel_query_suffix = f"(@{','.join(str(ch_idx) for ch_idx, ch_name in channels)})"
        # voltage
        add_class_descriptor(
            new_cls,
            "voltage",
            DeviceCommandQuantity(
                command_get=f"MEAS:VOLT? {channel_query_suffix}",
                format_fun=lambda x: x.split(","),
                dtype=float,
                unit="V",
            ),
        )
        # current
        add_class_descriptor(
            new_cls,
            "current",
            DeviceCommandQuantity(
                command_get=f"MEAS:CURR? {channel_query_suffix}",
                format_fun=lambda x: x.split(","),
                dtype=float,
                unit="V",
            ),
        )
        # power
        add_class_descriptor(
            new_cls,
            "power",
            DeviceCommandQuantity(
                command_get=f"MEAS:POW? {channel_query_suffix}",
                format_fun=lambda x: x.split(","),
                dtype=float,
                unit="V",
            ),
        )
        # status
        add_class_descriptor(
            new_cls,
            "state",
            DeviceCommandQuantity(
                command_get=f"OUTP? {channel_query_suffix}",
                format_fun=lambda x: x.split(","),
                dtype=bool,
                unit="V",
            ),
        )
        # per channel commands
        for ch_idx, ch_name in channels:
            attr_name = f"{ch_name}_voltage"
            add_class_descriptor(
                new_cls,
                attr_name,
                DeviceCommandQuantity(
                    command_get=f"MEAS:VOLT? (@{ch_idx!s})",
                    command_set="SOUR:VOLT {}, " + f"(@{ch_idx!s}); *OPC?",
                    dtype=float,
                    unit="V",
                    return_check="1",
                ),
            )
            attr_name = f"{ch_name}_current"
            add_class_descriptor(
                new_cls,
                attr_name,
                DeviceCommandQuantity(
                    command_get=f"MEAS:CURR? (@{ch_idx!s})",
                    command_set="SOUR:CURR {}, " + f"(@{ch_idx!s}); *OPC?",
                    dtype=float,
                    unit="A",
                    return_check="1",
                ),
            )
        return object.__new__(new_cls)

    def _observable_data(self) -> dict:
        data = {}
        for query, unit in self._default_observables:
            for (_ch_idx, ch_name), result in zip(self.channels, getattr(self, query), strict=True):
                obs_name = f"{ch_name}_{query}"
                data[obs_name] = (result, unit)
        return data
