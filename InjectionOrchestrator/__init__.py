import json
import logging

import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    acts = []
    input_data = context.get_input() or {}
    for act_data in input_data.get("activities", []):
        context.set_custom_status(f"{act_data['activityName']}")
        for blob in act_data.get("blobs", []):
            for row in blob:
                logging.info("Processing element of $id %s", row.get("$id"))
                act = yield context.call_activity(
                    act_data.get("activityName"), json.dumps(row)
                )
                acts.append(act)
        for f in act_data.get("files"):
            yield context.call_activity(
                "Archive_File",
                json.dumps({"file": f, "container": act_data["containerName"]}),
            )

    yield context.call_activity("Web_Callback", (input_data.get("callBackUri", "")))
    return acts


main = df.Orchestrator.create(orchestrator_function)
