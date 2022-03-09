from typing import Dict, Optional

from pydantic import BaseModel, Field


class MLModelData(BaseModel):
    meta: Dict[str, str] = Field(None, title="model metadata as key-value pairs")


class MLModel(MLModelData):
    id: int = Field(None, title="model identified, numeric")
    version: int = Field(None, title="model version, numeric")
    model_id: Optional[str] = Field(None, title="id under which model is stored in gridfs")


class MLAlgorithmData(BaseModel):
    meta: Dict[str, str] = Field(None, title="algorithm metadata as key-value pairs")


class MLAlgorithm(MLAlgorithmData):
    name: str = Field(None, title="algorithm name")
    version: int = Field(None, title="algorithm version, numeric")
    algorithm_id: Optional[str] = Field(None, title="id under which algorithm is stored in gridfs")


class MLCollectorData(BaseModel):
    meta: Dict[str, str] = Field(None, title="collector metadata as key-value pairs")


class MLCollector(MLCollectorData):
    name: str = Field(None, title="collector name")
    version: int = Field(None, title="collector version, numeric")
    collector_id: Optional[str] = Field(None, title="id under which collector is stored in gridfs")