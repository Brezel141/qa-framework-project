# tests/conftest.py
import pytest
from app import create_app, db

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:" # Use an in-memory db for tests
    })

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
        yield testing_client # this is where the testing happens!

    with flask_app.app_context():
        db.drop_all()