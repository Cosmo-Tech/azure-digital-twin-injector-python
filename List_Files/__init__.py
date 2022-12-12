import logging
import json
from ..config import configuration
from azure.storage.blob import BlobServiceClient


from ..Dependencies.General_Functions import (
    ls_files
)


def main(msg: str):
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    client_input = service_client.get_container_client(
        configuration["inputContainerName"]
    )
    activities = json.loads(msg)
    logging.info("Listing files in input storage")
    for i, act_data in enumerate(activities):
        files = ls_files(client_input, act_data["containerName"], recursive=True)
        activities[i]["files"] = files
    return activities
