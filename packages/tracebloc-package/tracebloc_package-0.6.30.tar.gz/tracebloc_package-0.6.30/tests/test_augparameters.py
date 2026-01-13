import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from io import StringIO
from tracebloc_package.linkModelDataSet import LinkModelDataSet
from tracebloc_package.utils.constants import (
    TENSORFLOW_FRAMEWORK,
    PYTORCH_FRAMEWORK,
    SKLEARN_FRAMEWORK,
    IMAGE_CLASSIFICATION,
)


class TestAugmentationParameters(unittest.TestCase):
    def setUp(self):
        current_dir = os.getcwd()
        self.test_kwargs = {
            "modelId": "test_model_id",
            "model": MagicMock(),
            "modelname": "tensorflow_functional_model",
            "datasetId": "test_dataset_id",
            "token": "test_token",
            "weights": False,
            "totalDatasetSize": 150,
            "total_images": {
                "edge1": 100,
                "edge2": 50,
            },
            "num_classes": 2,
            "class_names": {"class1": 70, "class2": 70},
            "data_shape": 224,
            "batchsize": 8,
            "model_path": f"{current_dir}/tests/test_models/tensorflow_functional_model.py",
            "url": "https://test.api.url/",
            "environment": "development",
            "framework": TENSORFLOW_FRAMEWORK,
            "model_type": "classification",
            "category": IMAGE_CLASSIFICATION,
            "loss": None,
            "model_id": "test_model_id",
            "hf_token": "test_hf_token",
            "utilisation_category": "low",
            "feature_modification": False,
            "table_name": "welds_data",
        }
        self.link_model = LinkModelDataSet(**self.test_kwargs)

    def test_samplewise_center(self):
        """Test samplewise_center parameter validation"""
        # Test valid boolean input
        self.link_model.samplewise_center(True)
        self.assertEqual(self.link_model._LinkModelDataSet__samplewise_center, True)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.samplewise_center("True")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "samplewise_center:Invalid input type", captured_output.getvalue()
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test PyTorch framework
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)
        captured_output = StringIO()
        sys.stdout = captured_output
        pytorch_model.samplewise_center(True)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "samplewise_center is not supported on pytorch", captured_output.getvalue()
        )

    def test_samplewise_std_normalization(self):
        """Test samplewise_std_normalization parameter validation"""
        # Test valid boolean input
        self.link_model.samplewise_std_normalization(True)
        self.assertEqual(
            self.link_model._LinkModelDataSet__samplewise_std_normalization, True
        )
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.samplewise_std_normalization(1)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "samplewise_std_normalization:Invalid input type",
            captured_output.getvalue(),
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_rotation_range(self):
        """Test rotation_range parameter validation"""
        # Test valid integer input
        self.link_model.rotation_range(45)
        self.assertEqual(self.link_model._LinkModelDataSet__rotation_range, 45)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.rotation_range(45.5)
        sys.stdout = sys.__stdout__
        self.assertIn("rotation_range:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test sklearn rotation range case
        captured_output = StringIO()
        sys.stdout = captured_output
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        sklearn_model = LinkModelDataSet(**sklearn_kwargs)
        sklearn_model.rotation_range(45)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "The parameter rotation_range is not supported on sklearn",
            captured_output.getvalue(),
        )
        self.assertTrue(sklearn_model._LinkModelDataSet__eligibility_passed)

    def test_width_shift_range(self):
        """Test width_shift_range parameter validation"""
        # Test valid float input
        self.link_model.width_shift_range(0.2)
        self.assertEqual(self.link_model._LinkModelDataSet__width_shift_range, 0.2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test valid integer input
        self.link_model.width_shift_range(2)
        self.assertEqual(self.link_model._LinkModelDataSet__width_shift_range, 2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.width_shift_range("0.2")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "width_shift_range:Invalid input type", captured_output.getvalue()
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_height_shift_range(self):
        """Test height_shift_range parameter validation"""
        # Test valid float input
        self.link_model.height_shift_range(0.2)
        self.assertEqual(self.link_model._LinkModelDataSet__height_shift_range, 0.2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test valid integer input
        self.link_model.height_shift_range(2)
        self.assertEqual(self.link_model._LinkModelDataSet__height_shift_range, 2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.height_shift_range("0.2")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "height_shift_range:Invalid input type", captured_output.getvalue()
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_brightness_range(self):
        """Test brightness_range parameter validation"""
        # Test valid tuple input for TensorFlow
        self.link_model.brightness_range((0.1, 0.9))
        self.assertEqual(
            self.link_model._LinkModelDataSet__brightness_range, str((0.1, 0.9))
        )
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test valid list input for TensorFlow
        self.link_model.brightness_range([0.1, 0.9])
        self.assertEqual(
            self.link_model._LinkModelDataSet__brightness_range, str([0.1, 0.9])
        )
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test PyTorch framework
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)
        pytorch_model.brightness_range(0.5)
        self.assertEqual(pytorch_model._LinkModelDataSet__brightness_range, str(0.5))
        self.assertTrue(pytorch_model._LinkModelDataSet__eligibility_passed)

    def test_shear_range(self):
        """Test shear_range parameter validation"""
        # Test valid float input
        self.link_model.shear_range(0.2)
        self.assertEqual(self.link_model._LinkModelDataSet__shear_range, 0.2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.shear_range(2)
        sys.stdout = sys.__stdout__
        self.assertIn("shear_range:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_zoom_range(self):
        """Test zoom_range parameter validation"""
        # Test valid float input
        self.link_model.zoom_range(0.2)
        self.assertEqual(self.link_model._LinkModelDataSet__zoom_range, 0.2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test valid list input
        self.link_model.zoom_range([0.8, 1.2])
        self.assertEqual(self.link_model._LinkModelDataSet__zoom_range, [0.8, 1.2])
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.zoom_range("0.2")
        sys.stdout = sys.__stdout__
        self.assertIn("zoom_range:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_channel_shift_range(self):
        """Test channel_shift_range parameter validation"""
        # Test valid float input
        self.link_model.channel_shift_range(0.2)
        self.assertEqual(self.link_model._LinkModelDataSet__channel_shift_range, 0.2)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.channel_shift_range(2)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "channel_shift_range:Invalid input type", captured_output.getvalue()
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test PyTorch with non-RGB image type
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)
        pytorch_model._LinkModelDataSet__data_type = "grayscale"
        captured_output = StringIO()
        sys.stdout = captured_output
        pytorch_model.channel_shift_range(0.2)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "channel_shift_range:You can not set channel_shift_range if image type is not rgb",
            captured_output.getvalue(),
        )

    def test_fill_mode(self):
        """Test fill_mode parameter validation"""
        link_model_kwargs = self.test_kwargs.copy()
        link_model = LinkModelDataSet(**link_model_kwargs)
        # Test valid input for TensorFlow
        link_model.fill_mode("nearest")
        self.assertEqual(link_model._LinkModelDataSet__fill_mode, "nearest")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test PyTorch framework
        link_model_kwargs["framework"] = PYTORCH_FRAMEWORK
        link_model = LinkModelDataSet(**link_model_kwargs)
        link_model.fill_mode("edge")
        self.assertNotEqual(link_model._LinkModelDataSet__fill_mode, "edge")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.fill_mode("invalid_mode")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "fill_mode:Please provide supported fill modes", captured_output.getvalue()
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_cval(self):
        """Test cval parameter validation"""
        # Test valid float input
        self.link_model.cval(0.5)
        self.assertEqual(self.link_model._LinkModelDataSet__cval, 0.5)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.cval(1)
        sys.stdout = sys.__stdout__
        self.assertIn("cval:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_horizontal_flip(self):
        """Test horizontal_flip parameter validation"""
        # Test valid boolean input
        self.link_model.horizontal_flip(True)
        self.assertEqual(self.link_model._LinkModelDataSet__horizontal_flip, True)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.horizontal_flip(1)
        sys.stdout = sys.__stdout__
        self.assertIn("horizontal_flip:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_vertical_flip(self):
        """Test vertical_flip parameter validation"""
        # Test valid boolean input
        self.link_model.vertical_flip(True)
        self.assertEqual(self.link_model._LinkModelDataSet__vertical_flip, True)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.vertical_flip(1)
        sys.stdout = sys.__stdout__
        self.assertIn("vertical_flip:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_rescale(self):
        """Test rescale parameter validation"""
        # Test valid float input
        self.link_model.rescale(1.0 / 255.0)
        self.assertEqual(self.link_model._LinkModelDataSet__rescale, 1.0 / 255.0)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.rescale("0.0039")
        sys.stdout = sys.__stdout__
        self.assertIn("rescale:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_shuffle(self):
        """Test shuffle parameter validation"""
        # Test valid boolean input
        self.link_model.shuffle(False)
        self.assertEqual(self.link_model._LinkModelDataSet__shuffle, False)
        self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output
        self.link_model.shuffle(1)
        sys.stdout = sys.__stdout__
        self.assertIn("shuffle:Invalid input type", captured_output.getvalue())
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)


if __name__ == "__main__":
    unittest.main()
