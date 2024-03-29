from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class OutOfService(Exception):
    pass

class Service:
    def __init__(self, sName: str, batches: List[Batch], service_number: int = 0):
        self.sName = sName
        self.batches = batches
        self.service_number = service_number
    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.service_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfService(f"Out of service for serviceName {line.sName}")


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sName: str
    qty: int


class Batch:
    def __init__(self, ref: str, sName: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sName = sName
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sName == line.sName and self.available_quantity >= line.qty
