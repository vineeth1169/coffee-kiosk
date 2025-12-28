import pytest
from src.app import create_app
from src.extensions import db, socketio

@pytest.fixture
def app():
    config = {'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'}
    app = create_app(config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def socketio_client(app):
    # use the socketio instance from extensions
    client = socketio.test_client(app, flask_test_client=app.test_client())
    yield client
    client.disconnect()


@pytest.fixture
def live_server(app):
    """Run the Flask app on a local port for E2E tests using Playwright."""
    from threading import Thread
    from werkzeug.serving import make_server

    port = 5001
    server = make_server('127.0.0.1', port, app)
    thread = Thread(target=server.serve_forever)
    thread.setDaemon(True)
    thread.start()
    yield f'http://127.0.0.1:{port}'
    server.shutdown()
    thread.join()


# Helpers to capture screenshots on failure for Playwright E2E tests
import shutil
from pathlib import Path


def pytest_runtest_makereport(item, call):
    # attach the call outcome so fixtures can inspect it
    if call.when == "call":
        setattr(item, "rep_call", call)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, tmp_path):
    """Capture a screenshot into `playwright-artifacts` when a Playwright test fails.
    This fixture is conditional: it only attempts to use the `page` fixture when present.
    """
    # Only attempt to get `page` if test requests it (avoids initializing Playwright for all tests)
    try:
        page = request.getfixturevalue('page')
    except Exception:
        # no page fixture for this test
        yield
        return

    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        dest = Path('playwright-artifacts')
        dest.mkdir(exist_ok=True)
        path = Path(tmp_path) / f"{request.node.name}.png"
        try:
            page.screenshot(path=str(path))
            shutil.copy(str(path), str(dest / path.name))
        except Exception:
            # best-effort; don't block teardown if screenshot fails
            pass
