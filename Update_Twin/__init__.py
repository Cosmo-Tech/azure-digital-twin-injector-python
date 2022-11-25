import logging
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient

from ..config import configuration


def main(msg: str):
    json_message = json.loads(msg)
    url = configuration["digitalTwinUrl"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id = json_message["$id"]

    # Rename metadata model key
    metadata = json_message["$metadata.$model"]
    json_message["$metadata"] = {"$model": metadata}
    json_message.pop("$metadata.$model")

    patch = []
    for key, value in json_message.items():

        # can not update the id and metadata of the twin, and only updates the twin's properties that have not null values
        if key != "$id" and key != "$metadata" and value is not None:
            patch.append({"op": "add", "path": "/" + key, "value": value})

    # try to update the twin in the ADT, and if there is no exception a Dev Log is displayed
    # service_client.update_digital_twin(digital_twin_id, patch)
    logging.info(
        "Dev Log: The following twin has been updated successfully: %s", json_message
    )
