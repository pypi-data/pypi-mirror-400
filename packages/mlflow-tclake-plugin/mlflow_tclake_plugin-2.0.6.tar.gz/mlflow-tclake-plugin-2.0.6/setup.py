from setuptools import find_packages, setup

setup(
    name="mlflow-tclake-plugin",
    version="2.0.6",
    description="Tclake plugin for MLflow",
    packages=find_packages(),
    # Require MLflow as a dependency of the plugin, so that plugin users can simply install
    # the plugin & then immediately use it with MLflow
    install_requires=["mlflow>=2.7.2", "tencentcloud-sdk-python-common>=3.0.1478"],
    entry_points={
        "mlflow.model_registry_store": (
            "tclake=mlflow_tclake_plugin.tclake_store:TCLakeStore"
        ),
    },
)
