import inspect
import os
import pprint
import shutil
import requests, json
from termcolor import colored
from tracebloc_package.utils import check_parameters
from tracebloc_package.utils.general_utils import (
    getImagesCount,
    validate_kwargs,
    get_model_params_count,
    encode_method,
)
from tracebloc_package.utils.constants import (
    CONSTANT,
    STANDARD,
    ADAPTIVE,
    CUSTOM,
    TYPE,
    VALUE,
    TRAINED_WEIGHTS_FILENAME,
    TENSORFLOW_FRAMEWORK,
    PYTORCH_FRAMEWORK,
    TABULAR_CLASSIFICATION,
    TEXT_CLASSIFICATION,
    SKLEARN_FRAMEWORK,
    IMAGE_CLASSIFICATION,
    OBJECT_DETECTION,
    KEYPOINT_DETECTION,
    SEMANTIC_SEGMENTATION,
)
from tracebloc_package.utils.feature_dict import (
    DATASET_FEATURE_MAPPING,
    METHOD_LIST,
    METHOD_EXAMPLES,
)


class LinkModelDataSet:
    """
    creating a training plan and assign data set
    parameters: modelId, datasetId, token

    methods:get_parameters, get_trainingplan
    """

    def __init__(self, **kwargs):
        self.default_dict = kwargs
        validate_kwargs(
            kwargs,
            {
                "modelId",
                "model",
                "modelname",
                "datasetId",
                "token",
                "weights",
                "totalDatasetSize",
                "total_images",
                "num_classes",
                "class_names",
                "data_shape",
                "batchsize",
                "model_path",
                "url",
                "environment",
                "framework",
                "model_type",
                "category",
                "loss",
                "model_id",
                "hf_token",
                "tokenizer_id",
                "utilisation_category",
                "feature_modification",
                "table_name",
            },
        )
        self.__framework = kwargs["framework"]
        self.__url = kwargs["url"]
        self.__token = kwargs["token"]
        self.__earlystopCallback = {}
        self.__reducelrCallback = {}
        self.__modelCheckpointCallback = {}
        self.__terminateOnNaNCallback = {}
        self.__learningRateSet = False
        self.__optimizerSet = False
        self.__callbacks = str()
        self.__message = "training"
        self.__datasetId = kwargs["datasetId"]
        self.__epochs = 1 if self.__framework == SKLEARN_FRAMEWORK else 10
        self.__cycles = 5 if self.__framework == SKLEARN_FRAMEWORK else 1
        self.__modelId = kwargs["modelId"]
        self.__modelName = kwargs["modelname"]
        self.__model = kwargs["model"]
        self.__data_shape = kwargs["data_shape"]
        self.__data_type = "rgb"
        self.__optimizer = "sgd"
        self.__totalDatasetSize = kwargs["totalDatasetSize"]
        self.__category = kwargs["category"]
        self.__trainingDatasetSize = kwargs["totalDatasetSize"]
        self.__trainingClasses = kwargs["class_names"]
        self.__subdataset = {}
        self.__model_id = kwargs["model_id"]
        self.__hf_token = kwargs["hf_token"]
        self.__tokenizer_id = kwargs["tokenizer_id"]
        self.__lora_enable = False
        self.__lora_r = 256
        self.__lora_alpha = 512
        self.__lora_dropout = 0.05
        self.__q_lora = False
        if kwargs["loss"] is not None:
            self.__lossFunction = {TYPE: CUSTOM, VALUE: "loss.py"}
        else:
            self.__lossFunction = (
                {TYPE: STANDARD, VALUE: "crossentropy"}
                if self.__category == TEXT_CLASSIFICATION
                else {TYPE: STANDARD, VALUE: "mse"}
            )
        self.__learningRate = {TYPE: CONSTANT, VALUE: 0.001}
        self.__seed = False
        self.__total_images = kwargs["total_images"]
        self.__data_per_edge = kwargs["total_images"]
        self.__num_classes = kwargs["num_classes"]
        self.__class_names = kwargs["class_names"]
        self.__batchSize = kwargs["batchsize"]
        self.__featurewise_center = False
        self.__samplewise_center = False
        self.__featurewise_std_normalization = False
        self.__samplewise_std_normalization = False
        self.__zca_whitening = False
        self.__rotation_range = 0
        self.__width_shift_range = 0.0
        self.__height_shift_range = 0.0
        self.__brightness_range = "None"
        self.__shear_range = 0.0
        self.__zoom_range = 0.0
        self.__channel_shift_range = 0.0
        self.__fill_mode = "constant"
        self.__cval = 0.0
        self.__horizontal_flip = False
        self.__vertical_flip = False
        self.__rescale = "None"
        self.__validation_split = self.__default_validation_split()
        self.__shuffle = True
        self.__layers_non_trainable = ""
        self.__metrics = str(["accuracy"])
        self.__objective = ""
        self.__name = "None"
        self.__model_type = kwargs["model_type"]
        self.__model_params = self.__set_model_params()
        self.__upperboundTime = 0
        self.__weights = kwargs["weights"]
        self.__data_per_class = json.dumps(self.__class_names)
        self.__feature_interaction = {}
        self.__eligibility_passed = True
        self.__error_method = []
        self.__reform_model = False
        self.__utilisation_category = kwargs["utilisation_category"]
        self.model_path = kwargs["model_path"]
        self._model_name = kwargs["modelname"]
        self.tmp_path = os.path.join(
            self.model_path.rsplit("/", 1)[0],
            f"tmpmodel_{self._model_name[:64]}",
        )
        if not os.path.isdir(self.tmp_path):
            os.mkdir(self.tmp_path)
        self._environment = kwargs["environment"]
        self.__experimenturl = "https://ai.tracebloc.io/experiments/"
        if kwargs["environment"] == "development" or kwargs["environment"] == "ds":
            self.__experimenturl = "https://dev.tracebloc.io/experiments/"
        elif kwargs["environment"] == "staging":
            self.__experimenturl = "https://stg.tracebloc.io/experiments/"
        self.__table_name = kwargs.get(
            "table_name", "welds_data"
        )  # Default to welds_data
        if kwargs.get("feature_modification", False):
            print(
                "User can create new features for this dataset."
                "\nTo get feature list use 'get_features()'."
                "\nFor this you can use 'feature_interaction' method for this."
            )
            self.__feature_list = self.__get_feature_list()

    def resetTrainingPlan(self):
        self.__earlystopCallback = {}
        self.__reducelrCallback = {}
        self.__modelCheckpointCallback = {}
        self.__terminateOnNaNCallback = {}
        self.__learningRateSet = False
        self.__optimizerSet = False
        self.__callbacks = str()
        self.__epochs = 10
        self.__cycles = 1
        self.__data_shape = self.default_dict["data_shape"]
        self.__data_type = "rgb"
        self.__optimizer = "sgd"
        self.__trainingDatasetSize = self.default_dict["totalDatasetSize"]
        self.__trainingClasses = self.default_dict["class_names"]
        # self.__lossFunction = {TYPE: STANDARD, VALUE: "mse"}
        self.__learningRate = {TYPE: CONSTANT, VALUE: 0.001}
        self.__seed = False
        self.__batchSize = self.default_dict["batchsize"]
        self.__featurewise_center = False
        self.__samplewise_center = False
        self.__featurewise_std_normalization = False
        self.__samplewise_std_normalization = False
        self.__zca_whitening = False
        self.__rotation_range = 0
        self.__width_shift_range = 0.0
        self.__height_shift_range = 0.0
        self.__brightness_range = "None"
        self.__shear_range = 0.0
        self.__zoom_range = 0.0
        self.__channel_shift_range = 0.0
        self.__fill_mode = "constant"
        self.__cval = 0.0
        self.__horizontal_flip = False
        self.__vertical_flip = False
        self.__rescale = "None"
        self.__validation_split = self.__default_validation_split()
        self.__shuffle = True
        self.__layers_non_trainable = ""
        self.__metrics = str(["accuracy"])
        self.__objective = ""
        self.__name = "None"
        self.__model_type = self.default_dict["model_type"]
        self.__category = self.default_dict["category"]
        self.__upperboundTime = 0
        self.__data_per_edge = self.__total_images
        self.__data_per_class = json.dumps(self.__class_names)
        self.__feature_interaction = {}
        self.__eligibility_passed = True
        self.__reform_model = False
        print("Training Plan Parameters reset")

    def __print_error(self, error):
        self.__eligibility_passed = False
        method = inspect.currentframe().f_back.f_code.co_name
        text = colored(
            error,
            "red",
        )
        print(text, "\n")
        self.__error_method.append(method)

    def __set_model_params(self):
        return get_model_params_count(framework=self.__framework, model=self.__model)

    def __not_supported_parameters(self, parameter, framework="pytorch", message=False):
        if message:
            print_statement = parameter
        else:
            print_statement = (
                f"The parameter {parameter} is not supported on {framework}\n"
            )
        text = colored(
            print_statement,
            "red",
        )
        print(text, "\n")
        return

    def __remove_error_method(self):
        method = inspect.currentframe().f_back.f_code.co_name
        if method in self.__error_method:
            self.__error_method.remove(method)
        if len(self.__error_method) == 0:
            self.__eligibility_passed = True

    def trainingClasses(self, training_dataset: dict):
        """
        creates sub dataset of the current dataset of the no of images per class selected by user
        Please provide number of images per class
        example: dataset: {'car': 65, 'person': 42}
        Classes in dataset car, person

        trainingObject.trainingClasses({'car': 30, 'person': 30})
        """
        class_names = self.__class_names.keys()
        for class_name in class_names:
            num_images = int(self.__class_names[class_name])
            least_data = 5 if num_images > 5 else 1
            if class_name in training_dataset.keys():
                value = training_dataset[class_name]
                if least_data < value <= num_images:
                    pass
                else:
                    error_msg = (
                        f"trainingClasses: Please provide num of images for class {class_name}\n "
                        f"greater than 5 and less than equal to {num_images}\n"
                    )
                    self.__print_error(error_msg)
                    return
            else:
                error_msg = (
                    "trainingClasses: trainingDatasetSize dictionary must contain all classes that are present in the "
                    "dataset.\n"
                    " Customisation in terms of classes is not allowed.\n"
                )
                self.__print_error(error_msg)
                return
        self.__trainingClasses = training_dataset
        self.__trainingDatasetSize = getImagesCount(training_dataset)
        # recalculate the validation split
        header = {"Authorization": f"Token {self.__token}"}
        data = {
            "edges_involved": json.dumps(list(self.__data_per_edge.keys())),
            "data_per_class": json.dumps(training_dataset),
            "type": "recalculate_image_count_per_edge",
            "datasetId": self.__datasetId,
        }
        re = requests.post(
            f"{self.__url}check-model/",
            headers=header,
            data=data,
        )
        body_unicode = re.content.decode("utf-8")
        content = json.loads(body_unicode)
        if re.status_code == 200:
            self.__data_per_edge = content["total_data_per_edge"]
            if self.__validation_split < self.__default_validation_split():
                self.__validation_split = self.__default_validation_split()
            self.__data_per_class = json.dumps(
                training_dataset
            )  # assign images count for sub-dataset
            self.__subdataset = json.dumps(
                {
                    "trainingDatasetSize": self.__trainingDatasetSize,
                    "trainingClasses": self.__trainingClasses,
                }
            )
            self.__remove_error_method()
        else:  # pragma: no cover
            if self._environment == "production" or self._environment == "":
                self.__print_error("trainingClasses:Error while setting subdataset\n")
            else:
                self.__print_error(content["message"])

    def __update_image_model(self):
        """
        change image type and size data as user choice in model file provided by user
        """
        header = {"Authorization": f"Token {self.__token}"}
        data = {
            "model_name": self.__modelId,
            "data_shape": self.__data_shape,
            "data_type": self.__data_type,
            "type": "reform_model",
        }
        re = requests.post(
            f"{self.__url}check-model/",
            headers=header,
            data=data,
        )
        if re.status_code == 202:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            self.__modelId = content["model_name"]
        elif re.status_code == 400:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            error_message = f"dataType:Error Occured while setting updated image format \nfor model as {content['message']}\n"
            self.__print_error(error_message)

    def __getattr__(self, name):
        """
        Dynamic method creation based on category
        """
        if name == "data_shape" and self.__category in [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
            KEYPOINT_DETECTION,
            SEMANTIC_SEGMENTATION,
        ]:

            def data_shape(value: int):
                """
                Set image size for computer vision models
                parameters: integer. value must be between 48 and 224
                example: trainingObject.data_shape(224)
                default: 224
                maximum value : 224
                warning : for pytorch please only image size for which layers are designed and is specified in model file is allowed
                """
                if self.__framework == TENSORFLOW_FRAMEWORK:
                    if type(value) is int and (48 <= value <= 224):
                        self.__data_shape = value
                        self.__update_image_model()
                        self.__remove_error_method()
                    else:
                        error_msg = (
                            "data_shape:Invalid type or value not in range [48, 224]"
                        )
                        self.__print_error(error_msg)
                else:
                    error_msg = (
                        "data_shape:Image size is fixed for each model for pytorch\n"
                    )
                    self.__not_supported_parameters(error_msg, message=True)
                    self.__remove_error_method()

            return data_shape

        elif name == "feature_points" and self.__category == TABULAR_CLASSIFICATION:

            def feature_points(value: int):
                """
                Set number of feature points for tabular models
                parameters: integer. value must be positive
                example: trainingObject.feature_points(10)
                default: based on model input
                """
                if type(value) is int and value > 0:
                    self.__data_shape = value
                    self.__remove_error_method()
                else:
                    error_msg = (
                        "feature_points:Invalid type or value must be positive integer"
                    )
                    self.__print_error(error_msg)

            return feature_points

        elif name == "sequence_length" and self.__category == TEXT_CLASSIFICATION:

            def sequence_length(value: int):
                """
                Set sequence length for text classification models
                parameters: integer. value must be positive
                example: trainingObject.sequence_length(512)
                default: based on model input
                """
                if type(value) is int and value > 0:
                    self.__data_shape = value
                    self.__remove_error_method()
                else:
                    error_msg = (
                        "sequence_length:Invalid type or value must be positive integer"
                    )
                    self.__print_error(error_msg)

            return sequence_length

        # If method doesn't exist for this category, fall back to parent class
        return super().__getattribute__(name)

    def get_available_methods(self):
        """
        Get list of available methods based on current category
        """
        if self.__category in [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
            KEYPOINT_DETECTION,
            SEMANTIC_SEGMENTATION,
        ]:
            return ["data_shape"]
        elif self.__category == TABULAR_CLASSIFICATION:
            return ["feature_points"]
        elif self.__category == TEXT_CLASSIFICATION:
            return ["sequence_length"]
        else:
            return []

    def dataType(self, data_type: str):
        """
        Set image type to be used for training
        parameters: string type values.
        supported type: ['rgb', 'gray']
        example: trainingObject.dataType('rgb')
        default: rgb
        """
        allowed_types = ["rgb", "grayscale"]
        try:
            if type(data_type) is str:
                allowed_types.index(data_type.lower())
                self.__data_type = data_type.lower()
                if self.__framework == TENSORFLOW_FRAMEWORK:
                    self.__update_image_model()
                self.__remove_error_method()
            else:
                error_msg = f"dataType:enter image type as string\n"
                self.__print_error(error_msg)
        except:
            error_msg = f"dataType:Enter values from {allowed_types}\n"
            self.__print_error(error_msg)

    def seed(self, seed: bool):
        """
        Boolean.
        Sets the global random seed when selected
        default: False
        example:trainingObject.seed(True)
        """
        if type(seed) == bool:
            self.__seed = str(seed)
            self.__remove_error_method()
        else:
            error_msg = "seed:Invalid input type\n"
            self.__print_error(error_msg)

    def experimentName(self, name: str):
        """
        String.
        Name of the experiment
        example:trainingObject.experimentName('Classifying manufacturing defects')
        """
        if type(name) == str:
            if name == "":
                error_msg = "experimentName:experiment name cannot be empty\n"
                self.__print_error(error_msg)
            else:
                self.__name = str(name)
        else:
            error_msg = "experimentName:Invalid input type\n"
            self.__print_error(error_msg)

    def objective(self, objective: str):
        """
        String.
        Objective of the experiment
        example:trainingObject.objective('Classify images using Convolutional Neural Networks (specifically, VGG16)
        pre-trained on the ImageNet dataset with Keras deep learning library.')
        """
        if type(objective) == str:
            self.__objective = objective
            self.__remove_error_method()
        else:
            error_msg = "objective:Please enter a string in objective\n"
            self.__print_error(error_msg)

    def epochs(self, epochs: int):
        """
        Integer.
        Number of epochs to train the model.
        An epoch is an iteration over the entire data provided.
        Note that in conjunction with initial_epoch, epochs is to be understood as "final epoch".
        The model is not trained for a number of iterations given by epochs,
        but merely until the epoch of index epochs is reached.
        example: trainingObject.epochs(100)
        default: 10
        """
        if self.__framework == SKLEARN_FRAMEWORK:
            self.__not_supported_parameters(
                parameter="For Sklearn framework epochs cannot be updated. Epoch is set to 1",
                framework=self.__framework,
                message=True,
            )
            self.__epochs = 1
            self.__remove_error_method()
        elif type(epochs) == int and epochs != 0:
            self.__epochs = epochs
            self.__remove_error_method()
        else:
            error_msg = "epochs:Invalid input type or value '0' given for epochs\n"
            self.__print_error(error_msg)

    def cycles(self, cycles: int):
        """
        Set number of cycles
        parameters: integer type values.
        example: trainingObject.cycles(10)
        default: 1
        """
        if self.__framework == SKLEARN_FRAMEWORK:
            self.__not_supported_parameters(
                parameter="For Sklearn framework cycles cannot be updated. Cycle is set to 1",
                framework=self.__framework,
                message=True,
            )
            self.__cycles = 1
            self.__remove_error_method()
        elif type(cycles) == int:
            if cycles <= 0:
                error_msg = "cycles:cycle value cannot be negative or zero\n"
                self.__print_error(error_msg)
            else:
                self.__cycles = cycles
                self.__remove_error_method()
        else:
            self.__eligibility_passed = False
            error_msg = "cycles:Invalid input type\n"
            self.__print_error(error_msg)

    def __default_validation_split(self):
        """
        set default validation split when training object is created
        """
        # get edge with lowest images
        edge_min = min(self.__data_per_edge, key=self.__data_per_edge.get)
        images = int(self.__data_per_edge[edge_min])
        minimum = round(self.__num_classes / images, 2)
        if minimum == 0:
            return 0.1
        elif minimum > 0.5:
            return 0.5
        return minimum

    def validation_split(self, validation_split: float):
        """
        Float. Fraction of images reserved for validation (strictly between 0 and 1).
        example: trainingObject.validation_split(0.2)
        default: 0.1
        """
        minimum = self.__default_validation_split()

        if type(validation_split) == float and minimum <= validation_split <= 0.5:
            self.__validation_split = validation_split
            self.__remove_error_method()
        else:
            error_msg = f"validation_split:Invalid input type or value not in [{minimum}, 0.5]\n"
            self.__print_error(error_msg)

    def optimizer(self, optimizer: str):
        """
        String (name of optimizer)
        example: trainingObject.optimizer('rmsprop')
        supported optimizers: ['adam','rmsprop','sgd','adadelta', 'adagrad', 'adamax','nadam', 'ftrl'] for tensorflow
        supported optimizers: ["adam", "rmsprop", "sgd", "adadelta", "adagrad", "adamax"] for pytorch
        default: 'sgd'
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            o = [
                "adam",
                "rmsprop",
                "sgd",
                "adadelta",
                "adagrad",
                "adamax",
                "nadam",
                "ftrl",
            ]
            optlrrateflag = True
            error = None
            try:
                optimizer = optimizer.lower()
                o.index(optimizer)
                if self.__learningRateSet:
                    optlrrateflag, error = check_parameters.get_optimizer(
                        optimizer, self.__learningRate.copy()
                    )
                if not optlrrateflag and error is not None:  # pragma: no cover
                    error_msg = (
                        f"optimizer:While setting optimiser error Occurred as {error}\n"
                    )
                    self.__print_error(error_msg)
                else:
                    self.__optimizer = optimizer
                    self.__optimizerSet = True
                    self.__remove_error_method()
            except Exception as e:
                error_msg = f"optimizer:Please provide supported optimizers:\n {o}\n"
                self.__print_error(error_msg)
        else:
            o = [
                "adam",
                "adamw",
                "rmsprop",
                "sgd",
                "adadelta",
                "adagrad",
                "adamax",
            ]
            try:
                o.index(optimizer)
                self.__optimizer = optimizer
                self.__remove_error_method()
            except:
                error_msg = f"optimizer:Please provide supported optimizers: \n{o}\n"
                self.__print_error(error_msg)

    def learningRate(self, learningRate: dict):
        """
        Set learning rate by passing a dictionary
        There are three different type of learningrate : constant, adaptive, custom
        default: {'type': 'constant', 'value': 0.0001}
        Set constant type learning rate for optimization.
        parameters: value
        example: trainingObject.learningRate({'type': 'constant', 'value': 0.0001})

        Adaptive learning rate as per learning rate schedulars present in tensorflow
        parameters: dictionary containing schedular Name in schedular key value and rest all neccessary parameters added in dictionary
        example: trainingObject.learningRate({'type': 'adaptive', 'value': {'decay_rate': 0.9, 'decay_steps': 100, 'initial_learning_rate': 0.1, 'schedular': 'ExponentialDecay'}})

        Set learning rate for as custom function.
        first write custom learning rate function as method and pass method name in learning rate
        example:
        def custom_LearningRate_schedular(epoch):
            if epoch < 5:
                return 0.01
            else:
                return 0.01 * tf.math.exp(0.1 * (10 - epoch))
        trainingObject.learningRate({'type': 'custom', 'value': {'name': custom_LearningRate_schedular, 'epoch': 5}})
        """
        try:
            if self.__framework == TENSORFLOW_FRAMEWORK:
                optlrrateflag = True
                error = None
                if TYPE in learningRate.keys():
                    if self.__optimizerSet:
                        optlrrateflag, error = check_parameters.get_optimizer(
                            self.__optimizer, learningRate.copy()
                        )
                    if not optlrrateflag:
                        error_msg = f"learningRate:While setting Learning Rate error Occurred as \n{error}\n"
                        self.__print_error(error_msg)
                    else:
                        if learningRate[TYPE] == CUSTOM and callable(
                            learningRate[VALUE]["name"]
                        ):
                            try:
                                encoded_data = encode_method(
                                    learningRate[VALUE]["name"]
                                )
                                self.__learningRate = {
                                    TYPE: CUSTOM,
                                    VALUE: encoded_data,
                                    "original": learningRate[VALUE],
                                }
                                self.__learningRateSet = True
                                self.__remove_error_method()
                            except Exception as e:
                                error_msg = f"learningRate:Error while setting custom learning rate : \n{e}\n"
                                self.__print_error(error_msg)
                        elif learningRate[TYPE] == ADAPTIVE:
                            self.__learningRate = learningRate
                            self.__learningRateSet = True
                            self.__remove_error_method()
                        elif learningRate[TYPE] == CONSTANT:
                            if learningRate[VALUE] > 0:
                                self.__learningRate = learningRate
                                self.__learningRateSet = True
                                self.__remove_error_method()
                            elif learningRate[VALUE] == 0:
                                error_msg = (
                                    "learningRate:learning rate value cannot be zero\n"
                                )
                                self.__print_error(error_msg)
                            else:
                                error_msg = "learningRate:learning rate value cannot be negative\n"
                                self.__print_error(error_msg)
                        else:
                            error_msg = "learningRate:Input not as per given convention for learningRate\n"
                            self.__print_error(error_msg)
                else:
                    error_msg = "learningRate:Input not as per given convention for learningRate\n"
                    self.__print_error(error_msg)
            else:
                if learningRate[TYPE] == CONSTANT:
                    self.__learningRate = learningRate
                    self.__remove_error_method()
                else:
                    error_msg = "learningRate:Adaptive and Custom learning rate"
                    self.__not_supported_parameters(
                        parameter=error_msg, framework=self.__framework
                    )
                    self.__remove_error_method()
        except Exception as e:
            error_msg = f"learningRate:Input not as per given convention for learningRate as got error {e}\n"
            self.__print_error(error_msg)

    def lossFunction(self, lossFunction: dict):
        """
        Set the loss function.

        Parameters: String type values or custom loss function.

        Default: {'type': 'standard', 'value': 'mse'}

        Set standard loss functions like this:
        Example: `trainingObject.lossFunction({'type': 'standard', 'value': 'categorical_crossentropy'})`

        Supported loss functions for TensorFlow:
        ['binary_crossentropy', 'categorical_crossentropy', 'mse']

        Supported loss functions for PyTorch:
        ['crossentropy', 'mse', 'l1']

        Set a custom loss function like this:
        Example:
        ```python
        def custom_mse(y_true, y_pred):
            # Calculate squared difference between target and predicted values
            loss = torch.square(y_pred - y_true)  # (batch_size, 2)

            # Multiply the values with weights along the batch dimension
            loss = loss * torch.tensor([0.3, 0.7])  # (batch_size, 2)

            # Sum both loss values along the batch dimension
            loss = torch.sum(loss, axis=1)  # (batch_size,)
            return loss

        trainingObject.lossFunction({'type': 'custom', 'value': custom_mse})

        """
        try:
            if self.__framework == TENSORFLOW_FRAMEWORK:
                l = ["binary_crossentropy", "categorical_crossentropy", "mse"]
                if TYPE in lossFunction.keys() and VALUE in lossFunction.keys():
                    if lossFunction[TYPE] == STANDARD:
                        try:
                            l.index(lossFunction[VALUE].lower())
                            self.__lossFunction = lossFunction
                            self.__remove_error_method()
                        except:
                            error_msg = f"lossFunction:Please provide tensorflow supported default loss functions losses: \n{l}\n"
                            self.__print_error(error_msg)
                    elif lossFunction[TYPE] == CUSTOM:
                        shutil.copy(
                            lossFunction[VALUE], os.path.join(self.tmp_path, "loss.py")
                        )
                        if os.path.exists(os.path.join(self.tmp_path, "loss.py")):
                            try:
                                from tracebloc_package.utils.model_upload_utils import (
                                    task_classes_dict,
                                )

                                # Get appropriate task class based on category and framework
                                task_class = task_classes_dict.get(
                                    (self.__category, self.__framework)
                                )

                                if task_class:
                                    # Create task class instance
                                    task_instance = task_class(
                                        model=self.__model,
                                        model_name=self.__modelName,
                                        model_type=self.__model_type,
                                        category=self.__category,
                                        classes=self.__num_classes,
                                        progress_bar=None,
                                        message="",
                                        tmp_dir_path=self.tmp_path,
                                        token=self.__token,
                                        weights=self.__weights,
                                        url=self.__url,
                                        model_path=self.model_path,
                                        tmp_model_file_path=self.tmp_path,
                                        progress_bar_1=None,
                                        weights_path=self.tmp_path,
                                        framework=self.__framework,
                                        data_shape=self.__data_shape,
                                        batch_size=self.__batchSize,
                                        num_feature_points=None,
                                    )

                                    # Validate model with custom loss
                                    task_instance.small_training_loop(
                                        weight_filename=TRAINED_WEIGHTS_FILENAME,
                                        custom_loss=True,
                                    )

                                    encoded_data = encode_method(lossFunction[VALUE])
                                    self.__lossFunction = {
                                        TYPE: CUSTOM,
                                        VALUE: encoded_data,
                                    }
                                    self.__remove_error_method()
                                else:  # pragma: no cover
                                    error_msg = f"lossFunction: No task class found for category {self.__category} and framework {self.__framework}\n"
                                    self.__print_error(error_msg)
                                    return

                            except Exception as e:  # pragma: no cover
                                error_msg = f"lossFunction:custom loss provided gives error as \n{e}\n"
                                self.__print_error(error_msg)
                                return
                        else:
                            error_msg = "loss.py file missing \n Please refer docs for more information."
                            self.__print_error(error_msg)
                            return
                    else:
                        error_msg = "lossFunction:Invalid input function given for loss function\n"
                        self.__print_error(error_msg)
                else:
                    error_msg = "lossFunction:type missing\n"
                    self.__print_error(error_msg)
            elif self.__framework == SKLEARN_FRAMEWORK:
                l = ["mse", "binarycrossentropy"]
                if (
                    TYPE in lossFunction.keys()
                    and VALUE in lossFunction.keys()
                    and lossFunction[TYPE] == STANDARD
                ):
                    try:
                        l.index(lossFunction[VALUE].lower())
                        self.__lossFunction = lossFunction
                        self.__remove_error_method()
                    except:
                        error_msg = f"lossFunction:Please provide sklearn supported default loss functions losses: \n{l}\n"
                        self.__print_error(error_msg)
                else:
                    error_msg = f"lossFunction:only standard loss function supported in sklearn \n{l}\n"
                    self.__print_error(error_msg)
            else:
                if self.__category == TEXT_CLASSIFICATION:
                    l = ["crossentropy"]
                elif self.__category == TABULAR_CLASSIFICATION:
                    l = ["mse", "crossentropy", "binarycrossentropy"]
                else:
                    l = ["crossentropy", "mse", "l1"]
                if (
                    TYPE in lossFunction.keys()
                    and VALUE in lossFunction.keys()
                    and lossFunction[TYPE] == STANDARD
                ):
                    try:
                        l.index(lossFunction[VALUE].lower())
                        self.__lossFunction = lossFunction
                        self.__remove_error_method()
                    except:
                        error_msg = f"lossFunction:Please provide pytorch supported default loss functions losses: \n{l}\n"
                        self.__print_error(error_msg)
                elif lossFunction[TYPE] == CUSTOM:
                    shutil.copy(
                        lossFunction[VALUE], os.path.join(self.tmp_path, "loss.py")
                    )
                    if os.path.exists(os.path.join(self.tmp_path, "loss.py")):
                        try:
                            from tracebloc_package.utils.model_upload_utils import (
                                task_classes_dict,
                            )

                            # Get appropriate task class based on category and framework
                            task_class = task_classes_dict.get(
                                (self.__category, self.__framework)
                            )

                            if task_class:
                                task_instance = task_class(
                                    model=self.__model,
                                    model_name=self.__modelName,
                                    model_type=self.__model_type,
                                    category=self.__category,
                                    classes=self.__num_classes,
                                    progress_bar=None,
                                    message="",
                                    tmp_dir_path=self.tmp_path,
                                    token=self.__token,
                                    weights=self.__weights,
                                    url=self.__url,
                                    model_path=self.model_path,
                                    tmp_model_file_path=self.tmp_path,
                                    progress_bar_1=None,
                                    weights_path=self.tmp_path,
                                    framework=self.__framework,
                                    data_shape=self.__data_shape,
                                    batch_size=self.__batchSize,
                                    num_feature_points=None,
                                )

                                # Validate model with custom loss
                                task_instance.small_training_loop(
                                    weight_filename=TRAINED_WEIGHTS_FILENAME,
                                    custom_loss=True,
                                )

                                encoded_data = encode_method(lossFunction[VALUE])
                                self.__lossFunction = {
                                    TYPE: CUSTOM,
                                    VALUE: encoded_data,
                                }
                                self.__remove_error_method()
                            else:  # pragma: no cover
                                error_msg = f"lossFunction: No task class found for category {self.__category} and framework {self.__framework}\n"
                                self.__print_error(error_msg)
                                return

                        except Exception as e:
                            error_msg = f"lossFunction:custom loss provided give error as \n{e}\n"
                            self.__print_error(error_msg)
                            return
                    else:
                        error_msg = "loss.py file missing in the zip.\n Please refer docs for more information."
                        self.__print_error(error_msg)
                        return
        except Exception as e:
            error_msg = f"lossFunction:Input not as per given convention for lossFunction as got error {e}\n"
            self.__print_error(error_msg)

    def __check_layers(self, layersFreeze):
        """
        load model and get all layers avaiable in model
        """
        try:
            for layer_to_freeze in layersFreeze:
                layer = self.__model.get_layer(layer_to_freeze)
        except Exception as e:
            return False, e
        return True, ""

    def layersFreeze(self, layersFreeze: list):
        """
        Provide name of layers in a list to be frozen before training a model.
        Get layers name in a model provided with the summary shown above.
        example: trainingObject.layersFreeze(['layer_name','layer_name', ...])
        default: None
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(layersFreeze) == list and all(
                isinstance(sub, str) for sub in layersFreeze
            ):
                layers_eligible = True
                status, _error = self.__check_layers(layersFreeze)
                if not status:
                    layers_eligible = False
                if layers_eligible:
                    layersFreeze = str(layersFreeze)
                    self.__layers_non_trainable = layersFreeze
                    self.__remove_error_method()
                else:
                    error_msg = f"layersFreeze:Provide layers only which model contains for layersFreeze : \n{_error}\n"
                    self.__print_error(error_msg)
            else:
                error_msg = (
                    "layersFreeze:Provide values as list of strings for layersFreeze\n"
                )
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters(
                parameter="layersFreeze", framework=self.__framework
            )
            self.__remove_error_method()

    def terminateOnNaNCallback(self):
        """
        Callback that terminates training when a NaN loss is encountered.
        example: trainingObject.terminateOnNaNCallback()
        """
        c = [""]
        self.__terminateOnNaNCallback["terminateOnNaN"] = c

    def modelCheckpointCallback(self, monitor: str, save_best_only: bool):
        """
        Callback to save the model weights. parameters: monitor: Quantity to be monitored, save_best_only:  if
        save_best_only=True, it only saves when the model is considered the "best" and the latest best model
        according to the quantity monitored will not be overwritten. example: trainingObject.modelCheckpointCallback(
        'val_loss', True)
        """
        f = ["accuracy", "loss", "val_loss", "val_accuracy"]
        try:
            f.index(monitor.lower())
            if type(save_best_only) == bool:
                c = [monitor, save_best_only]
                self.__modelCheckpointCallback["modelCheckpoint"] = c
                self.__remove_error_method()
            else:
                error_msg = "modelCheckpointCallback:Invalid datatype for arguments given for save_best_only\n"
                self.__print_error(error_msg)
        except:
            error_msg = f"modelCheckpointCallback:Please provide supported monitor values: {f}\n"
            self.__print_error(error_msg)

    def earlystopCallback(self, monitor: str, patience: int):
        """
        Stop training when a monitored metric has stopped improving.
        parameters: monitor: Quantity to be monitored,
                                patience: Number of epochs with no improvement after which training will be stopped.
        example: trainingObject.earlystopCallback('loss', 10)


        """
        f = ["accuracy", "loss", "val_loss", "val_accuracy"]
        try:
            f.index(monitor.lower())
            if type(patience) == int:
                c = [monitor, patience]
                self.__earlystopCallback["earlystopping"] = c
                self.__remove_error_method()
            else:
                error_msg = "earlystopCallback:Invalid datatype for arguments given for patience\n"
                self.__print_error(error_msg)
        except:
            error_msg = (
                f"earlystopCallback:Please provide supported monitor values: {f}\n"
            )
            self.__print_error(error_msg)

    def reducelrCallback(
        self, monitor: str, factor: float, patience: int, min_delta: float
    ):
        """
        Reduce learning rate when a metric has stopped improving. parameters: monitor: Quantity to be monitored,
        factor: factor by which the learning rate will be reduced. new_lr = lr * factor. patience: number of epochs
        with no improvement after which learning rate will be reduced. min_delta: threshold for measuring the new
        optimum, to only focus on significant changes.
        example: trainingObject.reducelrCallback('loss', 0.1, 10, 0.0001)
        """
        f = ["accuracy", "loss", "val_loss", "val_accuracy"]
        try:
            f.index(monitor.lower())
            if (
                type(factor) == float
                and type(patience) == int
                and type(min_delta) == float
            ):
                c = [monitor, factor, patience, min_delta]
                self.__reducelrCallback["reducelr"] = c
                self.__remove_error_method()
            else:
                error_msg = "reducelrCallback:Invalid datatype for arguments given for reducelrCallback\n"
                self.__print_error(error_msg)
        except:
            error_msg = (
                f"reducelrCallback:Please provide supported monitor values: {f}\n"
            )
            self.__print_error(error_msg)

    def __setCallbacks(self):
        """
        List of dictionaries.
        List of tensorflow callbacks for training.
        default: []
        """
        c = []
        if len(self.__reducelrCallback) != 0:
            c.append(self.__reducelrCallback)
        if len(self.__earlystopCallback) != 0:
            c.append(self.__earlystopCallback)
        if len(self.__modelCheckpointCallback) != 0:
            c.append(self.__modelCheckpointCallback)
        if len(self.__terminateOnNaNCallback) != 0:
            c.append(self.__terminateOnNaNCallback)

        self.__callbacks = str(c)

    def samplewise_center(self, samplewise_center: bool):
        """
        Boolean. Set each sample mean to 0.
        example: trainingObject.samplewise_center(True)
        default: False
        """
        if self.__framework != PYTORCH_FRAMEWORK:
            if type(samplewise_center) == bool:
                self.__samplewise_center = samplewise_center
                self.__remove_error_method()
            else:
                error_msg = (
                    "samplewise_center:Invalid input type given for samplewise_center\n"
                )
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("samplewise_center")
            self.__remove_error_method()

    def samplewise_std_normalization(self, samplewise_std_normalization: bool):
        """
        Boolean. Divide each input by its std.
        example: trainingObject.samplewise_std_normalization(True)
        default: False
        """
        if self.__framework != PYTORCH_FRAMEWORK:
            if type(samplewise_std_normalization) == bool:
                self.__samplewise_std_normalization = samplewise_std_normalization
                self.__remove_error_method()
            else:
                error_msg = "samplewise_std_normalization:Invalid input type given for samplewise_std_normalization\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("samplewise_std_normalization")
            self.__remove_error_method()

    def rotation_range(self, rotation_range: int):
        """
        Int. Degree range for random rotations.
        example: trainingObject.rotation_range(2)
        default: 0
        """
        if self.__framework != SKLEARN_FRAMEWORK:
            if type(rotation_range) == int:
                self.__rotation_range = rotation_range
                self.__remove_error_method()
            else:
                error_msg = (
                    "rotation_range:Invalid input type given for rotation_range\n"
                )
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters(
                "rotation_range", framework=SKLEARN_FRAMEWORK
            )
            self.__remove_error_method()

    def width_shift_range(self, width_shift_range):
        """
        Float or int
        float: fraction of total width, if < 1, or pixels if >= 1.
        int: integer number of pixels from interval (-width_shift_range, +width_shift_range)
        With width_shift_range=2 possible values are integers [-1, 0, +1], same as with width_shift_range=[-1, 0, +1],
        while with width_shift_range=1.0 possible values are floats in the interval [-1.0, +1.0).
        example: trainingObject.width_shift_range(0.1)
        default: 0.0
        """
        if type(width_shift_range) == float or type(width_shift_range) == int:
            self.__width_shift_range = width_shift_range
            self.__remove_error_method()
        else:
            error_msg = (
                "width_shift_range:Invalid input type given for width_shift_range\n"
            )
            self.__print_error(error_msg)

    def height_shift_range(self, height_shift_range):
        """
        Float or int
        float: fraction of total height, if < 1, or pixels if >= 1.
        int: integer number of pixels from interval (-height_shift_range, +height_shift_range)
        With height_shift_range=2 possible values are integers [-1, 0, +1], same as with height_shift_range=[-1, 0, +1],
        while with height_shift_range=1.0 possible values are floats in the interval [-1.0, +1.0).
        example: trainingObject.height_shift_range(0.1)
        default: 0.0
        """
        if type(height_shift_range) == float or type(height_shift_range) == int:
            self.__height_shift_range = height_shift_range
            self.__remove_error_method()
        else:
            error_msg = (
                "height_shift_range:Invalid input type given for height_shift_range\n"
            )
            self.__print_error(error_msg)

    def brightness_range(self, brightness_range):
        """
        Tuple or list of two floats. Range for picking a brightness shift value from.
        example: trainingObject.brightness_range((0.1,0.4))
        default: None
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if (type(brightness_range) == tuple and len(brightness_range) == 2) or (
                type(brightness_range) == list and len(brightness_range)
            ) == 2:
                if (
                    type(brightness_range[0]) == float
                    and type(brightness_range[1]) == float
                ):
                    brightness_range = str(brightness_range)
                    self.__brightness_range = brightness_range
                    self.__remove_error_method()
                else:
                    error_msg = (
                        "brightness_range:provide float values for brightness_range\n"
                    )
                    self.__print_error(error_msg)
            else:
                error_msg = "brightness_range:Please provide tuple of two floats for brightness_range\n"
                self.__print_error(error_msg)
        else:
            if type(brightness_range) == float:
                brightness_range = str(brightness_range)
                self.__brightness_range = brightness_range
                self.__remove_error_method()
            else:
                error_msg = (
                    "brightness_range:provide float value for brightness_range\n"
                )
                self.__print_error(error_msg)

    def shear_range(self, shear_range: float):
        """
        Float. Shear Intensity (Shear angle in counter-clockwise direction in degrees)
        example: trainingObject.shear_range(0.2)
        default: 0.0
        """
        if type(shear_range) == float:
            self.__shear_range = shear_range
            self.__remove_error_method()
        else:
            error_msg = "shear_range:Invalid input type given for shear_range\n"
            self.__print_error(error_msg)

    def zoom_range(self, zoom_range):
        """
        Float or [lower, upper]. Range for random zoom. If a float, [lower, upper] = [1-zoom_range, 1+zoom_range].
        example: trainingObject.zoom_range(0.2)
        default: 0.0
        """
        if type(zoom_range) == float or type(zoom_range) == list:
            self.__zoom_range = zoom_range
            self.__remove_error_method()
        else:
            error_msg = "zoom_range:Invalid input type given for zoom_range\n"
            self.__print_error(error_msg)

    def channel_shift_range(self, channel_shift_range: float):
        """
        Float. Range for random channel shifts.
        example: trainingObject.channel_shift_range(0.4)
        default: 0.0
        """
        if self.__framework == PYTORCH_FRAMEWORK and self.__data_type != "rgb":
            error_msg = "channel_shift_range:You can not set channel_shift_range if image type is not rgb\n"
            self.__print_error(error_msg)
        elif type(channel_shift_range) == float:
            self.__channel_shift_range = channel_shift_range
            self.__remove_error_method()
        elif self.__framework == SKLEARN_FRAMEWORK:
            self.__not_supported_parameters(
                "channel_shift_range", framework=SKLEARN_FRAMEWORK
            )
            self.__remove_error_method()
        else:
            error_msg = (
                "channel_shift_range:Invalid input type given for channel_shift_range\n"
            )
            self.__print_error(error_msg)

    def fill_mode(self, fill_mode: str):
        """
        Set fill mode
        parameters: string type values .
        default: 'constant'

        supported fill_mode functions: ["constant", "nearest", "reflect", "wrap"] for tensorflow
        supported fill_mode functions: ["constant", "edge", "symmetric", "reflect", "wrap"] for pytorch

        example: trainingObject.fill_mode("nearest")
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            f = ["constant", "nearest", "reflect", "wrap"]
        elif self.__framework == PYTORCH_FRAMEWORK:
            f = ["constant", "edge", "symmetric", "reflect", "wrap"]
        else:
            f = ["mean", "median", "mode"]
        try:
            f.index(fill_mode.lower())
            self.__fill_mode = fill_mode.lower()
            if self.__fill_mode != f[0]:
                self.cval(0.0)
            self.__remove_error_method()
        except:
            error_msg = f"fill_mode:Please provide supported fill modes: {f}\n"
            self.__print_error(error_msg)

    def cval(self, cval: float):
        """
        Float or Int. Value used for points outside the boundaries when fill_mode = "constant".
        example: trainingObject.cval(0.3)
        default: 0.0
        """
        if type(cval) == float:
            self.__cval = cval
            self.__remove_error_method()
            if self.__framework == PYTORCH_FRAMEWORK:
                self.__fill_mode = "constant"
        elif self.__framework == SKLEARN_FRAMEWORK:
            self.__not_supported_parameters("cval", framework=SKLEARN_FRAMEWORK)
            self.__remove_error_method()
        else:
            error_msg = "cval:Invalid input type given for cval\n"
            self.__print_error(error_msg)

    def horizontal_flip(self, horizontal_flip: bool):
        """
        Boolean. Randomly flip inputs horizontally.
        example: trainingObject.horizontal_flip(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(horizontal_flip) == bool:
                self.__horizontal_flip = horizontal_flip
                self.__remove_error_method()
            else:
                error_msg = (
                    "horizontal_flip:Invalid input type given for horizontal_flip\n"
                )
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters(
                "horizontal_flip", framework=self.__framework
            )
            self.__remove_error_method()

    def vertical_flip(self, vertical_flip: bool):
        """
        Boolean. Randomly flip inputs vertically.
        example: trainingObject.vertical_flip(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(vertical_flip) == bool:
                self.__vertical_flip = vertical_flip
                self.__remove_error_method()
            else:
                error_msg = "vertical_flip:Invalid input type given for vertical_flip\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("vertical_flip", framework=self.__framework)
            self.__remove_error_method()

    def rescale(self, rescale: float):
        """
        rescaling factor. Defaults to None. If None, no rescaling is applied,
        otherwise we multiply the data by the value provided (after applying all other transformations).
        example: trainingObject.rescale(0.003921568627)
        default: None
        """
        if isinstance(rescale, float):
            self.__rescale = rescale
            self.__remove_error_method()
        else:
            error_msg = "rescale:Invalid input type given for rescale\n"
            self.__print_error(error_msg)

    def shuffle(self, shuffle: bool):
        """
        whether to shuffle the data (default: True)
        example: trainingObject.shuffle(False)
        default: True
        """
        if type(shuffle) == bool:
            self.__shuffle = shuffle
            self.__remove_error_method()
        else:
            error_msg = "shuffle:Invalid input type given for shuffle\n"
            self.__print_error(error_msg)

    def __get_feature_list(self):
        """
        Get feature list from DATASET_FEATURE_MAPPING or fetch from API if not found
        """
        # First try to get from predefined mapping
        feature_list = DATASET_FEATURE_MAPPING.get(self.__table_name)

        # If not found in mapping, fetch from API
        if feature_list is None:
            try:
                header = {"Authorization": f"Token {self.__token}"}

                # Make GET request to fetch schema for table_name
                response = requests.get(
                    f"{self.__url}dataset/global_meta_data/?dataset_id={self.__datasetId}",
                    headers=header,
                )

                if response.status_code == 200:
                    content = response.json()
                    # Extract schema from response
                    feature_list = list(content.get("schema", {}).keys())
                    if not feature_list:
                        print(
                            f"Warning: No features found for dataset = '{self.__datasetId}'"
                        )
                    excluded_columns = {
                        "id",
                        "created_at",
                        "updated_at",
                        "status",
                        "data_intent",
                        "data_id",
                        "filename",
                        "extension",
                        "annotation",
                        "ingestor_id",
                    }
                    feature_list = [
                        col for col in feature_list if col not in excluded_columns
                    ]
                else:
                    print(
                        f"Warning: Failed to fetch schema from API. Status code: {response.status_code}"
                    )
                    feature_list = []
                return feature_list
            except Exception as e:
                print(f"Warning: Error fetching schema from API: {str(e)}")
                return []

    def get_features(self):  # pragma: no cover
        if not self.__feature_list:
            print(
                f"Warning: No features available for dataset type '{self.__table_name}'"
            )
        else:
            pprint.pprint(
                f"The feature list for {self.__table_name} is {self.__feature_list}"
            )
        pprint.pprint(f"The method options are: {METHOD_LIST}")
        pprint.pprint(f"The example for each method use are: {METHOD_EXAMPLES}")

    def feature_interaction(self, dict):
        """
        Create new feature and provide both feature name and its interaction method
        Examples:
        - For basic interactions: {'feature1': feature1, 'feature2': feature2, 'method': method}
        - For single feature methods: {'feature1': feature1, 'method': 'outlier simulation'}
        - For include/exclude lists: {'feature_list': [feature1, feature2, ...], 'method': 'include'/'exclude'}
        """
        # Validate input parameter
        if not isinstance(dict, dict):
            error_msg = "feature_interaction: Input must be a dictionary\n"
            self.__print_error(error_msg)
            return

        if not dict:
            error_msg = "feature_interaction: Input dictionary cannot be empty\n"
            self.__print_error(error_msg)
            return

        if not self.__feature_list:
            error_msg = f"feature_interaction: No features available for table name '{self.__table_name}'\n"
            self.__print_error(error_msg)
            return

        # Validate method key exists and is a string
        if "method" not in dict:
            error_msg = "feature_interaction: 'method' key is required\n"
            self.__print_error(error_msg)
            return

        if not isinstance(dict["method"], str):
            error_msg = "feature_interaction: 'method' must be a string\n"
            self.__print_error(error_msg)
            return

        if not dict["method"].strip():
            error_msg = "feature_interaction: 'method' cannot be empty\n"
            self.__print_error(error_msg)
            return

        if dict["method"] not in METHOD_LIST:
            error_msg = "feature_interaction: Invalid method name provided\n"
            self.__print_error(error_msg)
            return

        method = dict["method"]

        # Handle include/exclude methods
        if method in ["include", "exclude"]:
            if "feature_list" not in dict:
                error_msg = "feature_interaction: feature_list is required for include/exclude methods\n"
                self.__print_error(error_msg)
                return

            if not isinstance(dict["feature_list"], list):
                error_msg = "feature_interaction: feature_list must be a list\n"
                self.__print_error(error_msg)
                return

            if not dict["feature_list"]:
                error_msg = "feature_interaction: feature_list cannot be empty\n"
                self.__print_error(error_msg)
                return

            # Validate all features in the list are strings and not empty
            for i, feature in enumerate(dict["feature_list"]):
                if not isinstance(feature, str):
                    error_msg = (
                        f"feature_interaction: feature_list[{i}] must be a string\n"
                    )
                    self.__print_error(error_msg)
                    return
                if not feature.strip():
                    error_msg = (
                        f"feature_interaction: feature_list[{i}] cannot be empty\n"
                    )
                    self.__print_error(error_msg)
                    return

            # Validate all features in the list exist in feature list
            invalid_features = [
                f for f in dict["feature_list"] if f not in self.__feature_list
            ]
            if invalid_features:
                error_msg = f"feature_interaction: Invalid feature names provided: {invalid_features}\n"
                self.__print_error(error_msg)
                return

            # Initialize method key if not exists
            if method not in self.__feature_interaction:
                self.__feature_interaction[method] = []

            # Add new features to the list if they don't exist
            for feature in dict["feature_list"]:
                if feature not in self.__feature_interaction[method]:
                    self.__feature_interaction[method].append(feature)

        else:
            # Handle other methods
            # Validate feature1 key exists and is a string
            if "feature1" not in dict:
                error_msg = "feature_interaction: 'feature1' key is required\n"
                self.__print_error(error_msg)
                return

            if not isinstance(dict["feature1"], str):
                error_msg = "feature_interaction: 'feature1' must be a string\n"
                self.__print_error(error_msg)
                return

            if not dict["feature1"].strip():
                error_msg = "feature_interaction: 'feature1' cannot be empty\n"
                self.__print_error(error_msg)
                return

            if dict["feature1"] not in self.__feature_list:
                error_msg = "feature_interaction: Invalid feature name provided for 'feature1'\n"
                self.__print_error(error_msg)
                return

            # Validate feature2 if provided
            if "feature2" in dict:
                if not isinstance(dict["feature2"], str):
                    error_msg = "feature_interaction: 'feature2' must be a string\n"
                    self.__print_error(error_msg)
                    return

                if not dict["feature2"].strip():
                    error_msg = "feature_interaction: 'feature2' cannot be empty\n"
                    self.__print_error(error_msg)
                    return

                if dict["feature2"] not in self.__feature_list:
                    error_msg = "feature_interaction: Invalid feature name provided for 'feature2'\n"
                    self.__print_error(error_msg)
                    return

            # Initialize method key if not exists
            if method not in self.__feature_interaction:
                self.__feature_interaction[method] = []

            # Create new feature interaction
            new_interaction = {"feature1": dict["feature1"]}

            # Only add feature2 if it exists and is not None
            if "feature2" in dict and dict["feature2"] is not None:
                new_interaction["feature2"] = dict["feature2"]

            # Add new interaction if it doesn't exist
            if new_interaction not in self.__feature_interaction[method]:
                self.__feature_interaction[method].append(new_interaction)
        self.__remove_error_method()

    def enable_lora(self, lora_enable: bool = False):
        assert isinstance(lora_enable, bool), "lora_enable must be a boolean."
        self.__lora_enable = lora_enable

    def set_lora_parameters(
        self, lora_r: int, lora_alpha: int, lora_dropout: float, q_lora: bool
    ):
        assert self.__lora_enable == True, "Enable lora first using enable_lora"
        """
        Set parameters related to LoRA.

        Parameters:
        - lora_r (int): The rank for the LoRA layer. Must be a positive integer.
        - lora_alpha (int): The scaling factor alpha for LoRA. Must be a positive integer.
        - lora_dropout (float): The dropout rate for LoRA layers. Must be a float between 0 and 1.
        - q_lora (bool): Whether to enable or disable Q LoRA.

        Examples:
            trainingObject.set_lora_parameters(256, 512, 0.05, False)

        Defaults:
            lora_r: 256, lora_alpha: 512, lora_dropout: 0.05, q_lora: False
        """
        if self.__category != TEXT_CLASSIFICATION:
            print(
                "Operation not allowed. This function only works for language models."
            )
            return  # Early exit

        try:
            assert (
                isinstance(lora_r, int) and lora_r > 0
            ), "lora_r must be a positive integer."
            assert (
                isinstance(lora_alpha, int) and lora_alpha > 0
            ), "lora_alpha must be a positive integer."
            assert (
                isinstance(lora_dropout, float) and 0 <= lora_dropout <= 1
            ), "lora_dropout must be a float between 0 and 1."
            assert isinstance(q_lora, bool), "q_lora must be a boolean."

            # If all assertions pass, set the parameters
            self.__lora_r = lora_r
            self.__lora_alpha = lora_alpha
            self.__lora_dropout = lora_dropout
            self.__q_lora = q_lora

            # Remove previous errors if any
            self.__remove_error_method()

            # Validate LoRA configuration with a small training loop
            if (
                self.__framework == PYTORCH_FRAMEWORK
                and self.__category == TEXT_CLASSIFICATION
            ):
                print("Validating LoRA configuration...")

                # Create parameters dictionary for LoRA
                parameters = {
                    "lora_r": self.__lora_r,
                    "lora_alpha": self.__lora_alpha,
                    "lora_dropout": self.__lora_dropout,
                    "q_lora": self.__q_lora,
                }

                # Get the appropriate task class
                from tracebloc_package.utils.model_upload_utils import task_classes_dict
                from tracebloc_package.utils.constants import TRAINED_WEIGHTS_FILENAME

                # Get the TorchTextClassifier class
                task_class = task_classes_dict.get(
                    (TEXT_CLASSIFICATION, PYTORCH_FRAMEWORK)
                )

                if task_class:
                    # Create task instance with LoRA enabled
                    model_upload_params = {
                        "model": self.__model,
                        "model_name": self._model_name,
                        "token": self.__token,
                        "url": self.__url,
                        "category": self.__category,
                        "classes": self.__num_classes,
                        "framework": self.__framework,
                        "message": "",
                        "progress_bar": None,
                        "tmp_model_file_path": self.tmp_path,
                        "tmp_dir_path": self.tmp_path,
                        "model_type": self.__model_type,
                        "num_feature_points": None,
                        "data_shape": self.__data_shape,
                        "batch_size": self.__batchSize,
                        "weights": self.__weights,
                        "model_path": self.model_path,
                        "weights_path": self.tmp_path,
                        "progress_bar_1": None,
                        "model_id_llm": self.__model_id,
                        "lora_enable": True,
                        "parameters": parameters,
                    }

                    # Create the task instance with all required parameters
                    task_instance = task_class(**model_upload_params)

                    # Run a small training loop to validate LoRA configuration
                    try:
                        task_instance.small_training_loop(
                            weight_filename=TRAINED_WEIGHTS_FILENAME
                        )
                        print("LoRA configuration validated successfully!")
                    except Exception as e:
                        error_msg = f"LoRA validation failed: {e}"
                        self.__print_error(error_msg)
                        return
                else:
                    print(
                        "Could not validate LoRA configuration - task class not found."
                    )

        except AssertionError as e:
            self.__print_error(str(e))

    def __checkTrainingPlan(self):
        # call API to compare current training plan for duplication
        header = {"Authorization": f"Token {self.__token}"}
        data = self.__get_params_training()
        # print(data,"\n\n")
        re = requests.post(
            f"{self.__url}trainingplan/{self.__datasetId}/",
            headers=header,
            json=data,
        )
        # print(re.text)
        if re.status_code == 200:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            # print(content)
            if content["status"]:
                userResponse = input(
                    "You already have an experiment with current Training Plan want to proceed?\n\n"
                )
                if userResponse.lower() == "yes" or userResponse.lower() == "y":
                    return True
                elif userResponse.lower() == "no" or userResponse.lower() == "n":
                    return False
                else:
                    text = colored(f"Training Plan:Please Enter Valid Input\n", "red")
                    print(text, "\n")
            else:
                return True

    def start(self):
        if not self.__eligibility_passed:
            text = colored(
                f"Error: Not all Training Parameters are set properly.\n", "red"
            )
            print(text, "\n")
            return
        else:
            if self.__learningRate[TYPE] == CUSTOM:
                self.__learningRate["original"]["name"] = self.get_function_name(
                    self.__learningRate["original"]["name"]
                )
        # set callbacks
        self.__setCallbacks()
        # call checkTrainingPlan for duplication check
        # duplication = self.__checkTrainingPlan()
        # if duplication:
        # Create Experiment
        header = {"Authorization": f"Token {self.__token}"}
        re = requests.post(
            f"{self.__url}experiments/", headers=header, data=self.__getParameters()
        )
        if re.status_code == 201:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            text = colored(
                f"Experiment created with id:{content['experimentKey']}", "green"
            )
            print(text, "\n")
            explink = (
                self.__experimenturl
                + self.__datasetId
                + "/"
                + content["experimentKey"]
                + "/"
            )
            print("Training request sent....")
            print(
                "Updated weights will be available to download once training completed"
            )
            print("\n")
            print(" Link to Experiment is : " + str(explink))
            print(" Training Plan Information for Experiment is :")
            self.getTrainingPlan()
        elif re.status_code == 403:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            message = content["message"]
            text = colored(message, "red")
            print(text, "\n")
        elif re.status_code == 400:
            text = colored("Error:Mandatory Fields Missing", "red")
            print(text, "\n")
        else:
            if self._environment != "production":
                print(re.content, "\n")
            text = colored(
                "Error:Experiment creation Failed. Please ensure you have entered correct parameters.",
                "red",
            )
            print(text, "\n")
        self.resetTrainingPlan()

    def get_function_name(self, method_object):
        """
        Get the name of a function or method object.

        Args:
            method_object (function): A function or method object.

        Returns:
            str: The name of the function or method.
        """
        if callable(method_object):
            return method_object.__name__
        else:
            raise ValueError("Provided object is not a callable function or method.")

    def __getParameters(self):
        parameters = {
            "message": "training",
            "datasetId": self.__datasetId,
            "epochs": self.__epochs,
            "cycles": self.__cycles,
            "modelName": self.__modelId,
            "optimizer": self.__optimizer,
            "lossFunction": json.dumps(self.__lossFunction),
            "learningRate": json.dumps(self.__learningRate),
            "batchSize": self.__batchSize,
            "seed": self.__seed,
            "featurewise_center": self.__featurewise_center,
            "samplewise_center": self.__samplewise_center,
            "featurewise_std_normalization": self.__featurewise_std_normalization,
            "samplewise_std_normalization": self.__samplewise_std_normalization,
            "zca_whitening": self.__zca_whitening,
            "rotation_range": self.__rotation_range,
            "width_shift_range": self.__width_shift_range,
            "height_shift_range": self.__height_shift_range,
            "brightness_range": self.__brightness_range,
            "shear_range": self.__shear_range,
            "zoom_range": self.__zoom_range,
            "channel_shift_range": self.__channel_shift_range,
            "fill_mode": self.__fill_mode,
            "cval": self.__cval,
            "horizontal_flip": self.__horizontal_flip,
            "vertical_flip": self.__vertical_flip,
            "rescale": self.__rescale,
            "validation_split": self.__validation_split,
            "shuffle": self.__shuffle,
            "layersFreeze": self.__layers_non_trainable,
            "metrics": self.__metrics,
            "objective": self.__objective,
            "name": self.__name,
            "model_type": self.__model_type,
            "category": self.__category,
            "upperboundTime": self.__upperboundTime,
            "callbacks": self.__callbacks,
            "pre_trained_weights": self.__weights,
            "subdataset": self.__subdataset,
            "data_per_edge": json.dumps(self.__data_per_edge),
            "data_per_class": self.__data_per_class,
            "data_shape": self.__data_shape,
            "data_type": self.__data_type,
            "framework": self.__framework,
            "model_id": self.__model_id,
            "hf_token": self.__hf_token,
            "tokenizer_id": self.__tokenizer_id,
            "lora_enabled": self.__lora_enable,
            "lora_r": self.__lora_r,
            "lora_alpha": self.__lora_alpha,
            "lora_dropout": self.__lora_dropout,
            "q_lora": self.__q_lora,
            "model_parameters": self.__model_params,
            "utilisation_category": self.__utilisation_category,
            "feature_interaction": json.dumps(self.__feature_interaction),
        }

        return parameters

    def __get_params_training(self):
        parameters = {
            "message": "training",
            "datasetId": self.__datasetId,
            "epochs": self.__epochs,
            "cycles": self.__cycles,
            "modelName": self.__modelId,
            "optimizer": self.__optimizer,
            "lossFunction": json.dumps(self.__lossFunction),
            "learningRate": json.dumps(self.__learningRate),
            "batchSize": self.__batchSize,
            "seed": self.__seed,
            "featurewise_center": self.__featurewise_center,
            "samplewise_center": self.__samplewise_center,
            "featurewise_std_normalization": self.__featurewise_std_normalization,
            "samplewise_std_normalization": self.__samplewise_std_normalization,
            "zca_whitening": self.__zca_whitening,
            "rotation_range": self.__rotation_range,
            "width_shift_range": self.__width_shift_range,
            "height_shift_range": self.__height_shift_range,
            "brightness_range": self.__brightness_range,
            "shear_range": self.__shear_range,
            "zoom_range": self.__zoom_range,
            "channel_shift_range": self.__channel_shift_range,
            "fill_mode": self.__fill_mode,
            "cval": self.__cval,
            "horizontal_flip": self.__horizontal_flip,
            "vertical_flip": self.__vertical_flip,
            "rescale": self.__rescale,
            "validation_split": self.__validation_split,
            "shuffle": self.__shuffle,
            "layersFreeze": self.__layers_non_trainable,
            "metrics": self.__metrics,
            "objective": self.__objective,
            "name": self.__name,
            "model_type": self.__model_type,
            "category": self.__category,
            "upperboundTime": self.__upperboundTime,
            "callbacks": self.__callbacks,
            "pre_trained_weights": self.__weights,
            "subdataset": self.__subdataset,
            "data_shape": self.__data_shape,
            "data_type": self.__data_type,
            "framework": self.__framework,
            "model_id": self.__model_id,
            "hf_token": self.__hf_token,
            "tokenizer_id": self.__tokenizer_id,
            "lora_enabled": self.__lora_enable,
            "lora_r": self.__lora_r,
            "lora_alpha": self.__lora_alpha,
            "lora_dropout": self.__lora_dropout,
            "q_lora": self.__q_lora,
            "model_parameters": self.__model_params,
            "utilisation_category": self.__utilisation_category,
            "feature_interaction": json.dumps(self.__feature_interaction),
        }

        return parameters

    def getTrainingPlan(self):
        if self.__eligibility_passed:
            print(
                f" \033[1mTraining Description\033[0m\n\n",
                f"experimentName: {self.__name}\n",
                f"modelName: {self.__modelName}\n",
                f"objective: {self.__objective}\n",
                f"\n \033[1mDataset Parameters\033[0m\n\n",
                f"datasetId: {self.__datasetId}\n",
                f"totalDatasetSize: {self.__totalDatasetSize}\n",
                f"allClasses: {self.__class_names}\n\n",
                f"trainingDatasetSize: {self.__trainingDatasetSize}\n",
                f"trainingClasses: {self.__trainingClasses}\n",
                f"{'data_shape' if self.__category in [IMAGE_CLASSIFICATION, OBJECT_DETECTION, KEYPOINT_DETECTION, SEMANTIC_SEGMENTATION] else 'feature_points' if self.__category == TABULAR_CLASSIFICATION else 'sequence_length' if self.__category == TEXT_CLASSIFICATION else 'data_shape'}: {self.__data_shape}\n",
                f"dataType: {self.__data_type}\n",
                f"seed: {self.__seed}\n",
                "\n \033[1mTraining Parameters\033[0m\n\n",
                f"epochs: {self.__epochs}\n",
                f"cycles: {self.__cycles}\n",
                f"batchSize: {self.__batchSize}\n",
                f"validation_split: {self.__validation_split}\n",
                "\n \033[1mHyperparameters\033[0m\n\n",
                f"optimizer: {self.__optimizer}\n",
                f"lossFunction: {self.__lossFunction}\n",
                f"learningRate: {self.__learningRate}\n",
                f"layersFreeze: {self.__layers_non_trainable}\n",
                f"earlystopCallback: {self.__earlystopCallback}\n",
                f"reducelrCallback: {self.__reducelrCallback}\n",
                f"modelCheckpointCallback: {self.__modelCheckpointCallback}\n",
                f"terminateOnNaNCallback: {self.__terminateOnNaNCallback}\n",
                "\n \033[1mAugmentation Parameters\033[0m\n\n",
                f"brightness_range: {self.__brightness_range}\n",
                f"channel_shift_range: {self.__channel_shift_range}\n",
                f"cval: {self.__cval}\n",
                f"fill_mode: {self.__fill_mode}\n",
                f"height_shift_range: {self.__height_shift_range}\n",
                f"horizontal_flip: {self.__horizontal_flip}\n",
                f"rescale: {self.__rescale}\n",
                f"rotation_range: {self.__rotation_range}\n",
                f"samplewise_center: {self.__samplewise_center}\n",
                f"samplewise_std_normalization: {self.__samplewise_std_normalization}\n",
                f"shear_range: {self.__shear_range}\n",
                f"shuffle: {self.__shuffle}\n",
                f"vertical_flip: {self.__vertical_flip}\n",
                f"width_shift_range: {self.__width_shift_range}\n",
                f"zoom_range: {self.__zoom_range}\n",
            )
            if self.__category == TABULAR_CLASSIFICATION:
                print(f"feature_interaction: {self.__feature_interaction}\n")
            if self.__category == TEXT_CLASSIFICATION:
                print(
                    "\n \033[1mLLM Parameters\033[0m\n\n",
                    f"model_id: {self.__model_id}\n",
                    f"tokenizer_id: {self.__tokenizer_id}\n",
                    f"lora_enable: {self.__lora_enable}\n",
                    f"lora_r: {self.__lora_r}\n",
                    f"lora_alpha: {self.__lora_alpha}\n",
                    f"lora_dropout: {self.__lora_dropout}\n",
                    f"q_lora: {self.__q_lora}\n",
                )

        else:
            print("Error: Not all Training Parameters are set properly\n")
            return
