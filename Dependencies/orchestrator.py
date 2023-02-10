import logging
import os
import requests

from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy
import azure.functions as func

from ..Dependencies import General_Functions

logger = logging.getLogger('Orchestrator')
httplogger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
httplogger.setLevel(logging.WARNING)


class Orchestrator:
    """Orchestration Class

    Retrieve csv files, transform line by line and put it in a queue."""

    def __init__(self, input_path, output_queue):
        self.account_name = os.environ["storageAccountName"]
        self.connection_string = os.environ["AzureWebJobsStorage"]
        self.input_container_name = "input-files"
        self.history_container_name = "history-files"
        self.input_path = input_path
        self.output_queue = output_queue

    def row_transform(self, row):
        pass

    def run(self, req):
        """Run orchestration

        read files from storage and send them to queue"""
        req_body = req.get_json() if req.get_body() else {}

        service_client = BlobServiceClient.from_connection_string(self.connection_string)
        client_input = service_client.get_container_client(self.input_container_name)
        queue_client = QueueClient.from_connection_string(self.connection_string, self.output_queue)
        # Set up Base64 encoding function
        queue_client.message_encode_policy = BinaryBase64EncodePolicy()

        try:
            # list all the files in the input container
            logger.info(f'reading Azure storage {self.input_path} from {client_input.container_name}')
            files = General_Functions.ls_files(client_input, self.input_path, recursive=True)
            for f in files:

                # process each blob in the input container that is a csv file
                if f.endswith(".csv"):

                    # read blob content into a json array
                    blob_json_array = General_Functions.read_blob_into_json_array(client_input,
                                                                                  self.input_path + "/" + f)

                    # create a message in the output queue fo each element of the json array
                    for row in blob_json_array:

                        message = self.row_transform(row)

                        # insert the message in the output queue after encoding it
                        message_bytes = message.encode("ascii")
                        queue_client.send_message(queue_client.message_encode_policy.encode(content=message_bytes))
                        logger.info(
                            "Dev Log: The message: %s has been sent to %s ",
                            message,
                            self.output_queue,
                        )

                    logger.info(
                        "Dev Log: All the messages generated from the file %s have been sent to %s",
                        f,
                        self.output_queue,
                    )
                    # move the processed csv file from the input container to the history container
                    General_Functions.move_blob(
                        service_client,
                        self.account_name,
                        self.input_container_name + "/" + self.input_path,
                        self.history_container_name + "/" + self.input_path,
                        f,
                    )
        except Exception as e:
            logger.exception(e)
            if req_body.get("callBackUri"):
                General_Functions.do_callback(req_body.get("callBackUri"), str(e))
            return func.HttpResponse("Message queue has been filled", status_code=500)

        if req_body.get("callBackUri"):
            logging.info('callback registered')
            if General_Functions.wait_end_of_queue_process(self.connection_string, self.output_queue):
                m = "Message queue has been processed"
                logging.info(m)
                General_Functions.do_callback(req_body.get("callBackUri"))
                return func.HttpResponse(m, status_code=200)
            else:
                m = f"Message has been detected in {self.output_queue}-poison queue. Other messages are still being processed."
                logging.error(m)
                General_Functions.do_callback(req_body.get("callBackUri"), m)
                return func.HttpResponse(m, status_code=400)
        else:
            return func.HttpResponse("Message queue has been filled", status_code=202)
