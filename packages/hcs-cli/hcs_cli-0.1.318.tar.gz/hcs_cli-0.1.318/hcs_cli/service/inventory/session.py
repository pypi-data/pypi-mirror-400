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

from hcs_core.sglib.client_util import hdc_service_client
from hcs_core.util.query_util import with_query

_client = hdc_service_client("inventory")


def sessions(template_id: str, vm_id: str, org_id: str, **kwargs):
    url = f"/v1/{template_id}/{vm_id}/sessions"
    if org_id:
        url += "?org_id=" + org_id
    url = with_query(url, **kwargs)
    return _client.get(url)


def assign(payload):
    # https://horizonv2-sg.devframe.cp.horizon.omnissa.com/inventory/swagger-ui/#/Inventory/assign
    url = "/v1/assign"
    return _client.post(url, payload)


def assignV2(payload):
    # https://horizonv2-sg.devframe.cp.horizon.omnissa.com/inventory/swagger-ui/#/Inventory/assign
    url = "/v2/assign"
    return _client.post(url, payload)


def deassign(template_id: str, org_id: str, payload):
    # https://horizonv2-sg.devframe.cp.horizon.omnissa.com/inventory/swagger-ui/#/Inventory/deassign
    url = f"/v1/{template_id}/deassign?org_id={org_id}"
    return _client.post(url, payload)


def logoff(template_id: str, org_id: str, payload: dict):
    url = f"/v1/{template_id}/logoff?org_id={org_id}"
    return _client.post(url, payload)


def logoffV2(org_id: str, payload: dict):
    url = f"/v2/logoff?org_id={org_id}"
    return _client.post(url, payload)


def update_session(org_id: str, template_id: str, payload: dict):
    url = f"/v1/{template_id}/sessionUpdate?org_id={org_id}"
    return _client.post(url, payload)


def create_manual_session(org_id: str, template_id: str, edge_id: str, payload: dict):
    url = f"/v1/{template_id}/session?org_id={org_id}&edge_id={edge_id}"
    return _client.post(url, payload)
