import requests
from typing import Optional
import logging


def main(callBackUri: Optional[str]):
    if not callBackUri:
        return
    requests.get(url=callBackUri)
    logging.info("Callback %s called", callBackUri)
    return {"status": "called", "callback": callBackUri}
