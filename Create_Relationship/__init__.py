import logging
import json
import azure.functions as func
import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body.replace("'", '"'))
    url = os.environ["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    relationshipId = (
        json_message["$relationshipName"]
        + "-"
        + json_message["$sourceId"]
        + "-"
        + json_message["$targetId"]
    )

    # try to upsert the relationship in the ADT, and if there is no exception a Dev Log is displayed
    service_client.upsert_relationship(
        json_message["$sourceId"], relationshipId, json_message
    )
    logging.info(
        "Dev Log: The following relationship has been created successfully: %s",
        json_message,
    )
