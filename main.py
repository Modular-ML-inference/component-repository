from http import HTTPStatus

import gridfs
import uvicorn
from bson import ObjectId
from fastapi import FastAPI, status, UploadFile, File, Response, HTTPException
from pymongo import MongoClient
from starlette.responses import StreamingResponse

from config import HOST, DB_PORT, PORT
from pydloc.models import MLModel, MLAlgorithm, MLCollector, MLModelData, MLAlgorithmData, MLCollectorData

app = FastAPI()


@app.post("/model", status_code=status.HTTP_201_CREATED)
async def create_model(model: MLModel):
    db = client.repository
    if len(list(db.models.find({'id': model.id, 'version': model.version}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='Model with this id and version already in repository')
    else:
        try:
            db.models.insert_one(model.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/model/{id}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_model(id: int, version: int, file: UploadFile = File(...)):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.models.find({'id': id, 'version': version}).limit(1))) > 0:
        data = await file.read()
        model_id = fs.put(data, filename=f'model/{id}/{version}')
        db.models.update_one({'id': id, 'version': version}, {"$set": {"model_id": str(model_id)}},
                             upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.put("/model/meta/{id}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_model_meta(id: int, version: int, meta: MLModelData):
    db = client.repository
    if len(list(db.models.find({'id': id, 'version': version}).limit(1))) > 0:
        db.models.update_one({'id': id, 'version': version}, {"$set": {"meta": dict(meta.meta)}},
                             upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.get("/model")
async def get_model_list():
    db = client.repository
    keys = list(MLModel.__fields__)
    list_m = [{key: document.get(key) for key in keys} for document in db.models.find()]
    return list_m


@app.get("/model/{id}/{version}")
async def get_model(id: int, version: int):
    db = client.repository
    model_id = db.models.find_one({'id': id, 'version': version})['model_id']
    db_grid = client.repository_grid
    fs = gridfs.GridFSBucket(db_grid)
    file_handler = fs.open_download_stream(ObjectId(model_id))

    def read_gridfs():
        eachline = file_handler.readline()
        while eachline:
            yield eachline
            eachline = file_handler.readline()

    return StreamingResponse(read_gridfs())


@app.delete("/model/{id}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(id: int, version: int):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.models.find({'id': id, 'version': version}).limit(1))) > 0:
        model_id = db.models.find_one({'id': id, 'version': version})['model_id']
        db.models.delete_many({'id': id, 'version': version, 'model_id': model_id})
        fs.delete(model_id)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.post("/algorithm", status_code=status.HTTP_201_CREATED)
async def create_algorithm(algorithm: MLAlgorithm):
    db = client.repository
    if len(list(db.algorithms.find({'name': algorithm.name, 'version': algorithm.version}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='Algorithm already exists')
    else:
        try:
            db.algorithms.insert_one(algorithm.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/algorithm/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_algorithm(name: str, version: int, file: UploadFile = File(...)):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.algorithms.find({'name': name, 'version': version}).limit(1))) > 0:
        data = await file.read()
        algorithm_id = fs.put(data, filename=f'algorithm/{name}/{version}')
        db.algorithms.update_one({'name': name, 'version': version},
                                 {"$set": {"algorithm_id": str(algorithm_id)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="algorithm not found")


@app.put("/algorithm/meta/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_algorithm_meta(name: str, version: int, meta: MLAlgorithmData):
    db = client.repository
    if len(list(db.algorithms.find({'name': name, 'version': version}).limit(1))) > 0:
        db.algorithms.update_one({'name': name, 'version': version}, {"$set": {"meta": dict(meta.meta)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="algorithm not found")


@app.get("/algorithm")
async def get_algorithm_list():
    db = client.repository
    keys = list(MLAlgorithm.__fields__)
    list_m = [{key: document.get(key) for key in keys} for document in db.algorithms.find()]
    return list_m


@app.get("/algorithm/{name}/{version}")
async def get_algorithm(name: str, version: int):
    db = client.repository
    algorithm_id = db.algorithms.find_one({'name': name, 'version': version})['algorithm_id']
    db_grid = client.repository_grid
    fs = gridfs.GridFSBucket(db_grid)
    file_handler = fs.open_download_stream(ObjectId(algorithm_id))

    def read_gridfs():
        eachline = file_handler.readline()
        while eachline:
            yield eachline
            eachline = file_handler.readline()

    return StreamingResponse(read_gridfs(), media_type="application/octet-stream")


@app.delete("/algorithm/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_algorithm(name: str, version: int):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.algorithms.find({'name': name, 'version': version}).limit(1))) > 0:
        algorithm_id = db.algorithms.find_one({'name': name, 'version': version})['algorithm_id']
        db.algorithms.delete_many({'name': name, 'version': version, 'algorithm_id': algorithm_id})
        fs.delete(algorithm_id)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.post("/collector", status_code=status.HTTP_201_CREATED)
async def create_collector(collector: MLCollector):
    db = client.repository
    if len(list(db.collectors.find({'name': collector.name, 'version': collector.version}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='Collector already exists')
    else:
        try:
            db.collectors.insert_one(collector.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/collector/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_collector(name: str, version: int, file: UploadFile = File(...)):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.collectors.find({'name': name, 'version': version}).limit(1))) > 0:
        data = await file.read()
        collector_id = fs.put(data, filename=f'collector/{name}/{version}')
        db.collectors.update_one({'name': name, 'version': version},
                                 {"$set": {"collector_id": str(collector_id)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="collector not found")


@app.put("/collector/meta/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_collector_meta(name: str, version: int, meta: MLCollectorData):
    db = client.repository
    if len(list(db.collectors.find({'name': name, 'version': version}).limit(1))) > 0:
        db.collectors.update_one({'name': name, 'version': version}, {"$set": {"meta": dict(meta.meta)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="collector not found")


@app.get("/collector")
async def get_collector_list():
    db = client.repository
    keys = list(MLCollector.__fields__)
    list_m = [{key: document.get(key) for key in keys} for document in db.collectors.find()]
    return list_m


@app.get("/collector/{name}/{version}")
async def get_collector(name: str, version: int):
    db = client.repository
    collector_id = db.collectors.find_one({'name': name, 'version': version})['collector_id']
    db_grid = client.repository_grid
    fs = gridfs.GridFSBucket(db_grid)
    file_handler = fs.open_download_stream(ObjectId(collector_id))

    def read_gridfs():
        eachline = file_handler.readline()
        while eachline:
            yield eachline
            eachline = file_handler.readline()

    return StreamingResponse(read_gridfs(), media_type="application/octet-stream")


@app.delete("/collector/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collector(name: str, version: int):
    db = client.repository
    db_grid = client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.collectors.find({'name': name, 'version': version}).limit(1))) > 0:
        collector_id = db.collectors.find_one({'name': name, 'version': version})['collector_id']
        db.collectors.delete_many({'name': name, 'version': version, 'collector_id': collector_id})
        fs.delete(collector_id)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


if __name__ == "__main__":
    with MongoClient(port=DB_PORT) as client:
        uvicorn.run(app, host=HOST, port=PORT)
