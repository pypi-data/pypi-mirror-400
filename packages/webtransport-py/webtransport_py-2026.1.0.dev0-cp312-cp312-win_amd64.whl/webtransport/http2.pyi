import enum


class Config:
    """HTTP/2 設定"""

    def __init__(self) -> None: ...

    @property
    def initial_window_size(self) -> int:
        """初期ウィンドウサイズ"""

    @initial_window_size.setter
    def initial_window_size(self, arg: int, /) -> None: ...

    @property
    def max_concurrent_streams(self) -> int:
        """最大同時ストリーム数"""

    @max_concurrent_streams.setter
    def max_concurrent_streams(self, arg: int, /) -> None: ...

    @property
    def max_frame_size(self) -> int:
        """最大フレームサイズ"""

    @max_frame_size.setter
    def max_frame_size(self, arg: int, /) -> None: ...

    @property
    def max_header_list_size(self) -> int:
        """最大ヘッダーリストサイズ"""

    @max_header_list_size.setter
    def max_header_list_size(self, arg: int, /) -> None: ...

    @property
    def is_server(self) -> bool:
        """サーバーモード"""

    @is_server.setter
    def is_server(self, arg: bool, /) -> None: ...

    @property
    def send_preface(self) -> bool:
        """HTTP/2 プリフェイスを送信するか"""

    @send_preface.setter
    def send_preface(self, arg: bool, /) -> None: ...

class EventType(enum.Enum):
    """HTTP/2 イベント種別"""

    HEADERS = 0

    DATA = 1

    STREAM_END = 2

    STREAM_RESET = 3

    GO_AWAY = 4

    WINDOW_UPDATE = 5

    SETTINGS = 6

    PING = 7

class Event:
    """HTTP/2 イベント"""

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
    def last_stream_id(self) -> int:
        """GOAWAY の last_stream_id"""

class Connection:
    """HTTP/2 コネクション (Sans-IO)"""

    @staticmethod
    def create_client(config: Config) -> Connection:
        """クライアントとして接続を作成"""

    @staticmethod
    def create_server(config: Config) -> Connection:
        """サーバーとして接続を作成"""

    def receive(self, data: bytes) -> int:
        """受信したデータを処理"""

    def send(self) -> bytes | None:
        """送信すべきデータを取得"""

    def submit_request(self, headers: list[tuple[str, str]]) -> int:
        """リクエストを送信"""

    def submit_response(self, stream_id: int, headers: list[tuple[str, str]]) -> None:
        """レスポンスを送信"""

    def send_data(self, stream_id: int, data: bytes, eof: bool = False) -> None:
        """ストリームにデータを送信"""

    def reset_stream(self, stream_id: int, error_code: int = 0) -> None:
        """ストリームをリセット"""

    def goaway(self, error_code: int = 0) -> None:
        """GOAWAY を送信"""

    def ping(self) -> None:
        """PING を送信"""

    def next_event(self) -> Event | None:
        """次のイベントを取得"""

    def want_write(self) -> bool:
        """送信待ちデータがあるか"""

    def is_closed(self) -> bool:
        """接続が閉じられたか"""

def get_version() -> str:
    """nghttp2 のバージョンを取得"""
