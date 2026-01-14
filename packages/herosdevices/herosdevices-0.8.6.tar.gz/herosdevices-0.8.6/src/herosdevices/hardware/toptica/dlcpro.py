"""HEROS implementation of lasers controlled by the Toptica DLC PRO laser driver."""

import importlib
import json

from herosdevices.helper import add_class_descriptor, log, mark_driver
from herosdevices.interfaces.atomiq import LaserSource

from .lasersdk import LaserSDKCommandQuantity, LaserSDKConnection, attach_laser_sdk_exec_method


class DLCCommon(LaserSource):
    """Common baseclass for the Toptica DLC Pro laser driver.

    Do not use directly, use one of the abstracted laser drivers like :py:class:`DLPro`.
    """

    _default_observables: set[str]
    _format_template_args: dict
    _frequency: float = float("nan")
    _power_override: float = float("nan")
    system_health: bool = LaserSDKCommandQuantity(command="system-health", dtype=bool, observable=True)
    """Health status of the laser 0 if healthy, 1 if unhealthy ``system-health``"""

    emission_status: bool = LaserSDKCommandQuantity(command="emission", dtype=bool, observable=True)
    """Emission status of the laser 0 if off, 1 if on"""

    def __init__(
        self, address: str, frequency: float, power: float | None, observables: dict | None = None, **kwargs
    ) -> None:
        """Initialize the DLCCommon instance.

        Args:
            address: IP address of the laser driver. Example: "192.168.1.24"
            frequency: Frequency the laser is running on in Hz. Used for interfacing with atomiq. Can be an approximate
                value if you don't plan to use this feature. Example: 444779044095485.0
            power: Output power of the laser in W. Used for interfacing with atomiq. Can be an approximate
                value if you don't plan to use this feature. Example: 0.1
            observables: A set of attributes (like ``self.system_health``) that are emitted with the ``observable_data``
                HEROS event. If None, the default observables as defined in ``self._default_observables`` (which are
                typically all defined query attributes) are used. Example: ["system_health", "emission_status"]
            additional_queries: A dictionary of additional queries to the laser. The keys are the names of the
                attributes added to the class, the values are arguments for
                :py:class:`herosdevices.hardware.toptica.lasersdk.LaserSDKCommandQuantity`. ``{laser_num}`` can be
                used in the ``command`` string as a placeholder for the laser number specified when initializing the
                laser source.
                Example: {"scan_enabled":{"command":"{laser_num}:scan:enabled","dtype":"bool", "observable":true,
                "writable":true}}
            additional_execs: A dictionary of additional execution commands. The keys are the names of the methods
                added to the class, the values are arguments for
                :py:class:`herosdevices.hardware.toptica.lasersdk.attach_laser_sdk_exec_method`. ``{laser_num}`` can be
                used in the ``command`` string as a placeholder for the laser number specified when initializing the
                laser source.
                Example: {"get_trace": {"command": "{laser_num}:recorder:data:get-data","expected_args":
                {"index": "int", "length": "int"},"return_type": "bytes"}}
        """
        # collect all observables from all superclasses defined by LaserSDKCommandQuantity
        self._default_observables = set()
        for cls in type(self).__mro__:
            for clsvar in cls.__dict__.values():
                if type(clsvar) is LaserSDKCommandQuantity:
                    if clsvar.observable:
                        self._default_observables.add(clsvar.name)
        self.observables = observables if observables is not None else self._default_observables

        self._frequency = frequency
        if power is not None:
            self._power_override = power
        self._format_template_args = {}

        # remove kwargs for __new__ before passing on
        kwargs.pop("additional_execs", None)
        kwargs.pop("additional_queries", None)
        self.connection = LaserSDKConnection(address, **kwargs)
        super().__init__()

    def __new__(
        cls, *_args, additional_execs: dict | None = None, additional_queries: dict | None = None, **_kwargs
    ) -> "DLCCommon":
        """Return a new instance of the the laser class (with unique hash) and attach additional queries."""
        if additional_execs is None:
            additional_execs = {}
        if additional_queries is None:
            additional_queries = {}
        if additional_execs or additional_queries:
            arg_hash = hash(json.dumps(additional_execs | additional_queries))
            hashed_cls = type(f"{cls.__name__}_{arg_hash}", (cls,), {})
            for method_name, method_args in additional_execs.items():
                attach_laser_sdk_exec_method(hashed_cls, method_name, **method_args)
            for attr_name, attr_args in additional_queries.items():
                descriptor = LaserSDKCommandQuantity(**attr_args)
                add_class_descriptor(hashed_cls, attr_name, descriptor)
            return super().__new__(hashed_cls)
        return super().__new__(cls)

    def get_power(self) -> float:
        """Get the (user defined) power of the laser (W)."""
        return self._power_override

    def get_frequency(self) -> float:
        """Get the (user defined) frequency of the laser (Hz)."""
        return self._frequency

    def _observable_data(self) -> dict:
        data = {}

        for observable in self.observables:
            try:
                unit = type(self).__dict__[observable].unit
            except (KeyError, AttributeError):
                # seems like observable was not defined via a LaserSDKCommandQuantity or is just missing
                unit = None
            try:
                data[observable] = (getattr(self, observable), unit)
            except AttributeError:
                # observable not defined
                log.warning(
                    "Trying to get observable '%s', but it is not defined in the definition of %s. Skipping.",
                    observable,
                    type(self).__name__,
                )
        return data


@mark_driver(
    state="beta",
    info="Tunable external cavity diode lasers for cooling and controlling all atoms and ions",
    product_page="https://www.toptica.com/products/tunable-diode-lasers/ecdl-dfb-lasers/dl-pro",
    requires={"toptica.lasersdk.client": "toptica_lasersdk"},
)
class DLPro(DLCCommon):
    """Driver for Toptica DL Pro laser.

    Args:
        laser_num: Number of the laser in a single dlcpro. Relevant for the dual or quad laser DLC options.
        lock_option (bool): If the laser has the lock option installed.

    Attributes:
        lock_status: Status of the lock (if ``lock_option`` installed) ``laserx:dl:lock:state``
    """

    laser_health: bool = LaserSDKCommandQuantity(command="{laser_num}:health", dtype=bool, observable=True)
    "Health status ``laserx:health``"

    set_current: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:cc:current-set", dtype=float, observable=True, writable=True, unit="mA"
    )
    "Set diode Current (mA) ``laserx:dl:cc:current-set``"

    actual_current: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:cc:current-act",
        dtype=float,
        observable=True,
        unit="mA",
    )
    "Actual diode Current (mA) ``laserx:dl:cc:current-act``"

    set_temperature: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:tc:temp-set", dtype=float, observable=True, writable=True, unit="°C"
    )
    "Set diode Temperature (°C) ``laserx:dl:tc:temp-set``"

    actual_temperature: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:tc:temp-act",
        dtype=float,
        observable=True,
        unit="°C",
    )
    "Actual diode Temperature (°C) ``laserx:dl:tc:temp-act``"

    set_piezo_voltage: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:pc:voltage-set", dtype=float, observable=True, writable=True, unit="V"
    )
    "Set piezo voltage (V) ``laserx:dl:pc:voltage-set``"

    actual_piezo_voltage: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:pc:voltage-act",
        dtype=float,
        observable=True,
        unit="V",
    )
    "Actual piezo voltage (V) ``laserx:dl:pc:voltage-act``"

    diode_ontime: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:ontime",
        dtype=float,
        observable=True,
        unit="s",
    )
    "Diode on time (s) ``laserx:dl:ontime``"

    internal_pd: float = LaserSDKCommandQuantity(
        command="{laser_num}:dl:cc:pd",
        dtype=float,
        observable=True,
    )
    "Internal PD ``laserx:dl:cc:pd``"

    def __new__(cls, lock_option: bool = False, **kwargs) -> "DLPro":
        """Create a new instance and attach optional laser components."""
        if lock_option:
            if "additional_queries" not in kwargs:
                kwargs["additional_queries"] = {}
            kwargs["additional_queries"]["lock_status"] = {
                "command": "{laser_num}:dl:lock:state",
                "dtype": "bool",
                "observable": True,
            }
            if "additional_execs" not in kwargs:
                kwargs["additional_execs"] = {}
            kwargs["additional_execs"]["close_lock"] = {"command": "{laser_num}:dl:lock:close"}

        return super().__new__(cls, **kwargs)  # type: ignore

    def __init__(self, laser_num: int = 1, *args, **kwargs) -> None:
        # remove kwargs for __new__ before passing on
        kwargs.pop("lock_option", None)
        super().__init__(*args, **kwargs)
        self._format_template_args["laser_num"] = f"laser{laser_num}"


@mark_driver(
    state="beta",
    info="High-Power Tapered Laser Amplifier",
    product_page="https://www.toptica.com/products/tunable-diode-lasers/amplified-lasers/boosta-pro",
    requires={"toptica.lasersdk.client": "toptica_lasersdk"},
)
class BoosTAPro(DLCCommon):
    """Driver for Toptica BoosTAPro tapered amplifier.

    Args:
        laser_num: Number of the laser in a single dlcpro. Relevant for the dual or quad laser DLC options.
    """

    amp_set_current = LaserSDKCommandQuantity(
        command="{laser_num}:amp:cc:current-set", dtype=float, observable=True, writable=True, unit="mA"
    )
    "Set amplifier Current (mA) ``laserx:amp:cc:current-set``"

    amp_actual_current = LaserSDKCommandQuantity(
        command="{laser_num}:amp:cc:current-act",
        dtype=float,
        observable=True,
        unit="mA",
    )
    "Actual amplifier current (mA) ``laserx:amp:cc:current-act``"

    amp_set_temperature = LaserSDKCommandQuantity(
        command="{laser_num}:amp:tc:temp-set", dtype=float, observable=True, writable=True, unit="°C"
    )
    "Set amplifier temperature (°C)  ``laserx:amp:tc:temp-set``"

    amp_actual_temperature = LaserSDKCommandQuantity(
        command="{laser_num}:amp:tc:temp-act",
        dtype=float,
        observable=True,
        unit="°C",
    )
    "Actual amplifier temperature (°C) ``laserx:amp:tc:temp-act``"

    amp_ontime = LaserSDKCommandQuantity(
        command="{laser_num}:amp:ontime", dtype=float, observable=True, unit="s"
    )
    "Run hours of the amplifier (s) ``laserx:amp:ontime``"

    amp_emission = LaserSDKCommandQuantity(
        command="{laser_num}:amp:cc:emission", dtype=bool, observable=True, writable=True
    )
    "emission status of the amplifier ``laserx:amp:cc:emission``"


@mark_driver(
    state="beta",
    info="Tapered Amplifier Laser System",
    product_page="https://www.toptica.com/products/tunable-diode-lasers/amplified-lasers/ta-pro",
    requires={"toptica.lasersdk.client": "toptica_lasersdk"},
)
class TAPro(DLPro, BoosTAPro):
    """Driver for Toptica TAPro laser system.

    Args:
        laser_num: Number of the laser in a single dlcpro. Relevant for the dual DLC options.
    """

    amp_seed_power = LaserSDKCommandQuantity(
        command="{laser_num}:amp:pd:seed:power", dtype=float, observable=True, writable=False, unit="mW"
    )
    "Seed power at the amplifier stage (mW) ``laserx:amp:pd:seed:power``"

    amp_output_power = LaserSDKCommandQuantity(
        command="{laser_num}:amp:pd:amp:power", dtype=float, observable=True, writable=False, unit="mW"
    )
    "Output power at the amplifier stage (mW) ``laserx:amp:pd:amp:power``"

    def get_power(self) -> float:  # type: ignore[override]
        """Get the power of the laser (W) ``laserx:amp:pd:amp:power`` or user defined override."""
        if self._power_override != self._power_override:
            return self.amp_output_power
        return self._power_override

    def __init__(self, power: float | None = None, **kwargs) -> None:
        """Initialize a TAPro laser.

        Args:
            power: Output power of the laser in W. When ``None`` (default), the ``amp_output_power`` PD is used
                Example: 1.5
        """
        super().__init__(power=power, **kwargs)
        # we need to make the power optional since we can not infere it like the TAPro


@mark_driver(
    state="beta",
    info="High-power, tunable, frequency-doubled diode laser",
    product_page="https://www.toptica.com/products/tunable-diode-lasers/frequency-converted-lasers/ta-shg-pro",
    requires={"toptica.lasersdk.client": "toptica_lasersdk"},
)
class TASHGPro(TAPro):
    """Driver for Toptica TASHGPro second harmonic doubled laser system."""

    shg_set_temperature = LaserSDKCommandQuantity(
        command="{laser_num}:nlo:shg:tc:temp-set", dtype=float, observable=True, writable=True, unit="°C"
    )
    "SHG crystal set temperature (°C)  ``laserx:nlo:shg:tc:temp-set``"

    shg_actual_temperature = LaserSDKCommandQuantity(
        command="{laser_num}:nlo:shg:tc:temp-act",
        dtype=float,
        observable=True,
        unit="°C",
    )
    "SHG crystal actual temperature (°C) ``laserx:nlo:shg:tc:temp-act``"

    shg_output_power = LaserSDKCommandQuantity(
        command="{laser_num}:nlo:pd:shg:power", dtype=float, observable=True, writable=False, unit="mW"
    )
    "Output power of the SHG stage (mW) ``laserx:nlo:pd:shg:power``"

    shg_lock_status = LaserSDKCommandQuantity(
        command="{laser_num}:nlo:shg:lock:lock-enabled", dtype=bool, observable=True, writable=True
    )
    "SHG lock state (True/False) ``laserx:nlo:shg:lock:lock-enabled``"

    def get_power(self) -> float:  # type: ignore[override]
        """Get the power of the laser (W) ``laserx:nlo:pd:shg:power`` or user defined override."""
        if self._power_override != self._power_override:
            return self.shg_output_power
        return self._power_override

    def __new__(cls, **kwargs) -> "TASHGPro":
        """Create a new instance and attach optional laser components."""
        if "additional_execs" not in kwargs:
            kwargs["additional_execs"] = {}
        kwargs["additional_execs"]["shg_close_lock"] = {"command": "{laser_num}:nlo:shg:lock:close"}

        return super().__new__(cls, **kwargs)  # type: ignore


# Deprecated from here on.

DEFAULT_QUERIES = [
    ["set current", "dl.cc.current_set", "mA"],
    ["actual current", "dl.cc.current_act", "mA"],
    ["set temperature", "dl.tc.temp_set", "degC"],
    ["actual temperature", "dl.tc.temp_act", "degC"],
    ["diode ontime", "dl.ontime", "s"],
    ["system health", "system_health", ""],
    ["laser health", "health", ""],
    ["emission status", "emission", ""],
    ["internal PD", "dl.cc.pd", "uA"],
]

dlcproorders = (
    "emission_button_enabled",
    "interlock_open",
    "frontkey_locked",
    "emission",
    "system_health",
    "uptime",
    "io",
)
"""Define parameters of the DLCPro and the laser in order to build another function call later"""


class DlcProSource:
    """Reading Toptica DLC Pro parameters via ethernet."""

    def __init__(self, ip: str, laser: str = "laser1", queries: list[list[str]] = DEFAULT_QUERIES) -> None:
        self.sdk_client = importlib.import_module("toptica.lasersdk.client")
        self.sdk_dlcpro = importlib.import_module("toptica.lasersdk.dlcpro.v3_2_0")
        self.ip = ip
        self.laser = laser
        self.queries = queries
        self._dlc = None
        log.warning(
            "DlcProSource class (used here with ip %s) is deprecated, use new laser specific classes like DLCPro",
            self.ip,
        )

    def _setup(self) -> None:
        self._connect()

    def _connect(self) -> None:
        """Connect to controller."""
        try:
            con = self.sdk_client.NetworkConnection(self.ip)
            self._dlc = self.sdk_dlcpro.DLCpro(con).__enter__()
            log.debug("connected to %s", self.ip)
        except (self.sdk_client.DeviceNotFoundError, self.sdk_client.DeviceTimeoutError):
            log.error("Could not connect to DLCPro %s via ethernet", self.ip)

    def teardown(self) -> None:
        """Cleanup at the end."""
        try:
            if self._dlc is not None:
                self._dlc.__exit__()
            log.debug("closing down connection to %s", self.ip)
        except AttributeError:
            log.debug("connection to %s was already dead", self.ip)

    @property
    def session(self):  # noqa:ANN201
        """Return a dlc objects and connect if necessary."""
        if self._dlc is None:
            self._connect()
        return self._dlc

    def _observable_data(self) -> dict:
        """Receiving specified parameters of the Toptica DLC Pro."""
        if self.session is None:
            return None  # type: ignore # TODO: Why is this if and return needed here?

        data = {}

        # Connecting to the Toptica DLC Pro via IP address
        try:
            # Building the function call to get the specified parameters
            # Distinguish between parameters for the DLC Pro, the laser and the laserhead
            for description, func_name, unit in self.queries:
                if func_name.startswith(dlcproorders):
                    # Function call for DLCPro parameters
                    option = "self.session." + func_name + ".get"
                else:
                    # Function call for laserhead parameters
                    option = "self.session." + self.laser + "." + func_name + ".get"

                call = eval(option)  # noqa: S307 TODO: Don't use eval.
                value = call()
                data.update({description: (value, unit)})

        except Exception:  # noqa: BLE001
            # something went wrong, reconnect
            log.exception("something went wrong")
            self._dlc = None

        return data
