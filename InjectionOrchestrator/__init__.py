import json
import logging
from azure.storage.blob import BlobServiceClient
import azure.durable_functions as df

from ..Dependencies.General_Functions import (
    ls_files,
    read_blob_into_json_array,
    move_blob,
)
from ..config import configuration


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info(configuration["AzureWebJobsStorage"])
    service_client = BlobServiceClient.from_connection_string(
        configuration["AzureWebJobsStorage"]
    )
    client_input = service_client.get_container_client(
        configuration["inputContainerName"]
    )

    acts = []
    logging.info("acts are %s", configuration["activities"])
    acts_data = sorted(configuration["activities"], key=lambda a: a.get("order", 99))
    for act_data in acts_data:
        context.set_custom_status(f"Starting {act_data['activityName']}")
        files = ls_files(client_input, act_data["containerName"], recursive=True)
        for f in files:
            if not f.endswith(".csv"):
                continue
            blob_json_array = read_blob_into_json_array(
                client_input, act_data["containerName"] + "/" + f
            )
            for raw in blob_json_array:
                msg = json.dumps(raw)
                context.set_custom_status(str(act_data.get("activityName")))
                act = yield context.call_activity(act_data.get("activityName"), msg)
                acts.append(act)
                # move_blob(
                #     service_client,
                #     settings.storageAccountName,
                #     settings.inputContainerName + "/" + act_data.containerName,
                #     settings.historyContainerName + "/" + act_data.containerName,
                #     f,
                # )
    # return acts


main = df.Orchestrator.create(orchestrator_function)
