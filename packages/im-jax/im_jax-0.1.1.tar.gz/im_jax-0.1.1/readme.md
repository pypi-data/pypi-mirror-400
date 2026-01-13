# im_jax

Image interpolation utilities in JAX, focused on bicubic interpolation with predictable behavior at boundaries.
This is a pure JAX implementation comparable to `jax.scipy.ndimage.map_coordinates(..., order=3)`.
Linear interpolation is already available in `dm_pix`; this repository focuses on bicubic interpolation.

## Bicubic interpolation

Bicubic interpolation estimates pixel values from a 4x4 neighborhood, producing smoother results than bilinear
methods while preserving local gradients. This implementation is designed for batched, JAX-native workloads and
keeps shapes and dtypes stable across `jit`, `vmap`, and `grad`.

## Installation

```bash
pip install im_jax
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

```python
import jax.numpy as jnp
from im_jax import flat_nd_cubic_interpolate

image = jnp.arange(12.0, dtype=jnp.float32).reshape(3, 4)
locations = jnp.array([[0.5, 1.25], [1.0, 2.5]], dtype=jnp.float32)
values = flat_nd_cubic_interpolate(image, locations)
```

## Benchmarks and validation

See `docs/interpolation_benchmarks.ipynb` for accuracy checks, validation against reference results, and
runtime measurements.

## Tests

```bash
pytest
```

## Release / PyPI

This project is published to PyPI automatically from GitHub tags.

- Create a tag like `v0.1.0` and push it.
- GitHub Actions builds and publishes the release to PyPI.

## License

GPL-3.0-only. See `LICENSE`.
