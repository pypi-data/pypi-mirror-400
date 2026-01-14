"""Low-level communication interface with the toptica laser sdk."""

import importlib
import inspect
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from herosdevices.hardware.toptica.dlcpro import DLCCommon

from herosdevices.core import Any, DeviceCommandQuantity

R = TypeVar("R")


class _SafeFormatDict(dict):
    """A dict that allows for string formatting with missing keys."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class LaserSDKConnection:
    """A class to manage Toptica Laser SDK connections.

    This class provides functionality to handle
    `Toptica Laser SDK <https://www.toptica.com/technology/toptica-python-laser-sdk/python-laser-sdk>`_
    connections including opening/closing connections, reading data, and writing data.

    Requires the `toptica_lasersdk` package to be installed.

    Args:
        address: The address of the serial socket, something like /dev/ttyUSB0.
        keep_alive: Flag indicating whether to keep the connection open between operations.
        **kwargs: Keyword arguments passed to :code:`toptica.lasersdk.client.NetworkConnection`
    """

    def __init__(
        self,
        address: str,
        keep_alive: bool = True,
        **kwargs,
    ) -> None:
        toptica_client_sdk = importlib.import_module("toptica.lasersdk.client")
        self.address = address
        self.connection = toptica_client_sdk.Client(toptica_client_sdk.NetworkConnection(address, **kwargs))
        self.keep_alive = keep_alive

    @contextmanager
    def operation(self) -> Iterator[None]:
        """Context manager for handling connection operations.

        Ensures the connection is open before performing operations and closes it afterward
        if :code:`self.keep_alive` is False.

        Yields:
            Yields control back to the caller for performing operations within the context.
        """
        self.connection.open()
        try:
            yield
        finally:
            if not self.keep_alive:
                self.connection.close()

    def write(self, message: str, read_echo: bool = False, read_line: bool = False) -> None | str:  # noqa: ARG002
        """Write a message to the attached device.

        Args:
            message: The message to be written. Needs to be of the form ``command;value;dtype``, i.e.
                ``laser1:dl:cc:current-set;85.0;float`` to set the current of a laser diode to 85mA.
            read_echo: If True, reads back the echo from the device after writing. Defaults to False.
            read_line: Not used. Only for compatibility with other connection types.

        Returns:
            If read_echo is True, returns the echo read from the connection as string; otherwise returns None.
        """
        with self.operation():
            if read_echo:
                return self.connection.get(message)
            command, value, dtype = message.split(";")
            if dtype == "bool":
                dec_value = value == "True"
            else:
                dec_value = getattr(sys.modules["builtins"], dtype)(value)
            self.connection.set(command, dec_value)
        return None

    def exec(self, command: str, *args, return_type: None | type[R] = None) -> None | R:
        """Run an lasersdk "exec" command.

        Args:
            command: command to run on the connected laser/DLCPro
            args: positional arguments required as input for the given command
            return_type: type of the returned data if data is returned (must be a builtin type like `str` or `float`)
        """
        if return_type is not None:
            if type(return_type) is str:
                # Toptica only works with standard types
                try:
                    return_type = __builtins__[return_type]
                except KeyError as e:
                    msg = f"{return_type} is not a valid return_type for toptica lasersdk exec"
                    raise TypeError(msg) from e
            return self.connection.exec(command, *args, return_type=return_type)
        self.connection.exec(command, *args)
        return None


class LaserSDKCommandQuantity(DeviceCommandQuantity):
    """
    Descriptor for attaching getting/setting Toptica Laser SDK values directly to class attributes exposed to HEROs.

    This class provides functionality to define a class attribute of the host object based on certain set and get
    commands of a device on a given interface. Defining an attribute this way makes it directly accessible to HEROS.
    This class behaves the same as :py:class:`herosdevices.core.DeviceCommandQuantity`, but with adaptions to the
    Toptica Laser SDK.

    For more details see :py:class:`herosdevices.core.DeviceCommandQuantity`.

    args:
        command: Toptica Laser SDK command to query/set the target argument. Something like ``laser1:dl:cc:pd``.
        writable: If the attribute can be set (True) or is read only (False).
        observable: If True, the attribute is automatically added the the ``_default_observables`` list. See for example
            :py:class:`herosdevices.hardware.toptica.DLPro` for more details.
        **kwargs: All other arguments are passed to the parent class
            :py:class:`herosdevices.core.DeviceCommandQuantity`.

    """

    def __init__(
        self,
        command: str,
        writable: bool = False,
        observable: bool = False,
        format_fun: Callable[[str], Any] = lambda x: x,
        dtype: type = str,
        **kwargs,
    ) -> None:
        if writable:
            dtype_str = dtype if type(dtype) is str else dtype.__name__
            command_set = f"{command};{{{{}}}};{dtype_str}"
        else:
            command_set = None
        self.observable = observable
        self._format_set_done = False
        self._format_get_done = False
        super().__init__(command_set=command_set, command_get=command, format_fun=format_fun, **kwargs)

    def __set__(self, instance: "DLCCommon", value) -> None:  # noqa: ANN001
        """Adjust the command_set string with the instance's format template args then pass to the parent class."""
        if instance is not None and self.command_set is not None and not self._format_set_done:
            self.command_set = self.command_set.format_map(instance._format_template_args)
            self._format_set_done = True
        super().__set__(instance, value)

    def __get__(self, instance: "DLCCommon | None", owner: type) -> Any:  # type: ignore
        """Adjust the command_get string with the instance's format template args then pass to the parent class."""
        if instance is not None and self.command_get is not None and not self._format_get_done:
            self.command_get = self.command_get.format_map(instance._format_template_args)
            self._format_get_done = True
        return super().__get__(instance, owner)


def attach_laser_sdk_exec_method(
    cls: type, name: str, command: str, expected_args: dict | None = None, return_type: None | type[R] = None
) -> None:
    """Attaches a method to a class which runs a toptica lasersdk "exec" command on the target device.

    Typically you do not need to use this method directly as :py:class:`herosdevices.hardware.toptica.dlcpro.DLCCommon`
    takes care of that. Just pass the command as `additional_queries`.

    Args:
        cls: Class to attach the method to
        name: Name of the method
        command: Toptica lasersdk command path that the method will execute with "exec"
        expected_args: Dict of argument names (keys) and types (values) that the command takes
        return_type: Type of the return data, if the command returns data.

    Example:
        Use in the __new__ method of a class like:

        .. code:: python

            def __new__(cls, *_args, **_kwargs):
                attach_laser_sdk_exec_method(cls,name="my_method",command="laser1:dl:lock:close")

    """

    def func(obj: Any, *args) -> None | R:
        return obj.connection.exec(command.format_map(obj._format_template_args), *args, return_type=return_type)

    params = [inspect.Parameter(name="self", kind=inspect.Parameter.POSITIONAL_ONLY)]
    if expected_args is not None:
        params.extend(
            [
                # TODO: add annotation as soon as https://gitlab.com/atomiq-project/heros/-/issues/8 is fixed
                inspect.Parameter(name=name, kind=inspect.Parameter.POSITIONAL_ONLY)
                for name, typ in expected_args.items()
            ]
        )

    setattr(cls, name, func)
    getattr(cls, name).__name__ = name
    getattr(cls, name).__signature__ = inspect.Signature(parameters=params)
