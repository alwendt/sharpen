# Competitive boundary reconstruction

## Problem

Let `G` be a grayscale image believed to have been formed by blurring and
downsampling an unknown high-resolution binary image `B`. Recover a plausible
`B` whose pixels are in `{0, 1}` and whose boundaries are simpler and sharper
than the transition bands in `G`.

The inverse problem is underdetermined: many binary images produce almost the
same grayscale observation. The reconstruction therefore needs both a forward
model and a geometric prior.

## Physical metaphors

### Vacuum packing

Black material is enclosed by a flexible membrane. White exerts pressure on
the membrane, removing small white gaps and consolidating black material.
Surface tension discourages long, jagged boundaries. Black material is not
attracted to itself; consolidation is a consequence of pressure and reduced
interfacial energy.

### Competing armies

Pure-black and pure-white pixels are secure territory. Each phase projects
strength into the ambiguous gray band. The reconstructed boundary lies where
the competing strengths balance. Local evidence from the observed grayscale
image reinforces one side or the other.

These metaphors describe the same two-phase variational system.

## Constraints

1. A source pixel that is exactly black is fixed black at every subpixel.
2. A source pixel that is exactly white is fixed white at every subpixel.
3. Only the grayscale transition region is mobile.
4. Material may cross boundaries between gray source pixels.
5. The reconstructed image must approximately reproduce `G` through the chosen
   blur and downsampling operator.
6. Short, smooth boundaries are preferred over noisy or interleaved phases.

Near-black and near-white pixels can optionally be treated as soft anchors,
because previous resampling may prevent nominally solid regions from reaching
the exact endpoint values.

## Initial energy

The prototype evolves a continuous black-membership field `u` in `[0, 1]` at
the requested output resolution. It approximately minimizes

```text
E(u) = lambda_d ||D(u) - g||^2
     + lambda_s integral |grad u|^2
     + lambda_b integral u^2 (1-u)^2
```

where:

- `g = 1 - G/255` is observed black density;
- `D` averages each high-resolution block back to source resolution;
- the gradient term supplies surface tension;
- the double-well term separates the phases toward zero and one;
- hard anchors overwrite `u` after every evolution step.

The final binary image is obtained by thresholding `u` at `0.5`.

This initial energy uses source-aligned block averaging only as a convenient
forward model. A stronger version should use an estimated point-spread function
followed by resampling, so that fidelity is measured against the actual image
formation process rather than independently inside each source block.

## Closely related literature

The components are established even if this particular reconstruction recipe
and application are not known to have a standard name:

- Chan and Vese, *Active Contours Without Edges* (2001),
  <https://doi.org/10.1109/83.902291>
- Analoui and Allebach, *Model-Based Halftoning Using Direct Binary Search*
  (1992), <https://doi.org/10.1117/12.135959>
- Merriman-Bence-Osher threshold dynamics and volume-preserving mean-curvature
  flow
- Mass-conserving Allen-Cahn and Cahn-Hilliard phase-field models
- Total-variation and perimeter regularization for binary reconstruction

Potential descriptive names include **competitive boundary reconstruction**,
**pressure-driven binary super-resolution**, and **mass-conserving phase
separation under downsampling constraints**.

## Next experiments

1. Replace block averaging with blur-kernel estimation and realistic resizing.
2. Add global or neighborhood mass conservation instead of per-block fidelity.
3. Compare phase-field evolution with direct binary search and level sets.
4. Use coarse-to-fine evolution for large images.
5. Penalize curvature or small connected components explicitly.
6. Measure source reconstruction error, boundary length, curvature, topology,
   and stability across parameter choices.
7. Construct synthetic binary ground truth, blur it, and quantify recovery
   independently of the motivating logo.

