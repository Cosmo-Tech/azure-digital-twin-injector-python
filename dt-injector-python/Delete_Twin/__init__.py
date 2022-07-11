import logging
import sys
import json
import azure.functions as func
import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage):
    httplogger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    httplogger.setLevel(logging.WARNING)
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
    #                                 '%m-%d-%Y %H:%M:%S')
    # file_handler = logging.FileHandler('logDeleteTwin.log')
    # file_handler.setLevel(logging.INFO)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body)
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id =json_message["$id"]
    
    try:
        service_client.delete_digital_twin(digital_twin_id)
        logging.info("The following twin has been deleted successfully: %s",json_message)
    except Exception as e:
        logging.exception("The twin corresponding to the json message : %s couldn't be deleted due to the following exception :",json_message)
        logging.exception(e)
    


