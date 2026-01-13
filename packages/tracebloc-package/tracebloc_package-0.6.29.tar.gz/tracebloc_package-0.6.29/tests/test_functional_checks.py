import unittest
import tempfile
import os
from unittest.mock import Mock
from tracebloc_package.model_file_checks.functional_checks import CheckModel
from tracebloc_package.utils.constants import (
    IMAGE_CLASSIFICATION,
    TEXT_CLASSIFICATION,
    TABULAR_CLASSIFICATION,
    OBJECT_DETECTION,
    KEYPOINT_DETECTION,
    SEMANTIC_SEGMENTATION,
)


class TestCheckModelCategorySpecificVariables(unittest.TestCase):
    def setUp(self):
        self.progress_bar = Mock()
        self.check_model = CheckModel(self.progress_bar)

    def test_image_size_fetched_for_cv_categories(self):
        """Test that image_size is fetched and kept for CV categories"""
        cv_categories = [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
            KEYPOINT_DETECTION,
            SEMANTIC_SEGMENTATION,
        ]

        for category in cv_categories:
            text = f"""
framework = "tensorflow"
category = "{category}"
output_classes = 10
image_size = 224
batch_size = 16
"""
            if category == KEYPOINT_DETECTION:
                text += "num_feature_points = 16"
            with self.subTest(category=category):
                # Create a temporary file with CV category and image_size
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as tmp_file:
                    tmp_file.write(text)
                    tmp_file_path = tmp_file.name

                try:
                    main_file, remove_lines, filelines = self.check_model.get_variables(
                        tmp_file_path
                    )
                    self.assertTrue(main_file)
                    self.assertEqual(self.check_model.category, category)
                    self.assertEqual(self.check_model.image_size, 224)
                finally:
                    os.unlink(tmp_file_path)

    def test_image_size_reset_for_non_cv_categories(self):
        """Test that image_size is reset to None for non-CV categories"""
        non_cv_categories = [TEXT_CLASSIFICATION, TABULAR_CLASSIFICATION]

        for category in non_cv_categories:
            text = f"""
framework = "tensorflow"
category = "{category}"
output_classes = 10
image_size = 224
batch_size = 16
"""
            if category == TEXT_CLASSIFICATION:
                text += "sequence_length = 512"
            else:
                text += "num_feature_points = 16"
            with self.subTest(category=category):
                # Create a temporary file with non-CV category and image_size
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as tmp_file:
                    tmp_file.write(text)
                    tmp_file_path = tmp_file.name

                try:
                    main_file, remove_lines, filelines = self.check_model.get_variables(
                        tmp_file_path
                    )
                    self.assertTrue(main_file)
                    self.assertEqual(self.check_model.category, category)
                    self.assertIsNone(self.check_model.image_size)
                finally:
                    os.unlink(tmp_file_path)

    def test_num_feature_points_fetched_for_tabular_category(self):
        """Test that num_feature_points is fetched and kept for tabular category"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
framework = "sklearn"
category = "tabular_classification"
output_classes = 5
num_feature_points = 100
batch_size = 16
"""
            )
            tmp_file_path = tmp_file.name

        try:
            main_file, remove_lines, filelines = self.check_model.get_variables(
                tmp_file_path
            )
            self.assertTrue(main_file)
            self.assertEqual(self.check_model.category, TABULAR_CLASSIFICATION)
            self.assertEqual(self.check_model.num_feature_points, 100)
        finally:
            os.unlink(tmp_file_path)

    def test_num_feature_points_reset_for_non_tabular_categories(self):
        """Test that num_feature_points is reset to None for non-tabular categories"""
        non_tabular_categories = [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
        ]

        for category in non_tabular_categories:
            with self.subTest(category=category):
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as tmp_file:
                    tmp_file.write(
                        f"""
framework = "tensorflow"
category = "{category}"
output_classes = 10
num_feature_points = 100
image_size = 224
batch_size = 16
"""
                    )
                    tmp_file_path = tmp_file.name

                try:
                    main_file, remove_lines, filelines = self.check_model.get_variables(
                        tmp_file_path
                    )
                    self.assertTrue(main_file)
                    self.assertEqual(self.check_model.category, category)
                    self.assertIsNone(self.check_model.num_feature_points)
                finally:
                    os.unlink(tmp_file_path)

    def test_sequence_length_fetched_for_text_category(self):
        """Test that sequence_length is fetched and kept for text category"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
framework = "tensorflow"
category = "text_classification"
output_classes = 3
sequence_length = 512
batch_size = 16
"""
            )
            tmp_file_path = tmp_file.name

        try:
            main_file, remove_lines, filelines = self.check_model.get_variables(
                tmp_file_path
            )
            self.assertTrue(main_file)
            self.assertEqual(self.check_model.category, TEXT_CLASSIFICATION)
            self.assertEqual(self.check_model.sequence_length, 512)
        finally:
            os.unlink(tmp_file_path)

    def test_sequence_length_reset_for_non_text_categories(self):
        """Test that sequence_length is reset to None for non-text categories"""
        non_text_categories = [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
        ]

        for category in non_text_categories:
            with self.subTest(category=category):
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as tmp_file:
                    tmp_file.write(
                        f"""
framework = "tensorflow"
category = "{category}"
output_classes = 10
sequence_length = 512
image_size = 224
batch_size = 16
"""
                    )
                    tmp_file_path = tmp_file.name

                try:
                    main_file, remove_lines, filelines = self.check_model.get_variables(
                        tmp_file_path
                    )
                    self.assertTrue(main_file)
                    self.assertEqual(self.check_model.category, category)
                    self.assertIsNone(self.check_model.sequence_length)
                finally:
                    os.unlink(tmp_file_path)

    def test_category_specific_validation_errors(self):
        """Test that appropriate validation errors are raised for missing category-specific variables"""

        # Test CV category without image_size
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
framework = "tensorflow"
category = "image_classification"
output_classes = 10
batch_size = 16
"""
            )
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(Exception) as context:
                self.check_model.get_variables(tmp_file_path)
            self.assertIn(
                "Image size parameter missing from file",
                str(context.exception),
            )
        finally:
            os.unlink(tmp_file_path)

        # Test tabular category without num_feature_points
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
framework = "sklearn"
category = "tabular_classification"
output_classes = 5
batch_size = 16
"""
            )
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(Exception) as context:
                self.check_model.get_variables(tmp_file_path)
            self.assertIn(
                "Number of feature points missing from file",
                str(context.exception),
            )
        finally:
            os.unlink(tmp_file_path)

        # Test text category without sequence_length
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
framework = "tensorflow"
category = "text_classification"
output_classes = 3
batch_size = 16
"""
            )
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(Exception) as context:
                self.check_model.get_variables(tmp_file_path)
            self.assertIn(
                "Sequence length parameter missing from file",
                str(context.exception),
            )
        finally:
            os.unlink(tmp_file_path)


if __name__ == "__main__":
    unittest.main()
