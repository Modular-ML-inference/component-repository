#!/bin/bash
# Restore from dump
#mongorestore --db repository --collection models /dump/repository/models.bson
#mongorestore --db repository --collection strategies /dump/repository/strategies.bson
#mongorestore --db repository --collection transformations /dump/repository/transformations.bson
#mongorestore --db repository_grid --collection fs.chunks /dump/repository_grid/fs.chunks.bson
#mongorestore --db repository_grid --collection fs.files /dump/repository_grid/fs.files.bson

mongorestore --archive=db.dump