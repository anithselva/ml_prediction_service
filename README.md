# ML Prediction System

## System Diagram

The following diagram describes the system at a high level

![alt text](./docs/system_diagram.png "System Diagram")

## System Stack Considerations

**FastAPI and Uvicorn**: 

FastAPI ia a simple, but powerful web RESTful API framework based in Python. Benchmark tests have shown it to be on-part with NodeJS and Go. It also has a simple interface, allowing for an API server to be brought up within a few lines of code. To deploy this server, Uvicorn is used to host the web application

**RabbitMQ**: 

In order to support asynchronous requests, a queue system is implemented to handle prediction requests in message-broker manner. RabbitMQ was used for this purpose, based on its simplicity and that it can easily deployed in the cloud and deployed in distrubuted environments

**MySQL**

Prediction transactions are stored in a MySQL database. Having a fixed schema, a relational database was chosen. For this service, a UUID, Image String, and Prediction result is stored. With a UUID as primary key, and prediction result requiring no additional processing, using a SQL database will result in faster data retrieval times. 

**Prediction Engine**

A Prediction Engine written in Python is used as consumer for the MQ (message queue). It operates on a call-back mechanism in order to retreive the UUID for the prediction request, 

## Instructions:

The system supports asynchronous predictions. That is, the user is required to request a prediction through a POST command with their image for inference. If response is successful, they will be returned with a UUID that is unique to their prediction.

The system will process the request and upload its result to the Predictions database.
The user can retrieve their result by submitting a GET request by passing to it their UUID




**Request a Prediction:**

POST REQUEST : `localhost:5000/inference/image`

Input image must be base64 encoded and passed in to data raw as json in the following format:
```
{
    "name": "name",
    "data": "<base64encoded string>"
}
```

Example:

```
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
```

Note: For b64 encoding, try the following command:
```
base64 image.jpg 
```

**Retreive Prediction Result:**

GET REQUEST `localhost:5000/predictions/<uuid>`

```
curl --location --request GET 'http://127.0.0.1:5000/predictions/ab2o5pd2/' 

:return: 
    {
        "predictoin": "dogsled"
    }
```

## Assumptions:

(1) Images are < 1MB

(2) Images are permitted to be stored in the database or some data volume for retrieval

(3) Predictions are also permitted to be stored in the database. No purging of past predictions is required


## Transaction Database Schema:

| uuid     	| img      	| prediction 	|
|----------	|----------	|------------	|
| sj22pd4o 	| /9j/ ... 	| dogsled    	|

Data Types:
uuid: VARCHAR - 50 Characters
img : MEDIUM  - Limited to 1MB through python class mapping operators
predcition: VARCHAT - 50 Characters



## How to Test:

The implemented tests test the system end-to-end for the following:

(1) Server status 

(2) Server end-points (POST and GET) return data in expected format

(3) Model returns expected inference result

To run these end-to-end tests:

```
cd tests
source set_env.sh .
python test/test_end_to_end.py
```

The expected result should look like this:

```
....
----------------------------------------------------------------------
Ran 4 tests in 2.432s

OK
```


## Areas of Improvement:

## Scaleability

### Image Storage and Message Transfer

The base64 encoded raw image is being written directly to the database by the server, when a new UUID is generated, and the UUID alone is passed to the MQ. This decoupling mwas done in order to reduce the size of the payload being transported in the MQ. While this achieves that purpose, it is advised that rather than passing the raw image through message queues or storing it directly in the database, that the server directly store the image in a data volume (i.e. S3 bucket), and pass the **link** to the image with the UUID in the MQ. 

This would :

(1) limit the payload size transported in the MQ, 

(2) reduce the size of the database, 

(3) eliminate race condition between the server and the prediction engine. (For example, the current implementation assumes the server write to the DB will preceed the prediction engine inference for the same UUID. This may not be true depending on the latency of the DB)

## Testing

Due to time constraints, only a limited number of tests were written to verify functionality of the entire system. Given more time, unit tests would be written to test the system in smaller modules.

The current tests rely on a live deployment. When unit tests are written, they would not rely on a deployed system, but instead only consider the logic itself. Useful metrics such as code coverage can be measured through that type of test system, and can also be used to gate pull-requests, and deployments (CI/CD)

