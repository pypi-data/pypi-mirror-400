from setuptools import setup, find_packages
import os

version = {}
with open(os.path.join(os.path.dirname(__file__), 'src/wedata_automl', '__init__.py')) as f:
    exec(f.readlines()[0], version)


PACKAGE_NAME = "tencent-wedata3-auto-ml"
print(f"PACKAGE_NAME: {PACKAGE_NAME} VERSION: {version['__version__']}")

setup(
    name=PACKAGE_NAME,
    version=version['__version__'],
    description="AutoML SDK for Tencent Cloud WeData using FLAML with MLflow integration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZhangChunLin",
    author_email="blueszzhang@tencent.com",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flaml==2.3.6",
        "lightgbm>=4.0.0",
        "xgboost>=2.0.0",
        "prophet>=1.1",
        "statsmodels>=0.13",
        "holidays>=0.25",
        "catboost>=1.0.0",
        "scikit-learn>=1.5,<1.7",
        "numpy>=1.24,<3.0",
        "matplotlib>=3.5",
        "seaborn>=0.11"
    ],
    extras_require={
        "xgboost": ["xgboost>=1.6"],
        "lightgbm": ["lightgbm>=3.3"],
        "wedata": ["tencent-wedata-feature-engineering"],
        "shap": ["shap>=0.41"],
        "full": [
            "xgboost>=1.6",
            "lightgbm>=3.3",
            "tencent-wedata-feature-engineering==0.1.36",
            "shap>=0.41",
            "optuna==4.6.0",
            "flaml[spark]==2.3.6",
            "cachetools>=5.0.0",
            "tencentcloud-sdk-python-common>=3.0.1478"
        ],
        "notebook": [
            "jupyterlab",
            "ipykernel",
            "ipywidgets",
            "matplotlib",
            "seaborn"
        ]
    },
    entry_points={
        "console_scripts": [
            "wedata-automl-demo=wedata_automl.cli:main"
        ]
    },
    url="https://git.woa.com/WeDataOS/wedata-automl",
    project_urls={
        "Homepage": "https://git.woa.com/WeDataOS/wedata-automl",
        "Repository": "https://git.woa.com/WeDataOS/wedata-automl.git"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)