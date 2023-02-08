import logging
import requests

import azure.functions as func

ACTIONS = [
    "Create_Twins",
    "Create_Relationships",
    "Delete_Twins",
    "Delete_Relationships",
    "Update_Twins",
    "Update_Relationships",
]


def main(req: func.HttpRequest) -> func.HttpResponse:
    code = req.params.get("code")
    if not code:
        logging.error("Azure function 'code' is missing in query parameters")
        return func.HttpResponse(
            "Azure function 'code' is missing in query parameters", status_code=400
        )
    action = req.route_params.get("action")
    if not action or action not in ACTIONS:
        logging.error("'action' route parameter is invalid: %s", action)
        return func.HttpResponse(
            f"'action' route parameter is invalid: {action}", status_code=400
        )
    logging.info(f'calling {action} orechestrator')
    func_name = req.url.split(".net")[0]
    req_url = f"{func_name}.net/api/{action}_Orchestrator?code={code}"
    header = {"Content-Type": "application/json"}

    json_body = req.get_json() if req.get_body() else {}
    r = None
    try:
        requests.post(url=req_url, headers=header, json=json_body, timeout=1)
    except requests.exceptions.ReadTimeout:
        pass
    return func.HttpResponse(f"Calling action {action}", status_code=202)
