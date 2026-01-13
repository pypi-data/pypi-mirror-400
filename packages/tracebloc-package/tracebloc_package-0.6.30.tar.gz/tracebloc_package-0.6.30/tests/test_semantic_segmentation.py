import pytest
import torch
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from tracebloc_package.upload_model_classes.torch_semantic_segmentation import (
    TorchSemanticSegmentation,
)
from tracebloc_package.utils.constants import SEMANTIC_SEGMENTATION, PYTORCH_FRAMEWORK


class TestSemanticSegmentation:
    def test_semantic_segmentation_class_initialization(self):
        """Test that TorchSemanticSegmentation can be initialized correctly"""
        # Mock parameters
        mock_params = {
            "model_name": "test_model",
            "token": "test_token",
            "weights": False,
            "url": "http://test.com",
            "model_path": "/test/path",
            "tmp_model_file_path": "/tmp/test",
            "tmp_dir_path": "/tmp/test_dir",
            "progress_bar_1": MagicMock(),
            "classes": 2,
            "weights_path": "/test/weights",
            "model": MagicMock(),
            "category": SEMANTIC_SEGMENTATION,
            "progress_bar": MagicMock(),
            "message": "",
            "framework": PYTORCH_FRAMEWORK,
            "data_shape": 224,
            "batch_size": 16,
            "model_type": "standard",
            "num_feature_points": None,
        }

        # Create instance
        semantic_seg = TorchSemanticSegmentation(**mock_params)

        # Verify basic attributes
        assert semantic_seg.model_name == "test_model"
        assert semantic_seg.category == SEMANTIC_SEGMENTATION
        assert semantic_seg.framework == PYTORCH_FRAMEWORK
        assert semantic_seg.classes == 2
        assert semantic_seg.data_shape == 224
        assert semantic_seg.batch_size == 16

    def test_semantic_segmentation_dataset_creation(self):
        """Test that semantic segmentation dataset can be created"""
        from tracebloc_package.utils.semantic_segmentation_utils import (
            FakeSemanticSegmentationDataset,
        )

        # Create dataset
        dataset = FakeSemanticSegmentationDataset(
            data_shape=224, num_images=5, num_classes=2
        )

        # Verify dataset properties
        assert len(dataset) == 5
        assert dataset.num_classes == 2
        assert dataset.data_shape == 224

        # Test getting an item
        image, mask = dataset[0]
        assert image.shape == (3, 224, 224)  # CHW format
        assert mask.shape == (224, 224)  # HW format
        assert mask.dtype == torch.int64
        assert torch.all(mask >= 0) and torch.all(mask < 2)  # Valid class indices

    @patch(
        "tracebloc_package.upload_model_classes.torch_semantic_segmentation.dummy_dataset_pytorch"
    )
    @patch(
        "tracebloc_package.upload_model_classes.torch_semantic_segmentation.get_model_parameters"
    )
    def test_small_training_loop(self, mock_get_params, mock_dummy_dataset):
        """Test the small training loop method"""
        # Mock parameters
        mock_params = {
            "model_name": "test_model",
            "token": "test_token",
            "weights": False,
            "url": "http://test.com",
            "model_path": "/test/path",
            "tmp_model_file_path": "/tmp/test",
            "tmp_dir_path": "/tmp/test_dir",
            "progress_bar_1": MagicMock(),
            "classes": 2,
            "weights_path": "/test/weights",
            "model": MagicMock(),
            "category": SEMANTIC_SEGMENTATION,
            "progress_bar": MagicMock(),
            "message": "",
            "framework": PYTORCH_FRAMEWORK,
            "data_shape": 224,
            "batch_size": 16,
            "model_type": "standard",
            "num_feature_points": None,
        }

        # Create instance
        semantic_seg = TorchSemanticSegmentation(**mock_params)

        # Mock dataset and dataloader
        mock_dataset = MagicMock()
        mock_dataset.__len__ = MagicMock(return_value=10)  # Mock dataset length
        mock_dummy_dataset.return_value = mock_dataset

        # Mock configure_loss
        semantic_seg.configure_loss = MagicMock(
            return_value=torch.nn.CrossEntropyLoss()
        )

        # Mock semantic_segmentation_training
        semantic_seg.semantic_segmentation_training = MagicMock()

        # Call small_training_loop
        semantic_seg.small_training_loop("test_weights.pth")

        # Verify calls
        mock_dummy_dataset.assert_called_once()
        semantic_seg.configure_loss.assert_called_once()
        semantic_seg.semantic_segmentation_training.assert_called_once()
        mock_get_params.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
