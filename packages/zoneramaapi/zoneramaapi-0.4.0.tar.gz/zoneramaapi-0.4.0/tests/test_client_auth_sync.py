from hashlib import sha256
from zoneramaapi.client import ZoneramaClient
from tests.conftest import DummyResponse

def test_login_success(monkeypatch, zeep_clients):
    client = ZoneramaClient()

    # Inject mocked zeep
    monkeypatch.setattr(client, "_zeep", zeep_clients)

    zeep_clients.api.service.Login.return_value = DummyResponse(
        success=True,
        result=1234
    )

    ok = client.login("user", "password")

    assert ok is True
    assert client.logged_in is True
    assert client.logged_in_as == 1234

    zeep_clients.api.service.Login.assert_called_once_with(
        "user",
        sha256(b"password").hexdigest()
    )

def test_login_failure(monkeypatch, zeep_clients):
    client = ZoneramaClient()
    monkeypatch.setattr(client, "_zeep", zeep_clients)

    zeep_clients.api.service.Login.return_value = DummyResponse(
        success=False,
        result=None
    )

    ok = client.login("user", "wrong")

    assert ok is False
    assert client.logged_in is False
    assert client.logged_in_as is None

def test_logout_success(monkeypatch, zeep_clients):
    client = ZoneramaClient()
    monkeypatch.setattr(client, "_zeep", zeep_clients)

    client.logged_in_as = 123

    zeep_clients.api.service.Logout.return_value = DummyResponse(success=True)

    ok = client.logout()

    assert ok is True
    assert client.logged_in is False
    assert client.logged_in_as is None

    zeep_clients.api.service.Logout.assert_called_once()

def test_logout_not_logged_in(monkeypatch, zeep_clients):
    client = ZoneramaClient()
    monkeypatch.setattr(client, "_zeep", zeep_clients)

    ok = client.logout()

    assert ok is False
    zeep_clients.api.service.Logout.assert_not_called()

def test_context_manager_closes(monkeypatch, zeep_clients):
    client = ZoneramaClient()
    monkeypatch.setattr(client, "_zeep", zeep_clients)

    with client:
        pass

    zeep_clients.__enter__.assert_called_once()
    zeep_clients.close.assert_called_once()
