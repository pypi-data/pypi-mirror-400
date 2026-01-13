import sys
from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

package_url = "https://gitlab.com/tracebloc/tracebloc-py-package"
package_name = "tracebloc_package"
package_author_email = "lukas@tracebloc.io"

setup(
    name=package_name,
    version="0.6.29",
    description="Package required to run Tracebloc jupyter notebook to create experiment",
    url=package_url,
    license="MIT",
    python_requires=">=3",
    packages=find_packages(),
    author="Tracebloc",
    author_email=package_author_email,
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "absl-py",
        "dill",
        "pandas",
        "peft",
        "protobuf",
        "requests",
        "rich",
        "silence-tensorflow",
        "scikit-learn",
        "tensorflow",
        "tensorflow-datasets",
        "termcolor",
        "timm",
        "torch",
        "torchlightning",
        "torchmetrics",
        "torchvision",
        "tqdm",
        "transformers",
        "twine",
        "xgboost",
        "catboost",
        "lightgbm"
    ],
    zip_safe=False,
)
