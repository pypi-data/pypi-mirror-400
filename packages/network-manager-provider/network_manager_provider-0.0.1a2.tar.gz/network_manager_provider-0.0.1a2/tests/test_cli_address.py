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
from network_manager_provider.defaults import ADDRESS, INTERFACE
from network_manager_provider.codes import SUCCESS
from tests.support import (
    assign_cli_action,
    create_cli_action,
    read_cli_action,
    delete_cli_action,
    flush_cli_action,
    json_to_dict,
)


class TestCLIAddress(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.seed = str(random.random())[6:10]
        self.base_name = "veth-test-"
        self.name = f"{self.base_name}{self.seed}"
        self.kind = "dummy"
        create_return_code = create_cli_action(INTERFACE, self.name, self.kind)
        self.assertEqual(create_return_code, SUCCESS)

    def tearDown(self):
        flush_regex = f"{self.base_name}.*"
        flush_return_code = flush_cli_action(INTERFACE, "--regex", flush_regex)
        self.assertEqual(flush_return_code, SUCCESS)

    def test_cli_address_assign(self):
        address = "127.0.254.2"
        link_name = self.name
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = assign_cli_action(ADDRESS, address, link_name)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            link = output.get("link")
            self.assertEqual(link, link_name)
            assigned_address = output.get("address")
            self.assertEqual(assigned_address, address)

    def test_cli_address_with_mask(self):
        mask = "24"
        address = f"127.0.254.2/{mask}"
        link_name = self.name
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = assign_cli_action(ADDRESS, address, link_name)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            link = output.get("link")
            self.assertEqual(link, link_name)
            assigned_address = output.get("address")
            self.assertEqual(assigned_address, address)
            assigned_mask = output.get("mask")
            self.assertEqual(assigned_mask, mask)

    def test_cli_address_with_mask_in_kwargs(self):
        mask = "24"
        address = "127.0.254.2"
        link_name = self.name
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = assign_cli_action(
                ADDRESS, address, link_name, "--kwargs", f"mask={mask}"
            )
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            link = output.get("link")
            self.assertEqual(link, link_name)
            assigned_address = output.get("address")
            self.assertEqual(assigned_address, address)
            assigned_mask = output.get("mask")
            self.assertEqual(assigned_mask, mask)

    def test_cli_address_read(self):
        address = "127.0.254.3"
        link_name = self.name
        assign_return_code = assign_cli_action(ADDRESS, address, link_name)
        self.assertEqual(assign_return_code, SUCCESS)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            read_return_code = read_cli_action(ADDRESS, link_name)
            self.assertEqual(read_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            link = output.get("link")
            self.assertIsInstance(link, dict)
            self.assertEqual(link.get("name"), link_name)
            self.assertEqual(link.get("address"), address)

    def test_cli_address_delete(self):
        address = "127.0.254.4/32"
        link_name = self.name
        assign_return_code = assign_cli_action(ADDRESS, address, link_name)
        self.assertEqual(assign_return_code, SUCCESS)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            delete_return_code = delete_cli_action(ADDRESS, address, link_name)
            self.assertEqual(delete_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("msg", output)
            self.assertIn("Deleted successfully address", output["msg"])
            link = output.get("link")
            self.assertEqual(link, link_name)
            deleted_address = output.get("address")
            self.assertEqual(deleted_address, address)
