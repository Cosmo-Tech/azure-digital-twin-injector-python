import logging
import json
import azure.functions as func
import os
import sys
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity._credentials.imds import ImdsCredential


def main(msg: func.QueueMessage):

    message_body = msg.get_body().decode('utf-8')
    json_message = json.loads(message_body.replace("'",'"'))
    url = os.environ["AZURE_ADT_URL"]
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential, logging_enable=True)
    
    
    relationshipId=json_message["$relationshipName"]+"-"+json_message["$sourceId"]+"-"+json_message["$targetId"]

    patch=[]
    for key,value in json_message.items():
        if(key!="$sourceId" and key!="$targetId" and key!= "$relationshipName") : 
            patch.append({
                "op": "replace",
                "path": "/"+key,
                "value": value
            })

    # try to update the relationship in the ADT, and if there is no exception a Dev Log is displayed
    service_client.update_relationship(
        json_message["$sourceId"],
        relationshipId,
        patch
    )
    logging.info("Dev Log: The following relationship has been updated successfully: %s",json_message)

    


