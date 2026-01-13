import os
import torch
from torch import nn, optim
from tracebloc_package.model_file_checks.pytorch_checks import TorchChecks
from tracebloc_package.upload_model_classes.model_upload import Model
from tracebloc_package.utils.general_utils import (
    get_model_parameters,
    define_device,
)
from tracebloc_package.utils.constants import (
    PRETRAINED_WEIGHTS_FILENAME,
    TRAINED_WEIGHTS_FILENAME,
    PYTORCH_FRAMEWORK,
)
from tracebloc_package.utils.tabular_regression_utils import get_regression_dataloader


class TorchTabularRegression(Model, TorchChecks):
    def __init__(
        self,
        model_name,
        token,
        weights,
        url,
        model_path,
        tmp_model_file_path,
        tmp_dir_path,
        progress_bar_1,
        classes,
        weights_path,
        model,
        category,
        progress_bar,
        message,
        framework,
        data_shape,
        batch_size,
        model_type,
        num_feature_points,
    ):
        super().__init__(
            model_name=model_name,
            token=token,
            weights=weights,
            url=url,
            model_path=model_path,
            tmp_model_file_path=tmp_model_file_path,
            tmp_dir_path=tmp_dir_path,
            progress_bar_1=progress_bar_1,
            classes=classes,
            weights_path=weights_path,
            framework=framework,
            data_shape=data_shape,
            batch_size=batch_size,
            model_type=model_type,
            num_feature_points=num_feature_points,
        )
        TorchChecks.__init__(
            self,
            model=model,
            category=category,
            progress_bar=progress_bar,
            message=message,
            classes=classes,
        )
        self.__weights_path = weights_path
        self.tmp_file_path = ""
        self.device = define_device()
        self.loss = None

    def small_training_loop(
        self, weight_filename, custom_loss=False, criterion=nn.MSELoss()
    ):
        """
        Run a small training loop on dummy regression data.
        Uses MSE loss by default for regression.
        """
        try:
            # Validate input shape before creating dataloader
            # Create a dummy input to test model compatibility
            dummy_input = torch.randn(1, self.num_feature_points)
            try:
                with torch.no_grad():
                    dummy_output = self.model(dummy_input)
                # Validate output shape - should be (1, output_dim) or (1,)
                if dummy_output.dim() == 0:
                    raise ValueError(
                        f"Model output is scalar (0D tensor). Expected 1D or 2D tensor for regression. "
                        f"Model should output shape (batch, output_dim) or (batch,)."
                    )
                if dummy_output.dim() > 2:
                    raise ValueError(
                        f"Model output has {dummy_output.dim()} dimensions. Expected 1D or 2D tensor for regression. "
                        f"Got output shape: {dummy_output.shape}"
                    )
            except RuntimeError as e:
                # Check if it's a shape mismatch error (common with hardcoded input sizes)
                error_msg = str(e).lower()
                if "shape" in error_msg or "size" in error_msg or "mat" in error_msg or "cannot be multiplied" in error_msg:
                    # Try to extract expected vs actual dimensions from error
                    raise ValueError(
                        f"Model architecture mismatch: Model cannot process input shape (batch, {self.num_feature_points}). "
                        f"The model's architecture appears to be hardcoded for a different input size. "
                        f"Error: {e}. "
                        f"Please ensure your model accepts input of shape (batch_size, {self.num_feature_points}). "
                        f"If your model has hardcoded input dimensions (e.g., in Linear layers), "
                        f"they must match the number of features ({self.num_feature_points}). "
                        f"Tip: Check your model's Linear/Conv layers - they may have hardcoded dimensions "
                        f"that don't match the actual number of features in your dataset."
                    ) from e
                else:
                    raise ValueError(
                        f"Model cannot process input shape (batch, {self.num_feature_points}). "
                        f"Error: {e}. Please ensure your model accepts input of shape (batch_size, num_feature_points)."
                    ) from e
            except Exception as e:
                raise ValueError(
                    f"Model cannot process input shape (batch, {self.num_feature_points}). "
                    f"Error: {e}. Please ensure your model accepts input of shape (batch_size, num_feature_points)."
                ) from e

            # Additional check: Inspect model architecture to detect hardcoded dimensions
            # This helps catch issues before training starts
            try:
                for name, module in self.model.named_modules():
                    if isinstance(module, torch.nn.Linear):
                        # Check if this Linear layer might be receiving the wrong input size
                        # We can't know for sure without running, but we can warn about potential issues
                        if hasattr(module, 'in_features'):
                            # For models with Conv1d -> Linear, the input to Linear depends on
                            # (num_features * out_channels_from_last_conv)
                            # We can't calculate this exactly without running, but we can note it
                            pass
            except Exception:
                pass  # Don't fail validation if we can't inspect

            # Get regression dataloader with proper batch_size
            dataloader = get_regression_dataloader(
                num_feature_points=self.num_feature_points,
                batch_size=self.batch_size,
                output_dim=self.classes,
            )
            self.model.train()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)

            # Training loop
            for epoch in range(1):
                running_loss = 0.0

                for inputs, targets in dataloader:
                    # Validate input shape matches expected
                    if inputs.shape[1] != self.num_feature_points:
                        raise ValueError(
                            f"Input shape mismatch: expected (batch, {self.num_feature_points}), "
                            f"got (batch, {inputs.shape[1]})"
                        )
                    
                    optimizer.zero_grad()

                    # Forward pass
                    outputs = self.model(inputs)
                    
                    # Validate output shape
                    if outputs.dim() == 0:
                        raise ValueError(
                            "Model output is scalar (0D tensor). Regression models should output "
                            "1D tensor (batch,) or 2D tensor (batch, output_dim)."
                        )
                    if outputs.dim() > 2:
                        raise ValueError(
                            f"Model output has {outputs.dim()} dimensions. Expected 1D or 2D for regression. "
                            f"Got shape: {outputs.shape}"
                        )
                    
                    # Match training code behavior: use squeeze() to match actual training
                    # This matches the training code: outputs.squeeze() if outputs.dim() > 1 and outputs.shape[1] == 1
                    if outputs.dim() > 1 and outputs.shape[1] == 1:
                        outputs_for_loss = outputs.squeeze()  # Match training code behavior
                    else:
                        outputs_for_loss = outputs
                    
                    # Ensure targets are float (matching training: labels.float())
                    # Targets from dataloader are already float32, but ensure they're float
                    targets_for_loss = targets.float()
                    
                    # Handle edge case: if squeeze() made outputs scalar when batch_size=1
                    # This can happen with squeeze() removing all size-1 dimensions
                    if outputs_for_loss.dim() == 0:
                        # If batch_size=1 and output_dim=1, squeeze() makes it scalar
                        # Need to reshape to (1,) to match targets
                        outputs_for_loss = outputs_for_loss.unsqueeze(0)
                    
                    # Ensure targets match outputs shape after processing
                    # If outputs_for_loss is (batch,) and targets is (batch, 1), squeeze targets
                    if targets_for_loss.dim() > 1 and targets_for_loss.shape[1] == 1:
                        targets_for_loss = targets_for_loss.squeeze(1)
                    
                    # Final shape validation
                    if outputs_for_loss.shape != targets_for_loss.shape:
                        raise ValueError(
                            f"Output and target shape mismatch after processing: "
                            f"outputs {outputs_for_loss.shape} vs targets {targets_for_loss.shape}. "
                            f"Model output shape should match target shape for regression. "
                            f"Original outputs shape: {outputs.shape}, original targets shape: {targets.shape}"
                        )
                    
                    loss = criterion(outputs_for_loss, targets_for_loss)

                    # Backward pass and optimization
                    loss.backward()
                    optimizer.step()

                    running_loss += loss.item()

            # Dump weights from trained model
            get_model_parameters(
                model=self.model,
                weight_file_path=self.tmp_dir_path,
                weights_file_name=TRAINED_WEIGHTS_FILENAME,
                framework=PYTORCH_FRAMEWORK,
                preweights=False,
            )
            if self.progress_bar is not None:
                self.progress_bar.update(1)
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel not support training on {self.category} dataset as there is error {e} "
            raise

    def model_func_checks(self):
        """Check if model is eligible for regression."""
        try:
            self.is_model_supported()
            self.small_training_loop(TRAINED_WEIGHTS_FILENAME)
            
            if os.path.exists(
                os.path.join(self.tmp_dir_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pth")
            ):
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_dir_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                    preweights=True,
                )
                self.progress_bar.update(1)
            else:
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_dir_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                    preweights=False,
                )
                self.progress_bar.update(2)
            
            self.average_weights()
            self.load_averaged_weights()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel checks failed with error:\n {e}"
            eligible = False
        
        if not eligible:
            return eligible, self.message, None, self.progress_bar
        return eligible, self.message, self.model_name, self.progress_bar

