import requests
import logging


def main(callbackUri: str):
    """Call callback given in original request"""
    if not callbackUri:
        return
    header = {"Content-Type": "application/json"}
    requests.post(url=callbackUri, headers=header, data={})
    logging.info("Callback %s called", callbackUri)
