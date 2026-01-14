"""Dummy SLM for testing purposes."""

import time

import numpy as np
import numpy.typing as npt
from heros import event

from herosdevices.core.templates import DisplayDeviceTemplate


def compute_intensity_in_focal_plane(phase_pattern: np.array, value_2_pi: float = 1024) -> np.array:
    """Compute intensity in the focal plane of a lens after imprinting the given phase pattern."""
    # Assume uniform amplitude
    phase_radians = (phase_pattern / value_2_pi) * 2 * np.pi
    field = np.exp(1j * phase_radians)
    # Compute Fourier transform (shifted so center is in the middle)
    ft = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(field)))
    # Compute intensity (square of absolute value)
    intensity = np.abs(ft) ** 2
    # Normalize
    intensity /= np.max(intensity)
    return intensity


class SlmDummy(DisplayDeviceTemplate):
    """Dummy SLM for testing purposes."""

    default_config_dict: dict = {
        "slots": 32,
        "image_size": (1200, 1920),
        "value_2_pi": 1024,
    }
    image_size: tuple | list
    value_2_pi: float
    simulate: bool

    def __init__(
        self,
        config_dict: dict,
        default_config: str | None = None,
        keep_device_open: bool = True,
        simulate: bool = True,
    ) -> None:
        self.simulate = simulate
        DisplayDeviceTemplate.__init__(self, config_dict, default_config, keep_device_open)

    def _open(self) -> None:
        return None

    def _teardown(self) -> None:
        return None

    def _get_status(self) -> dict:
        """Return the current device status as dict."""
        return {
            "firmware_serialnumber": self.firmware_serialnumber(),
        }

    def _set_config(self, config: dict) -> bool:
        """Set the configuration from a dict."""
        self.slots = config["slots"]
        self.image_size = config["image_size"]
        self.value_2_pi = config["value_2_pi"]
        self.images = [None] * self.slots
        return True

    def _push_image(self, slot: int, image: npt.NDArray[np.uint16]) -> bool:
        """
        Load a phase pattern to a slot of the device.

        Args:
            slot: The slot to use.
            image: The phase pattern.
        """
        assert slot < len(self.images), f"Slot {slot} is out of range!"
        assert image.shape == tuple(self.image_size), (
            f"Phase pattern size {image.shape} does not match SLM size {self.image_size}"
        )
        self.images[slot] = image
        return True

    def _display_slot(self, slot: int = 1) -> bool:
        """Display a certain slot."""
        assert slot < len(self.images), f"Slot {slot} is out of range!"
        self.phase_data(self.images[slot], {"type": "phase", "slot": slot})
        if self.simulate:
            t0 = time.time()
            image = compute_intensity_in_focal_plane(self.images[slot], self.value_2_pi)
            dt = time.time() - t0
            self.simulation_data(image, {"type": "image", "slot": slot, "calculation_time": dt})
        return True

    def firmware_serialnumber(self) -> str:
        """Return a dummy firmware serial number."""
        return "20090123_142415"

    @event
    def simulation_data(self, image: np.ndarray, metadata: dict = {}) -> tuple:  # noqa: B006
        """Publish simulation results."""
        return image, metadata

    @event
    def phase_data(self, phase: np.ndarray, metadata: dict = {}) -> tuple:  # noqa: B006
        """Publish phase pattern."""
        return phase, metadata
