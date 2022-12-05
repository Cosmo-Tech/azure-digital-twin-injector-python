import logging

import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    try:
        client_input = req.get_json()
    except ValueError:
        client_input = {}
    instance_id = await client.start_new(
        "InjectionOrchestrator", client_input=client_input
    )
    logging.info(f"Started injection orchestrator with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)
