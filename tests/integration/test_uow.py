# pylint: disable=broad-except
import threading
import time
import traceback
from typing import List
import pytest
from sqlalchemy.sql import delete, insert, select, text

from src.allocation.adapters.orm import allocations, batches, services, order_lines
from src.allocation.domain import model
from src.allocation.service_layer import unit_of_work
from ..random_refs import random_sName, random_batchref, random_orderid


def insert_batch(session, ref, sName, qty, eta, service_version=1):
    # session.execute(
    #     "INSERT INTO products (sku, version_number) VALUES (:sku, :version)",
    #     dict(sku=sku, version=product_version),
    # )
    session.execute(insert(services).values(sName=sName, service_number=service_version))
    # session.execute(
    #     "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
    #     " VALUES (:ref, :sku, :qty, :eta)",
    #     dict(ref=ref, sku=sku, qty=qty, eta=eta),
    # )
    session.execute(
        insert(batches).values(reference=ref, sName=sName, _purchased_quantity=qty, eta=eta)
    )


def get_allocated_batch_ref(session, orderid, sName):
    # [[orderlineid]] = session.execute(
    #     "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
    #     dict(orderid=orderid, sku=sku),
    # )

    # SQLAlchemy ORM approach
    orderline = session.scalars(
        select(model.OrderLine)
        .where(model.OrderLine.orderid == orderid)
        .where(model.OrderLine.sName == sName)
    ).first()

    orderlineid = orderline.orderid

    # [[batchref]] = session.execute(
    #     "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
    #     " WHERE orderline_id=:orderlineid",
    #     dict(orderlineid=orderlineid),
    # )

    # SQLAlchmey 2.x join_from
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#setting-the-leftmost-from-clause-in-a-join
    stmt = (
        select(model.Batch.reference)
        .join_from(allocations, batches)
        .where(model.OrderLine.orderid == orderlineid)
    )

    # execute the prepared statement and take the first returned record
    batchref = session.execute(stmt).scalars().first()
    session.close()

    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory
    insert_batch(session, "batch1", "Cat-Care", 10, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        service = uow.services.get(sName="Cat-Care")
        line = model.OrderLine("o1", "Cat-CareH", 1)
        service.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, "o1", "Cat-Care")
    assert batchref == "batch1"
    session.close()


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "Dog-Walker", 10, None)

    new_session = session_factory
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
    session_factory.close()
    new_session.close()


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "Dog-Care", 10, None)
            raise MyException()

    new_session = session_factory
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
    session_factory.close()
    new_session.close()


def try_to_allocate(orderid, sName, exceptions):
    line = model.OrderLine(orderid, sName, 10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            service = uow.services.get(sName=sName)
            service.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)



   