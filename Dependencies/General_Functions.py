import os
import json
from io import StringIO
from ast import literal_eval
from csv import DictReader
from datetime import datetime
import time
import configparser
import sys
import math
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceNotFoundError


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


def read_blob_into_json_array(container_client, blob_name):
    """
    Reads a blob from a container and stores its content into a json array
    in which every element represents a line in the the blob
    """
    """
    Reads a blob from a container and stores its content into a json array
    in which every element represents a line in the the blob
    """
    downloaded_blob = container_client.download_blob(blob_name)

    # Read the csv-like string into DataFrame
    csv_data = DictReader(StringIO(downloaded_blob.content_as_text()))
    data = list(csv_data)
    # Process the json correctly if there are values in map or object format
    for element in data:
        for key, value in element.items():
            # condition on 'CriteriaFormula is specifec for asset
            # this field contain condition formula which mustn't be convert to json
            # TODO use DTDL to convert to expected type
            if (
                value.startswith("{")
                and value.endswith("}")
                and key != "CriteriaFormula"
            ):
                try:
                    element[key] = json.loads(value.replace(";", ","))
                    continue
                except json.JSONDecodeError:
                    pass
            try:
                element[key] = literal_eval(value)
            except Exception:
                pass
    return data


def wait_end_of_queue(queue_client: QueueClient):
    WAIT_STEP = 3
    while True:
        while True:
            try:
                properties = queue_client.get_queue_properties()
                break
            except ResourceNotFoundError:
                time.sleep(WAIT_STEP)
        count = properties.approximate_message_count
        if count == 0:
            # second wait to be sure
            time.sleep(WAIT_STEP)
            properties = queue_client.get_queue_properties()
            count = properties.approximate_message_count
            if count != 0:
                continue
            return
        time.sleep(WAIT_STEP)
