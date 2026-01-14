import concurrent.futures
import getpass
import importlib.metadata
import logging
import socket
from datetime import datetime, timezone

from py_mdr.client import MDRClient
from py_mdr.ocsf_models.events import SeverityID
from py_mdr.ocsf_models.events.system_activity.event_log_activity import EventLogActivity, LogTypeID
from py_mdr.ocsf_models.objects.actor import Actor
from py_mdr.ocsf_models.objects.enrichment import Enrichment
from py_mdr.ocsf_models.objects.file import File
from py_mdr.ocsf_models.objects.metadata import Metadata
from py_mdr.ocsf_models.objects.network import NetworkEndpoint
from py_mdr.ocsf_models.objects.process import Process
from py_mdr.ocsf_models.objects.product import Product
from py_mdr.ocsf_models.objects.user import User


class MDRHandler(logging.Handler):
    """
    Logger handler that can interact with the MDR service. The intention is that
    all logging information can be sent in the right format without hassle.
    """

    SEVERITY_ID = {
        logging.DEBUG: SeverityID.Other,
        logging.INFO: SeverityID.Informational,
        logging.WARNING: SeverityID.Medium,
        logging.ERROR: SeverityID.High,
        logging.FATAL: SeverityID.Fatal,
        logging.CRITICAL: SeverityID.Critical
    }

    def __init__(self,
                 dataset_name: str,
                 namespace: str,
                 host: str,
                 token: str,
                 ssl_verify: bool = True,
                 product: Product = Product(name="py-mdr", vendor_name="SBP"),
                 ):
        """
        Create main MDR handler
        :param dataset_name: Name of the dataset to use when storing data
        :param namespace: Namespace to use when storing data
        :param host: Host to where to send the log information with port (e.g. host.name.com:8088)
        :param token: Splunk token for authentication
        :param ssl_verify: Enable or disable SSL verification
        :param product: Additional product information to send with the log
        """
        super().__init__()
        self.client = MDRClient(
            dataset_name=dataset_name,
            namespace=namespace,
            host=host,
            token=token,
            ssl_verify=ssl_verify
        )
        self.product = product
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def emit(self, record):
        try:
            data = self.map_log_record(record)
            self.executor.submit(self.client.send, data)
        except Exception:
            self.handleError(record)

    def close(self):
        self.executor.shutdown(wait=True)
        super().close()

    def get_client(self):
        """
        Returns the client being used by the handler.
        :return:
        """
        return self.client

    def map_log_record(self, record: logging.LogRecord) -> EventLogActivity:
        metadata = Metadata(
            log_level=record.levelname,
            log_provider=__name__,
            log_version=importlib.metadata.version("py_mdr"),
            logged_time=datetime.now(timezone.utc),
            product=self.product,
        )

        enrichments = [
            Enrichment(name="file_information", data={
                "line_number": record.lineno,
                "module": record.module,
                "function_name": record.funcName
            })
        ]

        process = Process(
            name=record.processName,
            pid=record.process,
        )

        # Try to get additional optional enrichments. Set to none at this point as any statement
        # could fail.
        user_name = None
        hostname = None

        # noinspection PyBroadException
        try:
            user_name = getpass.getuser()
            hostname = socket.gethostname()
        except Exception:
            pass

        severity_id = MDRHandler.SEVERITY_ID.get(record.levelno, SeverityID.Unknown)
        event = EventLogActivity(
            time=datetime.fromtimestamp(record.created),
            file=File(name=record.filename),
            log_name=record.name,
            log_provider=__name__,
            log_type_id=LogTypeID.Application,
            log_type=LogTypeID.Application.name,
            message=record.msg,
            metadata=metadata,
            raw_data=str(record),
            severity=severity_id.name,
            severity_id=severity_id,
            enrichments=enrichments,
            src_endpoint=NetworkEndpoint(hostname=hostname),
            actor=Actor(process=process, user=User(name=user_name)),
        )

        return event
