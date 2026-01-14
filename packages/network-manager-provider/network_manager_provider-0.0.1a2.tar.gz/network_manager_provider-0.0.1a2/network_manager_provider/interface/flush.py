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
from network_manager_provider.interface.ls import ls
from network_manager_provider.interface.delete import delete


async def flush(regex=None, flush_kwargs=None, ip_route_init_kwargs=None):
    if not flush_kwargs:
        flush_kwargs = {}

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    list_success, list_response = await ls(
        regex=regex, ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not list_success:
        return False, list_response

    response = {"results": []}
    delete_actions = []
    for interface in list_response.get("links", []):
        delete_actions.append(delete(interface, delete_kwargs=flush_kwargs))
    for success, delete_response in await asyncio.gather(*delete_actions):
        response["results"].append(delete_response)
    return True, response
