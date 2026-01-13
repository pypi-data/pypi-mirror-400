import enum


class Config:
    """HTTP/3 設定"""

    def __init__(self) -> None: ...

    @property
    def max_field_section_size(self) -> int:
        """最大フィールドセクションサイズ"""

    @max_field_section_size.setter
    def max_field_section_size(self, arg: int, /) -> None: ...

    @property
    def qpack_max_dtable_capacity(self) -> int:
        """QPACK 動的テーブル最大容量"""

    @qpack_max_dtable_capacity.setter
    def qpack_max_dtable_capacity(self, arg: int, /) -> None: ...

    @property
    def qpack_blocked_streams(self) -> int:
        """QPACK ブロックされたストリーム数"""

    @qpack_blocked_streams.setter
    def qpack_blocked_streams(self, arg: int, /) -> None: ...

    @property
    def enable_webtransport(self) -> bool:
        """WebTransport 有効化"""

    @enable_webtransport.setter
    def enable_webtransport(self, arg: bool, /) -> None: ...

    @property
    def enable_h3_datagram(self) -> bool:
        """HTTP/3 Datagram 有効化"""

    @enable_h3_datagram.setter
    def enable_h3_datagram(self, arg: bool, /) -> None: ...

    @property
    def is_server(self) -> bool:
        """サーバーモード"""

    @is_server.setter
    def is_server(self, arg: bool, /) -> None: ...

class EventType(enum.Enum):
    """HTTP/3 イベント種別"""

    HEADERS = 0

    DATA = 1

    STREAM_END = 2

    PUSH_PROMISE = 3

    GO_AWAY = 4

    RESET = 5

    WEBTRANSPORT_SESSION_READY = 6

    WEBTRANSPORT_STREAM_DATA = 7

    WEBTRANSPORT_DATAGRAM = 8

class Event:
    """HTTP/3 イベント"""

    def __init__(self) -> None: ...

    @property
    def type(self) -> EventType:
        """イベント種別"""

    @property
    def stream_id(self) -> int:
        """ストリーム ID"""

    @property
    def headers(self) -> list[tuple[str, str]]:
        """ヘッダー"""

    @property
    def data(self) -> bytes:
        """データ"""

    @property
    def error_code(self) -> int:
        """エラーコード"""

    @property
    def push_id(self) -> int:
        """Push ID"""

class Connection:
    """HTTP/3 コネクション (Sans-IO)"""

    @staticmethod
    def create_client(config: Config) -> Connection:
        """クライアントとして接続を作成"""

    @staticmethod
    def create_server(config: Config) -> Connection:
        """サーバーとして接続を作成"""

    def receive_stream_data(self, stream_id: int, data: bytes, fin: bool = False) -> int:
        """QUIC ストリームからデータを受信"""

    def get_streams_to_send(self) -> list[tuple[int, bytes, bool]]:
        """送信すべきストリームデータを取得"""

    def bind_control_stream(self, stream_id: int) -> None:
        """コントロールストリームを設定"""

    def bind_qpack_encoder_stream(self, stream_id: int) -> None:
        """QPACK エンコーダーストリームを設定"""

    def bind_qpack_decoder_stream(self, stream_id: int) -> None:
        """QPACK デコーダーストリームを設定"""

    def submit_request(self, stream_id: int, headers: list[tuple[str, str]]) -> bool:
        """リクエストを送信"""

    def submit_response(self, stream_id: int, headers: list[tuple[str, str]]) -> bool:
        """レスポンスを送信"""

    def send_data(self, stream_id: int, data: bytes, fin: bool = False) -> None:
        """ストリームにデータを送信"""

    def reset_stream(self, stream_id: int, error_code: int = 0) -> None:
        """ストリームをリセット"""

    def goaway(self, id: int = 0) -> None:
        """GOAWAY を送信"""

    def next_event(self) -> Event | None:
        """次のイベントを取得"""

    def get_required_streams(self) -> list[tuple[str, bool]]:
        """必要な QUIC ストリームのリストを取得"""

    def is_closed(self) -> bool:
        """接続が閉じられたか"""

def get_version() -> str:
    """nghttp3 のバージョンを取得"""
