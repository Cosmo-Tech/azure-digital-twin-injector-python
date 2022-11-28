import logging
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from ..config import configuration


def main(msg: str):
    json_message = json.loads(msg)
    url = configuration["digitalTwinUrl"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)

    if any(
        key not in ["$relationshipName", "$sourceId", "$targetId"]
        for key in json_message.keys()
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

    # try to delete the relationship in the ADT, and if there is no exception a Dev Log is displayed
    try:
        service_client.delete_relationship(json_message["$sourceId"], relationshipId)
    except Exception as e:
        logging.error("Failed to delete relationship %s", relationshipId)
        return {"status": "failed", "$id": relationshipId, "message": str(e)}
    logging.info(
        "Dev Log: The following relationship has been deleted successfully: %s",
        json_message,
    )
    return {"status": "deleted", "$id": relationshipId}
