import logging

import azure.functions as func
import requests as reqs
import json
from customized_LP import MyLineProfiler
import aiohttp, asyncio
import time
profile = MyLineProfiler()

def main(req: func.HttpRequest) -> func.HttpResponse:
        profile.start()
        result = wrapper_function(req)
        profile.stop()
        return result

@profile
def wrapper_function(req: func.HttpRequest):
    url = "https://predictrw.azurewebsites.net/api/predictentry"
    input_name = json.loads(req.get_body())
    name = input_name["data"]
    predict_method = input_name["predict"]
    res = reqs.post(url, data=json.dumps(name))
    logging.info(res.content.decode("utf-8"))
    url = 'https://loadimage.azurewebsites.net/api/load'
    res = reqs.post(url, data=json.dumps(name))
    logging.info(res.content)
    url = 'https://updateort.azurewebsites.net/api/updateorient'
    res = reqs.post(url, data=res.content.decode("utf-8"))
    url = 'https://resizedown.azurewebsites.net/api/resizedown'
    res = reqs.post(url, data=res.content.decode("utf-8"))
    url = 'https://convert2np.azurewebsites.net/api/convert2np'
    res = reqs.post(url, data=res.content.decode("utf-8"))
    url='https://extractnp.azurewebsites.net/api/extract'
    res = reqs.post(url, data=json.dumps(json.dumps(res.content.decode("utf-8"))))
    url = 'https://crop2center.azurewebsites.net/api/crop?input=224'
    res = reqs.post(url, data=json.dumps(json.dumps(res.content.decode("utf-8"))))
    url = 'https://tensorpredict.azurewebsites.net/api/tensorpredict'
    res = reqs.post(url, data=json.dumps(json.dumps(res.content.decode("utf-8"))))
    return func.HttpResponse(body='Completed', status_code=202)