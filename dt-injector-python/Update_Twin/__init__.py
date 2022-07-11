import logging
import sys
import json
import azure.functions as func
import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage) :
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
    #                                 '%m-%d-%Y %H:%M:%S')
    # stdout_handler = logging.StreamHandler(sys.stdout)
    # stdout_handler.setLevel(logging.DEBUG)
    # stdout_handler.setFormatter(formatter)
    # file_handler = logging.FileHandler('logUpdateTwin.log')
    # file_handler.setLevel(logging.WARNING)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    # logger.addHandler(stdout_handler)

    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body)
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id =json_message["$id"]

    patch=[]
    for key,value in json_message.items():
        if(key!="$id" and key!="$metadata") : 
            patch.append({
                "op": "replace",
                "path": "/"+key,
                "value": value
            })

    try:
        service_client.update_digital_twin(digital_twin_id, patch)
        logging.info("The following twin has been updated successfully: %s",json_message)
    except Exception as e:
        logging.exception("The twin corresponding to the json message : %s couldn't be updated due to the following exception :",json_message)
        logging.exception(e)
