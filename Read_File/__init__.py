import json
import csv
from ast import literal_eval
from io import StringIO

from azure.storage.blob import BlobServiceClient

from ..config import configuration


def read_blob_into_json_array(container_client, blob_name):
    """
    Reads a blob from a container and stores its content into a json array
    in which every element represents a line in the the blob
    """
    downloaded_blob = container_client.download_blob(blob_name)

    # Read the csv-like string into DataFrame
    csv_data = csv.DictReader(StringIO(downloaded_blob.content_as_text()))
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


def main(file: str):
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    client_input = service_client.get_container_client(
        configuration["inputContainerName"]
    )
    return read_blob_into_json_array(client_input, file)
