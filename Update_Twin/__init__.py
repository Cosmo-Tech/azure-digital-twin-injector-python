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

    patch = []
    for key, value in json_message.items():

        # can not update the id and metadata of the twin, and only updates the twin's properties that have not null values
        if key != "$id" and key != "$metadata" and value is not None:
            patch.append({"op": "replace", "path": "/" + key, "value": value})

    # try to update the twin in the ADT, and if there is no exception a Dev Log is displayed
    service_client.update_digital_twin(digital_twin_id, patch)
    logging.info(
        "Dev Log: The following twin has been updated successfully: %s", json_message
    )
