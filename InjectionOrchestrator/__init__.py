import json
import logging

import azure.durable_functions as df

from ..config import configuration


def orchestrator_function(context: df.DurableOrchestrationContext):
    acts = []
    req_input = context.get_input() or {}
    acts_data = req_input.get("activities", configuration["activities"])
    acts_data = yield context.call_activity("List_Files", json.dumps(acts_data))
    for act_data in acts_data:
        context.set_custom_status(f"{act_data['activityName']}")
        for f in act_data.get("files", []):
            if not f.endswith(".csv"):
                logging.debug("Skipping file %s", f)
                continue
            context.set_custom_status(f"{f}: {act_data['activityName']}")
            logging.info("Processing file %s", f)
            blob_json_array = yield context.call_activity(
                "Read_File", act_data["containerName"] + "/" + f
            )
            for raw in blob_json_array:
                act = yield context.call_activity(
                    act_data.get("activityName"), json.dumps(raw)
                )
                acts.append(act)
            yield context.call_activity(
                "Archive_File",
                json.dumps({"file": f, "container": act_data["containerName"]}),
            )

    yield context.call_activity("Web_Callback", (req_input.get("callBackUri", "")))
    return acts


main = df.Orchestrator.create(orchestrator_function)
