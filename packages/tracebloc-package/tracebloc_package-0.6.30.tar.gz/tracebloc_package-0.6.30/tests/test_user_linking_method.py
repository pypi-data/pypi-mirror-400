import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys
import builtins

from tracebloc_package.linkModelDataSet import LinkModelDataSet

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from tracebloc_package.user import User

# Mock credentials for testing
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "test_password"
TEST_TOKEN = "dummy_test_token_12345"


@pytest.fixture
def mock_user():
    """Create a mock user that simulates the interactive login"""
    # Mock the input and getpass to simulate user entering credentials
    with patch("builtins.input", return_value=TEST_EMAIL), patch(
        "getpass.getpass", return_value=TEST_PASSWORD
    ), patch("requests.post") as mock_post:
        # Mock successful login response
        mock_post.return_value = MagicMock(
            status_code=200, text=json.dumps({"token": TEST_TOKEN})
        )

        # Create user instance which will trigger the mocked input prompts
        user = User()
        return user


class TestlinkModelDataset:
    def test_link_model_dataset_passed(self, mock_user):
        """Test linking model with dataset using TensorFlow model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/tensorflow_functional_model"
        )
        model_name = "tensorflow_functional_model"
        model_id = f"{model_name}_123"
        dataset_id = "test_dataset_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Create mock model
        mock_model = MagicMock()
        mock_model.count_params.return_value = 1000000  # 1M parameters

        # Ensure mock_user is logged in and has required attributes
        setattr(mock_user, "_User__token", "test_token")
        setattr(mock_user, "_User__model_id", model_id)
        setattr(mock_user, "_User__model_name", model_name)
        setattr(mock_user, "_User__framework", "tensorflow")
        setattr(mock_user, "_User__category", "image_classification")
        setattr(mock_user, "_User__classes", 2)
        setattr(mock_user, "_User__model", mock_model)

        # Set additional required attributes for linkModelDataset
        setattr(mock_user, "_User__model_id_llm", model_id)
        setattr(mock_user, "_User__hf_token", None)
        setattr(mock_user, "_User__weights", False)
        setattr(mock_user, "_User__totalDatasetSize", 0)
        setattr(mock_user, "_User__total_images", {})
        setattr(mock_user, "_User__num_classes", 0)
        setattr(mock_user, "_User__class_names", {})
        setattr(mock_user, "_User__data_shape", (224, 224, 3))
        setattr(mock_user, "_User__batch_size", 32)
        setattr(mock_user, "_User__model_path", model_path)
        setattr(mock_user, "_User__url", "https://api.tracebloc.io/")
        setattr(mock_user, "_User__environment", "production")
        setattr(mock_user, "_User__model_type", "functional")
        setattr(mock_user, "_User__loss", None)
        setattr(mock_user, "_User__utilisation_category", "standard")
        setattr(mock_user, "_User__feature_modification", False)
        setattr(mock_user, "_User__table_name", "welds_data")
        setattr(mock_user, "_User__ext", ".h5")
        setattr(mock_user, "_User__features", {"input_shape": (224, 224, 3)})

        try:
            with patch("requests.post") as mock_post, patch(
                "tracebloc_package.utils.general_utils.getImagesCount"
            ) as mock_get_images:
                # Mock successful dataset linking response
                mock_post.return_value = MagicMock(
                    status_code=200,
                    content=json.dumps(
                        {
                            "status": "passed",
                            "total_images": {"edge1": 100},
                            "datasetClasses": 2,
                            "class_names": {"class1": 50, "class2": 50},
                            "datasetShape": (224, 224, 3),
                            "outputClass": 2,
                            "inputShape": (224, 224, 3),
                            "allow_feature_modification": False,
                            "table_name": "welds_data",
                        }
                    ).encode("utf-8"),
                )

                # Mock getImagesCount to return total images
                mock_get_images.return_value = 100

                result = mock_user.linkModelDataset(dataset_id)

                # Verify API call
                mock_post.assert_called()

                # Verify dataset properties were set
                assert result is not None
                assert isinstance(result, LinkModelDataSet)
                assert getattr(mock_user, "_User__total_images") == {"edge1": 100}
                assert getattr(mock_user, "_User__num_classes") == 2
                assert getattr(mock_user, "_User__class_names") == {
                    "class1": 50,
                    "class2": 50,
                }
                assert getattr(mock_user, "_User__totalDatasetSize") == 100

        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    def test_link_model_dataset_failed(self, mock_user):
        """Test linking model with dataset using TensorFlow model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/tensorflow_functional_model"
        )
        model_name = "tensorflow_functional_model"
        model_id = f"{model_name}_123"
        dataset_id = "test_dataset_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Create mock model
        mock_model = MagicMock()
        mock_model.count_params.return_value = 1000000  # 1M parameters

        # Ensure mock_user is logged in and has required attributes
        setattr(mock_user, "_User__token", "test_token")
        setattr(mock_user, "_User__model_id", model_id)
        setattr(mock_user, "_User__model_name", model_name)
        setattr(mock_user, "_User__framework", "tensorflow")
        setattr(mock_user, "_User__category", "image_classification")
        setattr(mock_user, "_User__classes", 2)
        setattr(mock_user, "_User__model", mock_model)

        # Set additional required attributes for linkModelDataset
        setattr(mock_user, "_User__model_id_llm", model_id)
        setattr(mock_user, "_User__hf_token", None)
        setattr(mock_user, "_User__weights", False)
        setattr(mock_user, "_User__totalDatasetSize", 0)
        setattr(mock_user, "_User__total_images", {})
        setattr(mock_user, "_User__num_classes", 0)
        setattr(mock_user, "_User__class_names", {})
        setattr(mock_user, "_User__data_shape", (224, 224, 3))
        setattr(mock_user, "_User__batch_size", 32)
        setattr(mock_user, "_User__model_path", model_path)
        setattr(mock_user, "_User__url", "https://api.tracebloc.io/")
        setattr(mock_user, "_User__environment", "production")
        setattr(mock_user, "_User__model_type", "functional")
        setattr(mock_user, "_User__loss", None)
        setattr(mock_user, "_User__utilisation_category", "standard")
        setattr(mock_user, "_User__feature_modification", False)
        setattr(mock_user, "_User__table_name", "welds_data")
        setattr(mock_user, "_User__ext", ".h5")
        setattr(mock_user, "_User__features", {"input_shape": (224, 224, 3)})

        try:
            with patch("requests.post") as mock_post, patch(
                "builtins.print"
            ) as mock_print, patch(
                "tracebloc_package.utils.general_utils.getImagesCount"
            ) as mock_get_images:
                # Mock successful dataset linking response
                mock_post.return_value = MagicMock(
                    status_code=200,
                    content=json.dumps(
                        {
                            "status": "failed",
                            "datasetClasses": 2,
                            "datasetShape": (224, 224, 3),
                            "outputClass": 3,
                            "inputShape": (224, 224, 2),
                        }
                    ).encode("utf-8"),
                )

                # Mock getImagesCount to return total images
                mock_get_images.return_value = 100

                result = mock_user.linkModelDataset(dataset_id)

                # Verify API call
                mock_post.assert_called()

                # Check that the correct message was printed
                mock_print.assert_called_with(
                    "Please change your model parameters to match the datasets parameters."
                )

                # Verify dataset properties were set
                assert result is None

        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    def test_link_model_dataset_no_model(self, mock_user):
        """Test linking dataset when no model is uploaded"""
        # Ensure no model ID is set
        setattr(mock_user, "_User__model_id", None)

        result = mock_user.linkModelDataset("test_dataset_123")
        assert result is None

    def test_check_model_failing_case_400(self, mock_user):
        """Test __check_model method when API response is 400"""
        # Set a valid model ID for the test
        setattr(mock_user, "_User__model_id", "valid_model_id")
        test_dataset_id = "test_dataset_123"

        with patch("requests.post") as mock_post, patch(
            "builtins.print"
        ) as mock_print:  # Mock print to capture output
            # Mock API response with status code 400
            mock_post.return_value = MagicMock(status_code=400)

            # Call the private method directly for testing
            mock_user._User__check_model(test_dataset_id)

            # Check that the correct message was printed
            mock_print.assert_called_with(
                f"Please provide a valid dataset ID.\nThere is no dataset with ID: {test_dataset_id}.\n"
            )

    def test_check_model_failing_case_409(self, mock_user):
        """Test __check_model method when API response is 409"""
        # Set a valid model ID for the test
        setattr(mock_user, "_User__model_id", "valid_model_id")
        test_dataset_id = "test_dataset_123"

        with patch("requests.post") as mock_post, patch(
            "builtins.print"
        ) as mock_print:  # Mock print to capture output
            # Mock API response with status code 409
            mock_post.return_value = MagicMock(status_code=409)

            # Call the private method directly for testing
            mock_user._User__check_model(test_dataset_id)

            # Check that the correct message was printed
            mock_print.assert_called_with(
                f"Model Type and Dataset Category mismatched.\nPlease provide a valid model for dataset or choose different dataset.\nred"
            )

    def test_check_model_failing_case_300(self, mock_user):
        """Test __check_model method when API response is 300"""
        # Set a valid model ID for the test
        setattr(mock_user, "_User__model_id", "valid_model_id")
        test_dataset_id = "test_dataset_123"

        with patch("requests.post") as mock_post, patch(
            "builtins.print"
        ) as mock_print:  # Mock print to capture output
            # Mock API response with status code 300
            mock_post.return_value = MagicMock(status_code=300)

            # Call the private method directly for testing
            mock_user._User__check_model(test_dataset_id)

            # Check that the correct message was printed
            mock_print.assert_called_with("Error Occurred. Linking Failed!")
