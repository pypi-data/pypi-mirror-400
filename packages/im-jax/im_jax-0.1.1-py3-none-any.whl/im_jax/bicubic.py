"""Bicubic interpolation for 2D images in JAX."""

from __future__ import annotations

import jax
import jax.numpy as jnp

from .boundary import apply_boundary
from .kernels import cubic_weights
from .utils import ensure_locations_2xN, split_image_channels


def _flat_nd_cubic_interpolate_2d(image_hw, locations_2xN, mode, cval, a):
    image_hw = jnp.asarray(image_hw)
    locations_2xN = jnp.asarray(locations_2xN)

    dtype = jnp.result_type(image_hw, locations_2xN)
    image_hw = image_hw.astype(dtype)
    locations_2xN = locations_2xN.astype(dtype)

    x = locations_2xN[0]
    y = locations_2xN[1]
    x0 = jnp.floor(x).astype(jnp.int32)
    y0 = jnp.floor(y).astype(jnp.int32)
    fx = x - x0.astype(dtype)
    fy = y - y0.astype(dtype)

    wx = cubic_weights(fx, a)
    wy = cubic_weights(fy, a)

    offsets = jnp.array([-1, 0, 1, 2], dtype=jnp.int32)
    xi = x0[:, None] + offsets[None, :]
    yi = y0[:, None] + offsets[None, :]

    xi_bc, x_valid = apply_boundary(xi, image_hw.shape[0], mode)
    yi_bc, y_valid = apply_boundary(yi, image_hw.shape[1], mode)

    xi_bc = xi_bc.astype(jnp.int32)
    yi_bc = yi_bc.astype(jnp.int32)

    values = image_hw[xi_bc[:, :, None], yi_bc[:, None, :]]

    if mode == "constant":
        valid = x_valid[:, :, None] & y_valid[:, None, :]
        values = jnp.where(valid, values, jnp.asarray(cval, dtype=dtype))

    weights = wx[:, :, None] * wy[:, None, :]
    return jnp.sum(values * weights, axis=(1, 2))


def flat_nd_cubic_interpolate(
    image,
    locations,
    *,
    mode="reflect",
    cval=0.0,
    kernel="keys",
    a=-0.5,
    layout="HW",
):
    """Flat N-D cubic interpolation specialized for 2D images.

    locations follow the pixel-center convention and must be shaped (2, N).
    """
    if kernel != "keys":
        raise ValueError(f"Unsupported cubic kernel: {kernel}")

    locations_2xN = ensure_locations_2xN(locations)
    image_chw, has_channels = split_image_channels(image, layout)

    out = jax.vmap(
        _flat_nd_cubic_interpolate_2d,
        in_axes=(0, None, None, None, None),
        out_axes=0,
    )(image_chw, locations_2xN, mode, cval, a)

    if has_channels:
        return out
    return out[0]
