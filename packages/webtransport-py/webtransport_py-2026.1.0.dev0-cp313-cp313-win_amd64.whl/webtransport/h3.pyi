import enum


class Config:
    """WebTransport over HTTP/3 設定"""

    def __init__(self) -> None: ...

    @property
    def max_field_section_size(self) -> int: ...

    @max_field_section_size.setter
    def max_field_section_size(self, arg: int, /) -> None: ...

    @property
    def qpack_max_dtable_capacity(self) -> int: ...

    @qpack_max_dtable_capacity.setter
    def qpack_max_dtable_capacity(self, arg: int, /) -> None: ...

    @property
    def qpack_blocked_streams(self) -> int: ...

    @qpack_blocked_streams.setter
    def qpack_blocked_streams(self, arg: int, /) -> None: ...

    @property
    def is_server(self) -> bool: ...

    @is_server.setter
    def is_server(self, arg: bool, /) -> None: ...

class EventType(enum.Enum):
    """WebTransport イベント種別"""

    SESSION_READY = 0

    SESSION_CLOSED = 1

    STREAM_OPENED = 2

    STREAM_DATA = 3

    STREAM_CLOSED = 4

    DATAGRAM = 5

    ERROR = 6

class Event:
    """WebTransport イベント"""

    def __init__(self) -> None: ...

    @property
    def type(self) -> EventType: ...

    @property
    def session_id(self) -> int: ...

    @property
    def stream_id(self) -> int: ...

    @property
    def data(self) -> bytes:
        """イベントデータ"""

    @property
    def error_code(self) -> int: ...

    @property
    def error_message(self) -> str: ...

    @property
    def is_unidirectional(self) -> bool: ...

class StreamInfo:
    """WebTransport ストリーム情報"""

    def __init__(self) -> None: ...

    @property
    def stream_id(self) -> int: ...

    @property
    def session_id(self) -> int: ...

    @property
    def is_unidirectional(self) -> bool: ...

    @property
    def is_incoming(self) -> bool: ...

    @property
    def is_write_registered(self) -> bool: ...

class Session:
    """WebTransport over HTTP/3 セッション"""

    @staticmethod
    def create_client(config: Config) -> Session:
        """クライアントセッションを作成"""

    @staticmethod
    def create_server(config: Config) -> Session:
        """サーバーセッションを作成"""

    def receive_stream_data(self, stream_id: int, data: bytes, fin: bool = False) -> int:
        """QUIC ストリームからデータを受信"""

    def receive_datagram(self, data: bytes) -> None:
        """QUIC データグラムを受信"""

    def get_streams_to_send(self) -> list[tuple[int, bytes, bool]]:
        """送信すべきストリームデータを取得"""

    def get_datagrams_to_send(self) -> list[bytes]:
        """送信すべきデータグラムを取得"""

    def bind_control_stream(self, stream_id: int) -> None:
        """コントロールストリーム ID を設定"""

    def bind_qpack_encoder_stream(self, stream_id: int) -> None:
        """QPACK エンコーダーストリーム ID を設定"""

    def bind_qpack_decoder_stream(self, stream_id: int) -> None:
        """QPACK デコーダーストリーム ID を設定"""

    def connect(self, stream_id: int, url: str) -> bool:
        """WebTransport セッションを開始 (クライアント用)"""

    def accept_session(self, stream_id: int) -> bool:
        """WebTransport セッションを受理 (サーバー用)"""

    def reject_session(self, stream_id: int, status_code: int) -> None:
        """WebTransport セッションを拒否 (サーバー用)"""

    def open_stream(self, session_id: int, stream_id: int, is_unidirectional: bool) -> bool:
        """WebTransport ストリームを開く"""

    def send_stream_data(self, stream_id: int, data: bytes, fin: bool = False) -> None:
        """WebTransport ストリームにデータを送信"""

    def send_datagram(self, session_id: int, data: bytes) -> None:
        """WebTransport データグラムを送信"""

    def close_stream(self, stream_id: int, error_code: int = 0) -> None:
        """WebTransport ストリームを閉じる"""

    def close_session(self, session_id: int, error_code: int = 0, error_message: str = '') -> None:
        """WebTransport セッションを閉じる"""

    def next_event(self) -> Event | None:
        """次のイベントを取得"""

    def get_required_streams(self) -> list[tuple[str, bool]]:
        """必要な QUIC ストリーム ID のリストを取得"""

    def is_closed(self) -> bool:
        """接続が閉じられたか"""

    def get_session_ids(self) -> list[int]:
        """確立されたセッション ID のリストを取得"""

    def get_session_streams(self, session_id: int) -> list[StreamInfo]:
        """セッションに属するストリームを取得"""

    def set_max_client_streams_bidi(self, max_streams: int) -> None:
        """クライアントからの双方向ストリームの最大数を設定"""
