import requests
import logging


def main(callBackUri: str):
    if not callBackUri:
        return
    header = {'Content-Type': 'application/json'}
    requests.post(url=callBackUri, headers=header, data={})
    logging.info("Callback %s called", callBackUri)
    return {"status": "called", "callback": callBackUri}
