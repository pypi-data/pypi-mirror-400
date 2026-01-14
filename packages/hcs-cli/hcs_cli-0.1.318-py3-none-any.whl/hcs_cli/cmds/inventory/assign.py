"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import sys
import uuid

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import admin, auth, inventory, lcm, portal
from hcs_cli.support.param_util import parse_vm_path


@click.command()
@cli.org_id
@click.argument("vm_path", type=str, required=False)
def assign(org: str, vm_path: str):
    """Assign user to VM"""
    org_id = cli.get_org_id(org)
    template_id, vm_id = parse_vm_path(vm_path)

    template = admin.template.get(template_id, org_id)
    if template:
        edge_id = template["edgeDeploymentId"]
    else:
        # try with lcm
        template = lcm.template.get(template_id, org_id)
        edge_id = template["edgeGateway"]["id"]
    if not template:
        return "Template not found: " + template_id, 1
    payload = {
        "id": "dspec1",
        "userId": "user1",
        "clientId": "client-1",
        "entitlementId": "entitlement-1",
        "templateIds": [template_id],
        "allocationPolicy": "ANY",
        "sessionType": "DESKTOP",
        "username": "user1",
        "userPrincipalName": "aduser1@vmwhorizon.com",
        "userSid": "S-1-5-21-2502306595",
        "orgId": org_id,
        "location": template["location"],
        "vmId": vm_id,
        "templateType": template["templateType"],
        "resume": True,
        "clientSessionId": "client-uuid-1",
    }
    # print(json.dumps(payload, indent=4))
    inventory.assignV2(payload)

    # payload_manual_session = {
    #     "templateId": "string",
    #     "vmId": "string",
    #     "userId": "string",
    #     "agentSessionGuid": "string",
    #     "agentSessionId": "string",
    #     "agentStaticSessionGuid": "string",
    #     "sessionType": "DESKTOP",
    #     "templateType": "FLOATING",
    #     "clientId": "string",
    #     "sessionStatus": "string",
    #     "lastAssignedTime": "2025-12-16T20:56:08.988Z",
    #     "lastLoginTime": "2025-12-16T20:56:08.988Z",
    #     "lastStatusUpdateTime": "2025-12-16T20:56:08.988Z",
    #     "username": "string",
    #     "userPrincipalName": "string",
    #     "userSid": "string",
    #     "entitlementId": "string",
    #     "orgId": "string",
    #     "location": "string",
    #     "clientSessionId": "UUID string",
    #     "agentErrorCode": "AGENT_ERR_FAILURE",
    #     "staticCloudSessionId": "UUID string",
    #     "hibernated": true,
    #     "id": 0,
    #     "dspecId": "string"
    # }
    payload_update = {
        "id": "dspec1",
        "agentSessionGuid": "agent-session-guid-1",
        "agentSessionId": "agent-session-1",
        "agentStaticSessionGuid": "agent-static-session-guid-1",
        "sessionStatus": "string",
        "vmId": vm_id,
        "edgeId": edge_id,
        "agentErrorCode": "",
    }
    return inventory.update_session(org_id=org_id, template_id=template_id, payload=payload_update)


@click.command()
@cli.org_id
@click.option("-pg", "--pool-group", type=str, required=True)
@click.option("-p", "--pool", type=str, required=True)
@click.option("-n", "--num-users", type=str, required=True)
def bulk_assign(org: str, pool_group: str, pool: str, num_users: int):
    """Assign  multiple users to VMs"""
    org_id = cli.get_org_id(org)
    pg = portal.pool.get(pool_group, org_id)
    payload = {
        "id": "",
        "userId": "",
        "entitlementId": pool_group,
        "templateIds": [pool],
        "allocationPolicy": "ANY",
        "sessionType": "DESKTOP",
        "username": "",
        "userPrincipalName": "",
        "userSid": "",
        "orgId": org_id,
        "location": "US",
        "templateType": pg["templateType"],
        "resume": True,
    }
    users = auth.admin.search.users(org_id, {}, -1)

    num_users = int(num_users)
    if num_users > len(users["users"]):
        print(f'max available users in AD = {len(users["users"])}, set -n less than {len(users["users"])}')
        return
    fu = users["users"][:num_users]
    dspecs = []
    for user in fu:
        payload["id"] = str(uuid.uuid4())
        payload["userId"] = user["id"]
        payload["username"] = user["userName"]
        payload["userPrincipalName"] = user["userPrincipalName"]
        payload["userSid"] = user["userSid"]
        inventory.session.assignV2(payload)
        dspecs.append(payload["id"])
    print(f"created following dspecs - {dspecs}")
