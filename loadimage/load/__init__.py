import logging
import json
import azure.functions as func
import base64
import logging
import os
import io
from urllib.request import urlopen
from PIL import Image
import time
from customized_LP import MyLineProfiler

profile = MyLineProfiler()

def main(req: func.HttpRequest) -> func.HttpResponse:
    profile.start()
    result = wrapper_function(req)
    profile.stop()
    return result

@profile
def wrapper_function(req: func.HttpRequest):
    image_url = json.loads(req.get_body())
    logging.info("Predicting from url: " + image_url)
    with urlopen(image_url) as testImage:
        image = Image.open(testImage)
    img_byte_arr = io.BytesIO()   
    image.save(img_byte_arr, format='JPEG')
    img_data = base64.encodebytes(img_byte_arr.getvalue()).decode('utf-8')
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    result = json.dumps(img_data)    
    return func.HttpResponse(result, headers = headers)
