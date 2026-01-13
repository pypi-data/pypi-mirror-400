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


class TestUploadModel:
    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    @pytest.mark.filterwarnings("ignore")
    def test_upload_pytorch_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with PyTorch model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/pytorch_model")
        model_name = "pytorch_model"
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
    def test_upload_tensorflow_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with TensorFlow model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/tensorflow_functional_model"
        )
        model_name = "tensorflow_functional_model"
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
    def test_upload_sklearn_model(self, mock_post, mock_get_paths, mock_user):
        """Test uploadModel method with sklearn model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/sklearn_model")
        model_name = "sklearn_model"
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
    def test_upload_model_file_not_found(self, mock_get_paths, mock_user):
        """Test model upload with non-existent file"""
        current_dir = Path(__file__).parent
        non_existent_file = os.path.join(
            current_dir, "test_models/non_existent_model.py"
        )

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Ensure mock_user is logged in
        setattr(mock_user, "_User__token", "test_token")

        # Set up mock_get_paths to raise FileNotFoundError
        def raise_file_not_found(*args, **kwargs):
            raise FileNotFoundError(
                f"[Errno 2] No such file or directory: '{non_existent_file}'"
            )

        mock_get_paths.side_effect = raise_file_not_found

        try:
            with pytest.raises(Exception) as exc_info:
                mock_user.uploadModel(non_existent_file)
            error_message = str(exc_info.value)
            assert (
                f"[Errno 2] No such file or directory: '{non_existent_file}'"
                in error_message
            )
        finally:
            # Clean up only the temporary directory
            if os.path.exists(tmp_dir):
                import shutil

                shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_framework_empty(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/invalid_model_empty_framework"
        )
        model_name = "invalid_model_empty_framework"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Model checks failed with error:\n Framework parameter missing from file"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_cat_empty(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/invalid_model_empty_cat")
        model_name = "invalid_model_empty_cat"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Model checks failed with error:\n Category parameter missing from file"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_classes_empty(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/invalid_model_empty_classes"
        )
        model_name = "invalid_model_empty_classes"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Model checks failed with error:\n Output classes parameter missing from file"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_input_empty(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/invalid_model_empty_input")
        model_name = "invalid_model_empty_input"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Image size parameter missing from file"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_num_features_empty(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(
            current_dir, "test_models/invalid_model_empty_num_features"
        )
        model_name = "invalid_model_empty_num_features"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Model checks failed with error:\n Number of keypoints missing from file"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @pytest.mark.filterwarnings("ignore")
    def test_run_general_model_checks_failure(self, mock_user):
        """Test that model upload fails appropriately with invalid model"""
        current_dir = Path(__file__).parent
        model_path = os.path.join(current_dir, "test_models/missing_arg_model")
        model_name = "missing_arg_model"
        ext = ".py"

        # Create a temporary directory for test files
        tmp_dir = os.path.join(current_dir, "test_models", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Set up mock_get_paths return value
        with patch("tracebloc_package.user.get_paths") as mock_get_paths:
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

            # Mock model validator with tmp directory
            mock_validator = MagicMock()

            # Mock task_classes_dict
            mock_task_dict = MagicMock()
            mock_task_dict.get.return_value = lambda **kwargs: mock_validator

            try:
                with patch(
                    "tracebloc_package.utils.model_upload_utils.task_classes_dict",
                    mock_task_dict,
                ):
                    mock_user.uploadModel(model_path)

                    # Verify the upload failed
                    assert mock_user._User__message is not None
                    assert (
                        "Model checks failed with error:\n main file not found"
                        in mock_user._User__message
                    )

            finally:
                # Clean up only the temporary directory
                if os.path.exists(tmp_dir):
                    import shutil

                    shutil.rmtree(tmp_dir)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    def test_upload_sklearn_model_with_weights_error(
        self, mock_post, mock_get_paths, mock_user
    ):
        """Test sklearn model upload with weights=True but weights file doesn't exist"""
        # Mock the API response for successful upload
        mock_post.return_value.status_code = 202
        mock_post.return_value.content = json.dumps(
            {
                "text": "Model uploaded successfully",
                "check_status": True,
                "model_name": "test_sklearn_model",
            }
        ).encode()

        # Set up mock_get_paths return value with weights path
        mock_get_paths.return_value = (
            "test_sklearn_model",  # model_name
            "./test_sklearn_model.py",  # model_file_path
            "./test_sklearn_model_weights.pkl",  # weights_file_path (but file doesn't exist)
            ".py",  # extension
        )

        # Mock the model checks to pass
        with patch("tracebloc_package.user.CheckModel") as mock_check_model:
            mock_check_instance = mock_check_model.return_value
            mock_check_instance.model_func_checks.return_value = (
                True,
                "Success",
                "test_sklearn_model",
                None,
            )
            mock_check_instance.data_shape = 224
            mock_check_instance.batch_size = 16
            mock_check_instance.model_type = "linear"
            mock_check_instance.model_id = "test_model_id"
            mock_check_instance.hf_token = ""
            mock_check_instance.output_classes = 2
            mock_check_instance.framework = "sklearn"
            mock_check_instance.category = "tabular_classification"
            mock_check_instance.progress_bar = None
            mock_check_instance.tmp_file = "/tmp/test"
            mock_check_instance.tmp_file_path = "/tmp/test"
            mock_check_instance.num_feature_points = 10
            mock_check_instance.model = "test_model"

            # Mock the model upload class to raise the weights error
            with patch("tracebloc_package.user.task_classes_dict") as mock_task_dict:
                mock_upload_class = MagicMock()
                mock_upload_instance = mock_upload_class.return_value
                mock_upload_instance.validate_model_file.side_effect = Exception(
                    "Weights file not found"
                )
                mock_task_dict.get.return_value = mock_upload_class

                # Test the upload with weights=True - should raise exception
                with pytest.raises(Exception, match="Weights file not found"):
                    mock_user.uploadModel("test_sklearn_model", weights=True)

    @patch("tracebloc_package.user.get_paths")
    @patch("requests.post")
    def test_upload_sklearn_model_with_weights_success(
        self, mock_post, mock_get_paths, mock_user
    ):
        """Test sklearn model upload with weights=True and weights file exists"""
        # Mock the API response for successful upload
        mock_post.return_value.status_code = 202
        mock_post.return_value.content = json.dumps(
            {
                "text": "Model uploaded successfully",
                "check_status": True,
                "model_name": "test_sklearn_model",
            }
        ).encode()

        # Set up mock_get_paths return value with weights path
        mock_get_paths.return_value = (
            "test_sklearn_model",  # model_name
            "./test_sklearn_model.py",  # model_file_path
            "./test_sklearn_model_weights.pkl",  # weights_file_path
            ".py",  # extension
        )

        # Mock the model checks to pass
        with patch("tracebloc_package.user.CheckModel") as mock_check_model:
            # Configure the mock to return a proper instance
            mock_check_instance = MagicMock()
            mock_check_instance.model_func_checks.return_value = (
                True,
                "Success",
                "test_sklearn_model",
                None,
            )
            mock_check_instance.data_shape = 69
            mock_check_instance.batch_size = 16
            mock_check_instance.model_type = "linear"
            mock_check_instance.model_id = "test_model_id"
            mock_check_instance.hf_token = ""
            mock_check_instance.output_classes = 2
            mock_check_instance.framework = "sklearn"
            mock_check_instance.category = "tabular_classification"
            mock_check_instance.progress_bar = None
            mock_check_instance.tmp_file = "/tmp/test"
            mock_check_instance.tmp_file_path = "/tmp/test"
            mock_check_instance.num_feature_points = 69
            mock_check_instance.model = "test_model"

            # Make the constructor return our mock instance
            mock_check_model.return_value = mock_check_instance

            # Mock the model upload class to succeed
            with patch("tracebloc_package.user.task_classes_dict") as mock_task_dict:
                mock_upload_class = MagicMock()
                mock_upload_instance = mock_upload_class.return_value
                mock_upload_instance.validate_model_file.return_value = None
                mock_upload_instance.received_model_name = "test_model_id"
                mock_upload_instance.utilisation_category = "low"
                mock_task_dict.get.return_value = mock_upload_class

                # Test the upload with weights=True
                mock_user.uploadModel("test_sklearn_model", weights=True)
                # Verify that the model validation was called
                mock_upload_instance.validate_model_file.assert_called_once()
