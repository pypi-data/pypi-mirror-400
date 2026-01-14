# py-MDR

The goal of this project is to enable the seamless interaction with Schuberg Philis' MDR from Python without
friction. This is mainly achieved via a Handler class implementation for the Python logging mechanisms that
sends the information in the correct format to the HEC endpoint.

## Installation

Package is published in [PyPI](https://pypi.org/project/py-mdr/). 

```sh
pip install py-mdr
```

## Usage

### Handler
The handler is a derivative of `logging.Handler` that sends the data to OpenSearch via the `hec` endpoint. Bear into consideration
that at the time of writing, sending the information is a **synchronous task**, meaning that it will block the current
thread until the message is received or it timeouts. In the future this will be changed so this just adds to a queue
and a secondary thread tries to send the information asynchronously. 

After installing the project, the handler can be integrated in the top level logger like this:

```python
import logging

from py_mdr.handler import MDRHandler
from py_mdr.ocsf_models.objects.product import Product

# If no "source-type" is provided for MDRHandler, then the logger name is used
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(
    MDRHandler(host="route.to.hec.endpoint:8088",       # Defaults to os.getenv("MDR_HOST")
               token="A-VALID-TOKEN",                   # Defaults to os.getenv("MDR_TOKEN")
               ssl_verify=True,                         # Disable SSL on acceptance if necessary
               
               # All de Product metadata is copied into each request, helpful for manipulating in vector aggregator
               product = Product(name="<PROJECT>", vendor_name="<COMPANY>.<TEAM>"))
)

logger.info("Message that will be logged to MDR")
logger.warning("This one will also be logged")
```

#### Extending

In case that the basic format is not useful, to extend the class the simplest way is to derive from MDRHandler
and override the map_log_record() function. This returns a EventLogActivity object that

```python
import logging

from py_mdr.handler import MDRHandler
from py_mdr.ocsf_models.events.system_activity.event_log_activity import EventLogActivity
from py_mdr.ocsf_models.objects.enrichment import Enrichment


class BetterHandler(MDRHandler):
  def map_log_record(self, record: logging.LogRecord) -> EventLogActivity:
    log_activity = super().map_log_record(record)
    log_activity.enrichments.append(
      Enrichment(name="Additional information", value={"important": "stuff"})
    )

    return log_activity
```

### Client

To send other information to MDR different from EventLogActivity use the `MDRClient` class instead. This receives a 
derivative of `BaseEvent`, from which all the events in the OCSF Models schema derive from. This will handle flattening
the object, removing unused fields and sending it to the MDR hec endpoint. You can use it this way:

```python 
from py_mdr.client import MDRClient
from py_mdr.ocsf_models.events.findings.detection_finding import DetectionFinding

client = MDRClient(name="<PROJECT_NAME>",               # This is sent as splunk_sourcetype as "pymdr::<PROJECT_NAME>"
                   host="route.to.hec.endpoint:8088",   # Defaults to os.getenv("MDR_HOST")
                   token="A-VALID-TOKEN",               # Defaults to os.getenv("MDR_TOKEN")
                   ssl_verify=True                      # Disable SSL on acceptance if necessary
                   )

event = DetectionFinding()
event.metadata.product.vendor_name = "<COMPANY>"
event.metadata.product.name = "Data"
event.status = "Testing"
event.comment = "This is a comment"

client.send(event)
```

In case of it being necessary, a `dict` can be sent though this is discouraged. The events include fixed metadata that
is used in the background by MDR to catalogue and index events.

# OCSF Models

Several models from [OCSF](https://schema.ocsf.io/1.3.0/categories) have been added to make interaction with the tool
easier. The goal is to support correct data mapping from as near to the source as possible, and taking into
consideration
that MDR internally tries to map to these.

This builds from the [Prowler-Cloud/py-ocsf-models](https://github.com/prowler-cloud/py-ocsf-models) (Apache 2.0
license)
to have an initial making of base objects. Currently, the following events are implemented:

* System Activity [1]
    * [] File System Activity [1001]
    * [] Kernel Extension Activity [1002]
    * [] Kernel Activity [1003]
    * [] Memory Activity [1004]
    * [] Module Activity [1005]
    * [] Scheduled Job Activity [1006]
    * [] Process Activity [1007]
    * [x] [Event Log Activity](py_mdr/ocsf_models/events/system_activity/event_log_activity.py) [1008]

* Findings [2]
    * ~~[] Security Finding [2001]~~
    * [x] [Vulnerability Finding](py_mdr/ocsf_models/events/findings/vulnerability_finding.py) [2002]
    * [] Compliance Finding [2003]
    * [x] [Detection Finding](py_mdr/ocsf_models/events/findings/detection_finding.py) [2004]
    * [] Incident Finding [2005]
    * [] Data Security Finding [2006]

* Identity & Access Management [3]
    * [] Account Change [3001]
    * [] Authentication [3002]
    * [] Authorize Session [3003]
    * [] Entity Management [3004]
    * [] User Access Management [3005]
    * [] Group Management [3006]

* Network Activity [4]
    * [] Network Activity [4001]
    * [] HTTP Activity [4002]
    * [] DNS Activity [4003]
    * [] DHCP Activity [4004]
    * [] RDP Activity [4005]
    * [] SMB Activity [4006]
    * [] SSH Activity [4007]
    * [] FTP Activity [4008]
    * [] Email Activity [4009]
    * [] Network File Activity [4010]
    * [] Email File Activity [4011]
    * [] Email URL Activity [4012]
    * [] NTP Activity [4013]
    * [] Tunnel Activity [4014]

* Discovery [5]
    * [] Device Inventory Info [5001]
    * [] Device Config State [5002]
    * [] User Inventory Info [5003]
    * [] Operating System Patch State [5004]
    * [] Kernel Object Query [5006]
    * [] File Query [5007]
    * [] Folder Query [5008]
    * [] Admin Group Query [5009]
    * [] Job Query [5010]
    * [] Module Query [5011]
    * [] Network Connection Query [5012]
    * [] Networks Query [5013]
    * [] Peripheral Device Query [5014]
    * [] Process Query [5015]
    * [] Service Query [5016]
    * [] User Session Query [5017]
    * [] User Query [5018]
    * [] Device Config State Change [5019]
    * [x] [Software Inventory Info](py_mdr/ocsf_models/events/discovery/software_inventory.py) [5020]

* Application Activity [6]
    * [] Web Resources Activity [6001]
    * [] Application Lifecycle [6002]
    * [] API Activity [6003]
    * [] Web Resource Access Activity [6004]
    * [] Datastore Activity [6005]
    * [] File Hosting Activity [6006]
    * [] Scan Activity [6007]

* Remediation [7]
    * [] Remediation Activity [7001]
    * [] File Remediation Activity [7002]
    * [] Process Remediation Activity [7003]
    * [] Network Remediation Activity [7004]

# Future work

Some ideas that might be interesting to pursue in the future for this package:

* Add a CLI for sending information to MDR for projects that are not written in Python
* Using [LoggerAdapters](https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output) as a possible workaround for extra information in the records.
* Make the sending of log information an asynchronous task 