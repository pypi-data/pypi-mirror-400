import urllib3

from e2enetworks.cloud.tir import version as tir_version

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__version__ = tir_version.__version__

from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.apitoken import APITokens
from e2enetworks.cloud.tir.datasets.datasets import Datasets
from e2enetworks.cloud.tir.inference.endpoints import EndPoints
from e2enetworks.cloud.tir.images import Images
from e2enetworks.cloud.tir.inference.models import Models
from e2enetworks.cloud.tir.notebooks.notebook import Notebooks
from e2enetworks.cloud.tir.pipelines import PipelineClient
from e2enetworks.cloud.tir.projects import Projects
from e2enetworks.cloud.tir.skus import Plans
from e2enetworks.cloud.tir.teams import Teams
from e2enetworks.cloud.tir.api_client import ModelAPIClient
from e2enetworks.cloud.tir.finetuning.finetuner import FinetuningClient
from e2enetworks.cloud.tir.vector_db.vector_db import VectorDB
from e2enetworks.cloud.tir.distributed_jobs.distributed_job import DistributedJobClient
from e2enetworks.cloud.tir.integrations.integrations import Integration


init = client.Default.init
load_config = client.Default.load_config

__all__ = (
    "init",
    "PipelineClient",
    "load_config"
)


def help():
    """
AI Platform Help:

Provides an overview of available classes and methods in the platform.

Available classes:

- init: Provides functionalities for initialization.
- Images: Provides functionalities to interact with images.
- Plans: Provides functionalities to interact with skus.
- Integration: Provides functionalities to interact with integrations.
- Teams: Provides functionalities to interact with teams.
- Projects: Provides functionalities to interact with projects.
- Notebooks: Provides functionalities to interact with notebooks.
- Datasets: Provides functionalities to interact with datasets.
- EndPoints: Provides functionalities to interact with endpoints.
- Models: Provides functionalities to interact with models.
- PipelineClient: Provides functionalities to interact with Pipelines.
- APITokens: Provides functionalities to interact with API tokens.
- VectorDB: Provides functionalities to interact with Vector Databases.
    """

    # Call help() on each class
    class_objects = [
        client.Default, Images, Plans, Teams, Projects, Notebooks,
        Datasets, EndPoints, PipelineClient, Models, APITokens,
        ModelAPIClient, FinetuningClient, VectorDB, DistributedJobClient,
        Integration,
    ]

    for obj in class_objects:
        obj.help()
