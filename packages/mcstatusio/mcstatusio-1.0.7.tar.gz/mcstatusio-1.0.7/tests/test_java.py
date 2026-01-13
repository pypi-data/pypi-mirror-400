# tests/test_java.py
from mcstatusio import JavaServer
from mcstatusio.JavaServer import JavaServerStatusResponse
import pytest


@pytest.mark.asyncio
async def test_java_async_server_status():
    server = JavaServer("demo.mcstatus.io")
    status = await server.async_status()

    if isinstance(status, JavaServerStatusResponse):
        assert status.players.online >= 0
        assert status.players.max > 0
        assert isinstance(status.motd.clean, str)
    else:
        pytest.fail("Server should be online")


def test_java_sync_server_status():
    server = JavaServer("demo.mcstatus.io")
    status = server.status()

    if isinstance(status, JavaServerStatusResponse):
        assert status.players.online >= 0
        assert status.players.max > 0
        assert isinstance(status.motd.clean, str)
    else:
        pytest.fail("Server should be online")
