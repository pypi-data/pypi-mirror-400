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
from network_manager_provider.defaults import INTERFACE, BRIDGE
from network_manager_provider.codes import SUCCESS
from tests.support import (
    create_cli_action,
    read_cli_action,
    update_cli_action,
    delete_cli_action,
    flush_cli_action,
    list_cli_action,
    json_to_dict,
)


class TestCLIInterface(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.seed = str(random.random())[6:10]
        self.base_name = "veth-test-"
        self.name = f"{self.base_name}{self.seed}"
        self.kind = "dummy"

    def tearDown(self):
        flush_regex = f"{self.base_name}.*"
        flush_return_code = flush_cli_action(INTERFACE, "--regex", flush_regex)
        self.assertEqual(flush_return_code, SUCCESS)

    def test_cli_interface_create(self):
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_cli_action(INTERFACE, self.name, self.kind)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_interface_read(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(INTERFACE, self.name)
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_interface_read_mtu(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            args = ["mtu"]
            read_return_code = read_cli_action(INTERFACE, self.name, "--args", args)
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("link", output)
            self.assertIn("name", output["link"])
            self.assertEqual(output["link"]["name"], self.name)
            self.assertIn("mtu", output["link"])
            self.assertIsInstance(output["link"]["mtu"], int)
            self.assertEqual(output["link"]["mtu"], 1500)

    def test_cli_interface_update(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            update_return_code = update_cli_action(INTERFACE, self.name)
            self.assertEqual(update_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("msg", output)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(INTERFACE, self.name)
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("link", output)
            self.assertIn("name", output["link"])
            self.assertEqual(output["link"]["name"], self.name)

    def test_cli_interface_update_mtu(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        kwargs = "mtu=1400"
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            update_return_code = update_cli_action(
                INTERFACE, self.name, "--args", kwargs
            )
            self.assertEqual(update_return_code, SUCCESS)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(INTERFACE, self.name, "--args", "mtu")
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("link", output)
            self.assertIn("mtu", output["link"])
            self.assertEqual(output["link"]["mtu"], 1400)

    def test_cli_interface_update_set_status(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(INTERFACE, self.name, "--args", "state")
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("link", output)
            self.assertIn("state", output["link"])
            self.assertEqual(output["link"]["state"], "down")

        kwargs = "state=up"
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            update_return_code = update_cli_action(
                INTERFACE, self.name, "--args", kwargs
            )
            self.assertEqual(update_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("msg", output)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(
                INTERFACE, self.name, "--args", "operstate"
            )
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("link", output)
            self.assertIn("operstate", output["link"])
            # https://serverfault.com/questions/629676/dummy-network-interface-in-linux
            # The dummy driver does only implement a subset of the network device features.
            # As such, the operstate may remain UNKNOWN even when the interface is set to up
            self.assertEqual(output["link"]["operstate"], "UNKNOWN" or "UP")

    def test_cli_interface_delete(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            delete_return_code = delete_cli_action(INTERFACE, self.name)
            self.assertEqual(delete_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)

    def test_cli_interface_ls(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            ls_return_code = list_cli_action(INTERFACE)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("links", output)
            self.assertIsInstance(output["links"], list)
            expected_entry = {"name": self.name, "type": self.kind}
            self.assertIn(expected_entry, output["links"])

    def test_cli_interface_ls_regex(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            regex = f"{self.base_name}.*"
            ls_return_code = list_cli_action(INTERFACE, "--regex", regex)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("links", output)
            self.assertIsInstance(output["links"], list)
            expected_entry = {"name": self.name, "type": self.kind}
            self.assertIn(expected_entry, output["links"])

    def test_cli_interface_ls_types(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            ls_return_code = list_cli_action(INTERFACE, "--types", self.kind)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("links", output)
            self.assertIsInstance(output["links"], list)
            expected_entry = {"name": self.name, "type": self.kind}
            self.assertIn(expected_entry, output["links"])
            returned_types = [entry["type"] for entry in output["links"]]
            for returned_type in returned_types:
                self.assertEqual(returned_type, self.kind)

    def test_cli_interface_ls_bridge_type(self):
        create_return_code = create_cli_action(INTERFACE, self.name, BRIDGE)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            ls_return_code = list_cli_action(INTERFACE, "--types", BRIDGE)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("links", output)
            self.assertIsInstance(output["links"], list)
            self.assertNotIn(self.name, output["links"])
            expected_entry = {"name": self.name, "type": BRIDGE}
            self.assertIn(expected_entry, output["links"])
            returned_types = [entry["type"] for entry in output["links"]]
            for returned_type in returned_types:
                self.assertEqual(returned_type, BRIDGE)

    def test_cli_interface_flush(self):
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            flush_regex = f"{self.base_name}.*"
            flush_return_code = flush_cli_action(INTERFACE, "--regex", flush_regex)
            self.assertEqual(flush_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("results", output)
            self.assertIsInstance(output["results"], list)
            self.assertGreaterEqual(len(output["results"]), 1)
            self.assertIsInstance(output["results"][0], dict)
            self.assertIn("msg", output["results"][0])
