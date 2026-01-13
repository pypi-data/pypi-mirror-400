import sys
import unittest
import os
from pathlib import Path
from unittest.mock import patch
from tracebloc_package.utils.general_utils import get_paths, env_url


class TestGeneralUtils(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        current_dir = Path(__file__).parent
        test_models_path = os.path.join(current_dir, "test_models")
        if test_models_path not in sys.path:
            sys.path.insert(0, test_models_path)

        self.test_env = "development"
        self.test_token = "test_token_123"
        self.test_model_id = "test_model_123"
        self.test_dataset_id = "test_dataset_123"
        self.test_model = os.path.join(
            test_models_path, "tensorflow_functional_model.py"
        )

    def test_get_paths(self):
        """Test get_paths function with different scenarios"""
        # Test with valid model path
        current_dir = Path(__file__).parent
        test_models_path = os.path.join(current_dir, "test_models")
        model_path = os.path.join(test_models_path, "tensorflow_functional_model.py")

        paths = get_paths(path=model_path)

        # Verify the returned paths
        self.assertIsInstance(paths, tuple)
        self.assertEqual(len(paths), 4)
        self.assertEqual(paths[0], "tensorflow_functional_model")  # model name
        self.assertTrue(
            paths[1].endswith("tensorflow_functional_model.py")
        )  # full path
        self.assertEqual(paths[2], None)  # weights path
        self.assertEqual(paths[3], ".py")  # extension

        # Test with non-existent file
        non_existent_file = os.path.join(test_models_path, "non_existent_model.py")
        with self.assertRaises(FileNotFoundError):
            get_paths(path=non_existent_file)

        # Test with directory instead of file
        with self.assertRaises(FileNotFoundError):
            get_paths(path=test_models_path)

        # Test with empty path
        with self.assertRaises(ValueError):
            get_paths(path="")

        # Test with None path
        with self.assertRaises(ValueError):
            get_paths(path=None)

        # Test with invalid file extension
        invalid_ext_file = os.path.join(test_models_path, "test_file.txt")
        # Create temporary file for testing
        with open(invalid_ext_file, "w") as f:
            f.write("test content")
        try:
            with self.assertRaises(FileNotFoundError):
                get_paths(path=invalid_ext_file)
        finally:
            # Clean up temporary file
            if os.path.exists(invalid_ext_file):
                os.remove(invalid_ext_file)

        # Test with weights available
        paths_with_weights = get_paths(path=model_path, weights_available=True)
        self.assertTrue(
            paths_with_weights[2].endswith(("_weights.pkl", "_weights.pth"))
        )

        # Test with absolute vs relative path
        abs_path = os.path.abspath(model_path)
        rel_path = os.path.relpath(model_path)

        abs_result = get_paths(path=abs_path)
        rel_result = get_paths(path=rel_path)

        # Both should return the same model name and extension
        self.assertEqual(abs_result[0], rel_result[0])  # model name should match
        self.assertEqual(abs_result[3], rel_result[3])  # extension should match

    def test_env_url(self):
        """Test env_url function with different environments"""
        # Test local environment
        local_url = env_url("local")
        self.assertEqual(local_url, "http://127.0.0.1:8000/")

        # Test development environment
        dev_url = env_url("development")
        self.assertEqual(dev_url, "https://dev-api.tracebloc.io/")

        # Test staging environment
        staging_url = env_url("staging")
        self.assertEqual(staging_url, "https://stg-api.tracebloc.io/")

        # Test production environment
        prod_url = env_url("production")
        self.assertEqual(prod_url, "https://api.tracebloc.io/")

        # Test invalid environment
        invalid_url = env_url("invalid_env")
        self.assertEqual(invalid_url, None)

        # Test empty environment
        empty_url = env_url("")
        self.assertEqual(empty_url, "https://api.tracebloc.io/")

        # Test None environment
        none_url = env_url(None)
        self.assertEqual(none_url, None)

        # Test case sensitivity
        dev_url_upper = env_url("DEVELOPMENT")
        self.assertEqual(dev_url_upper, None)

        # Test with leading/trailing spaces
        dev_url_spaces = env_url("  development  ")
        self.assertEqual(dev_url_spaces, None)

    def tearDown(self):
        """Clean up after tests"""
        # Clean up any created test directories
        tmp_path = os.path.join(os.getcwd(), "tmp")
        if os.path.exists(tmp_path):
            import shutil

            shutil.rmtree(tmp_path)
