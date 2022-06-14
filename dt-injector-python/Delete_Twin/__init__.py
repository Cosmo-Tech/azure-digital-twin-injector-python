import logging
import json
import azure.functions as func
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage) -> None:
    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body)
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id =json_message["$id"]
    
    service_client.delete_digital_twin(digital_twin_id)



