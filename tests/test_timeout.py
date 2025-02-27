import asyncio
import typing
from unittest.mock import patch

import pytest

from mcstatus.address import Address
from mcstatus.protocol.connection import TCPAsyncSocketConnection


class FakeAsyncStream(asyncio.StreamReader):
    async def read(self, *args, **kwargs) -> typing.NoReturn:
        await asyncio.sleep(2)
        raise NotImplementedError("tests are designed to timeout before reaching this line")


async def fake_asyncio_asyncio_open_connection(hostname: str, port: int):
    return FakeAsyncStream(), None


class TestAsyncSocketConnection:
    def setup_method(self):
        self.tcp_async_socket = TCPAsyncSocketConnection()
        self.test_addr = Address("dummy_address", 1234)

    def test_tcp_socket_read(self):
        try:
            from asyncio.exceptions import TimeoutError  # type: ignore # (Import for older versions)
        except ImportError:
            from asyncio import TimeoutError

        with patch("asyncio.open_connection", fake_asyncio_asyncio_open_connection):
            asyncio.run(self.tcp_async_socket.connect(self.test_addr, timeout=0.01))

            with pytest.raises(TimeoutError):
                asyncio.run(self.tcp_async_socket.read(10))
