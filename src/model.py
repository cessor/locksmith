import uuid
import sqlite3


class Agent(object):
    def __init__(self, token, name, active):
        self.token = token
        self.name = name
        self.active = active


DATABASE_FILE = 'agents.sqlite'


class Agents(object):
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FILE)
        self.initialize()

    @property
    def agents(self):
        sql = '''select token, name, active from agents'''
        records = self.connection.cursor().execute(sql)
        for token, name, active in records:
            print(token, name, active)
            yield Agent(token, name, True if active else False)

    def initialize(self):
        sql = '''
        create table if not exists agents (
            token text primary key,
            name text not null,
            active integer not null default 1
        )
        '''
        self.connection.cursor().execute(sql)
        self.connection.commit()

    def add(self, name, token):
        try:
            uuid.UUID(token)
            sql = '''
                insert into agents (token, name, active) values (?, ?, ?)
            '''
            self.connection.cursor().execute(sql, (token, name, 1))
            self.connection.commit()
        except:
            pass

    def get(self, token):
        sql = '''
            select token, name, active from agents where token = ? limit 1
        '''
        record = self.connection.cursor().execute(sql, (token,)).fetchone()
        if not record:
            return

        token, name, active = record
        token = uuid.UUID(token)
        agent = Agent(token, name, True if active else False)
        return agent

    def toggle(self, token):
        agent = self.get(token)
        active = 0 if agent.active else 1
        sql = '''
            update agents set active = ? where token = ?
        '''
        self.connection.cursor().execute(sql, (active, token))
        self.connection.commit()

    def remove(self, token):
        sql = '''
            delete from agents where token = ?
        '''
        self.connection.cursor().execute(sql, (token, ))
        self.connection.commit()