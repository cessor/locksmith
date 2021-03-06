import logging
from tornado import gen
from tornado.web import RequestHandler, authenticated

from secret import Secret


USER_ID = 'USER_ID'


def fastauth(fn):
    return authenticated(gen.coroutine(fn))


class Authenticated(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(USER_ID)


class Private(Authenticated):
    def initialize(self, agents):
        self.agents = agents


class Home(Private):
    @fastauth
    def get(self):
        self.render("index.html", agents=self.agents)


class Login(RequestHandler):
    '''Make sure that the login handler is accessible'''
    def initialize(self, secret):
        self._secret = secret

    @gen.coroutine
    def get(self):
        self.render("login.html")

    @gen.coroutine
    def post(self):
        password = self.get_argument('password')
        if self._secret.verify(password):
            self.set_secure_cookie(USER_ID, USER_ID);
        self.redirect("/")


class Logout(RequestHandler):
    @gen.coroutine
    def get(self):
        self.clear_cookie(USER_ID)
        self.redirect("/")


class AddAgent(Private):
    @fastauth
    def post(self):
        name = self.get_argument("name", default='', strip=True)
        token = self.get_argument("token", default='', strip=True)
        if name and token:
            self.agents.add(name, token)

        self.redirect("/")


class ToggleAgent(Private):
    @fastauth
    def get(self, token):
        self.agents.toggle(token)
        self.redirect("/")


class RemoveAgent(Private):
    @fastauth
    def get(self, token):
        self.agents.remove(token)
        self.redirect("/")


class Authenticate(RequestHandler):
    def initialize(self, agents, proxy):
        self.agents = agents
        self._proxy = proxy

    @gen.coroutine
    def get(self, token):
        agent = self.agents.get(token)

        if not agent:
            # Not Found
            self.set_status(404)
            self.finish()
            return

        if not agent.active:
            # Forbidden
            self.set_status(403)
            self.finish()
            return

        try:
            cookies = self._proxy.login()
            self.finish(cookies)
            return

        except Exception as e:
            logging.info(e)
            # Expectation Failed
            self.set_status(417)
            self.finish()
