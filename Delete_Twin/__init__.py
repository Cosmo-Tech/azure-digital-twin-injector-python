import logging
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: str):
    json_message = json.loads(msg)
    url = configuration["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)

    if any(key not in ["$id", "$metadata.$model"] for key in json_message.keys()):
        logging.error("Twin file is missing columns")
        return {"status": "failed"}

    digital_twin_id = json_message["$id"]
    # Rename metadata model key
    metadata = json_message["$metadata.$model"]
    json_message["$metadata"] = {"$model": metadata}
    json_message.pop("$metadata.$model")

    # try to delete the twin in the ADT, and if there is no exception a Dev Log is displayed
    try:
        service_client.delete_digital_twin(digital_twin_id)
    except Exception as e:
        logging.error("Failed to delete twin %s", digital_twin_id)
        return {"status": "failed", "$id": digital_twin_id, "message": str(e)}
    logging.info(
        "Dev Log: The following twin has been deleted successfully: %s", json_message
    )
    return {"status": "deleted", "$id": digital_twin_id}