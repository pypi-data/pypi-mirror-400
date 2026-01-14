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
from network_manager_provider.route.ls import ls
from network_manager_provider.route.delete import delete


async def flush(to_regex, via=None, flush_kwargs=None, ip_route_init_kwargs=None):
    if not flush_kwargs:
        flush_kwargs = {}

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    response = {}
    list_success, list_response = await ls(
        to_regex=to_regex, ip_route_init_kwargs=ip_route_init_kwargs
    )

    if not list_success:
        response = {"msg": "Failed to find the routes that should be flushed"}
        return False, response

    response = {"results": []}
    delete_actions = []
    for route in list_response.get("routes", []):
        delete_actions.append(
            delete(
                route["to"],
                via=route["via"],
                delete_kwargs=flush_kwargs,
                ip_route_init_kwargs=ip_route_init_kwargs,
            )
        )
    for success, delete_response in await asyncio.gather(*delete_actions):
        response["results"].append(delete_response)
    return True, response
