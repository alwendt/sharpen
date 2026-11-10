#!/usr/bin/env python3
"""Experimental binary reconstruction by competing phase evolution."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class Parameters:
    scale: int = 4
    iterations: int = 500
    learning_rate: float = 0.12
    data_weight: float = 6.0
    surface_tension: float = 0.8
    separation: float = 0.15
    anchor_epsilon: float = 0.0


def block_mean(field: np.ndarray, source_shape: tuple[int, int], scale: int) -> np.ndarray:
    """Reduce a scale-expanded field to source resolution by area averaging."""
    height, width = source_shape
    return field.reshape(height, scale, width, scale).mean(axis=(1, 3))


def laplacian(field: np.ndarray) -> np.ndarray:
    """Five-point Laplacian with edge replication at the image boundary."""
    padded = np.pad(field, 1, mode="edge")
    return (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - 4.0 * field
    )


def reconstruct(gray: np.ndarray, parameters: Parameters) -> tuple[np.ndarray, np.ndarray]:
    """Return a binary reconstruction and its continuous phase field."""
    if gray.ndim != 2:
        raise ValueError("gray input must be a two-dimensional array")
    if parameters.scale < 1:
        raise ValueError("scale must be at least one")
    if parameters.iterations < 0:
        raise ValueError("iterations cannot be negative")

    observed_black = 1.0 - gray.astype(np.float32) / 255.0
    scale = parameters.scale
    field = np.repeat(np.repeat(observed_black, scale, axis=0), scale, axis=1)

    epsilon = parameters.anchor_epsilon
    fixed_black_source = observed_black >= 1.0 - epsilon
    fixed_white_source = observed_black <= epsilon
    fixed_black = np.repeat(np.repeat(fixed_black_source, scale, axis=0), scale, axis=1)
    fixed_white = np.repeat(np.repeat(fixed_white_source, scale, axis=0), scale, axis=1)

    for _ in range(parameters.iterations):
        reduced = block_mean(field, observed_black.shape, scale)
        block_error = reduced - observed_black
        fidelity_force = np.repeat(np.repeat(block_error, scale, axis=0), scale, axis=1)

        # Derivative of the double-well potential u^2(1-u)^2.
        separation_force = 2.0 * field * (1.0 - field) * (1.0 - 2.0 * field)

        field += parameters.learning_rate * (
            parameters.surface_tension * laplacian(field)
            - parameters.data_weight * fidelity_force
            - parameters.separation * separation_force
        )
        np.clip(field, 0.0, 1.0, out=field)

        # Secure black and white territory is immutable.
        field[fixed_black] = 1.0
        field[fixed_white] = 0.0

    binary = field >= 0.5
    return binary, field


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source grayscale image")
    parser.add_argument("output", type=Path, help="output one-bit PNG")
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--learning-rate", type=float, default=0.12)
    parser.add_argument("--data-weight", type=float, default=6.0)
    parser.add_argument("--surface-tension", type=float, default=0.8)
    parser.add_argument("--separation", type=float, default=0.15)
    parser.add_argument("--anchor-epsilon", type=float, default=0.0)
    parser.add_argument("--preview", type=Path, help="optional continuous-field PNG")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parameters = Parameters(
        scale=args.scale,
        iterations=args.iterations,
        learning_rate=args.learning_rate,
        data_weight=args.data_weight,
        surface_tension=args.surface_tension,
        separation=args.separation,
        anchor_epsilon=args.anchor_epsilon,
    )

    with Image.open(args.input) as source:
        gray = np.asarray(source.convert("L"))

    binary, field = reconstruct(gray, parameters)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Pillow mode 1 uses nonzero for white, while the field uses one for black.
    Image.fromarray(~binary).save(args.output)

    if args.preview is not None:
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        preview = np.rint((1.0 - field) * 255.0).astype(np.uint8)
        Image.fromarray(preview, mode="L").save(args.preview)

    reduced = block_mean(binary.astype(np.float32), gray.shape, parameters.scale)
    target = 1.0 - gray.astype(np.float32) / 255.0
    rmse = float(np.sqrt(np.mean((reduced - target) ** 2)))
    print(f"wrote {args.output} ({binary.shape[1]}x{binary.shape[0]}, RMSE={rmse:.6f})")


if __name__ == "__main__":
    main()

