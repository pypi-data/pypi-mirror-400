from tracebloc_package.upload_model_classes.torch_tabular_classifier import (
    TorchTabularClassifier,
)
from tracebloc_package.upload_model_classes.torch_tabular_regression import (
    TorchTabularRegression,
)
from tracebloc_package.upload_model_classes.torch_key_point_detector import (
    TorchKeyPointDetector,
)
from tracebloc_package.upload_model_classes.torch_object_detector import (
    TorchObjectDetector,
)
from tracebloc_package.upload_model_classes.torch_text_classifier import (
    TorchTextClassifier,
)
from tracebloc_package.utils.constants import (
    KEYPOINT_DETECTION,
    TEXT_CLASSIFICATION,
    TABULAR_CLASSIFICATION,
    TABULAR_REGRESSION,
    SEMANTIC_SEGMENTATION,
)
from tracebloc_package.utils.constants import (
    TENSORFLOW_FRAMEWORK,
    PYTORCH_FRAMEWORK,
    IMAGE_CLASSIFICATION,
    OBJECT_DETECTION,
    SKLEARN_FRAMEWORK,
)
from tracebloc_package.upload_model_classes.tf_image_classifier import TfImageClassifier
from tracebloc_package.upload_model_classes.skl_tabular_classifier import (
    SKLTabularClassifier,
)
from tracebloc_package.upload_model_classes.skl_tabular_regression import (
    SKLTabularRegression,
)
from tracebloc_package.upload_model_classes.torch_image_classifier import (
    TorchImageClassifier,
)
from tracebloc_package.upload_model_classes.torch_semantic_segmentation import (
    TorchSemanticSegmentation,
)

task_classes_dict = {
    (IMAGE_CLASSIFICATION, TENSORFLOW_FRAMEWORK): TfImageClassifier,
    (IMAGE_CLASSIFICATION, PYTORCH_FRAMEWORK): TorchImageClassifier,
    (OBJECT_DETECTION, PYTORCH_FRAMEWORK): TorchObjectDetector,
    (KEYPOINT_DETECTION, PYTORCH_FRAMEWORK): TorchKeyPointDetector,
    (TEXT_CLASSIFICATION, PYTORCH_FRAMEWORK): TorchTextClassifier,
    (TABULAR_CLASSIFICATION, PYTORCH_FRAMEWORK): TorchTabularClassifier,
    (TABULAR_CLASSIFICATION, SKLEARN_FRAMEWORK): SKLTabularClassifier,
    (TABULAR_REGRESSION, PYTORCH_FRAMEWORK): TorchTabularRegression,
    (TABULAR_REGRESSION, SKLEARN_FRAMEWORK): SKLTabularRegression,
    (SEMANTIC_SEGMENTATION, PYTORCH_FRAMEWORK): TorchSemanticSegmentation,
    # Add more categories and corresponding classes here
}
