from datetime import date
from src.allocation.domain.model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "Cat-Care", qty=10, eta=date.today())
    line = OrderLine("order-ref", "Cat-Care", 2)

    batch.allocate(line)

    assert batch.available_quantity == 8


def make_batch_and_line(sName, batch_qty, line_qty):
    return (
        Batch("batch-001", sName, batch_qty, eta=date.today()),
        OrderLine("order-123", sName, line_qty),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("Cat-Care", 10, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("Cat-Care", 2, 10)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("Cat-Care", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_sName_do_not_match():
    batch = Batch("batch-001", "Cat-Care", 10, eta=None)
    different_sName_line = OrderLine("order-123", "Dog-Walker", 1)
    assert batch.can_allocate(different_sName_line) is False


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("Cat-Care", 10, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 8


def test_deallocate():
    batch, line = make_batch_and_line("Cat-Care", 10, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 10


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("Cat-Care", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20
