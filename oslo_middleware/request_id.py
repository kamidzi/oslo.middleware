# Copyright (c) 2013 NEC Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_context import context
import webob.dec

from oslo_middleware import base


ENV_REQUEST_ID = 'openstack.request_id'
HTTP_RESP_HEADER_REQUEST_ID = 'x-openstack-request-id'


class RequestId(base.ConfigurableMiddleware):
    """Middleware that ensures request ID.

    It ensures to assign request ID for each API request and set it to
    request environment. The request ID is also added to API response.
    """

    # if compat_headers is set, we also return the request_id in those
    # headers as well. This allows projects like Nova to adopt
    # oslo.middleware without impacting existing users.
    compat_headers = []

    @webob.dec.wsgify
    def __call__(self, req):
        req_id = context.generate_request_id()
        req.environ[ENV_REQUEST_ID] = req_id
        response = req.get_response(self.application)

        return_headers = [HTTP_RESP_HEADER_REQUEST_ID]
        return_headers.extend(self.compat_headers)

        for header in return_headers:
            if header not in response.headers:
                response.headers.add(header, req_id)
        return response
