# import useful libraries
import os
import warnings
import gc
import requests
import json
import getpass

from tqdm import tqdm
from tracebloc_package.model_file_checks.functional_checks import CheckModel
from termcolor import colored
import rich

from .linkModelDataSet import LinkModelDataSet
from .utils.general_utils import (
    getImagesCount,
    get_paths,
    require_login,
    env_url,
    print_error,
    remove_tmp_file,
)
from tracebloc_package.utils.constants import (
    TENSORFLOW_FRAMEWORK,
    IMAGE_CLASSIFICATION,
    OBJECT_DETECTION,
    TEXT_CLASSIFICATION,
    TABULAR_CLASSIFICATION,
    TABULAR_REGRESSION,
    KEYPOINT_DETECTION,
    SEMANTIC_SEGMENTATION,
    YOLO,
)
from tracebloc_package.utils.model_upload_utils import task_classes_dict

warnings.filterwarnings("ignore")


class User:
    """
    Parameters: username, password

    ***
    Please provide a valid username and password
    Call getToken method on Login to get new token for provided
    username and password
    """

    def __init__(self, environment="production", username=None, password=None):
        self.__classes = None
        self.__model_upload_params = None
        self.__environment = environment
        self.__url = env_url(self.__environment)
        if self.__url is None:  # pragma: no cover
            text = colored(
                "\nThe class does not take any arguments. Just run: user = User()",
                "red",
            )
            print(text, "\n")
            return
        self.__username = username
        if not self.__username:
            self.__username = input("Enter your email address : ")
        self.__password = password
        if not self.__password:
            self.__password = getpass.getpass("Enter your password : ")
        self.__token = self.login()
        self.__ext = ".py"
        self.__data_shape = 224
        self.__batch_size = 16
        self.__model_path = ""
        self.__framework = TENSORFLOW_FRAMEWORK
        self.__category = IMAGE_CLASSIFICATION
        self.__model_type = ""
        self.__model_id = ""
        self.__hf_token = ""
        self.__tokenizer_id = ""
        self.__model_name = ""
        self.__model_file_path = ""
        self.__weights_file_path = ""
        self.__weights = False
        self.__general_checks_obj = None
        self.__model = None
        self.__model_id_llm = None
        self.__loss = None
        self.__message = None
        self.__utilisation_category = "low"
        self.__feature_modification = False
        self.__features = {}
        self.__table_name = ""

    def login(self):
        """Function to get Token for username provided"""
        r = requests.post(
            f"{self.__url}api-token-auth/",
            data={"username": self.__username, "password": self.__password},
        )
        if r.status_code == 200:
            print(f"\nLogged in as {self.__username}")
            token = json.loads(r.text)["token"]
            return token
        else:
            print("\n")
            text = colored(
                "Login credentials are not correct. Please try again.",
                "red",
            )
            print(text, "\n")
            return ""

    @require_login
    def logout(self):
        """Call this to logout from current sesion"""
        try:
            header = {"Authorization": f"Token {self.__token}"}
            r = requests.post(f"{self.__url}logout/", headers=header)
            if r.status_code == 200:
                self.__token = None
                print("You have been logged out.")
            else:
                print("Logout Failed. Retry!")
        except Exception as e:  # pragma: no cover
            print("Logout Failed. Retry!")

    def __set_model_val_params(self):
        """
        the function set the model validation parameters which will be used for the model file checks to
        validate if model is supported or not
        """
        # Assign category-specific variables to __data_shape for unified internal usage
        if self.__general_checks_obj.category in [
            IMAGE_CLASSIFICATION,
            OBJECT_DETECTION,
            SEMANTIC_SEGMENTATION,
        ]:
            # CV categories use image_size
            self.__data_shape = self.__general_checks_obj.image_size
        elif self.__general_checks_obj.category == KEYPOINT_DETECTION:
            self.__data_shape = self.__general_checks_obj.image_size
            self.__features = {
                "number_of_keypoints": self.__general_checks_obj.num_feature_points
            }
        elif self.__general_checks_obj.category in [TABULAR_CLASSIFICATION, TABULAR_REGRESSION]:
            # Tabular categories (classification and regression) use num_feature_points
            self.__data_shape = self.__general_checks_obj.num_feature_points
            self.__features = {
                "number_of_columns": self.__general_checks_obj.num_feature_points
            }
        elif self.__general_checks_obj.category == TEXT_CLASSIFICATION:
            # Text category uses sequence_length
            self.__data_shape = self.__general_checks_obj.sequence_length
        else:
            # Default fallback
            self.__data_shape = self.__general_checks_obj.image_size

        self.__batch_size = self.__general_checks_obj.batch_size
        self.__model_type = self.__general_checks_obj.model_type
        self.__model_id_llm = self.__general_checks_obj.model_id
        self.__hf_token = self.__general_checks_obj.hf_token
        self.__tokenizer_id = self.__general_checks_obj.tokenizer_id
        self.__classes = self.__general_checks_obj.output_classes
        self.__framework = self.__general_checks_obj.framework
        self.__category = self.__general_checks_obj.category
        # get parameters and update the model params
        self.__model_upload_params = {
            "model_name": self.__model_name,
            "model": self.__general_checks_obj.model,
            "token": self.__token,
            "url": self.__url,
            "category": self.__category,
            "classes": self.__classes,
            "framework": self.__framework,
            "message": self.__message,
            "progress_bar": self.__general_checks_obj.progress_bar,
            "tmp_model_file_path": self.__general_checks_obj.tmp_file,
            "tmp_dir_path": self.__general_checks_obj.tmp_file_path,
            "model_type": self.__general_checks_obj.model_type,
            "num_feature_points": self.__general_checks_obj.num_feature_points,
            "data_shape": self.__data_shape,
            "batch_size": self.__batch_size,
            "weights": self.__weights,
            "model_path": self.__model_file_path,
            "weights_path": self.__weights_file_path,
            "progress_bar_1": self.__progress_bar,
        }
        if self.__category == TEXT_CLASSIFICATION:
            self.__model_upload_params.update({"model_id_llm": self.__model_id_llm})
        gc.collect()

    def __run_general_model_checks(self):
        try:
            self.__progress_bar = tqdm(total=8, desc="Model Checks Progress")
            model_checks_generic = CheckModel(
                self.__progress_bar,
                model_name=self.__model_name,
                model_path=self.__model_file_path,
            )
            (
                status,
                self.__message,
                self.__model_name,
                __progress_bar,
            ) = model_checks_generic.model_func_checks()

            if not status:
                remove_tmp_file(tmp_dir_path=model_checks_generic.tmp_file_path)
                text = colored(
                    self.__message,
                    "red",
                )
                print(text, "\n")
                self.__progress_bar.close()
                raise Exception(self.__message)
            self.__model = model_checks_generic.model
            self.__general_checks_obj = model_checks_generic
            gc.collect()
        except:  # pragma: no cover
            print_error(
                text=f"\nUpload failed.\n",
                docs_print=True,
                docs="For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs["
                "/link]",
            )
            self.__progress_bar.close()
            return None

    @require_login
    def uploadModel(self, modelname: str, weights=False):
        """
        Make sure model file and weights are in current directory
        Parameters: modelname

        modelname: model file name eg: vgg-net, if file name is vgg-net.py
        weights: upload pre-trained weights if set True. Default: False

        *******
        return: model unique ID
        """
        try:
            # check if user is providing weights along with the model file
            if weights:
                self.__weights = weights
            else:
                self.__weights = False
            self.__model_name = modelname

            # get model name and paths: model file path and weight file path
            (
                self.__model_name,
                self.__model_file_path,
                self.__weights_file_path,
                self.__ext,
            ) = get_paths(path=self.__model_name, weights_available=weights)
            # run general model file checks
            self.__run_general_model_checks()
            if self.__general_checks_obj is None:
                return None
            self.__set_model_val_params()

            # validate and upload model provided
            model_check_obj = task_classes_dict.get(
                (self.__category, self.__general_checks_obj.framework), lambda: None
            )(**self.__model_upload_params)

            model_check_obj.validate_model_file()
            # get the new model id from server
            self.__model_id = model_check_obj.received_model_name
            self.__utilisation_category = model_check_obj.utilisation_category
            if (
                self.__category == OBJECT_DETECTION
                and model_check_obj.model_type == YOLO
            ):
                self.__loss = model_check_obj.loss
            else:
                self.__loss = None
            if self.__model_id == "" or self.__model_id is None:
                print_error(text=f"'{self.__model_name}' upload Failed.")
                self.__weights = False
                return
            else:
                print_error(text=f"\n'{self.__model_name}' upload successful.\n")
                remove_tmp_file(
                    tmp_dir_path=self.__general_checks_obj.tmp_file_path
                )  # remove file after successful
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @require_login
    def linkModelDataset(self, datasetId: str):
        """
        Role: Link and checks model & datasetId compatibility
              create training plan object

        parameters: modelId, datasetId
        return: training plan object
        """
        try:
            if self.__model_id == "" or self.__model_id is None:
                text = colored(
                    "Model not uploaded. Please first upload the model.", "red"
                )
                print(text, "\n")
                return None
            if self.__check_model(datasetId):
                return LinkModelDataSet(
                    model_id=self.__model_id_llm,
                    modelId=self.__model_id,
                    hf_token=self.__hf_token,
                    tokenizer_id=self.__tokenizer_id,
                    model=self.__model,
                    modelname=self.__model_name,
                    datasetId=datasetId,
                    token=self.__token,
                    weights=self.__weights,
                    totalDatasetSize=self.__totalDatasetSize,
                    total_images=self.__total_images,
                    num_classes=self.__num_classes,
                    class_names=self.__class_names,
                    data_shape=self.__data_shape,
                    batchsize=self.__batch_size,
                    model_path=self.__model_path,
                    url=self.__url,
                    environment=self.__environment,
                    framework=self.__framework,
                    model_type=self.__model_type,
                    category=self.__category,
                    loss=self.__loss,
                    utilisation_category=self.__utilisation_category,
                    feature_modification=self.__feature_modification,
                    table_name=self.__table_name,
                )
            else:
                return None
        except Exception as e:  # pragma: no cover
            text = colored("Model Link Failed!", "red")
            print(text, "\n")

    def __check_model(self, datasetId):
        try:
            header = {"Authorization": f"Token {self.__token}"}
            re = requests.post(
                f"{self.__url}check-model/",
                headers=header,
                data={
                    "datasetId": datasetId,
                    "modelName": self.__model_id,
                    "file_type": self.__ext,
                    "type": "linking_dataset",
                    "framework": self.__framework,
                    "category": self.__category,
                    "classes": self.__classes,
                    "match_point": json.dumps(self.__features),
                },
            )
            if re.status_code == 403 or re.status_code == 400:
                error_message = (
                    f"Please provide a valid dataset ID.\n"
                    f"There is no dataset with ID: {datasetId}.\n"
                )
                try:
                    body_unicode = re.content.decode("utf-8")
                    content = json.loads(body_unicode)
                    if "message" in content:
                        error_message += f"{content['message']}"
                except:
                    pass
                text = colored(error_message, "red")
                print(text)
                return False
            elif re.status_code == 409:
                error_message = "Model Type and Dataset Category mismatched"
                try:
                    body_unicode = re.content.decode("utf-8")
                    content = json.loads(body_unicode)
                    if "message" in content:
                        error_message += f"\n{content['message']}"
                except:
                    pass
                text = colored(error_message, "red")
                print(text)
                return False
            elif re.status_code == 202 or re.status_code == 200:
                body_unicode = re.content.decode("utf-8")
                content = json.loads(body_unicode)
                # Check if there's an error message in the response
                if "error" in content and content.get("error") and "message" in content:
                    error_message = "Error Occurred. Linking Failed!"
                    error_message += f"\n{content['message']}"
                    text = colored(error_message, "red")
                    print(text)
                    return False
                if content["status"] == "failed":
                    text = colored("Assignment failed!", "red")
                    print(text, "\n")
                    print(f"Dataset '{datasetId}' expected parameters:")
                    message = ""
                    # For regression, don't include output_classes
                    if self.__category != TABULAR_REGRESSION:
                        message = f"output_classes : {content['datasetClasses']}, "
                    if self.__features is not None:
                        keys_to_match = list(self.__features.keys())
                    else:
                        keys_to_match = None
                    if "matchPoints" in content.keys() and keys_to_match:
                        for key_to_match in keys_to_match:
                            if key_to_match in content["matchPoints"]:
                                expected = content["matchPoints"][key_to_match].get("expected")
                                if expected is not None and self.__category in [
                                    TABULAR_CLASSIFICATION,
                                    TABULAR_REGRESSION,
                                    KEYPOINT_DETECTION,
                                ]:
                                    message += f"num_feature_points : {expected}"
                                elif expected is not None:
                                    message += f"{key_to_match} : {expected}"
                    print(f"{message}\n")
                    print(f"'{self.__model_name}' parameters:")
                    message = ""
                    # For regression, don't include output_classes
                    if self.__category != TABULAR_REGRESSION:
                        message = f"output_classes : {content['outputClass']}, "
                    if keys_to_match:
                        for key_to_match in keys_to_match:
                            if self.__category in [
                                TABULAR_CLASSIFICATION,
                                TABULAR_REGRESSION,
                                KEYPOINT_DETECTION,
                            ]:
                                message += (
                                    f"num_feature_points : {self.__features[key_to_match]}"
                                )
                            else:
                                message += (
                                    f"{key_to_match} : {self.__features[key_to_match]}"
                                )
                    print(f"{message}\n")
                    print(
                        "Please change your model parameters to match the datasets parameters."
                    )
                    return False
                elif content["status"] == "passed":
                    self.__total_images = content["total_images"]
                    self.__num_classes = content["datasetClasses"]
                    self.__class_names = content["class_names"]
                    self.__totalDatasetSize = getImagesCount(self.__class_names)
                    self.__feature_modification = content["allow_feature_modification"]
                    self.__table_name = content["table_name"]
                    text = colored("Assignment successful!", "green")
                    print(text, "\n")
                    dataset_params = [
                        f"\n \033[1mDataset Parameters\033[0m\n\n",
                        f"datasetId: {datasetId}\n",
                        f"totalDatasetSize: {self.__totalDatasetSize}\n",
                    ]
                    # allClasses disabled in case of regression
                    if self.__category != TABULAR_REGRESSION:
                        dataset_params.append(f"allClasses: {self.__class_names}\n")
                    print(*dataset_params)
                    print("Please set a training plan.")
                    return True
            elif re.status_code == 204:
                error_message = "Error Occurred. Linking Failed!"
                try:
                    body_unicode = re.content.decode("utf-8")
                    content = json.loads(body_unicode)
                    if "message" in content:
                        error_message += f"\n{content['message']}"
                except:
                    pass
                text = colored(error_message, "red")
                print(text)
                return False
            else:
                error_message = "Error Occurred. Linking Failed!"
                try:
                    body_unicode = re.content.decode("utf-8")
                    content = json.loads(body_unicode)
                    if "message" in content:
                        error_message += f"\n{content['message']}"
                except:
                    pass
                text = colored(error_message, "red")
                print(text)
                return False
        except Exception as e:  # pragma: no cover
            error_message = "Communication Fail Error!"
            try:
                if 're' in locals() and hasattr(re, 'content'):
                    body_unicode = re.content.decode("utf-8")
                    content = json.loads(body_unicode)
                    if "message" in content:
                        error_message += f"\n{content['message']}"
            except:
                pass
            
            if self.__environment != "" or self.__environment != "production":
                print(f"Error occurred while setting variables as {e}")
            
            text = colored(error_message, "red")
            print(text)
            return False

    def help(self):
        print(
            "User is a method in this package which authenticates the user, provides access to Tracebloc, "
            "lets you upload your model, set the training plan and more.\n"
        )

        print("Only registered Users are allowed to access this package.\n")

        print("In order to authenticate, run cell.")

        print("Enter email register on tracebloc and password.\n")

        print("Other user attributes are uploadModel() and linkModelDataset()\n")

        print("uploadModel():")
        print("This helps user to upload a compatible model and weights.\n")

        print("linkModelDataset():")
        print("Link uploaded model with a dataset.\n")

        rich.print(
            "For more information check the [link=https://docs.tracebloc.io/join-use-case/start-training]docs[/link]"
        )
