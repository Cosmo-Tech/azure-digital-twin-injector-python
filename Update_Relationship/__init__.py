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

    patch = []
    for key, value in json_message.items():
        # can not update the source id, target id or name of the relationship, and only updates the relationship's properties that have not null values
        if (
            key != "$sourceId"
            and key != "$targetId"
            and key != "$relationshipName"
            and value is not None
        ):
            patch.append({"op": "add", "path": "/" + key, "value": value})

    logging.info(patch)

    # try to update the relationship in the ADT, and if there is no exception a Dev Log is displayed
    try:
        service_client.update_relationship(json_message["$sourceId"], relationshipId, patch)
    except Exception as e:
        logging.error("Failed to update relationship %s", relationshipId)
        return {"status": "failed", "$id": relationshipId, "message": str(e)}
    logging.info(
        "Dev Log: The following relationship has been updated successfully: %s",
        json_message,
    )
    return {"status": "updated", "$id": relationshipId}
