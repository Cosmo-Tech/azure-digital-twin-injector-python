import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body.replace("'", '"'))
    url = configuration["digitalTwinUrl"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    relationshipId = (
        json_message["$relationshipName"]
        + "-"
        + json_message["$sourceId"]
        + "-"
        + json_message["$targetId"]
    )

    patch = []
    for key, value in json_message.items():
        # can not update the source id, target id or name of the relationship, and only updates the relationship's properties that have not null values
        if (
            key != "$sourceId"
            and key != "$targetId"
            and key != "$relationshipName"
            and value is not None
        ):
            patch.append({"op": "add", "path": "/" + key, "value": value})

    logging.info(patch)

    # try to update the relationship in the ADT, and if there is no exception a Dev Log is displayed
    service_client.update_relationship(json_message["$sourceId"], relationshipId, patch)
    logging.info(
        "Dev Log: The following relationship has been updated successfully: %s",
        json_message,
    )
