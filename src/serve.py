import logging
import os
import re
import ssl

from tornado import gen
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, StaticFileHandler, url

import proxy
from model import Agents
from secret import Secret
from handlers import *


define('debug', default=True)
define('loglevel', default='debug')
define('port', default=8888)
define('proxy_user', default='')
define('proxy_password', default='')
define('proxy_url', default='')


def directory(path):
    return os.path.join(os.path.dirname(__file__), path)


def configure():
    # Read config file
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(path, 'config.cfg')
        options.parse_config_file(config_file, final=False)
    except Exception as e:
        logging.error(str(e))

    options.parse_command_line()

    agents = dict(agents=Agents())
    proxy = create_proxy(options)

    routes = [
        url(r"/?", Home, agents),
        url(r"/login", Login, dict(secret=Secret())),
        url(r"/logout", Logout),
        url(r"/add", AddAgent, agents),
        url((r"/remove/([^/]*)"), RemoveAgent, agents),
        url((r"/toggle/([^/]*)"), ToggleAgent, agents),
        url((
            r"/auth/([^/]*)"),
            Auth,
            dict(
                agents=Agents(),
                proxy=proxy.initialize(
                    options.proxy_url,
                    options.proxy_user,
                    options.proxy_password,
                    logger
                )
            )),
        url(
            r'/(favicon\.ico)',
            StaticFileHandler,
            dict(path=directory('static'))
        )
    ]

    settings = dict(
        autoreaload=True,
        compress_response=True,
        cookie_secret=os.urandom(64),
        debug=options.debug,
        logging=options.loglevel,
        login_url='/login',
        static_path=directory('static'),
        template_path=directory('templates'),
        xheaders=True,
        xsrf_cookies=True,
    )
    return Application(routes, **settings)


def main():
    # Generate one
    secret = Secret()
    secret.generate()

    # Run app
    app = configure()
    server = HTTPServer(app, xheaders=True)
    server.listen(port=options.port)

    logging.info(secret.read())
    logging.info('Running on port %s' % options.port)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
