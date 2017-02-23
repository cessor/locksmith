'''
    This module helps to provide a remote login to agents.
'''
import logging
import os
import requests


class ProxyConfigurationIncomplete(Exception):
    pass


class NotLoggedIn(Exception):
    pass


class Proxy(object):
    '''
    Logs in a user at the given proxy url and returns the pickled
    session cookies, so that these cookies can be used by an external agent.

    Note: As of now, I have no idea, if this works [JH, Feb 2017]

    Parameters
    ----------
    session: A session. Ideally, this is <requests.Session>
    proxy_url: The url to the proxies login form
    username, password: Proxy server credentials
    logger: A logger object that can provide info if something goes wrong.
    '''
    def __init__(self, session, proxy_url, username, password, logger):
        self._session = session
        self._proxy_url = proxy_url
        self._username = username
        self._password = password
        self._logger = logger

    def _pickled_cookie_jar(self, session):
        '''Encodes the cookie jar, to be depickled later.'''
        return str(Cookies(session))

    def _submit_login_form(self, session):
        '''Get cookies by posting your credentials to the proxy landing page'''
        response = session.post(
            self._proxy_url,
            data={
                'user': self._username,
                'pass': self._password
            }
        )
        return response

    def login(self):
        '''Returns the login cookies obtained by logging in at the proxy server. Raises an exception if this didn't work. '''
        session = self._session()
        response = self._submit_login_form(session)
        self._logger.info(response)

        if not response.status_code == 200:
            self._logger.info('Could not log in.')
            raise NotLoggedIn()

        return self._pickled_cookie_jar(session)


def configuration():
    '''Reads in the configuration for the proxy from the environment.
    This could be more modular.'''
    PROXY_URL = 'PROXY_URL'
    USERNAME = 'PROXY_USER'
    PASSWORD = 'PROXY_PASSWORD'

    proxy_url = os.environ.get(PROXY_URL)
    username = os.environ.get(USERNAME)
    password = os.environ.get(PASSWORD)

    if not all([username, password, proxy_url]):
        raise ProxyConfigurationIncomplete()

    return proxy_url, username, password


def initialize(logger):
    proxy_url, username, password = configuration()

    proxy = Proxy(
        session=requests.Session,
        proxy_url=proxy_url,
        username=username,
        password=password,
        logger=logger)
    return proxy