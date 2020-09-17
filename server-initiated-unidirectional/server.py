#!/usr/bin/env python3
import asyncio
import io
import struct
import urllib.parse
import time

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.connection import QuicConnection, END_STATES
from aioquic.quic.events import StreamDataReceived, StreamReset, QuicEvent

class TestHandler:
    def __init__(self, connection) -> None:
        self.connection = connection
        self.stream_id = self.connection.get_next_available_stream_id(True)
        self.connection.send_stream_data(self.stream_id, 'ping'.encode('ascii'), False) # don't close

    def quic_event_received(self, event: QuicEvent) -> None:
        print(event)

class QuicTransportProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pending_events = []
        self.handler = None
        self.client_indication_data = b''

    def quic_event_received(self, event: QuicEvent) -> None:
        if self.is_closing_or_closed():
            return

        if self.handler is not None:
            self.handler.quic_event_received(event)
            return

        if isinstance(event, StreamDataReceived) and event.stream_id == 2:
            self.client_indication_data += event.data
            if event.end_stream:
                self.process_client_indication()
                if self.is_closing_or_closed():
                    return
                for e in self.pending_events:
                    self.handler.quic_event_received(e)
                self.pending_events.clear()
        else:
            self.pending_events.append(event)

    def parse_client_indication(self, bs):
        while True:
            prefix = bs.read(4)
            if len(prefix) == 0:
                return # End-of-stream reached.
            if len(prefix) != 4:
                raise Exception('Truncated key-length tag')
            key, length = struct.unpack('!HH', prefix)
            value = bs.read(length)
            if len(value) != length:
                raise Exception('Truncated value')
            yield (key, value)

    def process_client_indication(self) -> None:
        indication = dict(self.parse_client_indication(io.BytesIO(self.client_indication_data)))
        origin = urllib.parse.urlparse(indication[0].decode())
        path = urllib.parse.urlparse(indication[1]).decode()

        self.handler = TestHandler(self._quic)

    def is_closing_or_closed(self) -> bool:
        return self._quic._close_pending or self._quic._state in END_STATES


if __name__ == '__main__':
    configuration = QuicConfiguration(
        alpn_protocols=['wq-vvv-01'],
        is_client=False,
        max_datagram_frame_size=1500,
    )
    configuration.load_cert_chain('localhost.crt', 'localhost.key')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve(
            '::1',
            4443,
            configuration=configuration,
            create_protocol=QuicTransportProtocol,
        ))
    loop.run_forever()
