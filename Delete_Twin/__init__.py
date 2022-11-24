import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body)
    url = configuration.get("digitalTwinUrl")
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)
    digital_twin_id = json_message["$id"]

    # Rename metadata model key
    metadata = json_message["$metadata.$model"]
    json_message["$metadata"] = {"$model": metadata}
    json_message.pop("$metadata.$model")

    # try to delete the twin in the ADT, and if there is no exception a Dev Log is displayed
    service_client.delete_digital_twin(digital_twin_id)
    logging.info(
        "Dev Log: The following twin has been deleted successfully: %s", json_message
    )
