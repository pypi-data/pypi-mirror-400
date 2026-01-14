"""Templates for creating camera device representations."""

from abc import abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import numpy as np
import numpy.typing as npt

from herosdevices.helper import log, merge_dicts
from herosdevices.interfaces import UnionInterfaceMeta
from herosdevices.interfaces.heros import ConfiguredDevice


class DisplayDeviceTemplate(ConfiguredDevice, metaclass=UnionInterfaceMeta):
    """
    Template (base class) for displays.

    To make a functional display device, the user needs to implement all abstract methods.
    In addition, this class does not cover the mechanism the actually push the image to eventaual image
    buffers or to actually display the imag since it is typically special to each vendor/API.
    """

    def __init__(
        self,
        config_dict: dict,
        default_config: str | None = None,
        keep_device_open: bool = True,
    ) -> None:
        """
        Create a new device object.

        Args:
            config_dict: Configuration dictionary, see EXAMPLE_CONFIG
            default_configuration: Default (starting) configuration
            keep_device_open: Keep the device open after it is first opened
        """
        self.keep_device_open = keep_device_open
        self._device = None

        self._config_dict: dict = {}
        self.update_configuration(config_dict)
        self.default_config: str = default_config if default_config is not None else "default"
        self._config: str = self.default_config
        self.configure()  # configure with default config

    @contextmanager
    def get_device(self) -> Iterator[None]:
        """
        Yield a device handle.

        .. code-block:: python

            # use the device in a with statement
            with self.get_device() as slm:
                slm.do_something()
        """
        log.spam("Requesting device")
        if self._device is None:
            self.open()
        yield self._device
        if not self.keep_device_open:
            self.teardown()

    def open(self) -> Any:
        """Open the device handler and assign it to `self._device`."""
        log.info("Opening device handler")
        self._device = self._open()

    def teardown(self) -> None:
        """Release the device handler and potentially de-initialize the API."""
        log.info("Closing device")
        self._teardown()
        self._device = None

    __del__ = teardown

    def reset(self) -> None:
        """Reset the device by closing and re-opening the handler."""
        log.error("Resetting device")
        self.teardown()
        try:
            self.open()
            self.configure()
        except Exception as e:  # noqa: BLE001
            log.warn(f"Opening and configuration during reset failed: {e}")

    def get_status(self) -> dict:
        """
        Get a dict with the current device status.

        Returns:
            A dict with the device status
        """
        return self._get_status()

    @property
    def config_dict(self) -> dict:
        """
        Get a copy of the configuration dict.

        Returns:
            Copy of the configuration dict
        """
        return {**self._config_dict}

    def update_configuration(self, new_config_dict: dict, merge: bool = True) -> None:
        """
        Update the configuration dict with new configuration.

        Each dict key corresponds a (new) configuration name.
        Each value is a dict with config property -> config value.

        Args:
            new_config_dict: A dict of configurations where the keys are the configuration names
            merge: If ``True``, the new dict is recursively merged with the current set config dict. If ``False`` the
                old configurations with the provided names (keys) are overwritten.
        """
        # finally update config
        if merge:
            self._config_dict = merge_dicts(self._config_dict, new_config_dict)
        else:
            # check if special config keyes are present
            for config_name, config in new_config_dict.items():
                for key in self._special_config_keys:
                    assert key in config, f"Required config key {key} not found in config {config_name}!"
            self._config_dict.update(new_config_dict)
            # check if special config keyes are present
            for config_name, config in new_config_dict.items():
                for key in self._special_config_keys:
                    assert key in config, f"Required config key {key} not found in config {config_name}!"

    def get_configuration(self) -> dict:
        """
        Get the currently active configuration.

        Returns:
            The currently active configuration.
        """
        return merge_dicts(self.default_config_dict, self.config_dict[self._config])

    def configure(self, config: str = "") -> bool:
        """
        Configure the device with the known configuration `config`.

        To add a configuration to the device, use :meth:`update_configuration`.

        Args:
            config: Key (name) of the configuration
        """
        if config == "":
            self._config = self.default_config
        else:
            self._config = config
        log.debug(f"Configuring device with setting key: {self._config}")
        return self._set_config(self.get_configuration())

    set_configuration = configure  # satisfy interface requirement

    def push_image(self, slot: int, image: npt.NDArray[np.uint16], display_now: bool = True) -> bool:
        """
        Upload an image into a specified memory slot.

        Args:
            slot: Slot number
            image: The image
            display_now: Flag whether to display the image immediately
        """
        log.info(f"Pushing image with shape: {image.shape} and dtype: {image.dtype} to slot: {slot}.")
        push_successful = self._push_image(slot, image)
        if push_successful and display_now:
            return self.display_slot(slot)
        return push_successful

    def display_slot(self, slot: int = 1) -> bool:
        """
        Set the memory slot to display on the SLM.

        Args:
            slot: Slot number
        """
        log.info(f"Displaying slot: {slot}.")
        return self._display_slot(slot)

    # the following methods need to be implement for specific devices
    @abstractmethod
    def _open(self) -> Any:
        """
        Device specific code to open the device handler and return it.

        .. code-block:: python

            # open slm via vendor API
            slm = vencor_api.get_handle()
            slm.connect()
            return slm
        """

    @abstractmethod
    def _teardown(self) -> None:
        """
        Device specific code to release the device handler and potentially de-initialize the API.

        .. code-block:: python

            # close slm
            with self.get_device() as camera:
                slm.disconnect()
            vendor_api.close()
        """

    @abstractmethod
    def _get_status(self) -> dict:
        """
        Device specific code to get a dict with the current device status.

        .. code-block:: python

            # get sensor temp
            with self.get_device() as camera:
                temp = camera.get_prop("sensor_temp")
            return {"sensor_temp": temp}

        Returns:
            A dict with the device status
        """

    @abstractmethod
    def _set_config(self, config: dict) -> bool:
        """
        Device specific code to configure device features.

        .. code-block:: python

            # apply config
            for key, val in config:
                try:
                    with self.get_device() as camera:
                        camera.apply_prop(name=key, value=val)
                except Exception as e:
                    log.error(e)
                    return False
            return True

        Args:
            config: A valid configuration dict passed from :meth:`set_config`

        Returns:
            True if configuration is possible
        """

    @abstractmethod
    def _push_image(self, slot: int, image: npt.NDArray[np.uint16]) -> bool:
        """
        Device specific code to upload an image into a specified memory slot.

        .. code-block:: python

            with self.get_device() as slm:
                slm.array_to_slot(image, slot)

        Args:
            slot: Slot number
            image: The image.

        Returns:
            True if operation was successful
        """

    @abstractmethod
    def _display_image(self, slot: int) -> bool:
        """
        Device specific code to display a memory slot.

        .. code-block:: python

            with self.get_device() as slm:
                slm.display(slot)

        Args:
            slot: Slot number

        Returns:
            True if operation was successful
        """
