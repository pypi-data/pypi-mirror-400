"""Module for ds18b20 temperature sensor probe representations."""

from herosdevices.core.bus import OneWire
from herosdevices.helper import mark_driver


@mark_driver(
    state="beta",
    info="Temperature Sensor -55°C to 125°C",
    product_page="https://www.analog.com/en/products/ds18b20.html",
)
class DS18B20(OneWire):
    """One wire temperature sensor type DS18B20."""

    _observables = [("temperature", float, "mdegC")]
