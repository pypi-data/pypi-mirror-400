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

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import admin, inventory, lcm
from hcs_cli.support.param_util import parse_vm_path


@click.command()
@cli.org_id
@click.argument("vm_path", type=str, required=False)
def deassign(org: str, vm_path: str):
    """Assign user to VM"""
    org_id = cli.get_org_id(org)
    template_id, vm_id = parse_vm_path(vm_path)
    sessions = inventory.sessions(template_id, vm_id, cli.get_org_id(org))

    template = admin.template.get(template_id, cli.get_org_id(org))
    if template:
        edge_deployment_id = template["edgeDeploymentId"]
    else:
        # try with lcm
        template = lcm.template.get(template_id, cli.get_org_id(org))
        if not template:
            return "Template not found: " + template_id, 1
        edge_deployment_id = template["edgeGateway"]["id"]

    all_ret = []
    for session in sessions:
        payload = {
            "vmHubName": template["hdc"]["vmHub"]["name"],
            "edgeDeploymentId": edge_deployment_id,
            "vmId": vm_id,
            "entitlementId": session.get("entitlementId"),
            "agentSessionGuid": session.get("agentSessionGuid"),
            "agentSessionId": session.get("agentSessionId"),
            "agentStaticSessionGuid": session.get("agentStaticSessionGuid"),
            "id": session.get("dspecId"),
            "userId": session.get("userId"),
            "type": session.get("sessionType"),
        }
        ret = inventory.deassign(template_id=template_id, org_id=org_id, payload=payload)
        all_ret.append(ret)

    if len(all_ret) == 1:
        return all_ret[0]
    return all_ret
