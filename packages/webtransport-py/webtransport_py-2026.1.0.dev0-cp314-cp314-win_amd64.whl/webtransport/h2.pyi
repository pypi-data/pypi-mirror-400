import enum


class CapsuleType(enum.Enum):
    """Capsule 種別"""

    DATAGRAM = 0

    PADDING = 420171064

    WT_RESET_STREAM = 420171065

    WT_STOP_SENDING = 420171066

    WT_STREAM = 420171067

    WT_STREAM_FIN = 420171068

    WT_MAX_DATA = 420171069

    WT_MAX_STREAM_DATA = 420171070

    WT_MAX_STREAMS_BIDI = 420171071

    WT_MAX_STREAMS_UNI = 420171072

    WT_DATA_BLOCKED = 420171073

    WT_STREAM_DATA_BLOCKED = 420171074

    WT_STREAMS_BLOCKED_BIDI = 420171075

    WT_STREAMS_BLOCKED_UNI = 420171076

    WT_CLOSE_SESSION = 10307

    WT_DRAIN_SESSION = 30894

class Config:
    """WebTransport over HTTP/2 設定"""

    def __init__(self) -> None: ...

    @property
    def initial_window_size(self) -> int: ...

    @initial_window_size.setter
    def initial_window_size(self, arg: int, /) -> None: ...

    @property
    def max_concurrent_streams(self) -> int: ...

    @max_concurrent_streams.setter
    def max_concurrent_streams(self, arg: int, /) -> None: ...

    @property
    def max_frame_size(self) -> int: ...

    @max_frame_size.setter
    def max_frame_size(self, arg: int, /) -> None: ...

    @property
    def max_header_list_size(self) -> int: ...

    @max_header_list_size.setter
    def max_header_list_size(self, arg: int, /) -> None: ...

    @property
    def is_server(self) -> bool: ...

    @is_server.setter
    def is_server(self, arg: bool, /) -> None: ...

    @property
    def wt_initial_max_data(self) -> int: ...

    @wt_initial_max_data.setter
    def wt_initial_max_data(self, arg: int, /) -> None: ...

    @property
    def wt_initial_max_stream_data(self) -> int: ...

    @wt_initial_max_stream_data.setter
    def wt_initial_max_stream_data(self, arg: int, /) -> None: ...

    @property
    def wt_initial_max_streams_bidi(self) -> int: ...

    @wt_initial_max_streams_bidi.setter
    def wt_initial_max_streams_bidi(self, arg: int, /) -> None: ...

    @property
    def wt_initial_max_streams_uni(self) -> int: ...

    @wt_initial_max_streams_uni.setter
    def wt_initial_max_streams_uni(self, arg: int, /) -> None: ...

class EventType(enum.Enum):
    """WebTransport over HTTP/2 イベント種別"""

    SESSION_READY = 0

    SESSION_CLOSED = 1

    SESSION_DRAINING = 2

    STREAM_DATA = 3

    STREAM_RESET = 4

    STOP_SENDING = 5

    DATAGRAM = 6

    ERROR = 7

class Event:
    """WebTransport over HTTP/2 イベント"""

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
    def fin(self) -> bool: ...

class Session:
    """WebTransport over HTTP/2 セッション"""

    @staticmethod
    def create_client(config: Config) -> Session:
        """クライアントセッションを作成"""

    @staticmethod
    def create_server(config: Config) -> Session:
        """サーバーセッションを作成"""

    def receive(self, data: bytes) -> int:
        """受信したデータを処理"""

    def send(self) -> bytes | None:
        """送信すべきデータを取得"""

    def connect(self, url: str) -> int:
        """WebTransport セッションを開始 (クライアント用)"""

    def accept_session(self, session_id: int) -> bool:
        """WebTransport セッションを受理 (サーバー用)"""

    def reject_session(self, session_id: int, status_code: int) -> None:
        """WebTransport セッションを拒否 (サーバー用)"""

    def open_stream(self, session_id: int, is_unidirectional: bool) -> int:
        """WebTransport ストリームを開く"""

    def send_stream_data(self, session_id: int, stream_id: int, data: bytes, fin: bool = False) -> None:
        """WebTransport ストリームにデータを送信"""

    def reset_stream(self, session_id: int, stream_id: int, error_code: int, reliable_size: int = 0) -> None:
        """WebTransport ストリームをリセット"""

    def stop_sending(self, session_id: int, stream_id: int, error_code: int) -> None:
        """送信停止を要求"""

    def send_datagram(self, session_id: int, data: bytes) -> None:
        """データグラムを送信"""

    def close_session(self, session_id: int, error_code: int = 0, error_message: str = '') -> None:
        """WebTransport セッションを閉じる"""

    def drain_session(self, session_id: int) -> None:
        """セッションのドレインを開始"""

    def next_event(self) -> Event | None:
        """次のイベントを取得"""

    def want_write(self) -> bool:
        """送信待ちデータがあるか"""

    def is_closed(self) -> bool:
        """接続が閉じられたか"""

    def get_session_ids(self) -> list[int]:
        """確立されたセッション ID のリストを取得"""

    def get_stream_ids(self, session_id: int) -> list[int]:
        """セッションに属するストリーム ID を取得"""
