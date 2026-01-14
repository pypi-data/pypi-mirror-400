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
from network_manager_provider.storage.dictdatabase import DictDatabase


async def read(bundle_id, directory=None):
    response = {}

    bundle_db = DictDatabase(BUNDLE, directory=directory)
    if not await bundle_db.exists():
        response["msg"] = "The Bundle database {} does not exist.".format(
            bundle_db.name
        )
        return False, response

    bundle = await bundle_db.get(bundle_id)
    if not bundle:
        response["msg"] = "The Bundle {} does not exist in the database.".format(
            bundle_id
        )
        return False, response

    response["id"] = bundle_id
    response["bundle"] = bundle
    response["msg"] = "Bundle details."
    return True, response
