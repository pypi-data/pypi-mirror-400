# Copyright (C) 2024  rasmunk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import asyncio
import unittest
import pytest
import os
import random
from io import StringIO
from unittest.mock import patch
from network_manager_provider.defaults import BUNDLE
from network_manager_provider.codes import SUCCESS, FAILURE

from network_manager_provider.utils.config import load_config

from tests.support import (
    TEST_RES_DIR,
    TMP_TEST_PATH,
    cli_action,
    json_to_dict,
    create_cli_action,
    read_cli_action,
    update_cli_action,
    delete_cli_action,
    flush_cli_action,
)

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)


def apply_cli_action(action_type, *args):
    args = [*args]
    return cli_action(action_type, "apply", args)


def undo_cli_action(action_type, *args):
    args = [*args]
    return cli_action(action_type, "undo", args)


class TestCLIbundle(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.seed = str(random.random())[6:10]
        self.base_name = "bundle-tests-"
        self.name = f"{self.base_name}{self.seed}"
        self.test_config_file = os.path.join(TEST_RES_DIR, "router_example.yml")

    def tearDown(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        flush_return_code = flush_cli_action(BUNDLE, *bundle_args)
        self.assertEqual(flush_return_code, SUCCESS)

    def test_cli_bundle_create(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("id", output)
            self.assertIn("bundle", output)
            self.assertIn("name", output["bundle"])
            self.assertEqual(self.name, output["bundle"]["name"])
            self.assertIn("config", output["bundle"])

    def test_cli_bundle_create_with_config(self):
        bundle_args = [
            "--config-file",
            self.test_config_file,
            "--directory",
            CURRENT_TEST_DIR,
        ]
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

            reference_config = asyncio.run(load_config(self.test_config_file))
            self.assertDictEqual(output["bundle"]["config"], reference_config)

    def test_cli_bundle_read(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            bundle_id = output["id"]
        self.assertIsNotNone(bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_bundle_update(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            bundle_id = output["id"]
        self.assertIsNotNone(bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            update_return_code = update_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(update_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_bundle_delete(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            bundle_id = output["id"]
        self.assertIsNotNone(bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            delete_return_code = delete_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(delete_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_bundle_flush(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(create_return_code, SUCCESS)
            _ = json_to_dict(captured_stdout.getvalue())

        flush_return_code = flush_cli_action(BUNDLE, *bundle_args)
        self.assertEqual(flush_return_code, SUCCESS)
        # TODO, validate that no bundles exist

    @pytest.mark.privileged
    def test_cli_bundle_apply(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(
                BUNDLE,
                self.name,
                *bundle_args + ["--config-file", self.test_config_file],
            )
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            bundle_id = output["id"]
        self.assertIsNotNone(bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            apply_return_code = apply_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(apply_return_code, SUCCESS)
            apply_output = json_to_dict(captured_stdout.getvalue())
            apply_bundle_id = apply_output["id"]
            self.assertEqual(bundle_id, apply_bundle_id)

            self.assertIn("bridges", apply_output)
            bridges = apply_output["bridges"]
            self.assertIsInstance(bridges, dict)
            self.assertIn("successes", bridges)
            self.assertIn("failures", bridges)
            self.assertEqual(len(bridges["failures"]), 0)
            self.assertEqual(len(bridges["successes"]), 1)

            self.assertIn("interfaces", apply_output)
            interfaces = apply_output["interfaces"]
            self.assertIsInstance(interfaces, dict)
            self.assertIn("successes", interfaces)
            self.assertIn("failures", interfaces)
            self.assertEqual(len(interfaces["failures"]), 0)
            self.assertEqual(len(interfaces["successes"]), 1)

            self.assertIn("namespaces", apply_output)
            namespaces = apply_output["namespaces"]
            self.assertIsInstance(namespaces, dict)
            self.assertIn("successes", namespaces)
            self.assertIn("failures", namespaces)
            self.assertEqual(len(namespaces["failures"]), 0)
            self.assertEqual(len(namespaces["successes"]), 2)

    def test_cli_bundle_apply_no_bundle(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = "non-existent-bundle-id"
        with patch("sys.stderr", new=StringIO()) as captured_stdout:
            apply_return_code = apply_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(apply_return_code, FAILURE)
            apply_output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(apply_output, dict)
            self.assertIn("msg", apply_output)
            self.assertIsInstance(apply_output["msg"], str)
            self.assertGreater(len(apply_output["msg"]), 0)
            self.assertIn("status", apply_output)
            self.assertEqual("failed", apply_output["status"])

    @pytest.mark.privileged
    def test_cli_bundle_undo(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        bundle_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(
                BUNDLE,
                self.name,
                *bundle_args + ["--config-file", self.test_config_file],
            )
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            bundle_id = output["id"]
        self.assertIsNotNone(bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            apply_return_code = apply_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(apply_return_code, SUCCESS)
            apply_output = json_to_dict(captured_stdout.getvalue())
            apply_bundle_id = apply_output["id"]
            self.assertEqual(bundle_id, apply_bundle_id)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            undo_return_code = undo_cli_action(BUNDLE, bundle_id, *bundle_args)
            self.assertEqual(undo_return_code, SUCCESS)
            undo_output = json_to_dict(captured_stdout.getvalue())
            undo_bundle_id = undo_output["id"]
            self.assertEqual(bundle_id, undo_bundle_id)

            self.assertIn("namespaces", undo_output)
            namespaces = undo_output["namespaces"]
            self.assertIsInstance(namespaces, dict)
            self.assertIn("successes", namespaces)
            self.assertIn("failures", namespaces)
            self.assertEqual(len(namespaces["failures"]), 0)
            self.assertEqual(len(namespaces["successes"]), 2)

            self.assertIn("interfaces", undo_output)
            interfaces = undo_output["interfaces"]
            self.assertIsInstance(interfaces, dict)
            self.assertIn("successes", interfaces)
            self.assertIn("failures", interfaces)
            self.assertEqual(len(interfaces["failures"]), 0)
            self.assertEqual(len(interfaces["successes"]), 1)

            self.assertIn("bridges", undo_output)
            bridges = undo_output["bridges"]
            self.assertIsInstance(bridges, dict)
            self.assertIn("successes", bridges)
            self.assertIn("failures", bridges)
            self.assertEqual(len(bridges["failures"]), 0)
            self.assertEqual(len(bridges["successes"]), 1)

    def test_cli_bundle_ls(self):
        bundle_args = ["--directory", CURRENT_TEST_DIR]
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(BUNDLE, self.name, *bundle_args)
            self.assertEqual(create_return_code, SUCCESS)
            _ = json_to_dict(captured_stdout.getvalue())

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            ls_return_code = cli_action(BUNDLE, "ls", bundle_args)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("bundles", output)
            self.assertIsInstance(output["bundles"], list)
            self.assertGreaterEqual(len(output["bundles"]), 1)
