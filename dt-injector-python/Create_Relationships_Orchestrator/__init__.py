import logging
import sys
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import (
           QueueClient,
           BinaryBase64EncodePolicy
    )
import json
from Dependencies import General_Functions

def main(req):

  httplogger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
  httplogger.setLevel(logging.WARNING)
  
  # Connection string to the azure storage account 
  CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=yousrastorageaccount;AccountKey=x0CS2CIE8PEkQL1VkYcZNl7yb3gfTnokfMF6WZSXqtUq9+aLVUoEkIN3pIDs8MQXEOois8NKhyw7+AStFZtYVw==;EndpointSuffix=core.windows.net"
  # Name of the container containing all the input blobs 
  INPUT_CONTAINER_NAME = "input-files"
  # Name of the container containing the blobs that have already been processed
  HISTORY_CONTAINER_NAME = "history-files"
  # Name of the azure storage account 
  ACCOUNT_NAME = "yousrastorageaccount"
  # Name of the output queue containing the messages produced by the orchestrator function
  OUTPUT_QUEUE_NAME = "create-relationship-queue"
  # Name of the container containing the specific blobs used in this function
  SPECIFIC_CONTAINER = "create-storage/create-relationships"
  
  service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
  client_input = service_client.get_container_client(INPUT_CONTAINER_NAME)
  queue_client = QueueClient.from_connection_string(CONNECTION_STRING, OUTPUT_QUEUE_NAME)
  # Set up Base64 encoding function
  queue_client.message_encode_policy = BinaryBase64EncodePolicy()

  # Process the Http request that had triggered the function
  # the request must have the following form 
  # req_body = {
  #         "action": "Create",
  #         "element": "Relationship"
  #     }
  req_body = req.get_json()
  try:
      action = req_body["action"]
      if(action != "Create") :
        logging.error("Dev Log: The action in request body doesn't match the triggered function : Create_Relationships_Orchestrator")
        return
  except:
      logging.error("Dev Log: Action is missing in request body")
      return 

  try:
      element = req_body["element"]
      if(element != "Relationship") :
        logging.error("Dev Log: The element in request body doesn't match the triggered function : Create_Relationships_Orchestrator")
        return
  except:
      logging.error("Dev Log: Element is missing in request body")
      return

  try :
    # list all the files in the input container
    files = General_Functions.ls_files(client_input,SPECIFIC_CONTAINER, recursive=True)
    for f in files:

      # process each blob in the input container that is a csv file
      if(f.endswith(".csv")) : 

        # read blob content into a json array        
        blob_json_array=General_Functions.read_blob_into_json_array(client_input,SPECIFIC_CONTAINER+'/'+f)


        # create a message in the output queue fo each element of the json array
        for i in blob_json_array:
          
          # convert each element to a json formatted string message
          message=json.dumps(i)

          # insert the message in the output queue after encoding it
          message_bytes = message.encode('ascii')
          queue_client.send_message(queue_client.message_encode_policy.encode(content=message_bytes))
          logging.info("Dev Log: The message: %s has been sent to %s ",message,OUTPUT_QUEUE_NAME)

        logging.info("Dev Log: All the messages generated from the file %s have been sent to %s",f,OUTPUT_QUEUE_NAME)
        # move the processed csv file from the input container to the history container 
        General_Functions.move_blob(service_client,ACCOUNT_NAME,INPUT_CONTAINER_NAME+"/"+SPECIFIC_CONTAINER,HISTORY_CONTAINER_NAME+"/"+SPECIFIC_CONTAINER,f)
  except Exception as e:
    logging.exception(e)
  return

