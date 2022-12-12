import json
import logging
import requests

from azure.storage.blob import BlobServiceClient
import azure.durable_functions as df

from ..Dependencies.General_Functions import (
    ls_files,
    read_blob_into_json_array,
    move_blob,
)
from ..config import configuration


def post_callback(callback_uri: str):
    """Call callback given in original request"""
    if not callback_uri:
        return
    header = {"Content-Type": "application/json"}
    requests.post(url=callback_uri, headers=header, data={})
    logging.info("Callback %s called", callback_uri)


def orchestrator_function(context: df.DurableOrchestrationContext):
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    client_input = service_client.get_container_client(
        configuration["inputContainerName"]
    )

    acts = []
    req_input = context.get_input() or {}
    acts_data = req_input.get("activities", configuration["activities"])
    for act_data in acts_data:
        context.set_custom_status(f"{act_data['activityName']}")
        files = ls_files(client_input, act_data["containerName"], recursive=True)
        for f in files:
            if not f.endswith(".csv"):
                logging.debug("Skipping file %s", f)
                continue
            context.set_custom_status(f"{f}: {act_data['activityName']}")
            logging.info("Processing file %s", f)
            blob_json_array = read_blob_into_json_array(
                client_input, act_data["containerName"] + "/" + f
            )
            for idx, raw in enumerate(blob_json_array):
                logging.info("Processing line %i: %s", idx, raw)
                msg = json.dumps(raw)
                act = yield context.call_activity(act_data.get("activityName"), msg)
                acts.append(act)

    for act_data in acts_data:
        for f in files:
            logging.info("Moving file %s to history container", f)
            move_blob(
                service_client,
                configuration["STORAGE_ACCOUNT_NAME"],
                configuration["inputContainerName"] + "/" + act_data["containerName"],
                configuration["historyContainerName"] + "/" + act_data["containerName"],
                f,
            )
    post_callback(req_input.get("callBackUri", ""))
    return acts


main = df.Orchestrator.create(orchestrator_function)
