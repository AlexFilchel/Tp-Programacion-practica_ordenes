from sqlmodel import Session

from app.db import engine


class UnitOfWork:
    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = Session(engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()