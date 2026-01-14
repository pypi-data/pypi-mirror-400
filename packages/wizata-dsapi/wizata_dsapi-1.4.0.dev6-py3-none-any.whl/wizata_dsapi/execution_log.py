from .api_dto import Dto
from .experiment import Experiment
from .pipeline import Pipeline
from .twin import Twin
from .template import Template
from .twinregistration import TwinRegistration
from .execution import ExecutionStatus
import uuid
import sys
import json


class ExecutionLog(Dto):
    """
    execution log contains all information about a current execution.
    - execution log replaces execution in version 11.4+
    - as based on loki storage, some data are values and others are indexes/labels
    - other properties are used only during execution time and are non-persistent

    # labels
    :ivar str experiment: short string key identifier of the experiment
    :ivar str pipeline: short string key identifier of the pipeline
    :ivar str template: short string key identifier of the template
    :ivar str twin: short string key identifier of the twin
    :ivar str edge_device_id: short string id of the IoT Edge Device
    :ivar wizata_dsapi.ExecutionStatus status: execution status

    # values
    :ivar uuid.UUID id: technical id of execution
    :ivar str pipeline_image_id: pipeline image identifier
    :ivar int queued_date: timestamp on which execution is queued, if none use createdDate
    :ivar int started_date: timestamp on which execution is started
    :ivar int waiting_time: duration of the waiting time in the queue
    :ivar int execution_time: duration of the execution from started
    :ivar uuid.UUID trigger_id: technical id of trigger
    :ivar version str: python version (major.minor) to use as target on runners, by default use current auto-detected version.

    # non-persistent values
    :ivar dict properties: properties containing key/value pairs used to parametrize the pipeline execution
    :ivar list warnings: list of error and/or warning messages
    """

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionLog":

        # un-pack properties if they are jsonify
        properties = data.get("properties")
        if isinstance(properties, str):
            properties = json.loads(properties)

        return cls(
            execution_id=uuid.UUID(data["id"]) if "id" in data else None,
            experiment=data.get("experiment"),
            pipeline=data.get("pipeline") if "pipeline" in data else uuid.UUID(data.get("pipelineId")) if "pipelineId" in data else None,
            template=data.get("template") if "template" in data else uuid.UUID(data.get("templateId")) if "templateId" in data else None,
            twin=data.get("twin") if "twin" in data else uuid.UUID(data.get("twinId")) if "twinId" in data else None,
            edge_device_id=data.get("edgeDeviceId"),
            status=ExecutionStatus(str(data["status"])) if "status" in data else None,
            pipeline_image_id=data.get("pipelineImageId"),
            queued_date=int(data.get("queuedDate")) if "queuedDate" in data and data["queuedDate"] is not None else None,
            started_date=int(data.get("startedDate")) if "startedDate" in data and data["startedDate"] is not None else None,
            waiting_time=int(data.get("waitingTime")) if "waitingTime" in data and data["waitingTime"] is not None else None,
            execution_time=int(data.get("executionTime")) if "executionTime" in data and data["executionTime"] is not None else None,
            trigger_id=uuid.UUID(data["executionTriggerId"]) if "executionTriggerId" in data and data["executionTriggerId"] is not None else None,
            version=data.get("version"),
            properties=properties
        )

    def __init__(self,
                 execution_id: uuid.UUID = None,
                 experiment: str|uuid.UUID|Experiment = None,
                 pipeline: str|uuid.UUID|Pipeline = None,
                 twin: str|uuid.UUID|Twin = None,
                 template: str|uuid.UUID|Template = None,
                 registration: uuid.UUID|TwinRegistration = None,
                 edge_device_id: str = None,
                 status: ExecutionStatus = None,
                 pipeline_image_id: str = None,
                 queued_date: int = None,
                 started_date: int = None,
                 waiting_time: int = None,
                 execution_time: int = None,
                 trigger_id: uuid.UUID = None,
                 version: str = None,
                 properties: dict = None):

        # labels
        self._experiment = None
        self._experiment_id = None
        self._experiment_key = None
        self.experiment = experiment

        self._pipeline = None
        self._pipeline_id = None
        self._pipeline_key = None
        self.pipeline = pipeline

        self._twin = None
        self._twin_id = None
        self._twin_key = None
        self.twin = twin

        self._template = None
        self._template_id = None
        self._template_key = None
        self.template = template

        self._registration = None
        self._registration_id = None
        self.registration = registration

        self.edge_device_id = edge_device_id
        self.status = status

        # values
        if execution_id is None:
            execution_id = uuid.uuid4()
        self.execution_id = execution_id
        self.pipeline_image_id = pipeline_image_id
        self.queued_date = queued_date
        self.started_date = started_date
        self.waiting_time = waiting_time
        self.execution_time = execution_time
        self.trigger_id = trigger_id
        self.version = version
        if version is None:
            self.version = f'{sys.version_info.major}.{sys.version_info.minor}'

        # non-persistent data
        if properties is None:
            properties = {}
        self.properties = properties
        self.models = []
        self.plots = []
        self.dataframes = []
        self.messages = []

    @property
    def experiment(self):
        """
        get experiment
        :return: object or key or id
        """
        if self._experiment is not None:
            return self._experiment
        if self._experiment_key is not None:
            return self._experiment_key
        return self._experiment_id

    @experiment.setter
    def experiment(self, value: str | uuid.UUID | Experiment | None):
        """
        set experiment - accept key/uuid or a Experiment
        """
        if value is None:
            self._experiment = None
            self._experiment_id = None
            self._experiment_key = None
            return

        if isinstance(value, Experiment):
            self._experiment = value
            self._experiment_key = value.key
            self._experiment_id = value.experiment_id
            return

        if isinstance(value, uuid.UUID):
            self._experiment = None
            self._experiment_id = value
            return

        if isinstance(value, str):
            self._experiment = None
            self._experiment_key = value
            return

        raise TypeError(f"Unsupported pipeline type: {type(value)}")

    def get_experiment_id(self):
        if self._experiment is not None:
            return self._experiment.experiment_id
        else:
            return self._experiment_id

    def get_experiment_key(self):
        if self._experiment is not None:
            return self._experiment.key
        else:
            return self._experiment_key

    @property
    def pipeline(self):
        """
        get pipeline
        :return: object or key or id
        """
        if self._pipeline is not None:
            return self._pipeline
        if self._pipeline_key is not None:
            return self._pipeline_key
        return self._pipeline_id

    @pipeline.setter
    def pipeline(self, value: str | uuid.UUID | Pipeline | None):
        """
        set pipeline - accept key/uuid or a Pipeline
        """
        if value is None:
            self._pipeline = None
            self._pipeline_id = None
            self._pipeline_key = None
            return

        if isinstance(value, Pipeline):
            self._pipeline = value
            self._pipeline_key = value.key
            self._pipeline_id = value.pipeline_id
            return

        if isinstance(value, uuid.UUID):
            self._pipeline = None
            self._pipeline_id = value
            return

        if isinstance(value, str):
            self._pipeline = None
            self._pipeline_key = value
            return

        raise TypeError(f"Unsupported pipeline type: {type(value)}")

    def get_pipeline_id(self):
        if self._pipeline is not None:
            return self._pipeline.pipeline_id
        else:
            return self._pipeline_id

    def get_pipeline_key(self):
        if self._pipeline is not None:
            return self._pipeline.key
        else:
            return self._pipeline_key

    @property
    def twin(self):
        """
        get twin
        :return: object or key or id
        """
        if self._twin is not None:
            return self._twin
        if self._twin_key is not None:
            return self._twin_key
        return self._twin_id

    @twin.setter
    def twin(self, value: str | uuid.UUID | Twin | None):
        """
        set twin - accept key/uuid or a Twin
        """
        if value is None:
            self._twin = None
            self._twin_id = None
            self._twin_key = None
            return

        if isinstance(value, Twin):
            self._twin = value
            self._twin_key = value.hardware_id
            self._twin_id = value.twin_id
            return

        if isinstance(value, uuid.UUID):
            self._twin = None
            self._twin_id = value
            return

        if isinstance(value, str):
            self._twin = None
            self._twin_key = value
            return

        raise TypeError(f"Unsupported twin type: {type(value)}")

    def get_twin_id(self):
        if self._twin is not None:
            return self._twin.twin_id
        else:
            return self._twin_id

    def get_twin_key(self):
        if self._twin is not None:
            return self._twin.hardware_id
        else:
            return self._twin_key

    @property
    def template(self):
        """
        get template
        :return: object or key or id
        """
        if self._template is not None:
            return self._template
        if self._template_key is not None:
            return self._template_key
        return self._template_id

    @template.setter
    def template(self, value: str | uuid.UUID | Template | None):
        """
        set template - accept key/uuid or a Template
        """
        if value is None:
            self._template = None
            self._template_id = None
            self._template_key = None
            return

        if isinstance(value, Template):
            self._template = value
            self._template_key = value.key
            self._template_id = value.template_id
            return

        if isinstance(value, uuid.UUID):
            self._template = None
            self._template_id = value
            return

        if isinstance(value, str):
            self._template = None
            self._template_key = value
            return

        raise TypeError(f"unsupported template type: {type(value)}")

    def get_template_id(self):
        if self._template is not None:
            return self._template.template_id
        else:
            return self._template_id

    def get_template_key(self):
        if self._template is not None:
            return self._template.key
        else:
            return self._template_key

    @property
    def registration(self):
        """
        get registration
        :return: object or id
        """
        if self._registration is not None:
            return self._registration
        return self._registration_id

    @registration.setter
    def registration(self, value: uuid.UUID | TwinRegistration | None):
        """
        set template - accept uuid or a TwinRegistration
        """
        if value is None:
            self._registration = None
            self._registration_id = None
            return

        if isinstance(value, TwinRegistration):
            self._registration = value
            self._registration_id = value.twin_registration_id
            return

        if isinstance(value, uuid.UUID):
            self._registration = None
            self._registration_id = value
            return

        raise TypeError(f"Unsupported registration type: {type(value)}")

    def get_registration_id(self):
        if self._registration is not None:
            return self._registration.twin_registration_id
        else:
            return self._registration

    def get_labels(self) -> dict:
        labels = {
            "experiment": self.get_experiment_key(),
            "pipeline": self.get_pipeline_key(),
            "template": self.get_template_key(),
            "twin": self.get_twin_key(),
            "edgeDeviceId": self.edge_device_id,
            "status": self.status.value if self.status else None
        }
        return {k: v for k, v in labels.items() if v is not None}

    def get_values(self) -> dict:
        data = {
            "id": str(self.execution_id) if self.execution_id else None,
            "pipelineImageId": self.pipeline_image_id,
            "queuedDate": self.queued_date,
            "startedDate": self.started_date,
            "waitingTime": self.waiting_time,
            "executionTime": self.execution_time,
            "executionTriggerId": str(self.trigger_id) if self.trigger_id else None,
            "version": self.version,
            "messages": self.messages or None
        }
        return {k: v for k, v in data.items() if v is not None}

    def to_dict(self) -> dict:
        """
        convert the log to a dictionary
        - don't forget to drop properties if needed
        :return: dict of the execution log
        """
        non_values = {
            "properties": self.properties or {}
        }
        return self.get_labels() | self.get_values() | non_values