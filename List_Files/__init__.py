import logging
import json
import os

from azure.storage.blob import BlobServiceClient

from ..config import configuration


def ls_files(client, path, recursive=False):
    """
    Lists files (blobs) under a path, optionally recursively inside the client's container
    """
    if not path == "" and not path.endswith("/"):
        path += "/"

    blob_iter = client.list_blobs(name_starts_with=path)
    files = []
    for blob in blob_iter:
        relative_path = os.path.relpath(blob.name, path)
        if recursive or "/" not in relative_path:
            files.append(relative_path)
    return files


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
