import uuid


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sName(name=""):
    return f"sName-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"