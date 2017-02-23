import os
import base64


FILE = '.secret'
LENGTH = 128


class Secret(object):
    def __init__(self):
        self.secret = None

    def random_string(self):
        return base64.b64encode(os.urandom(128)).decode('ascii')

    def generate(self):
        with open(FILE, 'w') as file:
            secret = self.random_string()
            file.write(secret)

    def read(self):
        with open(FILE) as f:
            return f.read().strip()

    def verify(self, other):
        self.secret = self.secret or self.read()
        return other == self.secret