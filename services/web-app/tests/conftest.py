"""
Test configuration and shared fixtures
"""

import pytest
import os
import tempfile
from app.app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create application for testing"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Configure for testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False
    }

    app, socketio = create_app("testing")
    app.config.update(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()