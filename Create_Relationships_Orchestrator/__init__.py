import logging
import json

import azure.functions as func

from ..Dependencies.orchestrator import Orchestrator


def main(req: func.HttpRequest) -> func.HttpResponse:

    # Name of the output queue containing the messages produced by the orchestrator function
    OUTPUT_QUEUE_NAME = "create-relationship-queue"
    # Name of the container containing the specific blobs used in this function
    SPECIFIC_CONTAINER = "create-storage/create-relationships"

    logging.info("Dev Log: Create relationship starting.")

    orc = Orchestrator(SPECIFIC_CONTAINER, OUTPUT_QUEUE_NAME)

    def transform(row):
        return json.dumps(row)

    orc.row_transform = transform
    return orc.run(req)
