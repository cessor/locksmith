'''
    This module helps to provide a remote login to agents.
'''
import logging
import os
import requests
from cookiejar import Cookies


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
        cookies = str(Cookies(session))
        self._logger.debug(cookies)
        return cookies

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
        self._logger.debug(response.content)
        self._logger.debug(session.cookies)
        return self._pickled_cookie_jar(session)


def initialize(proxy_url, username, password, logger):

    if not all([proxy_url, username, password]):
        raise ProxyConfigurationIncomplete()

    proxy = Proxy(
        session=requests.Session,
        proxy_url=proxy_url,
        username=username,
        password=password,
        logger=logger)
    return proxy
