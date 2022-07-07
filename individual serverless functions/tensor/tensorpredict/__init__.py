from datetime import datetime
import logging
import os
import io
from urllib.request import urlopen
from PIL import Image
import tensorflow as tf
import base64
import numpy as np

import logging
import azure.functions as func
import json
from .handler import _log_msg
# Import helper script
from customized_LP import MyLineProfiler
output_layer = 'loss:0'
input_node = 'Placeholder:0'

graph_def = tf.GraphDef()
labels = []
network_input_size = 0
scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'model.pb')
labels_filename = os.path.join(scriptdir, 'labels.txt')

def _initialize():
    global labels, network_input_size
    if not labels:
        with tf.io.gfile.GFile(filename, 'rb') as f:
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
        with open(labels_filename, 'rt') as lf:
            labels = [l.strip() for l in lf.readlines()]
        with tf.compat.v1.Session() as sess:
            input_tensor_shape = sess.graph.get_tensor_by_name('Placeholder:0').shape.as_list()
            network_input_size = input_tensor_shape[1]
            logging.info('network_input_size = ' + str(network_input_size))
profile = MyLineProfiler()

def main(req: func.HttpRequest) -> func.HttpResponse:
    profile.start()
    result = wrapper_function(req)
    profile.stop()
    return result

@profile
def wrapper_function(req: func.HttpRequest):
        _initialize()
        tf.compat.v1.reset_default_graph()
        tf.import_graph_def(graph_def, name='')
        cropped_image = np.array(json.loads(req.get_body()))
        with tf.compat.v1.Session() as sess:
            prob_tensor = sess.graph.get_tensor_by_name(output_layer)
            predictions, = sess.run(prob_tensor, {input_node: [cropped_image] })
            
            result = []
            highest_prediction = None
            for p, label in zip(predictions, labels):
                truncated_probablity = np.float64(round(p,8))
                if truncated_probablity > 1e-8:
                    prediction = {
                        'tagName': label,
                        'probability': truncated_probablity }
                    result.append(prediction)
                    if not highest_prediction or prediction['probability'] > highest_prediction['probability']:
                        highest_prediction = prediction

            response = {
                'created': datetime.utcnow().isoformat(),
                'predictedTagName': highest_prediction['tagName'],
                'prediction': result 
            }

            _log_msg("Results: " + str(response))
            headers = {
              "Content-type": "application/json",
              "Access-Control-Allow-Origin": "*"
             }
            return func.HttpResponse(json.dumps(response), headers = headers)