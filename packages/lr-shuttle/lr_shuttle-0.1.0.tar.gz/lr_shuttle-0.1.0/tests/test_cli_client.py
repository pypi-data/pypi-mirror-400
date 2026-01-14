import pytest
import shuttle.serial_client as serial_client_module


class DummyClient:
    def __init__(self):
        self.calls = []

    def _command(self, op, payload):
        self.calls.append((op, payload))
        return {"ok": True, "op": op, "payload": payload}


def test_spi_xfer_and_overrides():
    client = DummyClient()
    result = serial_client_module.NDJSONSerialClient.__new__(
        serial_client_module.NDJSONSerialClient
    )
    result._command = client._command
    out = result.spi_xfer(tx="aabb", n=2, foo="bar")
    assert out["ok"] is True
    assert client.calls[0][0] == "spi.xfer"
    assert client.calls[0][1]["tx"] == "aabb"
    assert client.calls[0][1]["n"] == 2
    assert client.calls[0][1]["foo"] == "bar"


def test_get_info_and_ping():
    client = DummyClient()
    result = serial_client_module.NDJSONSerialClient.__new__(
        serial_client_module.NDJSONSerialClient
    )
    result._command = client._command
    out = result.get_info()
    assert out["op"] == "get.info"
    out2 = result.ping()
    assert out2["op"] == "ping"


def test_spi_cfg_and_uart_cfg():
    client = DummyClient()
    result = serial_client_module.NDJSONSerialClient.__new__(
        serial_client_module.NDJSONSerialClient
    )
    result._command = client._command
    out = result.spi_cfg({"hz": 123})
    assert out["op"] == "spi.cfg"
    assert out["payload"]["spi"]["hz"] == 123
    out2 = result.uart_cfg({"baud": 9600})
    assert out2["op"] == "uart.cfg"
    assert out2["payload"]["uart"]["baud"] == 9600


def test_uart_tx():
    client = DummyClient()
    result = serial_client_module.NDJSONSerialClient.__new__(
        serial_client_module.NDJSONSerialClient
    )
    result._command = client._command
    out = result.uart_tx("cafe", port=1)
    assert out["op"] == "uart.tx"
    assert client.calls[-1][1]["data"] == "cafe"
    assert client.calls[-1][1]["port"] == 1


def test_spi_enable_disable():
    client = DummyClient()
    result = serial_client_module.NDJSONSerialClient.__new__(
        serial_client_module.NDJSONSerialClient
    )
    result._command = client._command
    result.spi_enable()
    result.spi_disable()
    assert client.calls[0][0] == "spi.enable"
    assert client.calls[1][0] == "spi.disable"
