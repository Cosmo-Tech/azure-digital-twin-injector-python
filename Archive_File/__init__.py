import logging
import json

from azure.storage.blob import BlobServiceClient

from ..config import configuration


def move_blob(
    service_client, account_name, copy_from_container, copy_to_container, blob_name
):
    """
    Moves a blob from a container to another container
    """
    source_blob = f"https://{account_name}.blob.core.windows.net/{copy_from_container}/{blob_name}"
    copied_blob = service_client.get_blob_client(copy_to_container, blob_name)

    # Copy the source_blob into the copied_blob
    copied_blob.start_copy_from_url(source_blob)

    # Delete the source file
    remove_blob = service_client.get_blob_client(copy_from_container, blob_name)
    remove_blob.delete_blob()


def main(msg: str):
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    body = json.loads(msg)
    logging.info("Moving file %s to history container", body["files"])
    for file in body["files"]:
        move_blob(
            service_client,
            configuration["STORAGE_ACCOUNT_NAME"],
            configuration["inputContainerName"] + "/" + body["container"],
            configuration["historyContainerName"] + "/" + body["container"],
            file,
        )
