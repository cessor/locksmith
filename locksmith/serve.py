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
from handlers import *
from model import Agents
from secret import Secret


define('debug', default=True)
define('loglevel', default='debug')
define('port', default=8888)
define('proxy_user', default='')
define('proxy_password', default='')
define('proxy_url', default='')


def pwd():
    return os.path.dirname(__file__)


def local(file):
    return os.path.join(pwd(), file)


def load_config_file():
    try:
        options.parse_config_file(local('config.cfg'), final=False)
    except Exception as e:
        logging.error(str(e))

    options.parse_command_line()


def configure():

    load_config_file()

    agents = dict(agents=Agents())

    proxy_ = proxy.initialize(
        options.proxy_url,
        options.proxy_user,
        options.proxy_password
    )

    routes = [
        url(r"/?", Home, agents),
        url(r"/login", Login, dict(secret=Secret())),
        url(r"/logout", Logout),
        url(r"/add", AddAgent, agents),
        url((r"/remove/([^/]*)"), RemoveAgent, agents),
        url((r"/toggle/([^/]*)"), ToggleAgent, agents),
        url((
            r"/auth/([^/]*)"),
            Authenticate,
            dict(agents=Agents(), proxy=proxy_)),
        url(
            r'/(favicon\.ico)',
            StaticFileHandler,
            dict(path=local('static'))
        )
    ]

    settings = dict(
        autoreaload=options.debug,
        compress_response=True,
        cookie_secret=os.urandom(64),
        debug=options.debug,
        logging=options.loglevel,
        login_url='/login',
        static_path=local('static'),
        template_path=local('templates'),
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
