from typing import Dict, Optional

from pydantic import BaseModel, Field


class MLTrainingResults(BaseModel):
    model_name: str = Field(None, title="model identified, string")
    model_version: str = Field(None, title="model version, numeric")
    training_id: str = Field(None, title="id of the training, results of "
                                         "which we're storing")
    results: Dict[str, str] = Field(None, title="training results as key-value pairs")
    weights_id: Optional[str] = Field(None, title="id under which final model weights "
                                                  "are "
                                                  "stored in GridFS")


class MLModelData(BaseModel):
    meta: Dict[str, str] = Field(None, title="model metadata as key-value pairs")


class MLModel(MLModelData):
    model_name: str = Field(None, title="model identified, string")
    model_version: str = Field(None, title="model version, numeric")
    model_id: Optional[str] = Field(None, title="id under which model is stored in "
                                                "GridFS")


class MLStrategyData(BaseModel):
    meta: Dict[str, str] = Field(None, title="algorithm metadata as key-value pairs")


class MLStrategy(MLStrategyData):
    strategy_name: str = Field(None, title="strategy name")
    strategy_description: Optional[str] = Field(None, title="strategy description")
    strategy_id: Optional[str] = Field(None,
                                        title="id under which strategy is stored in "
                                              "GridFS")


class MLCollectorData(BaseModel):
    meta: Dict[str, str] = Field(None, title="collector metadata as key-value pairs")


class MLCollector(MLCollectorData):
    name: str = Field(None, title="collector name")
    version: int = Field(None, title="collector version, numeric")
    collector_id: Optional[str] = Field(None,
                                        title="id under which collector is stored in GridFS")
