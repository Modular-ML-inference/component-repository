import base64
from http import HTTPStatus
from logging import log
from typing import Optional

import gridfs
import uvicorn
from bson import ObjectId
from fastapi import FastAPI, File, HTTPException, Response, UploadFile, status
from starlette.responses import StreamingResponse

from application.config import HOST, PORT
from application.database import client
from application.datamodels.models import (DataTransformation, 
                                           MLModel, MLModelData, Service, Inferencer)

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
async def get_model_list():
    database = app.client.repository
    collection = database.models
    models = collection.find({}, {'_id': 0})
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


@app.post("/transformation", status_code=status.HTTP_201_CREATED)
async def create_transformation(transformation: DataTransformation):
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
async def update_transformation_meta(meta: DataTransformation):
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

@app.post("/service", status_code=status.HTTP_201_CREATED)
async def create_service(service: Service):
    db = app.client.repository
    if len(list(db.services.find(
            {'id': service.id}).limit(1))) > 0:
        raise HTTPException(
            status_code=400, detail='Service with this id already exists')
    else:
        try:
            db.services.insert_one(service.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/service/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_service(id: str, file: UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.services.find({'id': id}).limit(1))) > 0:
        data = await file.read()
        service_id = fs.put(data, filename=f'service/{id}')
        db.services.update_one({'id': id},
                                      {"$set": {"storage_id": str(
                                          service_id)}},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.put("/service/meta/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_service_meta(meta: Service):
    db = app.client.repository
    if len(list(db.services.find({'id': meta.id}).limit(1))) > 0:
        db.services.update_one({'id': meta.id},
                                      {"$set": dict(meta)},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.get("/service")
async def get_service_list():
    database = app.client.repository
    collection = database.services
    services = collection.find({}, {'_id': 0, 'storage_id': 0})
    return list(services)


@app.get("/service/{id}")
async def get_service(id: str):
    db = app.client.repository
    storage_id = db.services.find_one({'id': id})[
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


@app.delete("/service/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(id: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.services.find({'id': id}).limit(1))) > 0:
        storage_id = db.services.find_one({'id': id})[
            'storage_id']
        db.services.delete_many({'id': id})
        fs.delete(ObjectId(storage_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/inferencer", status_code=status.HTTP_201_CREATED)
async def create_inferencer(inferencer: Inferencer):
    db = app.client.repository
    if len(list(db.inferencers.find(
            {'id': inferencer.id}).limit(1))) > 0:
        raise HTTPException(
            status_code=400, detail='Inferencer with this id already exists')
    else:
        try:
            db.inferencers.insert_one(inferencer.dict(by_alias=True))
        except Exception as e:
            print("An exception occurred ::", e)
            raise HTTPException(status_code=500)


@app.put("/inferencer/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_inferencer(id: str, file: UploadFile = File(...)):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.inferencers.find({'id': id}).limit(1))) > 0:
        data = await file.read()
        inferencer_id = fs.put(data, filename=f'inferencer/{id}')
        db.inferencers.update_one({'id': id},
                                      {"$set": {"storage_id": str(
                                          inferencer_id)}},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Inferencer not found")


@app.put("/inferencer/meta/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_inferencer_meta(meta: Inferencer):
    db = app.client.repository
    if len(list(db.inferencers.find({'id': meta.id}).limit(1))) > 0:
        db.inferencers.update_one({'id': meta.id},
                                      {"$set": dict(meta)},
                                      upsert=False)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Inferencer not found")


@app.get("/inferencer")
async def get_inferencer_list():
    database = app.client.repository
    collection = database.inferencers
    inferencers = collection.find({}, {'_id': 0, 'storage_id': 0})
    return list(inferencers)


@app.get("/inferencer/{id}")
async def get_inferencer(id: str):
    db = app.client.repository
    storage_id = db.inferencers.find_one({'id': id})[
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


@app.delete("/inferencer/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inferencer(id: str):
    db = app.client.repository
    db_grid = app.client.repository_grid
    fs = gridfs.GridFS(db_grid)
    if len(list(db.inferencers.find({'id': id}).limit(1))) > 0:
        storage_id = db.inferencers.find_one({'id': id})[
            'storage_id']
        db.inferencers.delete_many({'id': id})
        fs.delete(ObjectId(storage_id))
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    else:
        raise HTTPException(status_code=404, detail="Inferencer not found")

@app.on_event("shutdown")
def shutdown_db_client():
    app.client.close()


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=int(PORT))
