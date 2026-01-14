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
from network_manager_provider.namespace.ls import ls
from network_manager_provider.namespace.delete import delete


async def flush(regex, flush_kwargs=None):
    if not flush_kwargs:
        flush_kwargs = {}

    response = {}
    delete_actions = []
    found, response = await ls(regex=regex)
    if not found:
        response["msg"] = "Failed to flush namespaces because listing failed"
        return False, response

    delete_actions = [delete(ns) for ns in response.get("namespaces", [])]
    response = {"results": []}
    for success, delete_response in await asyncio.gather(*delete_actions):
        response["results"].append(delete_response)
    return True, response
