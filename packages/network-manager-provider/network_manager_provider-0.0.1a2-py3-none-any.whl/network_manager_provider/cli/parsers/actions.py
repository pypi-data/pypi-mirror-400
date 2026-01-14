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

import argparse


class PositionalArgumentsAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, "positional_arguments") or not getattr(
            namespace, "positional_arguments"
        ):
            setattr(namespace, "positional_arguments", [values])
        else:
            getattr(namespace, "positional_arguments").append(values)


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        key_value_list = values.split(",")
        key_value_dict = {
            key_value.split("=")[0]: key_value.split("=")[1]
            for key_value in key_value_list
        }
        setattr(namespace, self.dest, key_value_dict)


class ListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, (list, set, tuple)):
            key_value_list = values
        elif isinstance(values, str):
            key_value_list = values.split(",")
        else:
            raise TypeError("values must be a list, set, tuple or string")
        setattr(namespace, self.dest, key_value_list)
