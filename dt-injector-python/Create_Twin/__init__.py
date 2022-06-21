import logging
import json
import azure.functions as func
import os
import sys
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage) -> None:
    # Create logger
    # logger = logging.getLogger('azure')
    # logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler(stream=sys.stdout)
    # logger.addHandler(handler)

    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body)
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)
    digital_twin_id =json_message["$id"]

    err = service_client.upsert_digital_twin(digital_twin_id, json_message)
    logging.error(err)

