from azure.storage.blob import BlobServiceClient

from ..Dependencies.General_Functions import read_blob_into_json_array
from ..config import configuration


def main(file: str):
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    client_input = service_client.get_container_client(
        configuration["inputContainerName"]
    )
    return read_blob_into_json_array(client_input, file)
