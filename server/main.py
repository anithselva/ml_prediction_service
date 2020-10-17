from fastapi import FastAPI, File, UploadFile
import logging
import base64
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import base64
import pika # RabbitMQ
import uuid

# Prediction related dependencies
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
import json
import io

# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PredictionEntry import PredictionEntry

# Set up and load model
imagenet_class_index = json.load(open('imagenet_class_index.json'))
model = models.squeezenet1_0(pretrained=True)
model.eval()

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()

# Predicition related function
def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]


app = FastAPI()

class ImagePred(BaseModel):
    name: str
    data: str


SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/prediction"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# End points
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/image/")
async def post_prediction(ImagePred: ImagePred):
    logging.info("Received request")
    img_raw   = base64.b64decode(ImagePred.data)
    # pred_class = get_prediction(img_raw)

    prediction_uuid = str(uuid.uuid4())[:8]
    newPrediction = PredictionEntry(uuid=prediction_uuid, img=ImagePred.data)
    session.add(newPrediction)
    session.commit()
    resp = {"uuid": prediction_uuid}
    return resp

@app.get("/get_prediction/{prediction_uuid}")
async def read_table(prediction_uuid: str):

    preds = session.query(PredictionEntry).filter_by(uuid=prediction_uuid).first()
    if preds.prediction is None:
        return {"prediction": None}
    else:
        return {"prediction": preds.prediction}


