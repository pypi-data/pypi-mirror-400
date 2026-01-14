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

import re
from network_manager_provider.storage.dictdatabase import DictDatabase
from network_manager_provider.defaults import BUNDLE


async def ls(regex=None, directory=None):
    response = {}
    bundle_db = DictDatabase(BUNDLE, directory=directory)
    if not await bundle_db.exists():
        if not await bundle_db.touch():
            response["msg"] = (
                "The bundle database: {} did not exist in directory: {}, and it could not be created.".format(
                    bundle_db.name, directory
                )
            )
            return False, response

    bundles = await bundle_db.items()
    if not bundles:
        response["bundles"] = []
        response["msg"] = "No bundles found"
        return True, response
    bundles = [name for name in bundles.keys()]

    if regex:
        bundles = [name for name in bundles if re.match(regex, name)]

    response["bundles"] = bundles
    response["msg"] = "Found bundles"
    return True, response
