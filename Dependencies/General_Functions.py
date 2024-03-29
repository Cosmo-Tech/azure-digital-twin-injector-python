import logging
import os
import json
import requests
from io import StringIO
import time
import pandas as pd
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


def move_blob(service_client, account_name, copy_from_container, copy_to_container, blob_name):
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
    downloaded_blob = container_client.download_blob(blob_name)

    # Read the csv-like string into DataFrame
    df = pd.read_csv(
        StringIO(downloaded_blob.content_as_text()),
        dtype={"InstallationYear": pd.Int64Dtype()},
    )

    # Convert the DataFrame to JSON string
    json_data = df.to_json(orient="records")
    # Convert the JSON string to JSON object
    json_array = json.loads(json_data)
    # Process the json correctly if there are values in map or object format
    for element in json_array:
        for key, value in element.items():
            # condition on 'CriteriaFormula is specifec for asset
            # this field contain condition formula which mustn't be convert to json
            # TODO use DTDL to convert to expected type
            if (isinstance(value, str) and key != "CriteriaFormula" and value.startswith("{") and value.endswith("}")):
                element[key] = json.loads(value.replace(";", ","))
    return json_array


def wait_end_of_queue_process(conn_str: str, queue_name: str):
    """Wait loop for queue_name to be empty and check for {queue_name}-poison to not exist or be empty.

    Function will return 0 when queue_name is empty.
    Function will return 1 if {queue_name}-poison exist and is not empty
    """

    WAIT_STEP = 3
    queue_client = QueueClient.from_connection_string(conn_str, queue_name)
    poison_queue_client = QueueClient.from_connection_string(conn_str, f'{queue_name}-poison')

    last_turn = False
    while True:
        # is poison queue existe and not empty
        try:
            properties = poison_queue_client.get_queue_properties()
            logging.warn(f'poison_queue: {properties.approximate_message_count}')
            if properties.approximate_message_count != 0:
                return False
        except ResourceNotFoundError:
            pass
        # is queue empty
        properties = queue_client.get_queue_properties()
        if properties.approximate_message_count != 0:
            logging.debug(f'queue: {properties.approximate_message_count}')
            time.sleep(WAIT_STEP)
            continue
        # Confirm queue remain empty
        if not last_turn:
            last_turn = True
            time.sleep(WAIT_STEP)
            continue
        return True


def do_callback(callback_uri: str, msg=None, code=None):
    header = {"Content-Type": "application/json"}
    data = {}
    data['output'] = {}
    data['statusCode'] = 200

    if msg:
        data['output'] = {'Message': msg}
        data['error'] = {'ErrorCode': code, 'Message': msg}
        data['statusCode'] = 400

    requests.post(url=callback_uri, headers=header, json=data)
