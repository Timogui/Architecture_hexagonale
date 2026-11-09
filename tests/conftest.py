import os
import tempfile

import pytest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["FESTIPLAN_DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["FESTIPLAN_FAIL_NOTIFICATIONS"] = "false"
from app import models
from app.database import Base, SessionLocal, engine
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def prepare():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


@pytest.fixture()
def client():
    db = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()
    with TestClient(app) as c:
        yield c
