from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from allocation.domain import model
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#imperative-mapping
# using SQLAlchemy 2.0-style imperative mapping
mapper_registry = registry()

# metadata = MetaData()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sName", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

services = Table(
    "services",
    mapper_registry.metadata,
    Column("sName", String(255), primary_key=True),
    Column("service_number", Integer, nullable=False, server_default="0"),
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sName", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)
    batches_mapper = mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mapper_registry.map_imperatively(
        model.Service, services, properties={"batches": relationship(batches_mapper)}
    )