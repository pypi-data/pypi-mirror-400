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

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import admin, inventory, lcm
from hcs_cli.support.param_util import parse_vm_path


@click.command()
@cli.org_id
@click.argument("vm_path", type=str, required=False)
def logoff(org: str, vm_path: str):
    """Logoff all sessions on the vm.

    Example: hcs inventory logoff template_id/vm_id
    """

    org_id = cli.get_org_id(org)
    template_id, vm_id = parse_vm_path(vm_path)
    sessions = inventory.sessions(template_id, vm_id, cli.get_org_id(org))
    if not sessions:
        return
    # [
    #     {
    #         "templateId": null,
    #         "vmId": "expool000",
    #         "userId": "c12b884b-c813-4f73-81f5-df2052de9bc6",
    #         "agentSessionGuid": null,
    #         "agentSessionId": null,
    #         "agentStaticSessionGuid": null,
    #         "sessionType": "DESKTOP",
    #         "templateType": "FLOATING",
    #         "clientId": null,
    #         "sessionStatus": "ASSIGNED",
    #         "lastAssignedTime": "2025-12-16T18:55:45.078+00:00",
    #         "lastLoginTime": null,
    #         "lastStatusUpdateTime": "2025-12-16T18:55:45.078+00:00",
    #         "username": "u1ad1",
    #         "userPrincipalName": "u1ad1@horizonv2dev2.local",
    #         "userSid": "S-1-5-21-1840667356-2516272024-4034330832-1104",
    #         "releaseSessionOnDeassign": false,
    #         "entitlementId": "6941a2bfe79a1b9cef167ad2",
    #         "orgId": "7c4f9042-6119-45b6-93f5-24f1a80e2c62",
    #         "location": null,
    #         "clientSessionId": null,
    #         "agentErrorCode": "",
    #         "staticCloudSessionId": "dc907d57-85d8-478e-9d0c-028c1acd87f2",
    #         "hibernated": null,
    #         "id": null,
    #         "dspecId": "5722ff4a-7e75-4248-89e9-741d8a7ae91c"
    #     }
    # ]

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
        logoff_payload_v1 = {
            "edgeDeploymentId": edge_deployment_id,
            "vmId": vm_id,
            "userId": session.get("userId"),
            "entitlementId": session.get("entitlementId"),
            "vmHubName": template["hdc"]["vmHub"]["name"],
            "sessionType": session.get("sessionType"),
        }
        ret1 = inventory.logoff(template_id=template_id, org_id=org_id, payload=logoff_payload_v1)
        # print("PAYLOADv1: ", logoff_payload_v1)
        # print("RETv1: ", ret1)
        all_ret.append(ret1)

        logoff_payload_v2 = [
            {
                "agentSessionGuid": session.get("agentSessionGuid"),
                "userId": session.get("userId"),
                "sessionType": session.get("sessionType"),
                "vmHubName": template["hdc"]["vmHub"]["name"],
                "edgeDeploymentId": edge_deployment_id,
                "vmId": vm_id,
                "dspecId": session.get("dspecId"),
                "dtemplateId": template_id,
            }
        ]
        ret2 = inventory.logoffV2(org_id=org_id, payload=logoff_payload_v2)
        # print("PAYLOADv2: ", logoff_payload_v2)
        # print("RETv2: ", ret2)
        all_ret.append(ret2)

    return all_ret
