import json
import logging
from dataclasses import dataclass
from json import JSONDecodeError

import requests


@dataclass
class ClientError(Exception):
    status: int
    content: dict

    def __str__(self):
        return self.__repr__()


class APIUtils:
    logger = logging.getLogger('APIUtils')

    def __init__(self, api_key, verify: bool = True):
        self.api_key = api_key
        self.verify = verify

    def call(self, method: str, url: str, payload: dict = None):
        headers = {
            "Content-Type": "application/json",
            "X-API-TOKEN": self.api_key
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=payload,
                verify=self.verify
            )
            response.raise_for_status()

            if response.status_code == 204:
                return None

            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e}")
            self.logger.info(f"Response content: {response.content}")

            try:
                json_content = json.loads(response.content)
            except JSONDecodeError as e:
                self.logger.error(f"JSON Parsing Exception: {e}")
                raise ClientError(status=response.status_code, content={})

            raise ClientError(status=response.status_code, content=json_content)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Exception: {e}")
            raise
