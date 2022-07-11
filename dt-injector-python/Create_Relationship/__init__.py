import logging
import json
import azure.functions as func
import os
import sys
import uuid
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage):
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
    #                                 '%m-%d-%Y %H:%M:%S')
    # stdout_handler = logging.StreamHandler(sys.stdout)
    # stdout_handler.setLevel(logging.DEBUG)
    # stdout_handler.setFormatter(formatter)
    # file_handler = logging.FileHandler('logCreateRelationship.log')
    # file_handler.setLevel(logging.WARNING)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    # logger.addHandler(stdout_handler)

    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body.replace("'",'"'))
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)
    
    
    relationshipId=json_message["$relationshipName"]+"-"+json_message["$sourceId"]+"-"+json_message["$targetId"]

    try:
        service_client.upsert_relationship(
            json_message["$sourceId"],
            relationshipId,
            json_message
        )
        logging.info("The following relationship has been created successfully: %s",json_message)
    except Exception as e:
        logging.exception("The relationship corresponding to the json message : %s couldn't be created due to the following exception :",json_message)
        logging.exception(e)
    


