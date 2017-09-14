# Copyright 2011 OpenStack Foundation.
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

import logging
from ldap3 import Connection
import os

from oslo_middleware.healthcheck import opts
from oslo_middleware.healthcheck import pluginbase

LOG = logging.getLogger(__name__)


class LdapBindHealthcheck(pluginbase.HealthcheckBaseExtension):
    """LdapBind healthcheck middleware plugin

    This plugin checks ability to bind to successfully to an ldap server.

    Example of middleware configuration:

    .. code-block:: ini

      [filter:healthcheck]
      paste.filter_factory = oslo_middleware:Healthcheck.factory
      path = /healthcheck
      backends = ldap_bind
      # set to True to enable detailed output, False is the default
      uri = ldap://some.host.com
      bind_dn = CN=some,DC=user,DC=name
      bind_password = som3s3kret
      detailed = False
    """

    def __init__(self, *args, **kwargs):
        super(LdapBindHealthcheck, self).__init__(*args, **kwargs)
        self.oslo_conf.register_opts(opts.LDAP_BIND_OPTS,
                                     group='healthcheck')

    def healthcheck(self, server_port):
        conf = self.oslo_conf.healthcheck
        connect_args = {
            'server': conf.uri,
            'user': conf.bind_dn,
            'password': conf.bind_password,
        }
        conn = Connection(**connect_args)
        try:
            if not conn.bind():
                raise Exception('Bind error')
        except Exception as e:
            details = e.message if hasattr(e, 'message') else ' '.join(e.args)
            return pluginbase.HealthcheckResult(available=False,
                                                reason="Ldap bind failed.",
                                                details=details)
        conn.unbind()
        if not conn.closed:
            LOG.warning('LdapBind healthcheck middleware'
                        ' failed to unbind cleanly. Lingering socket exists.')

        return pluginbase.HealthcheckResult(available=True,
                                            reason="OK")
