import importlib
import pathlib
from unittest import TestCase

from metadata.config.common import load_config_file
from metadata.ingestion.api.workflow import Workflow


class WorkflowTest(TestCase):

    def test_get_200(self):
        key = 'metadata.ingestion.sink.metadata_rest_tables.MetadataRestTablesSink'
        if key.find(".") >= 0:
            module_name, class_name = key.rsplit(".", 1)
            MyClass = getattr(importlib.import_module(module_name), class_name)
            self.assertEqual((MyClass is not None), True)

    def test_get_4xx(self):
        MyClass = None
        key = 'metadata.ingestion.sink.MYSQL.mysqlSINK'
        if key.find(".") >= 0:
            module_name, class_name = key.rsplit(".", 1)
            try:
                MyClass = getattr(importlib.import_module(module_name), class_name)
            except:
                self.assertEqual((MyClass is not None), False)

    def test_title_typeClassFetch(self):
        isFile = True
        type = 'query-parser'
        if isFile:
            replace = type.replace('-', '_')
        else:
            replace = ''.join([i.title() for i in type.replace('-', '_').split('_')])
        self.assertEqual(replace, 'query_parser')

    def test_title_typeClassFetch_4xx(self):
        isFile = False
        type = 'query-parser'
        if isFile:
            replace = type.replace('-', '_')
        else:
            replace = ''.join([i.title() for i in type.replace('-', '_').split('_')])
        self.assertEqual(replace, 'QueryParser')

    def test_execute_200(self):
        config_file = pathlib.Path('tests/unit/mysql_test.json')
        workflow_config = load_config_file(config_file)

        if workflow_config.get('cron'):
            del workflow_config['cron']
        workflow = Workflow.create(workflow_config)
        workflow.execute()
        workflow.stop()
        file_path = '/tmp/mysql_test'
        with open(file_path) as ingestionFile:
            ingestionData = ingestionFile.read()
        self.assertEqual(ingestionData is not None, True)

    def test_execute_4xx(self):
        config_file = pathlib.Path('tests/unit/mysql_test.json')
        workflow_config = load_config_file(config_file)
        ingestionData = None
        try:
            file_path = '/tmp/mysql_test123'
            with open(file_path) as ingestionFile:
                ingestionData = ingestionFile.read()
        except:
            self.assertEqual(ingestionData is not None, False)
