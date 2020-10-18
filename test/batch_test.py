import requests
import base64
import json
import os
import time

## Simple script to run through all test images and receive a prediction


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

def run_through_imgs(folderpath):
    list_of_images = os.listdir(folderpath)
    idx = 1
    for img in list_of_images:
        print("Image %d: Filename %s" %(idx, img))

        r = createPredictionPostRequest(folderpath + "/" + img)
        response = json.loads(r.text)
        print(response)
        uuid = response['uuid']

        # Sleep between request, so as not to need to poll
        time.sleep(1)

        # Loopback the UUID to get result from prediction
        r = requests.get(SERVER_HOSTNAME + ":5000/predictions/" + uuid)
        prediction = json.loads(r.text)
        print(prediction)
        print("\n")
        idx +=1 


if __name__ == '__main__':

    SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', "http://127.0.0.1")
    test_img_folder = "./test_images"
    run_through_imgs(test_img_folder)