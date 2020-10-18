from fastapi import FastAPI, File, UploadFile
import logging
import base64
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import base64
import pika # RabbitMQ
import uuid

# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.PredictionEntry import PredictionEntry

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
except:
    raise Exception("Couldn't connect to rabbitmq")

channel = connection.channel()
channel.exchange_declare(exchange='predictions_exchange', exchange_type='fanout')

class ImagePred(BaseModel):
    name: str
    data: str

app = FastAPI()
try:
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:rootpassword@database:3306/prediction"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
except:
    raise Exception("Couldn't connect to database")


# End points
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/image/")
async def post_prediction(ImagePred: ImagePred):
    logging.info("Received request")
    prediction_uuid = str(uuid.uuid4())[:8]
    newPrediction = PredictionEntry(uuid=prediction_uuid, img=ImagePred.data)
    session.add(newPrediction)
    session.commit()
    resp = {"uuid": prediction_uuid}

    channel.basic_publish(exchange='predictions_exchange', routing_key='', body=bytes(prediction_uuid, encoding='utf8'))

    return resp

@app.get("/get_prediction/{prediction_uuid}")
async def read_table(prediction_uuid: str):
    preds = session.query(PredictionEntry).filter_by(uuid=prediction_uuid).first()
    if preds.prediction is None:
        return {"prediction": None}
    else:
        return {"prediction": preds.prediction}


