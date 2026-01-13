import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


# Custom dataset for regression
class TabularRegressionDataset(Dataset):
    def __init__(self, features, targets):
        self.features = features.astype(np.float32)
        self.targets = targets.astype(np.float32)  # Continuous values, not classes

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx]), torch.tensor(self.targets[idx])


def generate_tabular_regression_data(num_samples, num_feature_points, output_dim=1):
    """
    Generate dummy tabular data for regression testing.
    
    Args:
        num_samples: Number of data samples to generate
        num_feature_points: Number of input features/columns
        output_dim: Number of output dimensions (1 for single output, >1 for multi-output regression).
                    If None or empty string, defaults to 1 for single-output regression.
    
    Returns:
        features: numpy array of shape (num_samples, num_feature_points)
        targets: numpy array of shape (num_samples, output_dim) with continuous values
    """
    # Default to single-output regression if output_dim is None or empty string
    if output_dim is None or output_dim == "":
        output_dim = 1
    
    # Generate dummy features (same as classification)
    dummy_data = {
        f"feature_{i}": np.random.uniform(0, 100, num_samples)
        for i in range(num_feature_points)
    }
    
    # Generate continuous target values instead of class labels
    # For single-output regression: shape (num_samples,)
    # For multi-output regression: shape (num_samples, output_dim)
    if output_dim == 1:
        # Single output: generate values in a reasonable range (e.g., 0-1000)
        targets = np.random.uniform(0, 1000, num_samples)
    else:
        # Multi-output: generate values for each output dimension
        targets = np.random.uniform(0, 1000, (num_samples, output_dim))
    
    # Convert dictionary to DataFrame and extract features and targets
    features = pd.DataFrame(dummy_data).iloc[:, :num_feature_points].values
    return features, targets


def get_regression_dataloader(
    num_samples=50, 
    num_feature_points=69, 
    batch_size=4, 
    output_dim=1
):
    """
    Create a DataLoader for regression testing.
    
    Args:
        num_samples: Number of samples (default: 50)
        num_feature_points: Number of input features (default: 69)
        batch_size: Batch size for DataLoader (default: 4)
        output_dim: Number of output dimensions (default: 1). If None or empty string, defaults to 1.
    
    Returns:
        DataLoader with regression data
    """
    data_features, targets = generate_tabular_regression_data(
        num_samples=num_samples,
        num_feature_points=num_feature_points,
        output_dim=output_dim,
    )
    # Create Dataset and DataLoader
    dataset = TabularRegressionDataset(data_features, targets)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

