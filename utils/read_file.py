import json
import pandas as pd
from io import StringIO


def read_blob_into_json_array(container_client, blob_name):
    """
    Reads a blob from a container and stores its content into a json array
    in which every element represents a line in the the blob
    """
    downloaded_blob = container_client.download_blob(blob_name)

    # Read the csv-like string into DataFrame
    df = pd.read_csv(
        StringIO(downloaded_blob.content_as_text()),
        dtype={"InstallationYear": pd.Int64Dtype()},
    )

    # Convert the DataFrame to JSON string
    json_data = df.to_json(orient="records")
    # Convert the JSON string to JSON object
    json_array = json.loads(json_data)
    # Process the json correctly if there are values in map or object format
    for element in json_array:
        for key, value in element.items():
            # condition on 'CriteriaFormula is specifec for asset
            # this field contain condition formula which mustn't be convert to json
            # TODO use DTDL to convert to expected type
            if (
                key != "CriteriaFormula"
                and isinstance(value, str)
                and value.startswith("{")
                and value.endswith("}")
            ):
                element[key] = json.loads(value.replace(";", ","))
    return json_array
