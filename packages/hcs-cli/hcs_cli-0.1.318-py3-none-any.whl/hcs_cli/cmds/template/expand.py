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
import hcs_core.util.duration as duration
from hcs_core.ctxp import recent

import hcs_cli.service.admin as admin


@click.command(hidden=True)
@click.option(
    "--number",
    "-n",
    type=int,
    required=False,
    default=1,
    help="Number of VMs to expand. Use negative number to shrink.",
)
@click.argument("template_id", type=str, required=False)
@cli.org_id
@cli.wait
def expand(number: int, template_id: str, org: str, wait: str, **kwargs):
    """Update an existing template"""

    org_id = cli.get_org_id(org)

    template_id = recent.require("template", template_id)
    template = admin.template.get(template_id, org_id)

    if not template:
        return "Template not found: " + template_id

    spare_policy = template.get("sparePolicy", {})
    patch = {
        "sparePolicy": {
            "min": spare_policy.get("min", 0) + number,
            "max": spare_policy.get("max", 0) + number,
            "limit": spare_policy.get("limit", 0) + number,
        }
    }
    if patch["sparePolicy"]["min"] < 0:
        patch["sparePolicy"]["min"] = 0
    if patch["sparePolicy"]["max"] < 0:
        patch["sparePolicy"]["max"] = 0
    if patch["sparePolicy"]["limit"] < 0:
        patch["sparePolicy"]["limit"] = 0

    ret = admin.template.update(template_id, org_id, patch)
    if wait != "0":
        ret = admin.template.wait_for_ready(template_id, org_id, duration.to_seconds(wait))
    return ret
