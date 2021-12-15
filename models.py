from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr, relationship

from db_conf import SessionContext

Base = declarative_base()


class Core:
    """Общее для всех таблиц"""

    @declared_attr
    def __tablename__(cls):
        return f'{str(cls.__name__.lower())}'

    time_created = Column(DateTime(timezone=True), default=func.now())
    time_updated = Column(DateTime(timezone=True), default=func.now(),
                          onupdate=func.now())

    @classmethod
    def all(cls, session):
        """Получить все данные моделей"""

        with SessionContext(session) as _session:
            return _session.query(cls).all()

    @classmethod
    def add(cls, session, *args, **kwargs):
        """Добавить в базу"""

        with SessionContext(session) as session:
            obj = cls(*args, **kwargs)
            session.add(obj)
            session.commit()
        return obj

    @classmethod
    def get(cls, session, obj_id):
        """Получить объект класса cls из базы """

        obj = session.query(cls).filter(cls.id == obj_id).first()
        return obj

    def update(self, session, **kwargs):
        """Обновить данные экземпляра"""

        with SessionContext(session) as session:
            for key, value in kwargs.items():
                setattr(self, key, value)
                session.add(self)
                session.commit()

    def delete(self, session):
        """Удалить из базы"""
        with SessionContext(session) as session:
            session.delete(self)
            session.commit()


class Client(Core, Base):
    """Модель пользователя"""
    id = Column(Integer, primary_key=True)
    login = Column(String(50))
    info = Column(String(200))

    history = relationship('ClientHistory', backref='owner')

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f"<Client(id: {self.id}, login: '{self.login}', info: '{self.info}')>"

    @classmethod
    def get_by_login(cls, session, login):
        """Получить объект класса из базы"""
        obj = session.query(cls).filter(cls.login == login).first()
        return obj


class ClientHistory(Core, Base):
    """История пользователя"""
    id = Column(Integer, primary_key=True)
    owner_id = Column(ForeignKey('client.id'))
    ip_addr = Column(String)

    def __init__(self, ip_addr, owner_id):
        self.owner_id = owner_id
        self.ip_addr = ip_addr

    def __repr__(self):
        return f"<ClientHistory (time: '{self.time_updated}', owner_id: {self.owner_id}, ip: '{self.ip_addr}')>"


class Contacts(Core, Base):
    """Список контактов"""
    id = Column(Integer, primary_key=True)
    owner_id = Column(ForeignKey('client.id'))
    client_id = Column(ForeignKey('client.id'))

    def __init__(self, owner_id, client_id):
        self.client_id = client_id
        self.owner_id = owner_id

    def __repr__(self):
        return f"<Contacts (owner_id: '{self.owner_id}, client_id: '{self.client_id}')>"

    @classmethod
    def get_all_for_onwer(cls, session, owner_id):
        """Получить контакты для владельца по его id"""
        obj = session.query(cls).filter(owner_id=owner_id).all()
        return obj
