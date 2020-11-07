import pika
from pydantic import BaseModel
import base64

# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.PredictionEntry import PredictionEntry

# Prediction related dependencies
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
import json
import io

from utils.RabbitMQ import RabbitMQ

# Prediction related function
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

# Callback function to handle messages coming out of MQ
def callback(ch, method, properties, body):
    uuid = str(body.decode("utf-8"))
    print("Received request for prediction UUID %s" % uuid)

    preds = session.query(PredictionEntry).filter_by(uuid=uuid).first()
    if preds is not None:
        # print(preds.img)
        pred_class = get_prediction(base64.b64decode(preds.img))
        print(pred_class[1])
        preds.prediction = pred_class[1]
        session.commit()

if __name__ == '__main__':

    # Try to establish connection with MQ
    # Raise exception if this is not possible
    # try:
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    # except:
    #     raise Exception("Couldn't connect to rabbitmq")
    # channel = connection.channel()
    # channel.exchange_declare(exchange='predictions_exchange', exchange_type='fanout')
    # result = channel.queue_declare(queue='pred_queue', exclusive=True)
    # queue_name = result.method.queue
    # channel.queue_bind(exchange='predictions_exchange', queue='pred_queue')
    # print(' [*] Waiting for logs. To exit press CTRL+C')

    rabbit_sub = RabbitMQ("rabbitmq", "predictions_exchange", "pred_queue")
    rabbit_sub.connect()

    # Try to establish connection with DB
    # Raise exception if this is not possible
    try:
        SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:rootpassword@database:3306/prediction"
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = Session()
    except:
        raise Exception("Couldn't connect to database")

    # Set up and load PyTorch model
    imagenet_class_index = json.load(open('./inference_engine/imagenet_class_index.json'))
    model = models.squeezenet1_0(pretrained=True, progress=True)
    model.eval()

    rabbit_sub.subscribe(callback)
    # # Start channel to handle messages with callback
    # channel.basic_consume(
    #     queue=queue_name, on_message_callback=callback, auto_ack=True)

    # channel.start_consuming()

