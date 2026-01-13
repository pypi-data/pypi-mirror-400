from collections.abc import Sequence
import enum


class Config:
    """QUIC コネクション設定"""

    def __init__(self) -> None: ...

    @property
    def max_streams_bidi(self) -> int:
        """最大双方向ストリーム数"""

    @max_streams_bidi.setter
    def max_streams_bidi(self, arg: int, /) -> None: ...

    @property
    def max_streams_uni(self) -> int:
        """最大単方向ストリーム数"""

    @max_streams_uni.setter
    def max_streams_uni(self, arg: int, /) -> None: ...

    @property
    def max_data(self) -> int:
        """最大データサイズ"""

    @max_data.setter
    def max_data(self, arg: int, /) -> None: ...

    @property
    def max_stream_data_bidi_local(self) -> int:
        """ローカル双方向ストリームの最大データサイズ"""

    @max_stream_data_bidi_local.setter
    def max_stream_data_bidi_local(self, arg: int, /) -> None: ...

    @property
    def max_stream_data_bidi_remote(self) -> int:
        """リモート双方向ストリームの最大データサイズ"""

    @max_stream_data_bidi_remote.setter
    def max_stream_data_bidi_remote(self, arg: int, /) -> None: ...

    @property
    def max_stream_data_uni(self) -> int:
        """単方向ストリームの最大データサイズ"""

    @max_stream_data_uni.setter
    def max_stream_data_uni(self, arg: int, /) -> None: ...

    @property
    def idle_timeout_ns(self) -> int:
        """アイドルタイムアウト (ナノ秒)"""

    @idle_timeout_ns.setter
    def idle_timeout_ns(self, arg: int, /) -> None: ...

    @property
    def alpn_protocols(self) -> list[str]:
        """ALPN プロトコル"""

    @alpn_protocols.setter
    def alpn_protocols(self, arg: Sequence[str], /) -> None: ...

    @property
    def server_name(self) -> str:
        """サーバー名 (SNI)"""

    @server_name.setter
    def server_name(self, arg: str, /) -> None: ...

    @property
    def cert_file(self) -> str:
        """証明書ファイルパス"""

    @cert_file.setter
    def cert_file(self, arg: str, /) -> None: ...

    @property
    def key_file(self) -> str:
        """秘密鍵ファイルパス"""

    @key_file.setter
    def key_file(self, arg: str, /) -> None: ...

    @property
    def verify_peer(self) -> bool:
        """ピア検証を行うか"""

    @verify_peer.setter
    def verify_peer(self, arg: bool, /) -> None: ...

    @property
    def enable_datagram(self) -> bool:
        """Datagram を有効にするか"""

    @enable_datagram.setter
    def enable_datagram(self, arg: bool, /) -> None: ...

    @property
    def max_datagram_frame_size(self) -> int:
        """最大 Datagram フレームサイズ"""

    @max_datagram_frame_size.setter
    def max_datagram_frame_size(self, arg: int, /) -> None: ...

class EventType(enum.Enum):
    """QUIC イベント種別"""

    HANDSHAKE_COMPLETED = 0

    CONNECTION_CLOSED = 1

    STREAM_DATA = 2

    STREAM_OPENED = 3

    STREAM_CLOSED = 4

    STREAM_RESET = 5

    DATAGRAM = 6

    CONNECTION_ID_RETIRED = 7

class Event:
    """QUIC イベント"""

    def __init__(self) -> None: ...

    @property
    def type(self) -> EventType:
        """イベント種別"""

    @property
    def stream_id(self) -> int:
        """ストリーム ID"""

    @property
    def data(self) -> bytes:
        """データ"""

    @property
    def fin(self) -> bool:
        """FIN フラグ"""

    @property
    def error_code(self) -> int:
        """エラーコード"""

    @property
    def reason(self) -> str:
        """理由"""

class Connection:
    """QUIC コネクション (Sans-IO)"""

    @staticmethod
    def create_client(config: Config) -> Connection:
        """クライアントとして接続を作成"""

    @staticmethod
    def create_server(config: Config) -> Connection:
        """サーバーとして接続を作成"""

    @staticmethod
    def accept(config: Config, initial_packet: bytes) -> Connection:
        """初期パケットからサーバー接続を作成"""

    def receive(self, data: bytes) -> int:
        """受信したデータを処理"""

    def send(self) -> bytes | None:
        """送信すべきデータを取得"""

    def get_timeout(self) -> int | None:
        """次のタイムアウトまでの時間を取得 (ナノ秒)"""

    def handle_timeout(self) -> None:
        """タイムアウトを処理"""

    def open_stream(self, bidirectional: bool = True) -> int:
        """ストリームを開く"""

    def send_stream_data(self, stream_id: int, data: bytes, fin: bool = False) -> None:
        """ストリームにデータを送信"""

    def close_stream(self, stream_id: int, error_code: int = 0) -> None:
        """ストリームを閉じる"""

    def send_datagram(self, data: bytes) -> None:
        """Datagram を送信"""

    def close(self, error_code: int = 0, reason: str = '') -> None:
        """接続を閉じる"""

    def next_event(self) -> Event | None:
        """次のイベントを取得"""

    def is_established(self) -> bool:
        """接続が確立されているか"""

    def is_closed(self) -> bool:
        """接続が閉じられたか"""

    def is_handshake_completed(self) -> bool:
        """ハンドシェイクが完了したか"""

    def get_connection_id(self) -> bytes:
        """接続 ID を取得"""

def get_version() -> str:
    """ngtcp2 のバージョンを取得"""
