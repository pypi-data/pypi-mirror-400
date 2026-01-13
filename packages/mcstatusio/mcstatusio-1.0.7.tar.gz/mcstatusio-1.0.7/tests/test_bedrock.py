# tests/test_bedrock
from mcstatusio import BedrockServer
from mcstatusio.BedrockServer import BedrockServerStatusResponse
import pytest


@pytest.mark.asyncio
async def test_bedrock_async_server_status():
    server = BedrockServer("demo.mcstatus.io", 19132)
    status = await server.async_status()

    if isinstance(status, BedrockServerStatusResponse):
        assert status.players.online is not None and status.players.online >= 0
        assert status.players.max is not None and status.players.max > 0
        assert isinstance(status.motd.clean, str)
        assert isinstance(status.version.name, str)
    else:
        pytest.fail("Server should be online")


def test_bedrock_sync_server_status():
    server = BedrockServer("demo.mcstatus.io", 19132)
    status = server.status()

    if isinstance(status, BedrockServerStatusResponse):
        assert status.players.online is not None and status.players.online >= 0
        assert status.players.max is not None and status.players.max > 0
        assert isinstance(status.motd.clean, str)
        assert isinstance(status.version.name, str)
    else:
        pytest.fail("Server should be online")
