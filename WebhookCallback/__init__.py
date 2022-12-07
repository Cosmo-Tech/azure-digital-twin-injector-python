import requests
import logging


def main(callBackUri: str):
    if not callBackUri:
        return
    requests.get(url=callBackUri)
    logging.info("Callback %s called", callBackUri)
    return {"status": "called", "callback": callBackUri}
