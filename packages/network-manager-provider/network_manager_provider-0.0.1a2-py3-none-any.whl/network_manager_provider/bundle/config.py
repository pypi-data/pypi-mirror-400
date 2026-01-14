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

from jinja2.nativetypes import NativeEnvironment
from network_manager_provider.defaults import INTERFACE, BRIDGE, ROUTE
from network_manager_provider.interface.read import read as link_read


def get_lookup_variables(bundle_config):
    return bundle_config.get("lookup_variables", {})


def validate_variable_lookup(variable_lookup, lookup_type=INTERFACE):
    if "name" not in variable_lookup:
        return False, f"{lookup_type} lookup must contain 'name' field"
    if "attribute" not in variable_lookup:
        return False, f"{lookup_type} lookup must contain 'attribute' field"
    return True, None


async def retrieve_link_attribute(name, attribute):
    success, response = await link_read(name, read_args=[attribute])
    if not success:
        return False, response.get("msg", "Failed to read link for variable lookup")
    link = response.get("link", {})
    if attribute not in link:
        return False, f"Attribute '{attribute}' not found on link '{name}'"
    return True, link[attribute]


async def retrieve_variable_value(name, attribute, lookup_type=INTERFACE):
    if lookup_type == INTERFACE or lookup_type == BRIDGE:
        return await retrieve_link_attribute(name, attribute)
    return False, f"Unsupported lookup type: {lookup_type}"


async def prepare_lookup_variables(variables_lookups, lookup_type=INTERFACE):
    if lookup_type not in [INTERFACE, BRIDGE]:
        return False, f"Unsupported lookup type: {lookup_type}"

    prepared_variables = {}
    for variables_lookup in variables_lookups:
        is_valid, validation_msg = validate_variable_lookup(
            variables_lookup, lookup_type=lookup_type
        )
        if not is_valid:
            return False, validation_msg
        retrieved_success, retrieved_value = await retrieve_variable_value(
            variables_lookup["name"],
            variables_lookup["attribute"],
            lookup_type=lookup_type,
        )
        if not retrieved_success:
            return False, retrieved_value
        lookup_dict = {
            variables_lookup["name"]: {variables_lookup["attribute"]: retrieved_value}
        }
        prepared_variables.update(lookup_dict)
    return True, prepared_variables


async def recursively_format(template_vars, config):
    output_dict = {}
    # TODO, augment to support recursive templating
    if isinstance(config, list):
        templated_list = []
        for _config in config:
            templated_list.append(await recursively_format(template_vars, _config))
        return templated_list
    elif isinstance(config, dict):
        for key, value in config.items():
            output_dict[key] = await recursively_format(template_vars, value)
    elif isinstance(config, str):
        # Converts to the native python data type when rendering
        environment = NativeEnvironment()
        template = environment.from_string(config)
        return template.render(template_vars)
    elif isinstance(config, (int, float, bytes)):
        return config
    return output_dict
