import pytest
import requests

from src.allocation import config
from ..random_refs import random_sName, random_batchref, random_orderid


def test_api_works(test_client):
    url = config.get_api_url()
    r = test_client.get(f"{url}/")
    assert r.status_code == 200
    assert b"HELLO FROM THE API" in r.data


def post_to_add_batch(test_client, ref, sName, qty, eta):
    url = config.get_api_url()
    r = test_client.post(
        f"{url}/add_batch", json={"ref": ref, "sName": sName, "qty": qty, "eta": eta}
    )
    # r = requests.post(
    #     f"{url}/add_batch", json={"ref": ref, "sName": sName, "qty": qty, "eta": eta}
    # )
    assert r.status_code == 201

def test_happy_path_returns_201_and_allocated_batch(test_client):
    sName, othersName = random_sName("Cat-Care"), random_sName("other")
    print(sName)
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(test_client, laterbatch, sName, 10, "2023-05-02")
    post_to_add_batch(test_client, earlybatch, sName, 10, "2023-05-01")
    post_to_add_batch(test_client, otherbatch, othersName, 10, None)
    data = {"orderid": random_orderid(), "sName": sName, "qty": 2}

    url = config.get_api_url()
    r = test_client.post(f"{url}/allocate", json=data)
    assert r.status_code == 201
    assert r.json["batchref"] == earlybatch


def test_unhappy_path_returns_400_and_error_message(test_client):
    unknown_sName, orderid = random_sName(), random_orderid()
    data = {"orderid": orderid, "sName": unknown_sName, "qty": 20}
    url = config.get_api_url()
    r = test_client.post(f"{url}/allocate", json=data)
    # r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json["message"] == f"Invalid sName {unknown_sName}"
