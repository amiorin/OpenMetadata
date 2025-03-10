#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Metadata DAG function builder
"""

from airflow import DAG
from openmetadata.workflows.ingestion.common import build_ingestion_dag

try:
    from airflow.operators.python import PythonOperator
except ModuleNotFoundError:
    from airflow.operators.python_operator import PythonOperator

from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    IngestionPipeline,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    OpenMetadataWorkflowConfig,
    Sink,
    WorkflowConfig,
)


def build_metadata_workflow_config(
    ingestion_pipeline: IngestionPipeline,
) -> OpenMetadataWorkflowConfig:
    """
    Given an airflow_pipeline, prepare the workflow config JSON
    """
    workflow_config = OpenMetadataWorkflowConfig(
        source=ingestion_pipeline.source,
        sink=Sink(
            type="metadata-rest",
        ),
        workflowConfig=WorkflowConfig(
            openMetadataServerConfig=ingestion_pipeline.openMetadataServerConnection
        ),
    )

    return workflow_config


def build_metadata_dag(ingestion_pipeline: IngestionPipeline) -> DAG:
    """
    Build a simple metadata workflow DAG
    """
    workflow_config = build_metadata_workflow_config(ingestion_pipeline)
    dag = build_ingestion_dag(
        task_name="ingestion_task",
        ingestion_pipeline=ingestion_pipeline,
        workflow_config=workflow_config,
    )

    return dag
