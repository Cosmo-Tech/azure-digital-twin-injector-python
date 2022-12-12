import logging
import json
import copy

from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: str):
    json_message = json.loads(msg)
    url = configuration["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    if any(key not in json_message for key in ["$id", "$metadata.$model"]):
        logging.error("Twin file is missing columns")
        return {"status": "failed"}

    digital_twin_id = json_message["$id"]

    # Rename metadata model key
    metadata = json_message["$metadata.$model"]
    json_message["$metadata"] = {"$model": metadata}
    json_message.pop("$metadata.$model")

    # manage empty field and map-like columns
    new_msg = copy.deepcopy(json_message)
    for j in json_message:
        if json_message[j] in (None, ""):
            new_msg.pop(j)
            continue
        if "." in j:
            map_split = j.split(".")
            if map_split[0] not in new_msg:
                new_msg[map_split[0]] = {}
            new_msg[map_split[0]][map_split[1]] = json_message[j]
            new_msg.pop(j)

    # try to upsert the twin in the ADT, and if there is no exception a Dev Log is displayed
    try:
        created_twin = service_client.upsert_digital_twin(digital_twin_id, new_msg)
    except Exception as e:
        logging.error("Failed to create twin %s: %s", digital_twin_id, str(e))
        return {"status": "failed", "$id": digital_twin_id, "message": str(e)}
    logging.info(
        "Dev Log: The following twin has been created successfully: %s", created_twin
    )
    return {"status": "created", "$id": digital_twin_id}
