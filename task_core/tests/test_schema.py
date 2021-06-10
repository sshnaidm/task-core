"""unit tests of tasks"""
import os
import sys
import unittest
import yaml
from unittest import mock
from task_core import schema
from jsonschema.exceptions import ValidationError


INVENTORY_DATA_VALID = """
hosts:
  host-a:
    role: role-1
  host-b:
    role: role-1
"""

INVENTORY_DATA_INVALID = """
hosts:
  host-a: {}
"""

ROLES_DATA_VALID = """
role-1:
  services:
    - service-a
role-2:
  services:
    - service-a
    - service-b
    - service-c
    - service-d
"""

ROLES_DATA_INVALID = """
role-1: {}
"""

SERVICE_DATA_VALID = """
id: service-a
type: service
version: 1.0.0
tasks:
  - id: print
    driver: print
    message: "message from service a"

  - id: setup
    action: init
    driver: directord
    provides:
      - service-a.init
    jobs:
      - echo: "service a start"

  - id: run
    action: run
    driver: service
    provides:
      - service-a.run
    requires:
      - service-a.init
    jobs:
      - echo: "service a run"

  - id: finalize
    action: finalize
    driver: ansible_runner
    provides:
      - service-a.finalize
    requires:
      - service-a.run
    playbook: /foo/bar.yaml
    inventory: /foo/inv.yaml
"""


SERVICE_DATA_INVALID = """
id: service-a
type: service
version: 1.0.0
tasks:
  - id: print
    message: "this is a bad task"
"""


class TestBaseSchemaValidator(unittest.TestCase):
    """test base validator"""

    def tearDown(self):
        schema.BaseSchemaValidator._instance = None
        schema.BaseSchemaValidator._schema = None

    def test_instance(self):
        self.assertRaises(RuntimeError, schema.BaseSchemaValidator)

    def test_schema_not_implemented(self):
        obj = schema.BaseSchemaValidator.instance()
        try:
            obj.schema
        except Exception as e:
            self.assertIsInstance(e, NotImplementedError)

    def test_schema_fodler(self):
        obj = schema.BaseSchemaValidator.instance()
        self.assertEqual(
            obj.schema_folder, os.path.join(sys.prefix, "share", "task-core", "schema")
        )


class TestInventorySchemaValidator(unittest.TestCase):
    """Test InventorySchemaValidator object"""

    def setUp(self):
        super().setUp()
        folder_patcher = mock.patch(
            "task_core.schema.InventorySchemaValidator.schema_folder",
            new_callable=mock.PropertyMock,
        )
        self.mock_folder = folder_patcher.start()
        self.mock_folder.return_value = os.path.join(
            os.path.dirname(__file__), "..", "..", "schema"
        )
        self.addCleanup(folder_patcher.stop)

    def tearDown(self):
        schema.InventorySchemaValidator._instance = None
        schema.InventorySchemaValidator._schema = None

    def test_valid(self):
        """test valid data"""
        obj = schema.InventorySchemaValidator.instance()
        obj.validate(yaml.safe_load(INVENTORY_DATA_VALID))

    def test_invalid(self):
        """test invalid data"""
        obj = schema.InventorySchemaValidator.instance()
        self.assertRaises(ValidationError, obj.validate, INVENTORY_DATA_INVALID)


class TestRolesSchemaValidator(unittest.TestCase):
    """Test RolesSchemaValidator object"""

    def setUp(self):
        super().setUp()
        folder_patcher = mock.patch(
            "task_core.schema.RolesSchemaValidator.schema_folder",
            new_callable=mock.PropertyMock,
        )
        self.mock_folder = folder_patcher.start()
        self.mock_folder.return_value = os.path.join(
            os.path.dirname(__file__), "..", "..", "schema"
        )
        self.addCleanup(folder_patcher.stop)

    def tearDown(self):
        schema.RolesSchemaValidator._instance = None
        schema.RolesSchemaValidator._schema = None

    def test_valid(self):
        """test valid data"""
        obj = schema.RolesSchemaValidator.instance()
        obj.validate(yaml.safe_load(ROLES_DATA_VALID))

    def test_invalid(self):
        """test invalid data"""
        obj = schema.RolesSchemaValidator.instance()
        self.assertRaises(ValidationError, obj.validate, ROLES_DATA_INVALID)


class TestServiceSchemaValidator(unittest.TestCase):
    """Test ServiceSchemaValidator object"""

    def setUp(self):
        super().setUp()
        folder_patcher = mock.patch(
            "task_core.schema.ServiceSchemaValidator.schema_folder",
            new_callable=mock.PropertyMock,
        )
        self.mock_folder = folder_patcher.start()
        self.mock_folder.return_value = os.path.join(
            os.path.dirname(__file__), "..", "..", "schema"
        )
        self.addCleanup(folder_patcher.stop)

    def tearDown(self):
        schema.ServiceSchemaValidator._instance = None
        schema.ServiceSchemaValidator._schema = None

    def test_valid(self):
        """test valid data"""
        obj = schema.ServiceSchemaValidator.instance()
        obj.validate(yaml.safe_load(SERVICE_DATA_VALID))

    def test_invalid(self):
        """test invalid data"""
        obj = schema.ServiceSchemaValidator.instance()
        self.assertRaises(ValidationError, obj.validate, SERVICE_DATA_INVALID)
