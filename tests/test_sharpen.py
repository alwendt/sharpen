import unittest

import numpy as np

from sharpen import Parameters, reconstruct


class ReconstructTests(unittest.TestCase):
    def test_output_is_binary_and_scaled(self) -> None:
        gray = np.array([[0, 128, 255]], dtype=np.uint8)
        binary, field = reconstruct(gray, Parameters(scale=3, iterations=10))

        self.assertEqual(binary.shape, (3, 9))
        self.assertEqual(field.shape, binary.shape)
        self.assertEqual(binary.dtype, np.dtype(bool))

    def test_pure_pixels_are_immutable(self) -> None:
        gray = np.array([[0, 127, 255], [255, 128, 0]], dtype=np.uint8)
        binary, field = reconstruct(gray, Parameters(scale=4, iterations=25))

        self.assertTrue(np.all(field[0:4, 0:4] == 1.0))
        self.assertTrue(np.all(field[0:4, 8:12] == 0.0))
        self.assertTrue(np.all(field[4:8, 0:4] == 0.0))
        self.assertTrue(np.all(field[4:8, 8:12] == 1.0))
        self.assertTrue(np.all(binary[0:4, 0:4]))
        self.assertFalse(np.any(binary[0:4, 8:12]))


if __name__ == "__main__":
    unittest.main()

