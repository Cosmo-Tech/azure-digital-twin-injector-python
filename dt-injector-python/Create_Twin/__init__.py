import logging
import json
import azure.functions as func
import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode("utf-8")
    json_message = json.loads(message_body)
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)
    digital_twin_id = json_message["$id"]

    # try to upsert the twin in the ADT, and if there is no exception a Dev Log is displayed
    created_twin = service_client.upsert_digital_twin(digital_twin_id, json_message)
    logging.info(
        "Dev Log: The following twin has been created successfully: %s", created_twin
    )
