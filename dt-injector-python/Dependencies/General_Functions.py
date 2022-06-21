import os
import json
import pandas as pd
from io import StringIO
import logging

def ls_files(client, path, recursive=False):
  '''
  Lists files (blobs) under a path, optionally recursively inside the client's container
  '''
  if not path == '' and not path.endswith('/'):
    path += '/'

  blob_iter = client.list_blobs(name_starts_with=path)
  files = []
  for blob in blob_iter:
    relative_path = os.path.relpath(blob.name, path)
    if recursive or not '/' in relative_path:
      files.append(relative_path)
  return files

def move_blob(service_client,account_name,copy_from_container,copy_to_container,blob_name):
  '''
  Moves a blob from a container to another container
  '''
  source_blob = (f"https://{account_name}.blob.core.windows.net/{copy_from_container}/{blob_name}")
  copied_blob = service_client.get_blob_client(copy_to_container, blob_name)
  
  # Copy the source_blob into the copied_blob
  copied_blob.start_copy_from_url(source_blob)

  # Delete the source file
  remove_blob = service_client.get_blob_client(copy_from_container, blob_name)
  remove_blob.delete_blob()

def read_blob_into_json_array(container_client, blob_name):
  '''
  Reads a blob from a container and stores its content into a json array 
  in which every element represents a line in the the blob
  '''
  downloaded_blob = container_client.download_blob(blob_name)

  # Read the csv-like string into DataFrame
  df = pd.read_csv(StringIO(downloaded_blob.content_as_text()))

  # Convert the DataFrame to JSON string
  json_string=df.to_json (orient='records')
  # Convert the JSON string to JSON object
  json_array= json.loads(json_string)
  # Process the json correctly if there are values in map or object format 
  for element in json_array:
    for key,value in element.items():
      if(type(element[key]) == str and element[key].startswith("{") and element[key].endswith("}")) :
        element[key]=element[key].replace(";",",")
        element_to_json=json.loads(element[key])
        element[key]=element_to_json
  return json_array