import logging
import json

from azure.storage.blob import BlobServiceClient

from ..config import configuration
from ..Dependencies.General_Functions import move_blob


def main(msg: str):
    body = json.loads(msg)
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    logging.info("Moving file %s to history container", body["file"])
    move_blob(
        service_client,
        configuration["STORAGE_ACCOUNT_NAME"],
        configuration["inputContainerName"] + "/" + body["container"],
        configuration["historyContainerName"] + "/" + body["container"],
        body["file"],
    )
