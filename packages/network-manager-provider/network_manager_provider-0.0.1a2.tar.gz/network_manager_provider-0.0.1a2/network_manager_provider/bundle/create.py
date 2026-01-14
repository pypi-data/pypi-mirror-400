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

from network_manager_provider.defaults import BUNDLE
from network_manager_provider.utils.config import load_config
from network_manager_provider.storage.dictdatabase import DictDatabase


async def create(name, config=None, directory=None):
    response = {}

    if not config:
        config = {}

    config_file = None
    if isinstance(config, str):
        config_file = config

    bundle_db = DictDatabase(BUNDLE, directory=directory)
    if not await bundle_db.exists():
        if not await bundle_db.touch():
            response["msg"] = (
                "The Bundle database: {} did not exist in directory: {}, and it could not be created.".format(
                    bundle_db.name, directory
                )
            )
            return False, response

    bundle = {"name": name, "config": {}}
    # Load the bundle configuration file
    if config_file:
        bundle_config = await load_config(config_file)
        if not bundle_config:
            response["msg"] = (
                "Failed to load the Bundle configuration file: {}.".format(config_file)
            )
            return False, response
    else:
        bundle_config = config
    bundle["config"] = bundle_config

    bundle_id = await bundle_db.add(bundle)
    if not bundle_id:
        response["msg"] = (
            "Failed to save the Bundle information to the database: {}".format(
                bundle_db.name
            )
        )
        return False, response

    response["id"] = bundle_id
    response["bundle"] = bundle
    response["msg"] = "Created Bundle succesfully."
    return True, response
