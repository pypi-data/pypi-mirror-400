"""Primitive functions and classes representing visa connections."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import ModuleType

from heros.helper import log

try:
    import pyvisa
    from pyvisa.rname import ResourceName
except ModuleNotFoundError:
    pyvisa = cast("ModuleType", None)


class VisaConnection:
    """A class to manage VISA communication connections.

    This class provides functionality to handle visa connections including opening/closing connections, reading
    data, and writing data.

    Args:
        resource: The resource name of the visa instrument (e.g. ``TCPIP::my_device_hostname::INSTR``).
        keep_alive: Flag indicating whether to keep the connection open between operations.
        **kwargs: Keyword arguments passed to :code:`pyvisa.open_resource`
    """

    resource: str

    def __init__(
        self,
        resource: str,
        keep_alive: bool = True,
        **kwargs,
    ) -> None:
        self.resource = resource
        if pyvisa is None:
            raise ModuleNotFoundError(
                "Could not import the 'pyvisa' python module, visa devices will not be available available"
            )
        try:
            ResourceName.from_string(self.resource)
        except ValueError:
            log.exception(f"Invalid resource: {self.resource}")
        self._pyvisa_rm: pyvisa.ResourceManager | None = None
        self.connection: pyvisa.resources.MessageBasedResource | None = None
        self.keep_alive = keep_alive
        self._resource_kwargs = kwargs

    def _open(self) -> pyvisa.resources.MessageBasedResource:
        log.info(f"Connecting to {self.resource}")
        if self._pyvisa_rm is None:
            self._pyvisa_rm = pyvisa.ResourceManager("@py")
        assert self._pyvisa_rm is not None
        resource = self._pyvisa_rm.open_resource(self.resource, **self._resource_kwargs)
        assert isinstance(resource, pyvisa.resources.MessageBasedResource)
        return resource

    def _teardown(self) -> None:
        try:
            assert self.connection is not None
            self.connection.close()
        except pyvisa.errors.Error:
            log.exception("Error while closing.")
        finally:
            self.connection = None

    @contextmanager
    def operation(self) -> Iterator[None]:
        """Context manager for handling visa connection operations.

        Ensures the visa connection is open before performing operations and closes it afterward
        if :code:`self.keep_alive` is False.

        Yields:
            Yields control back to the caller for performing operations within the context.
        """
        if self.connection is None:
            self.connection = self._open()
        try:
            yield
        finally:
            if not self.keep_alive:
                self._teardown()

    def read(self) -> str | None:
        """Do device read query.

        Returns:
            The decoded data as string, or None if an error occurs.
        """
        with self.operation():
            assert self.connection is not None
            try:
                return self.connection.read().rstrip("\n")
            except pyvisa.errors.VisaIOError:
                log.exception("Error during query!")
                self._teardown()
        return None

    def write(self, message: str, read_echo: bool = False, *args, **kwargs) -> str | None:  # noqa: ARG002
        """Write to the visa connection.

        Args:
            message: The message to be written to the serial connection.
            read_echo: If True, reads back the echo after writing. Defaults to False.
        """
        with self.operation():
            assert self.connection is not None
            try:
                self.connection.write(message)
                if read_echo:
                    return self.connection.read()
            except pyvisa.errors.VisaIOError:
                log.exception("Error during query!")
                self._teardown()
        return None
