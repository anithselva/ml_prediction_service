from fastapi import FastAPI, File, UploadFile
import logging
import base64
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import pika 
import uuid
import uvicorn

# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.PredictionEntry import PredictionEntry

# Try to establish connection with MQ
# Raise exception if this is not possible
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='predictions_exchange', exchange_type='fanout')
except:
    raise Exception("Couldn't connect to rabbitmq")

# Try to establish connection with DB
# Raise exception if this is not possible
try:
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:rootpassword@database:3306/prediction"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
except:
    raise Exception("Couldn't connect to database")

class ImagePred(BaseModel):
    name: str
    data: str

app = FastAPI()

# End points
@app.get("/")
async def read_root():
    """
    This function just responds to the browser URL
    localhost:5000/
    :return: Hello World
    """
    return {"Hello": "World"}

@app.post("/inference/image")
async def post_prediction(ImagePred: ImagePred):
    """
    POST Method

    Input image must be base64 encoded and passed in to 
    data raw as json in the following format:
        {
            "name": "name",
            "data": "<base64encoded string>"
        }

    Example of curl:
    curl --location --request POST 'http://127.0.0.1:5000/inference/image/' \
    --header 'Content-Type: text/plain' \
    --data-raw '{
        "name": "dog",
        "data": "/9j/ ..."
        }'
    :return: 
        {
            uuid: <uuid>
        }
    """

    logging.info("Received request")
    prediction_uuid = str(uuid.uuid4())[:8]
    newPrediction = PredictionEntry(uuid=prediction_uuid, img=ImagePred.data)
    session.add(newPrediction)
    session.commit()
    resp = {"uuid": prediction_uuid}

    channel.basic_publish(exchange='predictions_exchange', routing_key='', body=bytes(prediction_uuid, encoding='utf8'))

    return resp

@app.get("/predictions/{prediction_uuid}")
async def read_table(prediction_uuid: str):
    """
    GET Method
        localhost:5000/predictions/<uuid>

    :return: 
        {
            prediction: prediction_class
        }
    """
    # preds = session.query(PredictionEntry).filter_by(uuid=prediction_uuid).first()
    preds = session.query(PredictionEntry).get(prediction_uuid)

    if preds.prediction is None:
        return {"prediction": None}
    else:
        return {"prediction": preds.prediction}
