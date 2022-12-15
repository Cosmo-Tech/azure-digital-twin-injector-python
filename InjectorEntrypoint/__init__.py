import os
import logging
import requests

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    action = req.route_params["action"]
    req_url = os.environ.get(action)
    if not req_url:
        logging.error("Could not find action %s", action)
    header = {"Content-Type": "application/json"}
    logging.warning(req_url)
    try:
        requests.post(url=req_url, headers=header, json=req.get_json(), timeout=1)
    except requests.exceptions.ReadTimeout:
        pass
    return func.HttpResponse(f"Calling action {action}", status_code=200)
