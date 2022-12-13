import logging
import json
import os
import copy

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient


def main(msg: func.QueueMessage):

    url = os.environ["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body)
    digital_twin_id = json_message["$id"]

    # manage empty field and map-like columns
    new_msg = copy.deepcopy(json_message)
    for j in json_message:
        if json_message[j] in (None, ''):
            new_msg.pop(j)
            continue
        if '.' in j:
            map_split = j.split('.')
            if map_split[0] not in new_msg:
                new_msg[map_split[0]] = {}
            new_msg[map_split[0]][map_split[1]] = json_message[j]
            new_msg.pop(j)

    # try to upsert the twin in the ADT, and if there is no exception a Dev Log is displayed
    created_twin = service_client.upsert_digital_twin(digital_twin_id, new_msg)
    logging.info(
        "Dev Log: The following twin has been created successfully: %s", created_twin
    )
