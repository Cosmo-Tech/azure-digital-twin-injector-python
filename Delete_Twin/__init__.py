import logging
import sys
import json
import azure.functions as func
import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body)
    url = os.environ["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id = json_message["$id"]

    # try to delete the twin in the ADT, and if there is no exception a Dev Log is displayed
    service_client.delete_digital_twin(digital_twin_id)
    logging.info(
        "Dev Log: The following twin has been deleted successfully: %s", json_message
    )
