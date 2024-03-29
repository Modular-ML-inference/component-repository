from typing import Dict, Optional, List, Any

from pydantic import BaseModel, Field


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


class DataTransformation(BaseModel):
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

class Inferencer(BaseModel):
    id: str
    description: Optional[str] = Field(None,
                                       title="the available data explaining the purpose of a given inferencer")
    library: Optional[str] = Field(None,
                                       title="the ML library the inferencer was developed for")
    needs: MachineCapabilities
    use_cuda: Optional[bool] = Field(
        False, title="whether the inferencer is configured to use cuda, bool")
    storage_id: Optional[str] = Field(None,
                                      title="id under which strategy is stored in "
                                      "GridFS")
    
class Service(BaseModel):
    id: str
    description: Optional[str] = Field(None,
                                       title="the available data explaining the purpose of a given service")
    needs: MachineCapabilities
    storage_id: Optional[str] = Field(None,
                                      title="id under which strategy is stored in "
                                      "GridFS")

class DataTransformationConfig(BaseModel):
    id: str
    params: Dict[str, Any]


class DataTransformationPipelineConfig(BaseModel):
    configuration: Dict[str, List[DataTransformationConfig]]
