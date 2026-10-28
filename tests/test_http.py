from http.server import ThreadingHTTPServer
import json
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest

from currency.rates import Store, RateError
from currency.server import handler_for
from test_rates import xml


@pytest.fixture
def server(tmp_path):
    store = Store(tmp_path, lambda day: xml(day))
    http = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(store))
    worker = Thread(target=http.serve_forever, daemon=True)
    worker.start()
    yield f"http://127.0.0.1:{http.server_port}", store
    http.shutdown()
    http.server_close()
    worker.join()


def test_http_conversion_and_validation(server):
    address, _ = server
    with urlopen(address + "/api/rates?date=2026-10-28") as response:
        rate = json.load(response)
    payload = {"snapshot": rate["snapshot"], "amount": "100", "from": "EUR", "to": "MDL"}
    def convert(body):
        return urlopen(Request(address + "/api/convert", json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"}))
    with convert(payload) as response:
        assert json.load(response)["amount"] == "2000.00"
    payload["amount"] = "-1"
    with pytest.raises(HTTPError) as error:
        convert(payload)
    assert error.value.code == 400


def test_http_offline_offers_cache(server):
    address, store = server
    with urlopen(address + "/api/rates?date=2026-10-28") as response:
        assert response.status == 200
    def offline(_):
        raise RateError("Нет сети")
    store.fetcher = offline
    with pytest.raises(HTTPError) as error:
        urlopen(address + "/api/rates")
    assert json.load(error.value)["cacheAvailable"] is True
    with urlopen(address + "/api/rates?cached=1") as response:
        assert json.load(response)["cached"] is True


def test_static_allowlist_and_health(server):
    address, _ = server
    with urlopen(address + "/") as response:
        assert "Конвертер валют" in response.read().decode()
    with urlopen(address + "/api/health") as response:
        assert json.load(response)["status"] == "ok"
    with pytest.raises(HTTPError) as error:
        urlopen(address + "/../REPORT.md")
    assert error.value.code == 404
