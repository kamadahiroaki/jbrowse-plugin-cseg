import os
import pathlib

# デフォルトの設定
DEFAULT_CONFIG = {
    'DATA_ROOT': '/data',
}

class Config:
    def __init__(self):
        self.data_root = os.getenv('CSEG_DATA_ROOT', DEFAULT_CONFIG['DATA_ROOT'])

    @property
    def data_path(self) -> pathlib.Path:
        """データファイルを保存するディレクトリのパス"""
        return pathlib.Path(self.data_root)

# グローバル設定インスタンス
config = Config()
