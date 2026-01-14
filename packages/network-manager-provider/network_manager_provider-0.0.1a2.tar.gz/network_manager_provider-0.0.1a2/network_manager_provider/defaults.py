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

import os

# Package name
PACKAGE_NAME = "network_manager_provider"

ASSIGN = "assign"
CREATE = "create"
READ = "read"
UPDATE = "update"
DELETE = "delete"
DUMP = "dump"
LS = "ls"
FLUSH = "flush"
APPLY = "apply"
UNDO = "undo"

BRIDGE = "bridge"
HOST = "host"

ADDRESS = "address"
ADDRESS_OPERATIONS = [ASSIGN, READ, DELETE]
ADDRESS_CLI = {ADDRESS: ADDRESS_OPERATIONS}

BUNDLE = "bundle"
BUNDLE_OPERATIONS = [CREATE, READ, UPDATE, DELETE, LS, FLUSH, APPLY, UNDO]
BUNDLE_CLI = {BUNDLE: BUNDLE_OPERATIONS}

INTERFACE = "interface"

INTERFACE_OPERATIONS = [CREATE, READ, UPDATE, DELETE, LS, FLUSH]
INTERFACE_CLI = {INTERFACE: INTERFACE_OPERATIONS}

NAMESPACE = "namespace"
NAMESPACE_OPERATIONS = [CREATE, READ, UPDATE, DELETE, LS, FLUSH]
NAMESPACE_CLI = {NAMESPACE: NAMESPACE_OPERATIONS}

ROUTE = "route"
ROUTE_OPERATIONS = [CREATE, DELETE, LS, FLUSH]
ROUTE_CLI = {ROUTE: ROUTE_OPERATIONS}

NETWORK_MANAGER_PROVIDER_CLI_STRUCTURE = [
    ADDRESS_CLI,
    BUNDLE_CLI,
    INTERFACE_CLI,
    NAMESPACE_CLI,
    ROUTE_CLI,
]

PERSISTENCE = "persistence"

# Default state directory
default_base_path = os.path.join(os.path.expanduser("~"), ".{}".format(PACKAGE_NAME))

# Default persistence directory
default_persistence_path = os.path.join(default_base_path, PERSISTENCE)
