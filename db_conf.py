import inspect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from errors import ServerDBError


class ServerDB:

    def __init__(self, base, db_name=None):
        self.db_name = f'sqlite:///{db_name}'
        self.engine = create_engine(db_name, echo=True)
        self.base = base
        self.session = None

    def load(self):
        self.base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close(self):
        if self.session:
            self.session.close()
            self.session = None


class SessionContext:
    """Контекстный менеджер операций с БД"""

    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.session.commit()
        else:
            self.session.rollback()
            func_name = inspect.stack([1][3])
            raise ServerDBError(f'Error in func:  {func_name}')
