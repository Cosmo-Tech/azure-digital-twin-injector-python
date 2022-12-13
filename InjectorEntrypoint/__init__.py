import logging

import azure.functions as func
import azure.durable_functions as df
from azure.storage.blob import BlobServiceClient

from ..config import configuration
from ..utils.read_file import read_blob_into_json_array
from ..utils.list_container import ls_files


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    try:
        input_data = req.get_json()
    except ValueError:
        input_data = {}
    input_data["activities"] = (
        input_data.get("activities") or configuration["activities"]
    )
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    container_client = service_client.get_container_client(
        configuration["inputContainerName"]
    )
    # Filling activities data with file paths and blob content
    for row, act_data in enumerate(input_data["activities"]):
        input_data["activities"][row]["files"] = ls_files(
            container_client, act_data["containerName"], True
        )
        input_data["activities"][row]["blob"] = [
            read_blob_into_json_array(
                container_client, f"{act_data['containerName']}/{f}"
            )
            for f in input_data["activities"][row]["files"]
        ]

    instance_id = await client.start_new(
        "InjectionOrchestrator", client_input=input_data
    )
    logging.info(f"Started injection orchestrator with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)
