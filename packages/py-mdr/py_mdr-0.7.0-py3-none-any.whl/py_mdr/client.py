import json
import logging
import re
import uuid
from urllib.parse import urlparse

import httpx
from httpx import RequestError
from py_mdr.ocsf_models.events.base_event import BaseEvent
from py_mdr.ocsf_models.objects.base_model import BaseModel


class MDRClient:
    """
    Represents a raw client that allows sending of arbitrary messages to the
    MDR hec interface.
    """

    def _validate_dataset_name(self, dataset_name: str, pattern: str = "^[a-z_]+$") -> bool:
        """
        Checks that the provided dataset name complies with the requirements
        """
        compiled_pattern = re.compile(pattern)
        if not compiled_pattern.match(dataset_name):
            self.logger.error(f"Invalid dataset name provided: {dataset_name}. Must only contain {compiled_pattern.pattern} characters.")
            raise ValueError(f"Invalid dataset name provided: {dataset_name}. Must only contain {compiled_pattern.pattern} characters.")
        return True

    def _validate_namespace(self, namespace: str, pattern: str = "^[a-z]+$") -> bool:
        """
        Checks that the provided namespace complies with the requirements
        """
        compiled_pattern = re.compile(pattern)
        if not compiled_pattern.match(namespace):
            self.logger.error(f"Invalid namespace provided: {namespace}. Must only contain {compiled_pattern.pattern} characters.")
            raise ValueError(f"Invalid namespace provided: {namespace}. Must only contain {compiled_pattern.pattern} characters.")
        return True

    def __init__(self,
                 dataset_name: str,
                 namespace: str,
                 host: str, 
                 token: str,
                 ssl_verify: bool = True):
        """
        Initializes the client. It takes by default the host and token values from the environment variables "MDR_HOST"
        and "MDR_TOKEN" respectively.

        :param dataset_name: Name to identify the application in OpenSearch. It can only contain [a-z_] characters.
        :param namespace: Namespace of the application to send the information into. Can only contain [a-z] characters and be at least 1 character long
        :param host: Hostname, with port, of where to send the log information (e.g. "host.name.tld:8080")
        :param token: Token for authenticating with the MDR client
        :param ssl_verify: If verify is enabled or not
        """
        self.logger = logging.getLogger(__name__)
        self._validate_dataset_name(dataset_name)
        self._validate_namespace(namespace)
        self.source_name = f"pymdr::{dataset_name}.{namespace}"
        self.host = host if host.startswith("http") else f"https://{host}"
        self.parsed_url = urlparse(self.host)
        self.api_endpoint_hec = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/services/collector/event"
        self.api_endpoint_health = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/services/collector/health"

        # According to documentation: https://docs.splunk.com/Documentation/SplunkCloud/9.3.2411/Data/AboutHECIDXAck#About_channels_and_sending_data
        # Channels should be unique per client are sent as a UUID. As to make it deterministic per client, UUIDv5 is used
        # with DNS namespace. Which is created out of the dataset name and namespace.
        client_channel_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{dataset_name}.{namespace}.schubergphilis.com")
        headers = {
            "Authorization": f"Splunk {token}",
            "X-Splunk-Request-Channel": str(client_channel_id)
        }
        self.token = token
        self.ssl_verify = ssl_verify
        self.client = self.get_valid_client(verify=ssl_verify, headers=headers)

    def get_valid_client(self, verify: bool, headers: dict) -> httpx.Client:
        """
        Tests the connection to the MDR endpoint by sending a test event.
        :raises Exception: If the connection fails for any reason.
        :return: True if the connection is successful.
        """
        try:
            client = httpx.Client(verify=verify, headers=headers)
            response = client.get(self.api_endpoint_health, follow_redirects=True)
            response.raise_for_status()
            self.logger.debug(f"Connection to MDR successful. Response: {response.text}")
            return client
        except httpx.ConnectError as error:
            message = f"SSL certificate verification failed: {error}" if "CERTIFICATE_VERIFY_FAILED" in str(error) else f"Failed to connect to MDR: {error}"
            self.logger.error(message)
            raise RuntimeError(message)

    def send(self, event: dict | BaseEvent):
        """
        Sends a new event to the MDR. The event should be a raw dictionary or a subclass of BaseEvent.
        :param event:
        :return:
        """
        response = None
        entry = {
            "source": self.source_name,
            "event": {
                "source_format": self.source_name,
                **(event.as_dict() if isinstance(event, BaseModel) else event)
            }
        }

        response = None  # Define the variable, so the exception handler can check on None
        try:
            response = self.client.post(
                self.api_endpoint_hec,
                json=entry,
                timeout=5)
            response.raise_for_status()
            self.logger.debug(f"Sent event of type {type(event)} to MDR. Response: {response.text}")
        except (RequestError, Exception) as e:
            self.logger.error(f"Exception while sending event to MDR ({e}). Response: ({response.text if response else '<NO RESPONSE>'})")

    def send_batch(self, events: list[dict | BaseEvent]):
        """
        Sends a batch of events to the MDR asynchronously. Each event should be a raw dictionary or a subclass of BaseEvent.
        :param events: List of events to send
        :return:
        """
        response = None
        events_string = ''.join(
            json.dumps({
                "source": self.source_name,
                "event": {
                    "source_format": self.source_name,
                    **(event.as_dict() if isinstance(event, BaseModel) else event)
                }
            }) for event in events
        )

        try:
            response = self.client.post(
                self.api_endpoint_hec,
                content=events_string,
                timeout=5)
            response.raise_for_status()
            self.logger.debug(f"Sent batch of {len(events)} events to MDR. Response: {response.text}")
        except (RequestError, Exception) as e:
            self.logger.error(f"Exception while sending batch to MDR ({e}). Response: ({response.text if response else '<NO RESPONSE>'})")
