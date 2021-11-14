from sqlalchemy import create_engine, DateTime, func
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///:my_db:', echo=True)
pool_recycle = 7200

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    login = Column(String(50))
    info = Column(String(200))

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f"<Client login: '{self.login}', info: '{self.info}'>"


class ClientHistory(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    # time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    ip = Column(Integer)

    def __init__(self, time, info):
        self.time = time
        self.info = info

    def __repr__(self):
        return f"<ClientHistory time: '{self.time}', ip: '{self.ip}'>"


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))

    def __init__(self, client_id):
        self.client_id = client_id

    def __repr__(self):
        return f"<Contacts client_id: '{self.client_id}'>"


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

client = Client("client1", "info 1")
session.add(client)
session.commit()

# print(client)
# print(client.id)
query = session.query(Client).first()
print(query)