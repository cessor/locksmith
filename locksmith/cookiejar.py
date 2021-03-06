import pickle
import base64


class EmptyCookieJar(Exception):
    pass


class Cookies(object):
    def __init__(self, session):
        self._session = session

    def __str__(self):
        '''Returns the session's cookie jar as a string'''
        if not self._session.cookies:
            raise EmptyCookieJar()
        jar = self._session.cookies.copy()
        bytes = pickle.dumps(jar)
        string = base64.b64encode(bytes)
        string = string.decode('ascii')
        return string

    @classmethod
    def load_jar(self, string):
        '''Makes a jar from a base64 encoded, pickled cookie string'''
        bytes = base64.b64decode(string)
        jar = pickle.loads(bytes)
        return jar