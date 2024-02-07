import unittest
import cv2
from src import camera_id
from PIL import Image
import numpy as np


class TestCameraID(unittest.TestCase):
    def test_image_to_ID(self):
        test_cases = [
            {
                "image": "tests/examples/camera_01.png",
                "format": "str",
                "expected_output": "01"
            },
            {
                "image": "tests/examples/camera_45.png",
                "format": "int",
                "expected_output": 45
            }
        ]

        for test_case in test_cases:
            image = np.array(Image.open(test_case["image"]))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            output = camera_id.screenshot_to_ID(image, typ=test_case["format"])
            print(output)

            self.assertEqual(output, test_case["expected_output"])
