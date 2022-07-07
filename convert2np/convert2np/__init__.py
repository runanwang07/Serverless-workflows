import logging
import json
import azure.functions as func
from .handler import _log_msg, load_img, dump_img
import numpy as np
#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from customized_LP import MyLineProfiler

profile = MyLineProfiler()

def main(req: func.HttpRequest) -> func.HttpResponse:
    profile.start()
    result = wrapper_function(req)
    profile.stop()
    return result

@profile
def wrapper_function(req: func.HttpRequest):
    image_content = json.loads(req.get_body())
    logging.info(image_content)
    image = load_img(image_content)
    _log_msg("Convert to numpy array")
    image = np.array(image)
    result = image[:, :, (2,1,0)]
    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    
    logging.info(result)    
    #blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    #blob_name = str(uuid.uuid4())
    #blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    #blob_client.upload_blob(json.dumps(result.tolist()))

    #return func.HttpResponse(blob_name, headers = headers)
    return func.HttpResponse(json.dumps(result.tolist()), headers = headers)