import base64
from http import HTTPStatus
from typing import Optional

import gridfs
import uvicorn
from bson import ObjectId
from logging import log, INFO
from fastapi import FastAPI, status, UploadFile, File, Response, HTTPException
from starlette.responses import StreamingResponse

from application.config import HOST, PORT
from application.database import client
from application.datamodels.models import MLModel, MLStrategy, MLCollector, MLModelData, \
    MLTrainingResults, MLStrategyData, FLDataTransformation

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.client = client


@app.post("/model", status_code=status.HTTP_201_CREATED)
async def create_model(model: MLModel):
    db = app.client.repository
    if len(list(db.models.find(
                {'model_name': model.model_name, 'model_version': model.model_version}).limit(
            1))) > 0:
        raise HTTPException(status_code=400,
                            detail='Model with this name and version already in repository')
    else:
        try:
            db.models.insert_one(model.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/model/{model_name}/{model_version}", status_code=status.HTTP_204_NO_CONTENT)
async def update_model(model_name: str, model_version: str, file: UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.models.find(
            {'model_name': model_name, 'model_version': model_version}).limit(1))) > 0:
        data = await file.read()
        model_id = fs.put(data, filename=f'model/{model_name}/{model_version}')
        db.models.update_one({'model_name': model_name, 'model_version': model_version},
                             {"$set": {"model_id": str(model_id)}},
                             upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.put("/model/meta/{model_name}/{model_version}",
         status_code=status.HTTP_204_NO_CONTENT)
async def update_model_meta(model_name: str, model_version: str, meta: MLModelData):
    db = app.client.repository
    if len(list(db.models.find(
            {'model_name': model_name, 'model_version': model_version}).limit(1))) > 0:
        db.models.update_one({'model_name': model_name, 'model_version': model_version},
                             {"$set": {"meta": dict(meta)}},
                             upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.get("/model")
async def get_model_list(trained: Optional[bool] = None):
    database = app.client.repository
    collection = database.models
    models = collection.find({}, {'_id': 0})
    if trained:
        models = [m for m in models if await get_results_list(m["model_name"],
                                                              m["model_version"])]
    return list(models)


@app.get("/model/meta")
async def get_model_meta(model_name: str, model_version: str):
    db = app.client.repository
    if len(list(db.models.find(
            {'model_name': model_name, 'model_version': model_version}).limit(1))) > 0:
        result = db.models.find_one(
            {'model_name': model_name, 'model_version': model_version}, {'_id': 0})
        return dict(result)
    else:
        raise HTTPException(status_code=404, detail="model meta not found")


@app.get("/model/{model_name}/{model_version}")
async def get_model(model_name: str, model_version: str):
    db = app.client.repository
    result = db.models.find_one(
        {'model_name': model_name, 'model_version': model_version})
    if 'model_id' in result and result['model_id'] is not None:
        model_id = \
            db.models.find_one(
                {'model_name': model_name, 'model_version': model_version})[
                'model_id']
        db_grid = app.client.repository_grid
        fs = gridfs.GridFSBucket(db_grid)
        file_handler = fs.open_download_stream(ObjectId(model_id))

        def read_gridfs():
            eachline = file_handler.readline()
            while eachline:
                yield eachline
                eachline = file_handler.readline()

        return StreamingResponse(read_gridfs())


@app.delete("/model/{model_name}/{model_version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_name: str, model_version: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.models.find(
            {'model_name': model_name, 'model_version': model_version}).limit(1))) > 0:
        model_id = \
            db.models.find_one(
                {'model_name': model_name, 'model_version': model_version})[
                'model_id']
        db.models.delete_many({'model_name': model_name, 'model_version': model_version,
                               'model_id': model_id})
        fs.delete(ObjectId(model_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.post("/training-results", status_code=status.HTTP_201_CREATED)
async def create_training_results(training: MLTrainingResults):
    db = app.client.repository
    # We can assume training of a given id for a given model version and name
    # to be unique
    if len(list(db.results.find({'model_name': training.model_name, 'model_version':
                                 training.model_version, 'training_id': training.training_id}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='This training id of a model of '
                                                    'this name and version '
                                                    'already in '
                                                    'repository')
    else:
        try:
            db.results.insert_one(training.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.get("/training-results")
async def get_all_training_results():
    database = client.repository
    collection = database.results
    results = collection.find({}, {'_id': 0})
    return list(results)


@app.get("/training-results/{model_name}/{model_version}")
async def get_results_list(model_name: str, model_version: str):
    database = app.client.repository
    collection = database.results
    results = collection.find({'model_name': model_name, 'model_version':
                               model_version}, {'_id': 0})
    return list(results)


@app.put("/training-results/{model_name}/{model_version}/{training_id}/{configuration_id}",
         status_code=status.HTTP_204_NO_CONTENT)
async def update_results(model_name: str, model_version: str, training_id: str,
                         configuration_id: str, file:
                         UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.results.find(
            {'model_name': model_name, 'model_version': model_version, 'training_id':
                training_id}).limit(1))) > 0:
        data = await file.read()
        weights_id = fs.put(data, filename=f'weights/{model_name}/{model_version}/{configuration_id}',
                                           training_id=f'{training_id}')
        db.results.update_one({'model_name': model_name, 'model_version':
                               model_version, 'training_id': training_id},
                              {"$set": {"weights_id": str(weights_id)}},
                              upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="model not found")


@app.get("/training-results/weights/{model_name}/{model_version}/{training_id}")
async def get_results_weights(model_name: str, model_version: str, training_id: str):
    db = app.client.repository
    result = db.results.find_one(
        {'model_name': model_name, 'model_version': model_version,
         'training_id': training_id})
    if 'weights_id' in result and result['weights_id'] is not None:
        model_id = \
            db.results.find_one(
                {'model_name': model_name, 'model_version': model_version,
                 'training_id': training_id})[
                'weights_id']
        db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    outputdata = fs.get(ObjectId(model_id)).read()
    return Response(content=base64.b64encode(outputdata))


@app.delete("/training-results/{model_name}/{model_version}/{training_id}",
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_results(model_name: str, model_version: str, training_id: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.results.find(
            {'model_name': model_name, 'model_version': model_version,
             'training_id': training_id}).limit(1))) > 0:
        weights_id = db.results.find_one(
            {'model_name': model_name, 'model_version': model_version,
             'training_id': training_id})[
            'weights_id']
        db.results.delete_many({'model_name': model_name, 'model_version':
                                model_version, 'training_id': training_id})
        fs.delete(ObjectId(weights_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(
            status_code=404, detail="Training results not found")


@app.post("/strategy", status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: MLStrategy):
    db = app.client.repository
    if len(list(db.strategies.find(
            {'strategy_name': strategy.strategy_name}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='Strategy already exists')
    else:
        try:
            db.strategies.insert_one(strategy.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/strategy/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def update_strategy(name: str, file: UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.strategies.find({'strategy_name': name}).limit(1))) > 0:
        data = await file.read()
        strategy_id = fs.put(data, filename=f'strategy/{name}')
        db.strategies.update_one({'strategy_name': name},
                                 {"$set": {"strategy_id": str(strategy_id)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Strategy not found")


@app.put("/strategy/meta/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def update_strategy_meta(name: str, meta: MLStrategyData):
    db = app.client.repository
    if len(list(db.strategies.find({'strategy_name': name}).limit(1))) > 0:
        db.strategies.update_one({'strategy_name': name},
                                 {"$set": {"meta": dict(meta.meta)}},
                                 upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Strategy not found")


@app.get("/strategy")
async def get_strategy_list():
    database = app.client.repository
    collection = database.strategies
    strategies = collection.find({}, {'_id': 0})
    return list(strategies)


@app.get("/strategy/{name}")
async def get_strategy(name: str):
    db = app.client.repository
    strategy_id = db.strategies.find_one({'strategy_name': name})[
        'strategy_id']
    db_grid = app.client.repository_grid
    fs = gridfs.GridFSBucket(db_grid)
    file_handler = fs.open_download_stream(ObjectId(strategy_id))

    def read_gridfs():
        eachline = file_handler.readline()
        while eachline:
            yield eachline
            eachline = file_handler.readline()

    return StreamingResponse(read_gridfs(), media_type="application/octet-stream")


@app.delete("/strategy/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(name: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.strategies.find({'strategy_name': name}).limit(1))) > 0:
        strategy_id = db.strategies.find_one({'strategy_name': name})[
            'strategy_id']
        db.strategies.delete_many({'strategy_name': name})
        fs.delete(ObjectId(strategy_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Strategy not found")


@app.post("/collector", status_code=status.HTTP_201_CREATED)
async def create_collector(collector: MLCollector):
    db = app.client.repository
    if len(list(db.collectors.find(
            {'name': collector.name, 'version': collector.version}).limit(1))) > 0:
        raise HTTPException(status_code=400, detail='Collector already exists')
    else:
        try:
            db.collectors.insert_one(collector.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.get("/models/available")
async def get_available_models():
    database = client.repository_grid
    collection = database.fs.files
    modelsAvailable = collection.find({}, {'_id': 0}).sort('uploadDate', 1)
    return list(modelsAvailable)


@app.get("/models/download/shell/{filename}")
async def get_model_trained(filename: str):
    parseFilename = filename.replace("_", "/")
    database = client.repository_grid
    collection = database.fs.files
    model = collection.find({'filename': parseFilename}, {'_id': 0}).sort('uploadDate',
                                                                          -1).limit(1)
    return list(model)


@app.post("/transformation", status_code=status.HTTP_201_CREATED)
async def create_transformation(transformation: FLDataTransformation):
    db = app.client.repository
    if len(list(db.transformations.find(
            {'id': transformation.id}).limit(1))) > 0:
        raise HTTPException(
            status_code=400, detail='Transformation with this id already exists')
    else:
        try:
            db.transformations.insert_one(transformation.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/transformation/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_transformation(id: str, file: UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.transformations.find({'id': id}).limit(1))) > 0:
        data = await file.read()
        transformation_id = fs.put(data, filename=f'transformation/{id}')
        db.transformations.update_one({'id': id},
                                      {"$set": {"storage_id": str(
                                          transformation_id)}},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Transformation not found")


@app.put("/transformation/meta/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_transformation_meta(meta: FLDataTransformation):
    db = app.client.repository
    if len(list(db.transformations.find({'id': meta.id}).limit(1))) > 0:
        db.transformations.update_one({'id': meta.id},
                                      {"$set": dict(meta)},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Transformation not found")


@app.get("/transformation")
async def get_transformation_list():
    database = app.client.repository
    collection = database.transformations
    transformations = collection.find({}, {'_id': 0, 'storage_id': 0})
    return list(transformations)


@app.get("/transformation/{id}")
async def get_transformation(id: str):
    db = app.client.repository
    storage_id = db.transformations.find_one({'id': id})[
        'storage_id']
    db_grid = app.client.repository_grid
    fs = gridfs.GridFSBucket(db_grid)
    file_handler = fs.open_download_stream(ObjectId(storage_id))

    def read_gridfs():
        eachline = file_handler.readline()
        while eachline:
            yield eachline
            eachline = file_handler.readline()

    return StreamingResponse(read_gridfs())


@app.delete("/transformation/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transformation(id: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.transformations.find({'id': id}).limit(1))) > 0:
        storage_id = db.transformations.find_one({'id': id})[
            'storage_id']
        db.transformations.delete_many({'id': id})
        fs.delete(ObjectId(storage_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Transformation not found")


@app.on_event("shutdown")
def shutdown_db_client():
    app.client.close()


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=int(PORT))
