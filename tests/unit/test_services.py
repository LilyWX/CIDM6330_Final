import pytest
from src.allocation.adapters import repository
from src.allocation.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, services):
        self._services = set(services)

    def add(self, services):
        self._services.add(services)

    def get(self, sName):
        return next((p for p in self._services if p.sName == sName), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.services = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
    

def test_add_batch_for_new_service():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "Cat-Care", 10, None, uow)
    assert uow.services.get("Cat-Care") is not None
    assert uow.committed


def test_add_batch_for_existing_service():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "Dog-Walker", 10, None, uow)
    services.add_batch("b2", "Dog-Walker", 9, None, uow)
    assert "b2" in [b.reference for b in uow.services.get("Dog-Walker").batches]
    
    
def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "Dog-Walker", 10, None, uow)
    result = services.allocate("o1", "Dog-Walker", 1, uow)
    assert result == "b1"


def test_allocate_error_for_invalid_sName():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "Cat-Care", 10, None, uow)

    with pytest.raises(services.InvalidSName, match="Invalid sName NONEXISTENTSName"):
        services.allocate("o1", "NONEXISTENTSName", 1, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "Cat-Care", 10, None, uow)
    services.allocate("o1", "Cat-Care", 1, uow)
    assert uow.committed