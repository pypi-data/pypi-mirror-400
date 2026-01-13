import unittest
from unittest.mock import Mock, patch, MagicMock
from tracebloc_package.user import User
from tracebloc_package.utils.constants import (
    IMAGE_CLASSIFICATION,
    TEXT_CLASSIFICATION,
    TABULAR_CLASSIFICATION,
    OBJECT_DETECTION,
    KEYPOINT_DETECTION,
    SEMANTIC_SEGMENTATION,
)


class TestUserUnifiedImageSize(unittest.TestCase):
    def setUp(self):
        # Mock the User class to avoid actual login and network calls
        with patch("tracebloc_package.user.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = '{"token": "test_token"}'
            self.user = User(
                environment="test", username="test@test.com", password="test"
            )

    def test_data_shape_assignment_for_cv_categories(self):
        """Test that __data_shape is assigned correctly for CV categories"""
        cv_categories = [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
            KEYPOINT_DETECTION,
            SEMANTIC_SEGMENTATION,
        ]

        for category in cv_categories:
            with self.subTest(category=category):
                # Mock the general_checks_obj
                mock_checks_obj = Mock()
                mock_checks_obj.image_size = 224
                mock_checks_obj.num_feature_points = 100
                mock_checks_obj.sequence_length = 512
                mock_checks_obj.batch_size = 16
                mock_checks_obj.model_type = "test"
                mock_checks_obj.model_id = "test_id"
                mock_checks_obj.hf_token = "test_token"
                mock_checks_obj.output_classes = 10
                mock_checks_obj.framework = "tensorflow"
                mock_checks_obj.category = category
                mock_checks_obj.model = Mock()
                mock_checks_obj.progress_bar = Mock()
                mock_checks_obj.tmp_file = "test_file"
                mock_checks_obj.tmp_file_path = "test_path"

                self.user._User__general_checks_obj = mock_checks_obj
                self.user._User__model_name = "test_model"
                self.user._User__token = "test_token"
                self.user._User__url = "http://test.com"
                self.user._User__message = "test"
                self.user._User__progress_bar = Mock()
                self.user._User__weights = False
                self.user._User__model_file_path = "test_path"
                self.user._User__weights_file_path = "test_weights"

                # Call the method
                self.user._User__set_model_val_params()

                # Verify that __data_shape is set to data_shape for CV categories
                self.assertEqual(self.user._User__data_shape, 224)

    def test_data_shape_assignment_for_tabular_category(self):
        """Test that __data_shape is assigned to num_feature_points for tabular category"""
        # Mock the general_checks_obj
        mock_checks_obj = Mock()
        mock_checks_obj.image_size = 224
        mock_checks_obj.num_feature_points = 100
        mock_checks_obj.sequence_length = 512
        mock_checks_obj.batch_size = 16
        mock_checks_obj.model_type = "test"
        mock_checks_obj.model_id = "test_id"
        mock_checks_obj.hf_token = "test_token"
        mock_checks_obj.output_classes = 5
        mock_checks_obj.framework = "sklearn"
        mock_checks_obj.category = TABULAR_CLASSIFICATION
        mock_checks_obj.model = Mock()
        mock_checks_obj.progress_bar = Mock()
        mock_checks_obj.tmp_file = "test_file"
        mock_checks_obj.tmp_file_path = "test_path"

        self.user._User__general_checks_obj = mock_checks_obj
        self.user._User__model_name = "test_model"
        self.user._User__token = "test_token"
        self.user._User__url = "http://test.com"
        self.user._User__message = "test"
        self.user._User__progress_bar = Mock()
        self.user._User__weights = False
        self.user._User__model_file_path = "test_path"
        self.user._User__weights_file_path = "test_weights"

        # Call the method
        self.user._User__set_model_val_params()

        # Verify that __data_shape is set to num_feature_points for tabular category
        self.assertEqual(self.user._User__data_shape, 100)

    def test_data_shape_assignment_for_text_category(self):
        """Test that __data_shape is assigned to sequence_length for text category"""
        # Mock the general_checks_obj
        mock_checks_obj = Mock()
        mock_checks_obj.image_size = 224
        mock_checks_obj.num_feature_points = 100
        mock_checks_obj.sequence_length = 512
        mock_checks_obj.batch_size = 16
        mock_checks_obj.model_type = "test"
        mock_checks_obj.model_id = "test_id"
        mock_checks_obj.hf_token = "test_token"
        mock_checks_obj.output_classes = 3
        mock_checks_obj.framework = "tensorflow"
        mock_checks_obj.category = TEXT_CLASSIFICATION
        mock_checks_obj.model = Mock()
        mock_checks_obj.progress_bar = Mock()
        mock_checks_obj.tmp_file = "test_file"
        mock_checks_obj.tmp_file_path = "test_path"

        self.user._User__general_checks_obj = mock_checks_obj
        self.user._User__model_name = "test_model"
        self.user._User__token = "test_token"
        self.user._User__url = "http://test.com"
        self.user._User__message = "test"
        self.user._User__progress_bar = Mock()
        self.user._User__weights = False
        self.user._User__model_file_path = "test_path"
        self.user._User__weights_file_path = "test_weights"

        # Call the method
        self.user._User__set_model_val_params()

        # Verify that __data_shape is set to sequence_length for text category
        self.assertEqual(self.user._User__data_shape, 512)

    def test_model_upload_params_use_unified_data_shape(self):
        """Test that model_upload_params uses the unified __data_shape for both data_shape and num_feature_points"""
        # Mock the general_checks_obj for tabular category
        mock_checks_obj = Mock()
        mock_checks_obj.image_size = 224
        mock_checks_obj.num_feature_points = 100
        mock_checks_obj.sequence_length = 512
        mock_checks_obj.batch_size = 16
        mock_checks_obj.model_type = "test"
        mock_checks_obj.model_id = "test_id"
        mock_checks_obj.hf_token = "test_token"
        mock_checks_obj.output_classes = 5
        mock_checks_obj.framework = "sklearn"
        mock_checks_obj.category = TABULAR_CLASSIFICATION
        mock_checks_obj.model = Mock()
        mock_checks_obj.progress_bar = Mock()
        mock_checks_obj.tmp_file = "test_file"
        mock_checks_obj.tmp_file_path = "test_path"

        self.user._User__general_checks_obj = mock_checks_obj
        self.user._User__model_name = "test_model"
        self.user._User__token = "test_token"
        self.user._User__url = "http://test.com"
        self.user._User__message = "test"
        self.user._User__progress_bar = Mock()
        self.user._User__weights = False
        self.user._User__model_file_path = "test_path"
        self.user._User__weights_file_path = "test_weights"

        # Call the method
        self.user._User__set_model_val_params()

        # Verify that both data_shape and num_feature_points in model_upload_params use the unified value
        self.assertEqual(self.user._User__model_upload_params["data_shape"], 100)
        self.assertEqual(
            self.user._User__model_upload_params["num_feature_points"], 100
        )


if __name__ == "__main__":
    unittest.main()
