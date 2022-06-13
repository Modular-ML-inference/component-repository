# FL Repository

Run `docker-compose up --force-recreate --build -d` to run the server.

Interactive API docs: http://127.0.0.1:9013/docs

New additions:
- Model weights and training results separated to endpoints starting with `training-results` 
  - Training id assumed to be unique for a given model name and version
- Endpoints starting with `model` hold information about the training configuration and base models, 
complete with model weights as well as structure

