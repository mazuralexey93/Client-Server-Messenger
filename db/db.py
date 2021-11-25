
from sqlalchemy import create_engine, DateTime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper

engine = create_engine('sqlite:///:my_db1:', echo=True)
pool_recycle = 7200


metadata = MetaData()

clients_table = Table('clients', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('login', String(50)),
                      Column('info', String(200)),
                      )

client_history = Table('history', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('time', DateTime),
                       Column('ip', Integer),
                       )

contacts_list = Table('contacts', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('client_id', Integer, ForeignKey('clients.id')),
                      )
metadata.create_all(engine)


class Client:
    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f"<Client login: '{self.login}', info: '{self.info}'>"


class ClientHistory:
    def __init__(self, time, ip):
        self.time = time
        self.ip = ip

    def __repr__(self):
        return f"<ClientHistory time: '{self.time}', ip: '{self.ip}'>"


class Contacts:
    def __init__(self, client_id):
        self.client_id = client_id

    def __repr__(self):
        return f"<Contacts client_id: '{self.client_id}'>"


print(mapper(Client, clients_table))
print(mapper(ClientHistory, client_history))
print(mapper(Contacts, contacts_list))

client = Client("client1", "client 1 info")
print(client)

