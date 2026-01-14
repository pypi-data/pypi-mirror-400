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

import unittest
import pytest
from io import StringIO
from unittest.mock import patch
from network_manager_provider.defaults import NAMESPACE
from network_manager_provider.codes import SUCCESS
from tests.support import (
    create_cli_action,
    flush_cli_action,
    list_cli_action,
    json_to_dict,
)


class TestCLINetworkNamespace(unittest.IsolatedAsyncioTestCase):

    def tearDown(self):
        flush_return_code = flush_cli_action(NAMESPACE)
        self.assertEqual(flush_return_code, SUCCESS)

    def test_list_namespaces(self):
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            list_return_code = list_cli_action(NAMESPACE)
            self.assertEqual(list_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIn("msg", output)
            self.assertIn("namespaces", output)
            self.assertIsInstance(output["namespaces"], list)

    @pytest.mark.privileged
    def test_create_namespace(self):
        namespace_name = "test_ns_create"
        # Create namespace
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_cli_action(NAMESPACE, namespace_name)
            self.assertEqual(create_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIn("msg", output)
            self.assertIn("status", output)
            self.assertEqual(output["status"], "success")

    @pytest.mark.privileged
    def test_list_after_create(self):
        namespace_name = "test_ns_list_after_create"

        # Ensure namespace exists
        create_cli_action(NAMESPACE, namespace_name)

        # List namespaces
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            list_return_code = list_cli_action(NAMESPACE)
            self.assertEqual(list_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIn("msg", output)
            self.assertIn("status", output)
            self.assertEqual(output["status"], "success")
            self.assertIn("namespaces", output)
            self.assertIsInstance(output["namespaces"], list)
            self.assertIn(namespace_name, output["namespaces"])
