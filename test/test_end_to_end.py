import unittest
import requests
import base64
import json
import time
import os

SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', "http://127.0.0.1")

# Helper function to form post request for a preduction.
# Returns the request object after pushing the request
def createPredictionPostRequest(image_path):
    img_fd = open(image_path, "rb")
    img_bytes = img_fd.read()
    img_fd.close()
    payload_json = { "name": "dog", "data": base64.b64encode(img_bytes).decode('utf-8')}
    payload = json.dumps(payload_json)
    r = requests.post(SERVER_HOSTNAME + ":5000/inference/image/", data=payload, headers={'Content-Type' : 'application/json'} )
    return r

class TestMLPredictionService(unittest.TestCase):

    # Basic test to make sure the server is up and running.
    def test_server_up(self):
        r = createPredictionPostRequest("./test_images/dog.jpg")
        r.raise_for_status()

    # Test for the Post Prediction endpoint
    def test_PostRequestReturnsValidUUID(self):      

        # Create and post a Prediction from an image  
        # Form json out of response and make sure a UUID was returned

        r = createPredictionPostRequest("./test_images/dog.jpg")
        response = json.loads(r.text)
        self.assertIsNotNone(response['uuid'])
        
    # Test for the Get Prediction endpoint
    def test_GetRequestReturnsPrediction(self):
        
        # Create and post a Prediction from an image  
        # Form json out of response and make sure a UUID was returned
        r = createPredictionPostRequest("./test_images/dog.jpg")
        response = json.loads(r.text)
        uuid = response['uuid']

        # Sleep between request, so as not to need to poll
        time.sleep(1)

        # Loopback the UUID to get result from prediction
        r = requests.get(SERVER_HOSTNAME + ":5000/predictions/" + uuid)
        prediction = json.loads(r.text)

        # Make sure it's not an empty response
        self.assertIsNotNone(prediction['prediction'])

    # Sanity test for the served model to be performing correctly
    # (Reporting correct inference output)
    def test_ImageModelSanityTest(self):

        # Create an post a Prediction from an image with an expected
        # output result ("dogsled")
        r = createPredictionPostRequest("./test_images/dog.jpg")
        response = json.loads(r.text)
        uuid = response['uuid']
        
        # Sleep between request, so as not to need to poll
        time.sleep(1)

        # Loopback the UUID to get result from prediction
        r = requests.get(SERVER_HOSTNAME + ":5000/predictions/" + uuid)
        prediction = json.loads(r.text)

        # Check to make sure inference result is as expected
        self.assertEqual(prediction['prediction'], "dogsled")
    
if __name__ == '__main__':
    unittest.main()