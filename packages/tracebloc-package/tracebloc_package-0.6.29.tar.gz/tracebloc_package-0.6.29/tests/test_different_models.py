import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys

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


class TestAllModel:
    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_kp_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with PyTorch model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/kp_model")
        model_name = "kp_model"
        ext = ".py"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}.py",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 2
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_kp_heatmap_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with PyTorch model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/kp_heatmap")
        model_name = "kp_heatmap"
        ext = ".py"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}.py",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 2
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_kp_rcnn_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with PyTorch model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/kp_rcnn")
        model_name = "kp_rcnn"
        ext = ".py"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}.py",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 2
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    def test_upload_tabular_pytorch_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with TensorFlow model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/tabular_pytorch_model")
        model_name = "tabular_pytorch_model"
        ext = ".py"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}.py",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 2
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_ob_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploading object detection model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/ob_model")
        model_name = "ob_model"
        ext = ".zip"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}{ext}",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 10
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_text_classification_model(
        self, mock_post, mock_get_paths, mock_user
    ):
        """Test uploading text classification model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/text_classification_model")
        model_name = "text_classification_model"
        ext = ".py"
        model_id = f"{model_name}_123"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        mock_get_paths.return_value = (
            model_name,  # model_name
            f"{model_path}{ext}",  # model_file_path
            None,  # weights_file_path
            ext,  # ext
        )

        # Set up progress bar
        mock_progress_bar = MagicMock()
        mock_progress_bar.total = 8
        mock_progress_bar.desc = "Model Checks Progress"
        setattr(mock_user, "_User__progress_bar", mock_progress_bar)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Create response JSON with model_name
        response_data = {
            "status": "success",
            "text": "Model uploaded successfully",
            "check_status": True,
            "model_name": model_id,
        }

        # Mock successful API response with proper content
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(response_data).encode("utf-8")
        mock_post.return_value = mock_response

        # Mock model validator with tmp directory
        mock_validator = MagicMock()
        mock_validator.received_model_name = model_id
        mock_validator.utilisation_category = "low"
        mock_validator.validate_model_file.return_value = True
        mock_validator.classes = 2
        mock_validator.tmp_file_path = tmp_dir

        # Mock task_classes_dict
        mock_task_dict = MagicMock()
        mock_task_dict.get.return_value = lambda **kwargs: mock_validator

        try:
            with patch(
                "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                mock_task_dict,
            ):
                mock_user.uploadModel(model_path)

                # Verify method calls
                mock_get_paths.assert_called_once_with(
                    path=model_path, weights_available=False
                )
                mock_post.assert_called()

                # Verify the model was loaded and checks were performed
                assert getattr(mock_user, "_User__general_checks_obj") is not None
                assert getattr(mock_user, "_User__model") is not None

                # Verify the model_id was set correctly
                assert getattr(mock_user, "_User__model_id") == model_id
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)
