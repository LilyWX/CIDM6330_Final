from datetime import date, timedelta
import pytest
from src.allocation.domain.model import Service, OrderLine, Batch, OutOfService

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches():
    in_service_batch = Batch("in-service-batch", "Cat-Care", 10, eta=None)
    service_batch = Batch("service-batch", "Cat-Care", 10, eta=tomorrow)
    service = Service(sName="Cat-Care", batches=[in_service_batch, service_batch])
    line = OrderLine("oref", "Cat-Care", 1)

    service.allocate(line)

    assert in_service_batch.available_quantity == 9
    assert service_batch.available_quantity == 10


def test_prefers_earlier_batches():
    earliest = Batch("today-services", "Cat-Care", 10, eta=today)
    medium = Batch("tomorrow-service","Cat-Care", 10, eta=tomorrow)
    latest = Batch("two-days-later-service", "Cat-Care", 10, eta=later)
    service = Service(sName="Cat-Care", batches=[medium, earliest, latest])
    line = OrderLine("order1", "Cat-Care", 1)

    service.allocate(line)

    assert earliest.available_quantity == 9
    assert medium.available_quantity == 10
    assert latest.available_quantity == 10


def test_cancel_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "Dog-Walker", 10, eta=None)
    available_batch = Batch("shipment-batch-ref", "Dog-WalkerR", 10, eta=tomorrow)
    line = OrderLine("oref", "Dog-Walker", 1)
    service = Service(sName="Dog-WalkerR", batches=[in_stock_batch, available_batch])
    allocation = service.allocate(line)
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "Dog-Walker", 1, eta=today)
    service = Service(sName="Dog-Walker", batches=[batch])
    service.allocate(OrderLine("order1", "Dog-Walker", 1))

    with pytest.raises(OutOfService, match="Dog-Walker"):
        service.allocate(OrderLine("order2", "Dog-Walker", 1))


def test_increments_service_number():
    line = OrderLine("oref", "Cat-Care", 1)
    service = Service(
        sName="Cat-Care", batches=[Batch("b1", "Cat-Care", 10, eta=None)]
    )
    service.service_number = 7
    service.allocate(line)
    assert service.service_number == 8