import abc
from allocation.domain import model

from sqlalchemy import select


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Service):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sName) -> model.Service:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, service):
        self.session.add(service)

    def get(self, sName):
        return self.session.scalars(
            select(model.Service).filter_by(sName=sName)
        ).first()