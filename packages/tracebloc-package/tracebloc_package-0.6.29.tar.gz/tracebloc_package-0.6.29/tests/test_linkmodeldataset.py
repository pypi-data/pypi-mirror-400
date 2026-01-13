import unittest
from unittest.mock import patch, MagicMock
import json
import os
import requests
from pathlib import Path

from tracebloc_package.linkModelDataSet import LinkModelDataSet
from tracebloc_package.utils.constants import (
    TENSORFLOW_FRAMEWORK,
    PYTORCH_FRAMEWORK,
    SKLEARN_FRAMEWORK,
    IMAGE_CLASSIFICATION,
    TABULAR_CLASSIFICATION,
    TEXT_CLASSIFICATION,
    CONSTANT,
    STANDARD,
    TYPE,
    VALUE,
)
from io import StringIO
import sys


class TestLinkModelDataSet(unittest.TestCase):
    def setUp(self):
        current_dir = os.getcwd()
        # Setup default test parameters
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

        # Mock the __images_per_edge variable as a dictionary
        self.link_model = LinkModelDataSet(**self.test_kwargs)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.link_model.tmp_path):
            import shutil

            shutil.rmtree(self.link_model.tmp_path)
        if os.path.exists(self.link_model.tmp_path):
            os.remove(self.link_model.tmp_path)

    def test_initialization(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test default initialization values
        self.assertEqual(link_model._LinkModelDataSet__framework, TENSORFLOW_FRAMEWORK)
        self.assertEqual(link_model._LinkModelDataSet__epochs, 10)
        self.assertEqual(link_model._LinkModelDataSet__cycles, 1)
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "sgd")
        self.assertEqual(link_model._LinkModelDataSet__validation_split, 0.04)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_reset_training_plan(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Modify some parameters
        link_model._LinkModelDataSet__epochs = 20
        link_model._LinkModelDataSet__cycles = 2
        link_model._LinkModelDataSet__optimizer = "adam"

        # Reset training plan
        link_model.resetTrainingPlan()

        # Verify reset values
        self.assertEqual(link_model._LinkModelDataSet__epochs, 10)
        self.assertEqual(link_model._LinkModelDataSet__cycles, 1)
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "sgd")

    def test_experiment_name(self):
        """Test experiment name validation"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid experiment name
        link_model.experimentName("test_experiment")
        self.assertEqual(link_model._LinkModelDataSet__name, "test_experiment")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test empty experiment name
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.experimentName("")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "experimentName:experiment name cannot be empty\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.experimentName(123)
        sys.stdout = sys.__stdout__
        self.assertIn("experimentName:Invalid input type\n", captured_output.getvalue())
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_objective(self):
        """Test objective validation"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid objective
        link_model.objective("classification")
        self.assertEqual(link_model._LinkModelDataSet__objective, "classification")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.objective(123)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "objective:Please enter a string in objective\n", captured_output.getvalue()
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test empty objective
        link_model.objective("")
        self.assertEqual(link_model._LinkModelDataSet__objective, "")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_cycles(self):
        """Test cycles validation"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid cycles
        link_model.cycles(5)
        self.assertEqual(link_model._LinkModelDataSet__cycles, 5)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.cycles("5")
        sys.stdout = sys.__stdout__
        self.assertIn("cycles:Invalid input type\n", captured_output.getvalue())
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test negative cycles
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.cycles(-1)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "cycles:cycle value cannot be negative or zero\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test zero cycles
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.cycles(0)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "cycles:cycle value cannot be negative or zero\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_epochs_validation(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid epochs
        link_model.epochs(20)
        self.assertEqual(link_model._LinkModelDataSet__epochs, 20)

        # Test invalid epochs
        link_model.epochs(0)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid type
        link_model.epochs("10")
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_layers_freeze(self):
        """Test layers freeze validation"""
        # Clear any previously imported modules
        if "tensorflow_model" in sys.modules:
            del sys.modules["tensorflow_model"]

        current_dir = Path(__file__).parent
        test_models_path = os.path.join(current_dir, "test_models")
        if test_models_path not in sys.path:
            sys.path.insert(0, test_models_path)

        from tensorflow_functional_model import MyModel

        model = MyModel()

        # Update test_kwargs with the real model
        test_kwargs = self.test_kwargs.copy()
        test_kwargs["model"] = model
        test_kwargs["num_classes"] = 3
        link_model = LinkModelDataSet(**test_kwargs)

        # Test valid layers freeze with list of strings (layer names)
        valid_layers = ["re_lu_12"]
        link_model.layersFreeze(valid_layers)
        self.assertEqual(
            link_model._LinkModelDataSet__layers_non_trainable, str(valid_layers)
        )
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid layer name
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.layersFreeze(["invalid_layer"])
        sys.stdout = sys.__stdout__
        self.assertIn(
            "layersFreeze:Provide layers only which model contains for layersFreeze",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type (not a list)
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.layersFreeze("dense_1")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "layersFreeze:Provide values as list of strings for layersFreeze",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test list with non-string elements
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.layersFreeze([1, 2, 3])
        sys.stdout = sys.__stdout__
        self.assertIn(
            "layersFreeze:Provide values as list of strings for layersFreeze",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test empty list
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.layersFreeze([])
        sys.stdout = sys.__stdout__
        self.assertIn(
            "",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test PyTorch framework case
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)

        captured_output = StringIO()
        sys.stdout = captured_output
        pytorch_model.layersFreeze(["layer1"])
        sys.stdout = sys.__stdout__
        self.assertIn(
            "The parameter layersFreeze is not supported on pytorch\n",
            captured_output.getvalue(),
        )
        self.assertTrue(pytorch_model._LinkModelDataSet__eligibility_passed)

        # Test SKLearn framework case
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        sklearn_model = LinkModelDataSet(**sklearn_kwargs)

        captured_output = StringIO()
        sys.stdout = captured_output
        sklearn_model.layersFreeze(["layer1"])
        sys.stdout = sys.__stdout__
        self.assertIn(
            "The parameter layersFreeze is not supported on sklearn",
            captured_output.getvalue(),
        )
        self.assertTrue(sklearn_model._LinkModelDataSet__eligibility_passed)

    def test_validation_split_validation(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid validation split
        link_model.validation_split(0.2)
        self.assertEqual(link_model._LinkModelDataSet__validation_split, 0.2)

        # Test validation split out of range
        link_model.validation_split(0.6)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid type
        link_model.validation_split("0.2")
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    @patch("requests.post")
    def test_check_training_plan(self, mock_post):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(
            {"status": True, "message": "Training plan exists"}
        ).encode()
        mock_post.return_value = mock_response

        # Test with user input "yes"
        with patch("builtins.input", return_value="yes"):
            result = link_model._LinkModelDataSet__checkTrainingPlan()
            self.assertTrue(result)

        # Test with user input "no"
        with patch("builtins.input", return_value="no"):
            result = link_model._LinkModelDataSet__checkTrainingPlan()
            self.assertFalse(result)

    def test_optimizer_validation(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid optimizer for tensorflow
        link_model.optimizer("adam")
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "adam")

        # Test invalid optimizer
        link_model.optimizer("invalid_optimizer")
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test pytorch framework
        link_model._LinkModelDataSet__framework = PYTORCH_FRAMEWORK
        link_model.optimizer("adam")
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "adam")

    def test_get_training_plan(self):
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test when eligibility is passed
        link_model._LinkModelDataSet__eligibility_passed = True
        link_model.getTrainingPlan()  # Should print training plan details

        # Test when eligibility is not passed
        link_model._LinkModelDataSet__eligibility_passed = False
        link_model.getTrainingPlan()  # Should not print anything

    def test_sklearn_framework_initialization(self):
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        sklearn_kwargs["category"] = TABULAR_CLASSIFICATION
        link_model = LinkModelDataSet(**sklearn_kwargs)
        # Verify sklearn-specific initialization
        self.assertEqual(link_model._LinkModelDataSet__framework, SKLEARN_FRAMEWORK)
        self.assertEqual(link_model._LinkModelDataSet__category, TABULAR_CLASSIFICATION)

    def test_earlystopCallback(self):
        """Test early stopping callback configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid early stopping configuration
        link_model.earlystopCallback("loss", 10)
        self.assertEqual(
            link_model._LinkModelDataSet__earlystopCallback,
            {"earlystopping": ["loss", 10]},
        )
        self.assertTrue(link_model._LinkModelDataSet__earlystopCallback)

        # Test invalid metric type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.earlystopCallback(123, 10)  # Invalid metric type

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify the error message
        expected_message = "earlystopCallback:Please provide supported monitor values: ['accuracy', 'loss', 'val_loss', 'val_accuracy']\n \n\n"
        self.assertEqual(captured_output.getvalue(), expected_message)

        # Test invalid patience type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.earlystopCallback("loss", "ten")  # Invalid patience type

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify the error message for invalid patience type
        expected_patience_error = (
            "earlystopCallback:Invalid datatype for arguments given for patience\n \n\n"
        )
        self.assertEqual(captured_output.getvalue(), expected_patience_error)

    def test_reducelrCallback(self):
        """Test reduce learning rate callback configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid reduce learning rate configuration
        link_model.reducelrCallback("loss", 0.1, 10, 0.0001)
        self.assertEqual(
            link_model._LinkModelDataSet__reducelrCallback,
            {"reducelr": ["loss", 0.1, 10, 0.0001]},
        )
        self.assertTrue(link_model._LinkModelDataSet__reducelrCallback)

        # Test invalid metric type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.reducelrCallback(123, 0.1, 10, 0.0001)  # Invalid metric type

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify the error message for invalid metric type
        expected_message = "reducelrCallback:Please provide supported monitor values: ['accuracy', 'loss', 'val_loss', 'val_accuracy']\n \n\n"
        self.assertEqual(captured_output.getvalue(), expected_message)

        # Test invalid patience type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.reducelrCallback("loss", 0.1, "ten", 0.0001)  # Invalid patience type

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify the error message for invalid patience type
        expected_patience_error = "reducelrCallback:Invalid datatype for arguments given for reducelrCallback\n \n\n"
        self.assertEqual(captured_output.getvalue(), expected_patience_error)

        # Test edge case with very low learning rate
        link_model.reducelrCallback("loss", 0.1, 10, 1e-10)
        self.assertEqual(
            link_model._LinkModelDataSet__reducelrCallback,
            {"reducelr": ["loss", 0.1, 10, 1e-10]},
        )

    def test_modelCheckpointCallback(self):
        """Test model checkpoint callback configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid model checkpoint configuration
        link_model.modelCheckpointCallback("val_loss", True)
        self.assertEqual(
            link_model._LinkModelDataSet__modelCheckpointCallback,
            {"modelCheckpoint": ["val_loss", True]},
        )
        self.assertTrue(link_model._LinkModelDataSet__modelCheckpointCallback)

        # Test invalid metric type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.modelCheckpointCallback(123, True)  # Invalid metric type

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify the error message for invalid metric type
        expected_message = "modelCheckpointCallback:Please provide supported monitor values: ['accuracy', 'loss', 'val_loss', 'val_accuracy']\n \n\n"
        self.assertEqual(captured_output.getvalue(), expected_message)

    def test_terminateOnNaNCallback(self):
        """Test terminate on NaN callback configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid terminate on NaN configuration
        link_model.terminateOnNaNCallback()
        self.assertTrue(link_model._LinkModelDataSet__terminateOnNaNCallback)

        with self.assertRaises(TypeError):
            link_model.terminateOnNaNCallback(123)  # Invalid input type

    def test_callback_configurations(self):
        """Test callback configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid early stopping configuration
        link_model.earlystopCallback("loss", 10)
        self.assertEqual(
            link_model._LinkModelDataSet__earlystopCallback,
            {"earlystopping": ["loss", 10]},
        )
        self.assertTrue(link_model._LinkModelDataSet__earlystopCallback)

        # Test valid reduce learning rate configuration
        link_model.reducelrCallback("loss", 0.1, 10, 0.0001)
        self.assertEqual(
            link_model._LinkModelDataSet__reducelrCallback,
            {"reducelr": ["loss", 0.1, 10, 0.0001]},
        )
        self.assertTrue(link_model._LinkModelDataSet__reducelrCallback)

        # Test valid model checkpoint configuration
        link_model.modelCheckpointCallback("val_loss", save_best_only=True)
        self.assertEqual(
            link_model._LinkModelDataSet__modelCheckpointCallback,
            {"modelCheckpoint": ["val_loss", True]},
        )
        self.assertTrue(link_model._LinkModelDataSet__modelCheckpointCallback)

        # Test valid terminate on NaN configuration
        link_model.terminateOnNaNCallback()
        self.assertTrue(link_model._LinkModelDataSet__terminateOnNaNCallback)

    def test_data_augmentation_parameters(self):
        """Test data augmentation configuration"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test rotation range
        link_model.rotation_range(30)
        self.assertEqual(link_model._LinkModelDataSet__rotation_range, 30)

        # Test invalid rotation range
        link_model.rotation_range(361.0)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test zoom range
        link_model.zoom_range(0.2)
        self.assertEqual(link_model._LinkModelDataSet__zoom_range, 0.2)

        # Test horizontal flip
        link_model.horizontal_flip(True)
        self.assertTrue(link_model._LinkModelDataSet__horizontal_flip)

    def test_error_handling(self):
        """Test error handling scenarios"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test missing required parameters
        invalid_kwargs = self.test_kwargs.copy()
        invalid_kwargs.pop("model")
        with self.assertRaises(KeyError):
            LinkModelDataSet(**invalid_kwargs)

        # Test API error handling
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException
            with self.assertRaises(Exception):
                link_model._LinkModelDataSet__checkTrainingPlan()

    @patch("requests.post")
    def test_edge_cases(self, mock_post):
        """Test edge cases and boundary conditions"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test maximum number of epochs
        link_model.epochs(1000)  # Assuming this is the max
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test zero validation split
        link_model.validation_split(0)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test empty class names
        edge_kwargs = self.test_kwargs.copy()
        edge_kwargs["class_names"] = {}
        LinkModelDataSet(**edge_kwargs)

        # Test single class dataset
        single_class_kwargs = self.test_kwargs.copy()
        single_class_kwargs["class_names"] = {"class1": 1000}
        single_class_kwargs["num_classes"] = 1

        # Capture stdout to verify error messages
        captured_output = StringIO()
        sys.stdout = captured_output

        LinkModelDataSet(**single_class_kwargs)

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify that appropriate error messages are printed
        output = captured_output.getvalue()
        self.assertIn("", output)

    def test_feature_interactions(self):
        """Test interactions between different features"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test validation split interaction
        link_model.validation_split(0.3)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_training_classes(self):
        """Test basic functionality of trainingClasses method"""
        dataset = LinkModelDataSet(**self.test_kwargs)

        # Create mock training dataset with class names and image counts
        mock_training_dataset = {"class1": 30, "class2": 30}

        # Mock API response
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                content=json.dumps(
                    {
                        "total_data_per_edge": {"edge1": 60},
                    }
                ).encode("utf-8"),
            )

            classes = dataset.trainingClasses(mock_training_dataset)

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args[1]
            self.assertEqual(
                call_args["headers"]["Authorization"],
                f"Token {self.test_kwargs['token']}",
            )
            self.assertEqual(
                json.loads(call_args["data"]["data_per_class"]), mock_training_dataset
            )
            self.assertEqual(
                call_args["data"]["type"], "recalculate_image_count_per_edge"
            )

            # Verify results
            self.assertEqual(
                dataset._LinkModelDataSet__trainingClasses, mock_training_dataset
            )
            self.assertEqual(dataset._LinkModelDataSet__data_per_edge, {"edge1": 60})
            self.assertTrue(dataset._LinkModelDataSet__eligibility_passed)

    def test_training_classes_less_images(self):
        """Test basic functionality of trainingClasses method"""
        dataset = LinkModelDataSet(**self.test_kwargs)

        # Create mock training dataset with class names and image counts
        mock_training_dataset = {"class1": 4, "class2": 30}

        # Mock API response
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                content=json.dumps(
                    {
                        "total_data_per_edge": {"edge1": 60},
                    }
                ).encode("utf-8"),
            )

            # Capture printed error message
            with patch("sys.stdout", new=StringIO()) as fake_output:
                dataset.trainingClasses(mock_training_dataset)

                # Verify error message
                expected_error = f"trainingClasses: Please provide num of images for class class1\n greater than 5 and less than equal to 70\n \n\n"
                self.assertEqual(fake_output.getvalue(), expected_error)

    def test_training_classes_more_images(self):
        """Test basic functionality of trainingClasses method"""
        dataset = LinkModelDataSet(**self.test_kwargs)

        # Create mock training dataset with class names and image counts
        mock_training_dataset = {"class1": 10, "class2": 30}

        # Mock API response
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                content=json.dumps(
                    {
                        "total_data_per_edge": {"edge1": 60},
                    }
                ).encode("utf-8"),
            )

            # Capture printed error message
            with patch("sys.stdout", new=StringIO()) as fake_output:
                dataset.trainingClasses(mock_training_dataset)

                # Verify error message
                expected_error = ""
                self.assertEqual(fake_output.getvalue(), expected_error)

    def test_training_classes_empty_dataset(self):
        """Test trainingClasses with empty dataset"""
        dataset = LinkModelDataSet(**self.test_kwargs)

        # Mock API response for empty dataset
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=400,  # Error status code
                content=json.dumps({"message": "Empty dataset not allowed"}).encode(
                    "utf-8"
                ),
            )

            # Pass empty dict as training dataset
            dataset.trainingClasses({})

            # Verify API wasn't called (validation should fail before API call)
            mock_post.assert_not_called()

            # Verify error state
            self.assertFalse(dataset._LinkModelDataSet__eligibility_passed)

    def test_training_classes_with_missing_distribution(self):
        """Test trainingClasses with missing classes in distribution"""
        dataset = LinkModelDataSet(**self.test_kwargs)

        # Create mock training dataset with missing class
        mock_training_dataset = {
            "class1": 30  # Missing class2 which should be in the dataset
        }

        # Mock API response
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=400,
                content=json.dumps(
                    {
                        "message": "Training dataset must contain all classes present in the dataset"
                    }
                ).encode("utf-8"),
            )

            # Capture printed error message
            with patch("sys.stdout", new=StringIO()) as fake_output:
                dataset.trainingClasses(mock_training_dataset)

                # Verify error message
                expected_error = (
                    "trainingClasses: trainingDatasetSize dictionary must contain all classes that are present in the "
                    "dataset.\n Customisation in terms of classes is not allowed.\n \n\n"
                )
                self.assertEqual(fake_output.getvalue(), expected_error)

            # Verify API wasn't called (validation should fail before API call)
            mock_post.assert_not_called()

            # Verify error state
            self.assertFalse(dataset._LinkModelDataSet__eligibility_passed)

    @patch("requests.post")
    def test_data_shape_validation(self, mock_post):
        """Test image shape validation in LinkModelDataSet"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(
            {
                "status": True,
                "model_name": "tensorflow_functional_model_id",
            }
        ).encode()
        mock_post.return_value = mock_response

        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid image size
        link_model.data_shape(224)
        self.assertEqual(link_model._LinkModelDataSet__data_shape, 224)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test image size too small
        link_model.data_shape(8 - 1)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test image size too large
        link_model.data_shape(224 + 1)
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test non-square image dimensions
        link_model.data_shape((224, 256))
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test valid image shape
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.data_shape((224, 224, 3))
        sys.stdout = sys.__stdout__
        self.assertIn(
            "data_shape:Invalid type or value not in range [48, 224]",
            captured_output.getvalue(),
        )

        # Test invalid shape type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.data_shape("invalid")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "data_shape:Invalid type or value not in range [48, 224]",
            captured_output.getvalue(),
        )
        self.assertNotEqual(link_model._LinkModelDataSet__data_shape, "invalid")

        # Test invalid shape length
        link_model._LinkModelDataSet__framework = "pytorch"
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.data_shape(224)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "data_shape:Image size is fixed for each model for pytorch\n \n\n",
            captured_output.getvalue(),
        )

    @patch("requests.post")
    def test_image_type_validation(self, mock_post):
        """Test image type validation in LinkModelDataSet"""
        test_kwargs = self.test_kwargs.copy()
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(
            {
                "status": True,
                "model_name": "tensorflow_functional_model_id",
            }
        ).encode()
        mock_post.return_value = mock_response
        link_model = LinkModelDataSet(**test_kwargs)

        # Test valid image type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.dataType("rgb")
        sys.stdout = sys.__stdout__
        self.assertEqual(link_model._LinkModelDataSet__data_type, "rgb")
        self.assertEqual(captured_output.getvalue(), "")  # No error message

        # Test invalid image type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.dataType("invalid_type")
        sys.stdout = sys.__stdout__
        self.assertIn(
            "dataType:Enter values from ['rgb', 'grayscale']\n \n\n",
            captured_output.getvalue(),
        )
        self.assertNotEqual(link_model._LinkModelDataSet__data_type, "invalid_type")

        # Test non-string input
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.dataType(123)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "dataType:enter image type as string\n", captured_output.getvalue()
        )

        # Test 400 the response
        message = "image type setting failed"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = json.dumps(
            {"status": False, "message": message}
        ).encode()
        mock_post.return_value = mock_response
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.dataType("rgb")
        sys.stdout = sys.__stdout__
        self.assertIn(
            f"dataType:Error Occured while setting updated image format \nfor model as {message}\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.content = json.dumps(
            {
                "status": True,
                "model_name": "tensorflow_functional_model_id",
            }
        ).encode()
        mock_post.return_value = mock_response
        link_model._LinkModelDataSet__framework = PYTORCH_FRAMEWORK
        # Test pytorch image type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.dataType("rgb")
        sys.stdout = sys.__stdout__
        self.assertEqual(link_model._LinkModelDataSet__data_type, "rgb")
        self.assertEqual(captured_output.getvalue(), "")  # No error message

    def test_seed_validation(self):
        """Test seed validation in LinkModelDataSet"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid seed
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.seed(True)
        sys.stdout = sys.__stdout__
        self.assertEqual(link_model._LinkModelDataSet__seed, "True")
        self.assertEqual(captured_output.getvalue(), "")  # No error message

        # Test invalid seed type
        link_model.seed(False)
        self.assertEqual(link_model._LinkModelDataSet__seed, "False")

        # Test invalid seed type
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.seed(1)
        sys.stdout = sys.__stdout__
        self.assertIn("seed:Invalid input type\n", captured_output.getvalue())
        self.assertNotEqual(link_model._LinkModelDataSet__seed, "1")


if __name__ == "__main__":
    unittest.main()
