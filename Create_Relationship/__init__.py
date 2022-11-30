import logging
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: str):
    json_message = json.loads(msg)
    url = configuration["DIGITAL_TWIN_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    if any(
        key not in json_message
        for key in ["$relationshipName", "$sourceId", "$targetId"]
    ):
        logging.error("Relationship file is missing columns")
        return {"status": "failed"}

    relationshipId = "".join(
        [
            json_message["$relationshipName"],
            "-",
            json_message["$sourceId"],
            "-",
            json_message["$targetId"],
        ]
    )

    # try to upsert the relationship in the ADT, and if there is no exception a Dev Log is displayed
    try:
        service_client.upsert_relationship(
            json_message["$sourceId"], relationshipId, json_message
        )
    except Exception as e:
        logging.error("Failed to create relation %s", relationshipId)
        return {"status": "failed", "$id": relationshipId, "message": str(e)}
    logging.info(
        "Dev Log: The following relationship has been created successfully: %s",
        json_message,
    )
    return {"status": "created", "$id": relationshipId}
