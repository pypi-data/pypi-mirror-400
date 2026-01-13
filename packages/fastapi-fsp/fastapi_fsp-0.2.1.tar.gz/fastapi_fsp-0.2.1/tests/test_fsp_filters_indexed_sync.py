from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.main import Hero


def seed(session: Session):
    session.add_all(
        [
            Hero(name="Deadpond", secret_name="Dive Wilson", age=None),
            Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
            Hero(name="ALPHA", secret_name="Alpha Secret", age=10),
            Hero(name="beta", secret_name="Beta Secret", age=20),
        ]
    )
    session.commit()


def test_indexed_single_filter_eq(session: Session, client: TestClient):
    seed(session)
    r = client.get(
        "/heroes/?filters[0][field]=name&filters[0][operator]=eq&filters[0][value]=Deadpond"
    )
    assert r.status_code == 200
    js = r.json()
    assert len(js["data"]) == 1
    assert js["data"][0]["name"] == "Deadpond"


def test_indexed_multiple_filters_combined(session: Session, client: TestClient):
    seed(session)
    # age >= 18 AND name ILIKE '%eta'
    r = client.get(
        "/heroes/?filters[0][field]=age&filters[0][operator]=gte&filters[0][value]=18"
        "&filters[1][field]=name&filters[1][operator]=ilike&filters[1][value]=%25eta"
    )
    assert r.status_code == 200
    names = [h["name"] for h in r.json()["data"]]
    # Only 'beta' is age >= 18 and ends with 'eta'
    assert set(names) == {"beta"}


def test_indexed_incomplete_filter_returns_400(session: Session, client: TestClient):
    seed(session)
    r = client.get("/heroes/?filters[0][field]=age&filters[0][operator]=gte")
    assert r.status_code == 400
