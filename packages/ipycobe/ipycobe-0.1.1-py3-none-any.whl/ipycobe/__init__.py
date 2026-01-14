import importlib.metadata
import pathlib
from typing import NotRequired, Required, TypedDict

import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("ipycobe")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class Marker(TypedDict):
    """A marker on the globe.

    Attributes:
        location: Latitude and longitude as [lat, lng].
        size: Size of the marker (0 to 1).
        color: Optional RGB color as [r, g, b] with values 0-1.
    """

    location: Required[tuple[float, float]]
    size: NotRequired[float]
    color: NotRequired[tuple[float, float, float]]


class Cobe(anywidget.AnyWidget):
    """A WebGL globe widget using the Cobe library.

    This widget renders an interactive 3D globe that can display markers
    and supports auto-rotation.

    Attributes:
        width: Width of the canvas in pixels.
        height: Height of the canvas in pixels.
        phi: Spherical coordinate angle (0 to 2*pi) for horizontal rotation.
        theta: Spherical coordinate angle (-pi to pi) for vertical rotation.
        dark: Dark mode intensity (0 to 1).
        diffuse: Diffuse lighting control (0 or greater).
        map_samples: Number of dots on the globe (0 to 100000).
        map_brightness: Brightness of the dots (0 or greater).
        base_color: RGB color of the globe base as [r, g, b] with values 0-1.
        marker_color: RGB color of markers as [r, g, b] with values 0-1.
        glow_color: RGB color of the glow effect as [r, g, b] with values 0-1.
        markers: List of marker dictionaries with location, size, and optional color.
        scale: Scale factor for the globe (0 or greater).
        device_pixel_ratio: Device pixel ratio for rendering quality.
        auto_rotate: Whether to auto-rotate the globe.
        auto_rotate_speed: Speed of auto-rotation in radians per frame.
        draggable: Whether the globe can be dragged to rotate it.
    """

    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"

    width = traitlets.Int(400).tag(sync=True)
    height = traitlets.Int(400).tag(sync=True)
    phi = traitlets.Float(0.0).tag(sync=True)
    theta = traitlets.Float(0.0).tag(sync=True)
    dark = traitlets.Float(1.0).tag(sync=True)
    diffuse = traitlets.Float(1.2).tag(sync=True)
    map_samples = traitlets.Int(16000).tag(sync=True)
    map_brightness = traitlets.Float(6.0).tag(sync=True)
    base_color = traitlets.List(
        traitlets.Float(), default_value=[0.3, 0.3, 0.3], minlen=3, maxlen=3
    ).tag(sync=True)
    marker_color = traitlets.List(
        traitlets.Float(), default_value=[1.0, 0.5, 0.0], minlen=3, maxlen=3
    ).tag(sync=True)
    glow_color = traitlets.List(
        traitlets.Float(), default_value=[1.0, 1.0, 1.0], minlen=3, maxlen=3
    ).tag(sync=True)
    markers = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    scale = traitlets.Float(1.0).tag(sync=True)
    device_pixel_ratio = traitlets.Float(2.0).tag(sync=True)
    auto_rotate = traitlets.Bool(False).tag(sync=True)
    auto_rotate_speed = traitlets.Float(0.005).tag(sync=True)
    draggable = traitlets.Bool(True).tag(sync=True)

    def add_marker(
        self,
        location: tuple[float, float],
        size: float = 0.05,
        color: tuple[float, float, float] | None = None,
    ) -> None:
        """Add a marker to the globe.

        Args:
            location: Latitude and longitude as (lat, lng).
            size: Size of the marker (0 to 1).
            color: Optional RGB color as (r, g, b) with values 0-1.
        """
        marker: Marker = {"location": location, "size": size}
        if color is not None:
            marker["color"] = color
        self.markers = [*self.markers, marker]

    def clear_markers(self) -> None:
        """Remove all markers from the globe."""
        self.markers = []
