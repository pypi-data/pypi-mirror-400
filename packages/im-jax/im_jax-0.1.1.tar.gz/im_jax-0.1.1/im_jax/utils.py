"""Utilities for layout and location handling."""

from __future__ import annotations

import jax.numpy as jnp


def ensure_locations_2xN(locations):
    """Normalize locations to shape (2, N)."""
    locations = jnp.asarray(locations)
    if locations.ndim != 2:
        raise ValueError("locations must be 2D with shape (2, N) or (N, 2)")
    if locations.shape[0] == 2:
        return locations
    if locations.shape[1] == 2:
        return locations.T
    raise ValueError("locations must have a dimension of size 2")


def split_image_channels(image, layout):
    """Return image as (C, H, W) and a flag indicating channel presence."""
    image = jnp.asarray(image)
    if layout == "HW":
        if image.ndim != 2:
            raise ValueError("layout='HW' requires image shape (H, W)")
        return image[None, ...], False
    if layout == "CHW":
        if image.ndim != 3:
            raise ValueError("layout='CHW' requires image shape (C, H, W)")
        return image, True
    raise ValueError(f"Unsupported layout: {layout}")
