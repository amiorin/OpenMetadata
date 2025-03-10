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
Validate workflow configs and filters
"""
import uuid
from copy import deepcopy

import sqlalchemy as sqa
from sqlalchemy.orm import declarative_base

from metadata.generated.schema.api.tests.createColumnTest import CreateColumnTestRequest
from metadata.generated.schema.api.tests.createTableTest import CreateTableTestRequest
from metadata.generated.schema.entity.data.table import Column, DataType, Table
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.metadataIngestion.databaseServiceMetadataPipeline import (
    DatabaseServiceMetadataPipeline,
)
from metadata.generated.schema.tests.column.columnValuesToBeBetween import (
    ColumnValuesToBeBetween,
)
from metadata.generated.schema.tests.columnTest import ColumnTestCase, ColumnTestType
from metadata.generated.schema.tests.table.tableRowCountToEqual import (
    TableRowCountToEqual,
)
from metadata.generated.schema.tests.tableTest import TableTestCase, TableTestType
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.orm_profiler.api.workflow import ProfilerWorkflow
from metadata.orm_profiler.processor.orm_profiler import OrmProfilerProcessor
from metadata.orm_profiler.profiler.default import DefaultProfiler
from metadata.orm_profiler.profiler.models import ProfilerDef
from metadata.orm_profiler.validations.models import TestDef, TestSuite

config = {
    "source": {
        "type": "sqlite",
        "serviceName": "my_service",
        "serviceConnection": {"config": {"type": "SQLite"}},
        "sourceConfig": {"config": {}},
    },
    "processor": {"type": "orm-profiler", "config": {}},
    "sink": {"type": "metadata-rest", "config": {}},
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://localhost:8585/api",
            "authProvider": "no-auth",
        }
    },
}

workflow = ProfilerWorkflow.create(config)


def test_init_workflow():
    """
    We can initialise the workflow from a config
    """
    assert isinstance(workflow.source_config, DatabaseServiceMetadataPipeline)
    assert isinstance(workflow.metadata_config, OpenMetadataConnection)

    assert isinstance(workflow.processor, OrmProfilerProcessor)
    assert workflow.processor.config.profiler is None
    assert workflow.processor.config.test_suite is None


def test_filter_entities():
    """
    We can properly filter entities depending on the
    workflow configuration
    """

    service_name = "service"
    schema_reference1 = EntityReference(
        id=uuid.uuid4(), name="one_schema", type="databaseSchema"
    )
    schema_reference2 = EntityReference(
        id=uuid.uuid4(), name="another_schema", type="databaseSchema"
    )

    all_tables = [
        Table(
            id=uuid.uuid4(),
            name="table1",
            databaseSchema=schema_reference1,
            fullyQualifiedName=f"{service_name}.db.{schema_reference1.name}.table1",
            columns=[Column(name="id", dataType=DataType.BIGINT)],
        ),
        Table(
            id=uuid.uuid4(),
            name="table2",
            databaseSchema=schema_reference1,
            fullyQualifiedName=f"{service_name}.db.{schema_reference1.name}.table2",
            columns=[Column(name="id", dataType=DataType.BIGINT)],
        ),
        Table(
            id=uuid.uuid4(),
            name="table3",
            databaseSchema=schema_reference2,
            fullyQualifiedName=f"{service_name}.db.{schema_reference2.name}.table3",
            columns=[Column(name="id", dataType=DataType.BIGINT)],
        ),
    ]

    # Simple workflow does not filter
    assert len(list(workflow.filter_entities(all_tables))) == 3

    # We can exclude based on the schema name
    exclude_filter_schema_config = deepcopy(config)
    exclude_filter_schema_config["source"]["sourceConfig"]["config"][
        "schemaFilterPattern"
    ] = {"excludes": ["one_schema"]}

    exclude_filter_schema_workflow = ProfilerWorkflow.create(
        exclude_filter_schema_config
    )
    assert len(list(exclude_filter_schema_workflow.filter_entities(all_tables))) == 1

    # We can include based on the schema name
    include_filter_schema_config = deepcopy(config)
    include_filter_schema_config["source"]["sourceConfig"]["config"][
        "schemaFilterPattern"
    ] = {"includes": ["another_schema"]}

    include_filter_schema_workflow = ProfilerWorkflow.create(
        include_filter_schema_config
    )
    assert len(list(include_filter_schema_workflow.filter_entities(all_tables))) == 1

    # We can exclude based on the table name
    exclude_filter_table_config = deepcopy(config)
    exclude_filter_table_config["source"]["sourceConfig"]["config"][
        "tableFilterPattern"
    ] = {"excludes": ["tab*"]}

    exclude_filter_table_workflow = ProfilerWorkflow.create(exclude_filter_table_config)
    assert len(list(exclude_filter_table_workflow.filter_entities(all_tables))) == 0

    # We can include based on the table name
    include_filter_table_config = deepcopy(config)
    include_filter_table_config["source"]["sourceConfig"]["config"][
        "tableFilterPattern"
    ] = {"includes": ["table1"]}

    include_filter_table_workflow = ProfilerWorkflow.create(include_filter_table_config)
    assert len(list(include_filter_table_workflow.filter_entities(all_tables))) == 1


def test_profile_def():
    """
    Validate the definitions of the profile in the JSON
    """
    profile_config = deepcopy(config)
    profile_config["processor"]["config"]["profiler"] = {
        "name": "my_profiler",
        "metrics": ["row_count", "min", "COUNT", "null_count"],
    }

    profile_workflow = ProfilerWorkflow.create(profile_config)

    profile_definition = ProfilerDef(
        name="my_profiler",
        metrics=["ROW_COUNT", "MIN", "COUNT", "NULL_COUNT"],
        time_metrics=None,
        custom_metrics=None,
    )

    assert isinstance(profile_workflow.processor, OrmProfilerProcessor)
    assert profile_workflow.processor.config.profiler == profile_definition


def test_default_profile_def():
    """
    If no information is specified for the profiler, let's
    use the SimpleTableProfiler and SimpleProfiler
    """

    profile_workflow = ProfilerWorkflow.create(config)

    assert isinstance(profile_workflow.processor, OrmProfilerProcessor)
    assert profile_workflow.processor.config.profiler is None

    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = sqa.Column(sqa.Integer, primary_key=True)
        name = sqa.Column(sqa.String(256))
        fullname = sqa.Column(sqa.String(256))
        nickname = sqa.Column(sqa.String(256))
        age = sqa.Column(sqa.Integer)

    table = Table(
        id=uuid.uuid4(),
        name="users",
        fullyQualifiedName="service.db.users",
        columns=[
            Column(name="id", dataType=DataType.INT),
            Column(name="name", dataType=DataType.STRING),
            Column(name="fullname", dataType=DataType.STRING),
            Column(name="nickname", dataType=DataType.STRING),
            Column(name="age", dataType=DataType.INT),
        ],
        database=EntityReference(id=uuid.uuid4(), name="db", type="database"),
        profileSample=80.0,
    )

    assert isinstance(
        profile_workflow.processor.build_profiler(User, table=table),
        DefaultProfiler,
    )


def test_tests_def():
    """
    Validate the test case definition
    """
    test_config = deepcopy(config)
    test_config["processor"]["config"]["test_suite"] = {
        "name": "My Test Suite",
        "tests": [
            {
                "table": "service.db.name",  # FQDN
                "table_tests": [
                    {
                        "testCase": {
                            "config": {
                                "value": 100,
                            },
                            "tableTestType": "tableRowCountToEqual",
                        },
                    },
                ],
                "column_tests": [
                    {
                        "columnName": "age",
                        "testCase": {
                            "config": {
                                "minValue": 0,
                                "maxValue": 99,
                            },
                            "columnTestType": "columnValuesToBeBetween",
                        },
                    }
                ],
            },
        ],
    }

    test_workflow = ProfilerWorkflow.create(test_config)

    assert isinstance(test_workflow.processor, OrmProfilerProcessor)
    suite = test_workflow.processor.config.test_suite

    expected = TestSuite(
        name="My Test Suite",
        tests=[
            TestDef(
                table="service.db.name",
                table_tests=[
                    CreateTableTestRequest(
                        testCase=TableTestCase(
                            config=TableRowCountToEqual(value=100),
                            tableTestType=TableTestType.tableRowCountToEqual,
                        ),
                    )
                ],
                column_tests=[
                    CreateColumnTestRequest(
                        columnName="age",
                        testCase=ColumnTestCase(
                            config=ColumnValuesToBeBetween(minValue=0, maxValue=99),
                            columnTestType=ColumnTestType.columnValuesToBeBetween,
                        ),
                    )
                ],
            )
        ],
    )

    assert suite == expected
