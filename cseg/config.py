import os
import pathlib

# デフォルトの設定
DEFAULT_CONFIG = {
    'DATA_ROOT': '/data',
    'VCF_DIR': 'vcf',
    'CSEG_DIR': 'cseg',
    'DB_DIR': 'db',
    'DB_NAME': 'cseg.db',
}

class Config:
    def __init__(self):
        self.data_root = os.getenv('CSEG_DATA_ROOT', DEFAULT_CONFIG['DATA_ROOT'])
        self.vcf_dir = os.getenv('CSEG_VCF_DIR', DEFAULT_CONFIG['VCF_DIR'])
        self.cseg_dir = os.getenv('CSEG_CSEG_DIR', DEFAULT_CONFIG['CSEG_DIR'])
        self.db_dir = os.getenv('CSEG_DB_DIR', DEFAULT_CONFIG['DB_DIR'])
        self.db_name = os.getenv('CSEG_DB_NAME', DEFAULT_CONFIG['DB_NAME'])

    @property
    def vcf_path(self) -> pathlib.Path:
        """VCFファイルを保存するディレクトリのパス"""
        return pathlib.Path(self.data_root) / self.vcf_dir

    @property
    def cseg_path(self) -> pathlib.Path:
        """CSEGファイルを保存するディレクトリのパス"""
        return pathlib.Path(self.data_root) / self.cseg_dir

    @property
    def db_path(self) -> pathlib.Path:
        """データベースファイルを保存するディレクトリのパス"""
        return pathlib.Path(self.data_root) / self.db_dir

    @property
    def db_file(self) -> pathlib.Path:
        """データベースファイルのパス"""
        return self.db_path / self.db_name

# グローバル設定インスタンス
config = Config()
