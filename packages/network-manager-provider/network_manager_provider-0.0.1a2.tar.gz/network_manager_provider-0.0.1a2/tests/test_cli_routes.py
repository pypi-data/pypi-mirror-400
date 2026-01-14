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
import random
from io import StringIO
from unittest.mock import patch
from network_manager_provider.defaults import ROUTE
from network_manager_provider.codes import SUCCESS
from tests.support import (
    create_cli_action,
    delete_cli_action,
    flush_cli_action,
    list_cli_action,
    json_to_dict,
)


class TestCLIroute(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.seed = str(random.random())[6:10]
        self.base_cidr = "127.0.254"
        self.subnet = "24"
        self.to = f"{self.base_cidr}.0/{self.subnet}"
        self.via = "127.0.254.1"

    def tearDown(self):
        flush_regex = f"{self.base_cidr}.*/{self.subnet}"
        flush_return_code = flush_cli_action(ROUTE, flush_regex)
        self.assertEqual(flush_return_code, SUCCESS)

    def test_cli_route_create(self):
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_cli_action(ROUTE, self.to, self.via)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_route_delete(self):
        create_return_code = create_cli_action(ROUTE, self.to, self.via)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            delete_return_code = delete_cli_action(ROUTE, self.to, self.via)
            self.assertEqual(delete_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_route_flush(self):
        create_return_code = create_cli_action(ROUTE, self.to, self.via)
        self.assertEqual(create_return_code, SUCCESS)

        flush_regex = f"{self.base_cidr}.*/{self.subnet}"
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            flush_return_code = flush_cli_action(ROUTE, flush_regex)
            self.assertEqual(flush_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("results", output)
            self.assertIsInstance(output["results"], list)
            self.assertGreaterEqual(len(output["results"]), 1)
            self.assertIsInstance(output["results"][0], dict)
            self.assertIn("msg", output["results"][0])

    def test_cli_route_ls(self):
        create_return_code = create_cli_action(ROUTE, self.to, self.via)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = list_cli_action(ROUTE)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("routes", output)
            self.assertIsInstance(output["routes"], list)
            self.assertGreaterEqual(len(output["routes"]), 1)
            self.assertIsInstance(output["routes"][0], dict)
            found_route = [
                route
                for route in output["routes"]
                if route["to"] == self.to and route["via"] == self.via
            ]
            self.assertEqual(len(found_route), 1)
