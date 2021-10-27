from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

# ---------------- models ---------------- #
class MLModelData(BaseModel):
    data: str = Field(None, title="model binary data encoded as base64 string")
    meta: dict[str,str] = Field(None, title="model metadata as key-value pairs")

class MLModel(MLModelData):
    id: int = Field(None, title="model identified, numeric")
    version: int = Field(None, title="model version, numeric")

models = {}
models['1|1']=MLModel(id=1,version=1,data='VGhlIEZpcnN0IEVydXB0aW9u',meta={'a':'1','b':'2'})
models['1|2']=MLModel(id=1,version=2,data='Uml0ZSBvZiBCZWx6ZW5sb2s=',meta={'a':'3','b':'4'})
models['2|1']=MLModel(id=2,version=1,data='T3V0Zmxhbms=',meta={'a':'5','b':'6'})
models['3|1']=MLModel(id=3,version=1,data='Q2hhcm1pbmcgUHJpbmNl',meta={'a':'7','b':'8'})


# ---------------- algortihms ---------------- #
class MLAlgorithmData(BaseModel):
    data: str = Field(None, title="algorithm binary data encoded as base64 string")
    meta: dict[str,str] = Field(None, title="algorithm metadata as key-value pairs")

class MLAlgorithm(MLAlgorithmData):
    name: str = Field(None, title="algorithm name")
    version: int = Field(None, title="algorithm version, numeric")

algorithms = {}
algorithms['algo_1|1']=MLAlgorithm(name='algo_1',version=1,data='VGhlIEZpcnN0IEVydXB0aW9u',meta={'a':'1','b':'2'})
algorithms['algo_1|2']=MLAlgorithm(name='algo_1',version=2,data='Uml0ZSBvZiBCZWx6ZW5sb2s=',meta={'a':'3','b':'4'})
algorithms['algo_2|1']=MLAlgorithm(name='algo_2',version=1,data='T3V0Zmxhbms=',meta={'a':'5','b':'6'})
algorithms['algo_3|1']=MLAlgorithm(name='algo_3',version=1,data='Q2hhcm1pbmcgUHJpbmNl',meta={'a':'7','b':'8'})


# ---------------- collectors ---------------- #
class MLCollectorData(BaseModel):
    data: str = Field(None, title="collector binary data encoded as base64 string")
    meta: dict[str,str] = Field(None, title="collector metadata as key-value pairs")

class MLCollector(MLCollectorData):
    name: str = Field(None, title="collector name")
    version: int = Field(None, title="collector version, numeric")

collectors = {}
collectors['coll_1|1']=MLCollector(name='coll_1',version=1,data='VGhlIEZpcnN0IEVydXB0aW9u',meta={'a':'1','b':'2'})
collectors['coll_1|2']=MLCollector(name='coll_1',version=2,data='Uml0ZSBvZiBCZWx6ZW5sb2s=',meta={'a':'3','b':'4'})
collectors['coll_2|1']=MLCollector(name='coll_2',version=1,data='T3V0Zmxhbms=',meta={'a':'5','b':'6'})
collectors['coll_3|1']=MLCollector(name='coll_3',version=1,data='Q2hhcm1pbmcgUHJpbmNl',meta={'a':'7','b':'8'})


# ---------------- models endpoint ---------------- #

def create_model_id(id:int, ver:int):
    return str(id) + "|" + str(ver)

@app.post("/model", status_code=status.HTTP_201_CREATED)
async def create_model(model:MLModel):
    mid = create_model_id(model.id, model.version)
    if mid in models:
        raise HTTPException(status_code=400,detail="model already exists")
    else:
        models[mid]=model

@app.put("/model/{id}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_model(id:int, version:int, model:MLModelData):
    mid = create_model_id(id, version)
    if mid in models:
        models[mid].data = model.data
        models[mid].meta = model.meta
    else:
        raise HTTPException(status_code=404,detail="model not found")

@app.get("/model")
async def get_model_list():
    return list(models.values())

@app.get("/model/{id}/{version}")
async def get_model(id:int, version:int):
    return models[create_model_id(id, version)]

@app.delete("/model/{id}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(id:int, version:int):
    mid = create_model_id(id, version)
    if mid in models:
        models.pop(mid)
    else:
        raise HTTPException(status_code=404,detail="model not found")


# ---------------- algorithms endpoint ---------------- #

def create_algo_id(name:str, ver:int):
    return name + "|" + str(ver)

@app.post("/algorithm", status_code=status.HTTP_201_CREATED)
async def create_algorithm(algorithm:MLAlgorithm):
    aid = create_algo_id(algorithm.name, algorithm.version)
    if aid in algorithms:
        raise HTTPException(status_code=400,detail="algorithm already exists")
    else:
        algorithms[aid]=algorithm

@app.put("/algorithm/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_algorithm(name:str, version:int, model:MLAlgorithmData):
    aid = create_algo_id(name, version)
    if aid in algorithms:
        algorithms[aid].data = model.data
        algorithms[aid].meta = model.meta
    else:
        raise HTTPException(status_code=404,detail="algorithm not found")

@app.get("/algorithm")
async def get_algorithm_list():
    return list(algorithms.values())

@app.get("/algorithm/{name}/{version}")
async def get_algorithm(name:str, version:int):
    return algorithms[create_algo_id(name, version)]

@app.delete("/algorithm/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_algorithm(name:str, version:int):
    aid = create_algo_id(name, version)
    if aid in algorithms:
        algorithms.pop(aid)
    else:
        raise HTTPException(status_code=404,detail="algorithm not found")


# ---------------- collectors endpoint ---------------- #

def create_coll_id(name:str, ver:int):
    return name + "|" + str(ver)

@app.post("/collector", status_code=status.HTTP_201_CREATED)
async def create_collector(collector:MLCollector):
    cid = create_coll_id(collector.name, collector.version)
    if cid in collectors:
        raise HTTPException(status_code=400,detail="collector already exists")
    else:
        collectors[cid]=collector

@app.put("/collector/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_collector(name:str, version:int, model:MLCollectorData):
    cid = create_coll_id(name, version)
    if cid in collectors:
        collectors[cid].data = model.data
        collectors[cid].meta = model.meta
    else:
        raise HTTPException(status_code=404,detail="collector not found")

@app.get("/collector")
async def get_collector_list():
    return list(collectors.values())

@app.get("/collector/{name}/{version}")
async def get_collector(name:str, version:int):
    return collectors[create_coll_id(name, version)]

@app.delete("/collector/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collector(name:str, version:int):
    cid = create_coll_id(name, version)
    if cid in collectors:
        collectors.pop(aid)
    else:
        raise HTTPException(status_code=404,detail="collector not found")
