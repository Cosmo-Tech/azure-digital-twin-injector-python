import logging
import json

import azure.functions as func

from ..Dependencies.orchestrator import Orchestrator


def main(req: func.HttpRequest) -> func.HttpResponse:

    # Name of the output queue containing the messages produced by the orchestrator function
    OUTPUT_QUEUE_NAME = "update-twin-queue"
    # Name of the container containing the specific blobs used in this function
    SPECIFIC_CONTAINER = "update-storage/update-twins"

    logging.info("Dev Log: Update twin starting.")

    orc = Orchestrator(SPECIFIC_CONTAINER, OUTPUT_QUEUE_NAME)

    def transform(row):
        # get the value of $metadata.$model
        metadata = row["$metadata.$model"]
        # copy it in a new property $metadata that contains an object $model
        row["$metadata"] = {"$model": metadata}
        # delete the old property $metadata.$model
        row.pop("$metadata.$model")

        # convert each element to a json formatted string message
        return json.dumps(row)

    orc.row_transform = transform
    return orc.run(req)
