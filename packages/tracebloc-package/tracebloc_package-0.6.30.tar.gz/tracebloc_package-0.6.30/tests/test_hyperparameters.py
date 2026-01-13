import shutil
import unittest
from unittest.mock import patch, MagicMock
import sys, os
from io import StringIO
import math
import pytest
from pathlib import Path

from tracebloc_package.linkModelDataSet import LinkModelDataSet
from tracebloc_package.utils.constants import (
    TENSORFLOW_FRAMEWORK,
    PYTORCH_FRAMEWORK,
    SKLEARN_FRAMEWORK,
    IMAGE_CLASSIFICATION,
    CONSTANT,
    TYPE,
    VALUE,
    CUSTOM,
    ADAPTIVE,
    STANDARD,
    TEXT_CLASSIFICATION,
)


class TestHyperparameters(unittest.TestCase):
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
            "model_type": "",
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

    def test_tensorflow_optimizer_validation(self):
        """Test optimizer validation for TensorFlow framework"""
        # Test valid optimizers
        valid_optimizers = [
            "sgd",
            "adam",
            "rmsprop",
            "adagrad",
            "adadelta",
            "adamax",
            "nadam",
        ]

        for opt in valid_optimizers:
            self.link_model.optimizer(opt)
            self.assertEqual(self.link_model._LinkModelDataSet__optimizer, opt)
            self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid optimizer
        captured_output = StringIO()
        sys.stdout = captured_output

        self.link_model.optimizer("invalid_optimizer")

        sys.stdout = sys.__stdout__
        self.assertIn(
            "optimizer:Please provide supported optimizers:\n ['adam', 'rmsprop', 'sgd', 'adadelta', 'adagrad', 'adamax', 'nadam', 'ftrl']\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output

        self.link_model.optimizer(123)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "optimizer:Please provide supported optimizers:\n ['adam', 'rmsprop', 'sgd', 'adadelta', 'adagrad', 'adamax', 'nadam', 'ftrl']\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_pytorch_optimizer_validation(self):
        """Test optimizer validation for PyTorch framework"""
        # Set framework to PyTorch
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        link_model = LinkModelDataSet(**pytorch_kwargs)

        # Test valid optimizers
        valid_optimizers = ["sgd", "adam", "rmsprop", "adagrad", "adadelta", "adamax"]

        for opt in valid_optimizers:
            link_model.optimizer(opt)
            self.assertEqual(link_model._LinkModelDataSet__optimizer, opt)
            self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid optimizer
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.optimizer("invalid_optimizer")

        sys.stdout = sys.__stdout__
        self.assertIn(
            "optimizer:Please provide supported optimizers: \n['adam', 'rmsprop', 'sgd', 'adadelta', 'adagrad', 'adamax']\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_sklearn_optimizer_validation(self):
        """Test optimizer validation for SKLearn framework"""
        # Set framework to SKLearn
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        link_model = LinkModelDataSet(**sklearn_kwargs)

        # Test optimizer setting for sklearn (should be ignored)
        link_model.optimizer("sgd")
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "sgd")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_optimizer_case_sensitivity(self):
        """Test optimizer validation is case insensitive"""
        # Test mixed case optimizers
        test_cases = ["SGD", "Adam", "RMSprop", "AdaGrad"]

        for opt in test_cases:
            self.link_model.optimizer(opt)
            self.assertEqual(self.link_model._LinkModelDataSet__optimizer, opt.lower())
            self.assertTrue(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_optimizer_with_empty_input(self):
        """Test optimizer validation with empty input"""
        captured_output = StringIO()
        sys.stdout = captured_output

        self.link_model.optimizer("")

        sys.stdout = sys.__stdout__
        self.assertIn(
            "optimizer:Please provide supported optimizers:\n ['adam', 'rmsprop', 'sgd', 'adadelta', 'adagrad', 'adamax', 'nadam', 'ftrl']\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(self.link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_validation(self):
        """Test learning rate validation for different frameworks"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid constant learning rate
        valid_lr = {TYPE: CONSTANT, VALUE: 0.001}
        link_model.learningRate(valid_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, valid_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test very small learning rate
        small_lr = {TYPE: CONSTANT, VALUE: 1e-7}
        link_model.learningRate(small_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, small_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test very large learning rate
        large_lr = {TYPE: CONSTANT, VALUE: 1.0}
        link_model.learningRate(large_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, large_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid learning rate type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.learningRate("0.001")

        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:Input not as per given convention for learningRate as got error 'str' object has no "
            "attribute 'keys'\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid learning rate dictionary format
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_lr = {"invalid_key": "invalid_value"}
        link_model.learningRate(invalid_lr)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:Input not as per given convention for learningRate\n \n\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test negative learning rate
        captured_output = StringIO()
        sys.stdout = captured_output

        negative_lr = {TYPE: CONSTANT, VALUE: -0.001}
        link_model.learningRate(negative_lr)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:learning rate value cannot be negative\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test unknown key learning rate
        captured_output = StringIO()
        sys.stdout = captured_output

        negative_lr = {TYPE: "unknown", VALUE: -0.001}
        link_model.learningRate(negative_lr)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:Input not as per given convention for learningRate\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_framework_specific(self):
        """Test learning rate validation for different frameworks"""
        # Test PyTorch framework
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)

        valid_lr = {TYPE: CONSTANT, VALUE: 0.001}
        pytorch_model.learningRate(valid_lr)
        self.assertEqual(pytorch_model._LinkModelDataSet__learningRate, valid_lr)
        self.assertTrue(pytorch_model._LinkModelDataSet__eligibility_passed)

        # Test unknown key learning rate
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_lr = {TYPE: ADAPTIVE, VALUE: -0.001}
        pytorch_model.learningRate(invalid_lr)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "The parameter learningRate:Adaptive and Custom learning rate is not supported on pytorch\n \n\n",
            captured_output.getvalue(),
        )
        self.assertTrue(pytorch_model._LinkModelDataSet__eligibility_passed)

        # Test SKLearn framework
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        sklearn_model = LinkModelDataSet(**sklearn_kwargs)

        sklearn_model.learningRate(valid_lr)
        self.assertEqual(sklearn_model._LinkModelDataSet__learningRate, valid_lr)
        self.assertTrue(sklearn_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_with_callbacks(self):
        """Test learning rate interaction with callbacks"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Set initial learning rate
        initial_lr = {TYPE: CONSTANT, VALUE: 0.001}
        link_model.learningRate(initial_lr)

        # Add ReduceLROnPlateau callback
        link_model.reducelrCallback("loss", 0.1, 10, 0.0001)

        # Verify learning rate is still valid
        self.assertEqual(link_model._LinkModelDataSet__learningRate, initial_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)
        self.assertTrue(link_model._LinkModelDataSet__reducelrCallback)

    def test_learning_rate_edge_cases(self):
        """Test edge cases for learning rate validation"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test zero learning rate
        captured_output = StringIO()
        sys.stdout = captured_output

        zero_lr = {TYPE: CONSTANT, VALUE: 0.0}
        link_model.learningRate(zero_lr)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:learning rate value cannot be zero\n",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test extremely small learning rate
        tiny_lr = {TYPE: CONSTANT, VALUE: 1e-10}
        link_model.learningRate(tiny_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, tiny_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test extremely large learning rate
        huge_lr = {TYPE: CONSTANT, VALUE: 1e5}
        link_model.learningRate(huge_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, huge_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_compatibility(self):
        """Test compatibility between learning rate and optimizer settings"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test Case 1: Valid constant learning rate with different optimizers
        valid_lr = {TYPE: CONSTANT, VALUE: 0.001}
        optimizers = [
            "adam",
            "sgd",
            "rmsprop",
            "adagrad",
            "adadelta",
            "adamax",
            "nadam",
            "ftrl",
        ]

        for opt in optimizers:
            link_model.optimizer(opt)
            link_model.learningRate(valid_lr)
            self.assertEqual(link_model._LinkModelDataSet__optimizer, opt)
            self.assertEqual(link_model._LinkModelDataSet__learningRate, valid_lr)
            self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_custom_schedule(self):
        """Test custom learning rate schedules with different optimizers"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Define a custom learning rate schedule function
        def custom_lr_schedule(epoch):
            return 0.001 * math.exp(-0.1 * epoch)

        # Test custom learning rate schedule with different optimizers
        custom_lr = {TYPE: CUSTOM, VALUE: {"name": custom_lr_schedule, "epoch": 5}}
        optimizers = ["adam", "sgd"]

        for opt in optimizers:
            link_model.optimizer(opt)
            link_model.learningRate(custom_lr)
            self.assertEqual(link_model._LinkModelDataSet__optimizer, opt)
            self.assertTrue(link_model._LinkModelDataSet__learningRateSet)
            self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_adaptive(self):
        """Test adaptive learning rate configurations with different optimizers"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test with different optimizers
        optimizers = ["adam", "sgd", "rmsprop"]

        for opt in optimizers:
            # Test adaptive learning rate
            adaptive_lr = {
                TYPE: ADAPTIVE,
                VALUE: {
                    "initial_learning_rate": 0.1,
                    "schedular": "ExponentialDecay",
                    "decay_steps": 100,
                    "decay_rate": 0.9,
                },
            }
            link_model.optimizer(opt)
            link_model.learningRate(adaptive_lr)
            self.assertEqual(link_model._LinkModelDataSet__optimizer, opt)
            self.assertEqual(link_model._LinkModelDataSet__learningRate, adaptive_lr)
            self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_all_learning_rate_adaptive(self):
        """Test all adaptive learning rate configurations"""
        link_model = LinkModelDataSet(**self.test_kwargs)
        opt = "sgd"
        link_model.optimizer(opt)

        # Test ExponentialDecay learning rate
        exponential_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "ExponentialDecay",
                "decay_steps": 100,
                "decay_rate": 0.9,
            },
        }
        link_model.learningRate(exponential_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, exponential_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test InverseTimeDecay learning rate
        inverse_time_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "InverseTimeDecay",
                "decay_steps": 100,
                "decay_rate": 0.9,
            },
        }
        link_model.learningRate(inverse_time_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, inverse_time_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test PiecewiseConstantDecay learning rate
        piecewise_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "PiecewiseConstantDecay",
                "boundaries": [100, 200, 300],
                "values": [0.1, 0.01, 0.001, 0.0001],
            },
        }
        link_model.learningRate(piecewise_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, piecewise_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test PolynomialDecay learning rate
        polynomial_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "PolynomialDecay",
                "decay_steps": 100,
                "end_learning_rate": 0.0001,
                "power": 0.5,
            },
        }
        link_model.learningRate(polynomial_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, polynomial_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test CosineDecay learning rate
        cosine_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "CosineDecay",
                "decay_steps": 100,
                "alpha": 0.0,
            },
        }
        link_model.learningRate(cosine_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, cosine_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test CosineDecayRestarts learning rate
        cosine_restarts_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "CosineDecayRestarts",
                "first_decay_steps": 100,
                "alpha": 0.0,
            },
        }
        link_model.learningRate(cosine_restarts_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, cosine_restarts_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid scheduler
        invalid_scheduler_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "InvalidScheduler",
                "decay_steps": 100,
            },
        }
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.learningRate(invalid_scheduler_lr)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:While setting Learning Rate error Occurred",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test missing required parameters
        missing_params_lr = {
            TYPE: ADAPTIVE,
            VALUE: {
                "initial_learning_rate": 0.1,
                "schedular": "ExponentialDecay",
                # Missing decay_steps and decay_rate
            },
        }
        captured_output = StringIO()
        sys.stdout = captured_output
        link_model.learningRate(missing_params_lr)
        sys.stdout = sys.__stdout__
        self.assertIn(
            "learningRate:While setting Learning Rate error Occurred",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_framework_specific(self):
        """Test framework-specific learning rate and optimizer combinations"""

        # Test PyTorch framework
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_model = LinkModelDataSet(**pytorch_kwargs)

        valid_lr = {TYPE: CONSTANT, VALUE: 0.001}
        pytorch_optimizers = ["adam", "sgd", "rmsprop", "adagrad", "adadelta", "adamax"]

        for opt in pytorch_optimizers:
            pytorch_model.optimizer(opt)
            pytorch_model.learningRate(valid_lr)
            self.assertEqual(pytorch_model._LinkModelDataSet__optimizer, opt)
            self.assertEqual(pytorch_model._LinkModelDataSet__learningRate, valid_lr)
            self.assertTrue(pytorch_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_error_cases(self):
        """Test error cases for learning rate and optimizer combinations"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test Case 1: Invalid optimizer with valid learning rate
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.optimizer("invalid_optimizer")
        link_model.learningRate({TYPE: CONSTANT, VALUE: 0.001})

        sys.stdout = sys.__stdout__
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test Case 2: Valid optimizer with invalid learning rate
        link_model.optimizer("adam")

        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.learningRate({TYPE: "invalid_type", VALUE: 0.001})

        sys.stdout = sys.__stdout__
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test Case 3: Invalid learning rate value type
        link_model.optimizer("adam")

        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.learningRate(
            {TYPE: CONSTANT, VALUE: "0.001"}
        )  # string instead of float

        sys.stdout = sys.__stdout__
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_order_independence(self):
        """Test that setting order of learning rate and optimizer doesn't matter"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test Case 1: Set optimizer first, then learning rate
        link_model.optimizer("adam")
        link_model.learningRate({TYPE: CONSTANT, VALUE: 0.001})
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Reset link_model
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test Case 2: Set learning rate first, then optimizer
        link_model.learningRate({TYPE: CONSTANT, VALUE: 0.001})
        link_model.optimizer("adam")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

    def test_learning_rate_optimizer_update_behavior(self):
        """Test behavior when updating learning rate or optimizer after initial setting"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Initial setup
        link_model.optimizer("adam")
        link_model.learningRate({TYPE: CONSTANT, VALUE: 0.001})

        # Test updating learning rate
        new_lr = {TYPE: CONSTANT, VALUE: 0.0001}
        link_model.learningRate(new_lr)
        self.assertEqual(link_model._LinkModelDataSet__learningRate, new_lr)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test updating optimizer
        link_model.optimizer("sgd")
        self.assertEqual(link_model._LinkModelDataSet__optimizer, "sgd")
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Verify learning rate is still valid after optimizer change
        self.assertEqual(link_model._LinkModelDataSet__learningRate, new_lr)

    def test_tensorflow_loss_function_validation(self):
        """Test loss function validation for TensorFlow framework"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test valid standard loss functions
        valid_loss = {TYPE: STANDARD, VALUE: "binary_crossentropy"}
        link_model.lossFunction(valid_loss)
        self.assertEqual(link_model._LinkModelDataSet__lossFunction, valid_loss)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test case insensitive
        valid_loss = {TYPE: STANDARD, VALUE: "BINARY_CROSSENTROPY"}
        link_model.lossFunction(valid_loss)
        self.assertEqual(link_model._LinkModelDataSet__lossFunction, valid_loss)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid loss function
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_loss = {TYPE: STANDARD, VALUE: "invalid_loss"}
        link_model.lossFunction(invalid_loss)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "lossFunction:Please provide tensorflow supported default loss functions losses:",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    @pytest.mark.filterwarnings("ignore")
    def test_tensorflow_custom_loss_function_validation(self):
        """Test custom loss function validation"""
        # Clear any previously imported modules that might interfere
        if "loss" in sys.modules:
            del sys.modules["loss"]
        if "tensorflow_functional_model" in sys.modules:
            del sys.modules["tensorflow_functional_model"]

        current_dir = Path(__file__).parent
        test_models_path = os.path.join(current_dir, "test_models")
        if test_models_path not in sys.path:
            sys.path.insert(0, test_models_path)

        from tensorflow_functional_model import MyModel

        # Create model instance
        model = MyModel()

        # Update test_kwargs with the real model
        test_kwargs = self.test_kwargs.copy()
        test_kwargs["model"] = model
        test_kwargs["num_classes"] = 3

        link_model = LinkModelDataSet(**test_kwargs)

        # Set the tmp_path to the test_models directory where tensorflow_custom_loss.py exists
        loss_file_path = os.path.join(test_models_path, "tensorflow_custom_loss.py")
        shutil.copy(loss_file_path, os.path.join(test_models_path, "loss.py"))

        # Test valid custom loss function
        custom_loss = {TYPE: CUSTOM, VALUE: loss_file_path}

        # Ensure the loss file exists
        if not os.path.exists(loss_file_path):
            pytest.fail(f"Loss file not found at {loss_file_path}")

        link_model.lossFunction(custom_loss)

        # Verify the loss function type and value were set correctly
        self.assertEqual(
            link_model._LinkModelDataSet__lossFunction[TYPE], custom_loss[TYPE]
        )
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)
        os.remove(os.path.join(test_models_path, "loss.py"))

    @pytest.mark.filterwarnings("ignore")
    def test_pytorch_custom_loss_function_validation(self):
        """Test custom loss function validation"""
        # Clear any previously imported modules that might interfere
        if "loss" in sys.modules:
            del sys.modules["loss"]
        if "pytorch_model" in sys.modules:
            del sys.modules["pytorch_model"]

        current_dir = Path(__file__).parent
        test_models_path = os.path.join(current_dir, "test_models")
        if test_models_path not in sys.path:
            sys.path.insert(0, test_models_path)

        from pytorch_model import Net

        # Create model instance
        model = Net()

        # Update test_kwargs with the real model
        test_kwargs = self.test_kwargs.copy()
        test_kwargs["model"] = model
        test_kwargs["num_classes"] = 3
        test_kwargs["framework"] = PYTORCH_FRAMEWORK

        link_model = LinkModelDataSet(**test_kwargs)

        # Set the tmp_path to the test_models directory where pytorch_custom_loss.py exists
        loss_file_path = os.path.join(test_models_path, "pytorch_custom_loss.py")
        shutil.copy(loss_file_path, os.path.join(test_models_path, "loss.py"))

        # Test valid custom loss function
        custom_loss = {TYPE: CUSTOM, VALUE: loss_file_path}

        # Ensure the loss file exists
        if not os.path.exists(loss_file_path):
            pytest.fail(f"Loss file not found at {loss_file_path}")

        link_model.lossFunction(custom_loss)

        # Verify the loss function type and value were set correctly
        self.assertEqual(
            link_model._LinkModelDataSet__lossFunction[TYPE], custom_loss[TYPE]
        )
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)
        os.remove(os.path.join(test_models_path, "loss.py"))

    def test_loss_function_missing_loss_file(self):
        """Test loss function validation when loss.py is missing"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Mock the missing loss.py file
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            captured_output = StringIO()
            sys.stdout = captured_output

            custom_loss = {TYPE: CUSTOM, VALUE: "custom_loss_function"}
            link_model.lossFunction(custom_loss)

            sys.stdout = sys.__stdout__
            self.assertIn(
                "lossFunction:Input not as per given convention for lossFunction as got error [Errno 2] No such file or directory: 'custom_loss_function'\n \n\n",
                captured_output.getvalue(),
            )
            self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_sklearn_loss_function_validation(self):
        """Test loss function validation for SKLearn framework"""
        sklearn_kwargs = self.test_kwargs.copy()
        sklearn_kwargs["framework"] = SKLEARN_FRAMEWORK
        link_model = LinkModelDataSet(**sklearn_kwargs)

        # Test valid standard loss function
        valid_loss = {TYPE: STANDARD, VALUE: "mse"}
        link_model.lossFunction(valid_loss)
        self.assertEqual(link_model._LinkModelDataSet__lossFunction, valid_loss)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid loss function
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_loss = {TYPE: STANDARD, VALUE: "invalid_loss"}
        link_model.lossFunction(invalid_loss)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "lossFunction:Please provide sklearn supported default loss functions losses:",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_pytorch_loss_function_validation(self):
        """Test loss function validation for PyTorch framework"""
        pytorch_kwargs = self.test_kwargs.copy()
        pytorch_kwargs["framework"] = PYTORCH_FRAMEWORK
        pytorch_kwargs["category"] = TEXT_CLASSIFICATION
        link_model = LinkModelDataSet(**pytorch_kwargs)

        # Test valid standard loss function for text classification
        valid_loss = {TYPE: STANDARD, VALUE: "crossentropy"}
        link_model.lossFunction(valid_loss)
        self.assertEqual(link_model._LinkModelDataSet__lossFunction, valid_loss)
        self.assertTrue(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid loss function
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_loss = {TYPE: STANDARD, VALUE: "invalid_loss"}
        link_model.lossFunction(invalid_loss)

        sys.stdout = sys.__stdout__
        self.assertIn(
            "lossFunction:Please provide pytorch supported default loss functions losses:",
            captured_output.getvalue(),
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

    def test_loss_function_invalid_input(self):
        """Test loss function validation with invalid input types"""
        link_model = LinkModelDataSet(**self.test_kwargs)

        # Test missing type key
        captured_output = StringIO()
        sys.stdout = captured_output

        invalid_loss = {VALUE: "binary_crossentropy"}
        link_model.lossFunction(invalid_loss)

        sys.stdout = sys.__stdout__
        self.assertIn("lossFunction:type missing", captured_output.getvalue())
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)

        # Test invalid input type
        captured_output = StringIO()
        sys.stdout = captured_output

        link_model.lossFunction("invalid_input")

        sys.stdout = sys.__stdout__
        self.assertIn(
            "lossFunction:Input not as per given convention", captured_output.getvalue()
        )
        self.assertFalse(link_model._LinkModelDataSet__eligibility_passed)


if __name__ == "__main__":
    unittest.main()
