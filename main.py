#!/usr/bin/env python
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
from six.moves import SimpleHTTPServer  # noqa
from six.moves import socketserver
import webob

from oslo_middleware import healthcheck
from oslo_config import cfg

import logging
import sys
import pdb

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOG = logging.getLogger(__name__)

def _create_handler(conf):
    class HttpHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        _conf = conf

        def do_GET(self):
            @webob.dec.wsgify
            def dummy_application(req):
                return 'test'

            app = healthcheck.Healthcheck(dummy_application, conf)
            req = webob.Request.blank("/healthcheck", accept='application/json',
                                    method='GET')
            res = req.get_response(app)
            self.send_response(res.status_code)
            for header_name, header_value in res.headerlist:
                self.send_header(header_name, header_value)
            self.end_headers()
            self.wfile.write(res.body)
            self.wfile.close()

    return HttpHandler

def create_server(conf):
    handler = _create_handler(conf)
    handler._conf.log_opt_values(lvl=logging.DEBUG, logger=LOG)
    server = socketserver.TCPServer(("", conf.port), handler)
    return server


def _configure_opts():
    conf = cfg.ConfigOpts()
    default_opts = [
            cfg.IntOpt('port',
                       default=8000,
                       help='Port to listen on.')
    ]

    conf.register_opts(default_opts)
    conf.register_cli_opts(default_opts)
    conf.register_opts(healthcheck.opts.HEALTHCHECK_OPTS, group='healthcheck')
    return conf

def main(args=None):
    """Runs a basic http server to show healthcheck functionality."""
    conf = _configure_opts()
    conf(args)

    server = create_server(conf)
    print("Serving at port: %s" % server.server_address[1])
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])

