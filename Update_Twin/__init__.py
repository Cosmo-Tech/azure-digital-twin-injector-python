import logging
import sys
import json
import azure.functions as func
import os
import copy
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

    # manage map-like columns
    new_msg = copy.deepcopy(json_message)
    for j in json_message:
        if '.' in j:
            map_split = j.split('.')
            if map_split[0] not in new_msg:
                new_msg[map_split[0]] = {}
            new_msg[map_split[0]][map_split[1]] = json_message[j]
            new_msg.pop(j)

    # create patch
    patch = []
    for key, value in new_msg.items():
        # can not update the id and metadata of the twin
        if key != "$id" and key != "$metadata":
            # only updates the twin's properties that have not null values
            if value is not None:
                patch.append({"op": "add", "path": "/" + key, "value": value})
            else:
                patch.append({"op": "remove", "path": "/" + key})

    logging.info(patch)
    # try to update the twin in the ADT, and if there is no exception a Dev Log is displayed
    service_client.update_digital_twin(digital_twin_id, patch)
    logging.info(
        "Dev Log: The following twin has been updated successfully: %s", json_message
    )
