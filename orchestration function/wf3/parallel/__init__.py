import logging

import azure.functions as func
import requests as reqs
import json
from customized_LP import MyLineProfiler
import aiohttp, asyncio
import time

profile = MyLineProfiler()

async def get_url(session, url, img_info, timeout=1000):
    start_t = time.time()
    res = ""
    logging.info("infor"+img_info)
    async with session.post(url, data=img_info, timeout=timeout) as response:
        while True:
            chunk = await response.content.read(1024)
            if not chunk:
                break
            res += str(chunk)
        await response.release()
    runtime = time.time()-start_t
    logging.info(runtime)
    return runtime,len(res)


async def async_payload_wrapper(async_loop, img_info):
    
    urls = [ "https://fcnrw.azurewebsites.net/api/fcn",
            "https://mobilenetrw.azurewebsites.net/api/mobilenet",
            "https://resnetrw.azurewebsites.net/api/resnet",
            "https://fastercnnrw.azurewebsites.net/api/fastercnn"
            ]

    async with aiohttp.ClientSession(loop=async_loop) as session:
        corou_to_execute = [get_url(session, url, img_info) for url in urls]
        await asyncio.gather(*corou_to_execute)

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
    try:
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(async_payload_wrapper(event_loop, res.content.decode("utf-8")))
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(async_payload_wrapper(event_loop, res.content.decode("utf-8")))
        else:
            raise
    return func.HttpResponse(body='Completed', status_code=202)