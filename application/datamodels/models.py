from typing import Dict, Optional, List, Any, Union

from pydantic import BaseModel, Field


class MLTrainingResults(BaseModel):
    model_name: str = Field(None, title="model identified, string")
    model_version: str = Field(None, title="model version, numeric")
    training_id: str = Field(None, title="id of the training, results of "
                                         "which we're storing")
    results: Dict[str, Union[str, float]] = Field(
        None, title="training results as key-value pairs")
    weights_id: Optional[str] = Field(None, title="id under which final model weights "
                                                  "are "
                                                  "stored in GridFS")
    configuration_id: str = Field(None, title="id of the configuration, results of "
                                              "which we're storing")


class MLModelData(BaseModel):
    library: str = Field(None, title="the model library")
    description: str = Field(
        None, title="description of what the model is for (more or less)")


class MLModel(BaseModel):
    model_name: str = Field(None, title="model identified, string")
    model_version: str = Field(None, title="model version, numeric")
    model_id: Optional[str] = Field(None, title="id under which model is stored in "
                                                "GridFS")
    meta: MLModelData = Field(None, title="model metadata as key-value pairs")


class MLStrategyData(BaseModel):
    meta: Dict[str, str] = Field(
        None, title="algorithm metadata as key-value pairs")


class MLStrategy(MLStrategyData):
    strategy_name: str = Field(None, title="strategy name")
    strategy_description: Optional[str] = Field(
        None, title="strategy description")
    strategy_id: Optional[str] = Field(None,
                                       title="id under which strategy is stored in "
                                             "GridFS")


class MLCollectorData(BaseModel):
    meta: Dict[str, str] = Field(
        None, title="collector metadata as key-value pairs")


class MLCollector(MLCollectorData):
    name: str = Field(None, title="collector name")
    version: int = Field(None, title="collector version, numeric")
    collector_id: Optional[str] = Field(None,
                                        title="id under which collector is stored in GridFS")


class MachineCapabilities(BaseModel):
    storage: Optional[float] = Field(
        None, title="the amount of storage needed in gigabytes, float")
    RAM: Optional[float] = Field(
        None, title="the amount of RAM needed in gigabytes, float")
    GPU: bool = Field(
        False, title="whether the existence of a GPU is needed, bool")
    preinstalled_libraries: Dict[str, str] = Field(None,
                                                   title="a list of necessary/available preinstalled libraries with compliant versions")
    available_models: Dict[str, str] = Field(None,
                                             title="a list of necessary/available models named by their name and version")


class FLDataTransformation(BaseModel):
    id: str
    description: Optional[str] = Field(None,
                                       title="the available data explaining the purpose of a given transformation")
    parameter_types: Dict[str, str] = Field(
        None, title="the list of input parameters and their types")
    default_values: Dict[str, Any] = Field(None,
                                           title="for the parameters having default values, input them along with the description of values")
    outputs: List[str] = Field(
        None, title="List of outputs and their expected types")
    needs: MachineCapabilities
    storage_id: Optional[str] = Field(None,
                                      title="id under which strategy is stored in "
                                      "GridFS")


class FLDataTransformationConfig(BaseModel):
    id: str
    params: Dict[str, Any]


class FLDataTransformationPipelineConfig(BaseModel):
    configuration: Dict[str, List[FLDataTransformationConfig]]
