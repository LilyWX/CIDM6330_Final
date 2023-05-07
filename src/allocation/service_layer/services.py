from __future__ import annotations
from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine
from allocation.service_layer import unit_of_work


class InvalidSName(Exception):
    pass

def add_batch(
    ref: str,
    sName: str,
    qty: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        service = uow.services.get(sName=sName)
        if service is None:
            service = model.Service(sName, batches=[])
            uow.services.add(service)
        service.batches.append(model.Batch(ref, sName, qty, eta))
        uow.commit()

def allocate(
    orderid: str,
    sName: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = OrderLine(orderid, sName, qty)
    with uow:
        service = uow.services.get(sName=line.sName)
        if service is None:
            raise InvalidSName(f"Invalid sName {line.sName}")
        batchref = service.allocate(line)
        uow.commit()
    return batchref