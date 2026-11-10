# sharpen

Techniques to recover blurred images that were originally black and white.

The motivating case is a low-resolution grayscale observation produced by
blurring and downsampling a sharp, binary logo. `sharpen` reconstructs a
higher-resolution image containing only pure black and pure white.

## Working model

The current experiment treats black and white as competing phases:

- Completely black and completely white source pixels are immutable anchors.
- Gray pixels form a disputed transition region.
- Material may move across the boundaries of the original pixels.
- Interfacial energy acts like surface tension, shortening and smoothing the
  boundary between the phases.
- A data-fidelity force keeps the reconstructed image consistent with the
  observed grayscale image when reduced to the source resolution.

This is closer to pressure-driven phase separation than to particles attracting
one another through gravity. See [THEORY.md](THEORY.md) for the formulation and
related literature.

## Try the prototype

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 sharpen.py input.png output.png --scale 4 --iterations 500
```

Useful options:

```text
--scale N              output pixels per source pixel in each dimension
--iterations N         number of phase-field evolution steps
--data-weight X        strength of agreement with source block averages
--surface-tension X    strength of boundary smoothing
--separation X         strength driving values toward black or white
--anchor-epsilon X     near-zero tolerance for immutable source pixels
--preview FILE         optional grayscale phase-field preview
```

The output PNG is mode `1`: every pixel is either black or white. The preview,
if requested, shows the continuous field immediately before thresholding.

## Status

This is an initial research prototype, not a finished restoration tool. Its
first purpose is to make the proposed physical model concrete and measurable.
The block-average fidelity term will eventually be replaced by an explicit
blur/downsampling forward model, and the optimizer needs multiscale and
mass-conserving variants.
