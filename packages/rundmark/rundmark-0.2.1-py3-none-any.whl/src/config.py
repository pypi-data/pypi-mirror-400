import os
import secrets
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict


class Config:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self, args: Optional[argparse.Namespace] = None):
        """Configインスタンスを初期化"""
        # コマンドライン引数のパース
        if args is None:
            args = self._parse_args()
        self.args = args
        
        # デバッグモードの有効化フラグ
        self.debug_mode = args.debug
        
        # ロギング設定
        if self.debug_mode:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # sudo機能の有効化フラグ
        self.sudo_enabled = args.sudo
        
        # ポート番号を取得
        # -pが指定されていない場合（args.port is None）はUnix domain socketモード（デフォルト）
        # -pが指定されている場合はTCPモード
        self.port_option = args.port
        
        # Unix domain socketモードの有効化フラグ
        # -uオプションが指定されているか、-pが指定されていない場合（デフォルト）はUnix domain socketモード
        self.unix_socket_mode = args.unix_socket or args.port is None
        
        # トークン認証の設定（URLアクセス制御用）
        self.access_token = os.environ.get("ACCESS_TOKEN", secrets.token_urlsafe(32))
        
        # セッション管理
        self.session_cookie_name = "m21_session"
        self.session_ttl_seconds = 60 * 60 * 8  # 8時間
        self.sessions: Dict[str, Dict] = {}
        
        # 静的ファイルのパス
        self.static_dir = Path(__file__).parent.parent / "static"
        
        # Markdownファイルの保存ベースディレクトリ（実行時のカレントディレクトリ）
        self.files_dir = Path.cwd()
        self.base_dir = self.files_dir.resolve()
        
        # .rundmarkディレクトリ
        self.rundmark_dir = self.base_dir / ".rundmark"
        
        # 最後に開いたファイル名の永続化ファイル
        self.last_file_store = self.rundmark_dir / ".last_file"
        
        # 最後に開いたファイル名（メモリ内で保持）
        self.last_opened_file: Optional[str] = None
        
        # 最後に開いたディレクトリパス（メモリ内で保持）
        self.last_opened_directory: Optional[str] = None
        
        # Language configurations
        self.language_configs = {
            'bash': {
                'command': lambda f: ['bash', f],
                'extension': 'sh',
            },
            'sh': {
                'command': lambda f: ['bash', f],
                'extension': 'sh',
            },
            'python': {
                'command': lambda f: ['python3', f],
                'extension': 'py',
            },
            'python3': {
                'command': lambda f: ['python3', f],
                'extension': 'py',
            },
            'javascript': {
                'command': lambda f: ['node', f],
                'extension': 'js',
            },
            'js': {
                'command': lambda f: ['node', f],
                'extension': 'js',
            },
            'node': {
                'command': lambda f: ['node', f],
                'extension': 'js',
            },
        }
        
        self.wrappers = {
            'uv': ['uv', 'run'],
            'poetry': ['poetry', 'run'],
            'pipenv': ['pipenv', 'run'],
        }
        
        self.timeout_seconds = 600
        
        # 実行中のタスクを管理
        self.running_tasks: Dict[str, Dict] = {}
        
        # .rundmarkディレクトリとそのサブディレクトリを作成
        self.rundmark_dir.mkdir(exist_ok=True)
        (self.rundmark_dir / "results").mkdir(exist_ok=True)
        (self.rundmark_dir / "tmp").mkdir(exist_ok=True)
        
        # 起動時に最後に開いたファイルを読み込む
        self.last_opened_file = self.load_last_file()

        # uvicornのログ設定
        uvicorn_log_path = self.rundmark_dir / "uvicorn.log"
        self.uvicorn_log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "default": {
                    "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "use_colors": None,
                },
            },
            "handlers": {
                "uvicorn_file": {
                    "formatter": "default",
                    "class": "logging.FileHandler",
                    "filename": str(uvicorn_log_path),
                    "mode": "a",
                },
                "access_file": {
                    "formatter": "access",
                    "class": "logging.FileHandler",
                    "filename": str(uvicorn_log_path),
                    "mode": "a",
                },
            },
            "loggers": {
                "uvicorn.access": {
                    "handlers": ["access_file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["uvicorn_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    
    @staticmethod
    def _parse_args() -> argparse.Namespace:
        """コマンドライン引数をパース"""
        parser = argparse.ArgumentParser(
            description='Rundmark - Markdown-based code execution server',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument(
            'path',
            nargs='?',
            type=str,
            help='File or directory path to set as working directory'
        )
        parser.add_argument(
            '-d', '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        parser.add_argument(
            '-s', '--sudo',
            action='store_true',
            help='Enable sudo execution'
        )
        parser.add_argument(
            '-u', '--unix-socket',
            action='store_true',
            help='Use Unix domain socket mode (default if -p is not specified)'
        )
        parser.add_argument(
            '-p', '--port',
            type=int,
            default=None,
            help='Port number for TCP mode (default: 8000 or available port)'
        )
        parser.add_argument(
            '-e', '--examples',
            action='store_true',
            help='Copy example files to current directory'
        )
        parser.add_argument(
            '-f', '--file',
            action='store_true',
            help='Run Markdown file directly using runner.py'
        )
        parser.add_argument(
            '-k', '--keep-going',
            action='store_true',
            help='Continue processing even if errors occur in direct execution mode'
        )
        return parser.parse_args()
    
    def load_last_file(self) -> Optional[str]:
        """永続化された最後に開いたファイルを読み込む"""
        if self.last_file_store.exists():
            try:
                with open(self.last_file_store, 'r', encoding='utf-8') as f:
                    filename = f.read().strip()
                    if filename:
                        # ファイルが存在するか確認（循環インポートを避けるため直接チェック）
                        file_path = (self.base_dir / filename).resolve()
                        if file_path.exists() and (self.base_dir in file_path.parents or file_path == self.base_dir):
                            return filename
                        else:
                            # ファイルが存在しない場合は削除
                            self.last_file_store.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to load last file: {e}")
        return None
    
    def save_last_file(self, filename: Optional[str]) -> None:
        """最後に開いたファイルを永続化"""
        try:
            if filename:
                with open(self.last_file_store, 'w', encoding='utf-8') as f:
                    f.write(filename)
                self.last_opened_file = filename
            else:
                # ファイルがNoneの場合は削除
                if self.last_file_store.exists():
                    self.last_file_store.unlink()
                self.last_opened_file = None
        except Exception as e:
            self.logger.warning(f"Failed to save last file: {e}")
    
    def set_global_variables(self, path: Optional[Path] = None):
        """グローバル変数を設定"""
        import os
        
        if path:
            path = Path(path)
            if path.exists():
                if path.is_file():
                    self.base_dir = path.parent
                    self.files_dir = path.parent
                    # change working directory to the parent directory
                    os.chdir(self.files_dir)
                    self.last_opened_file = path.name
                elif path.is_dir():
                    self.files_dir = path
                    self.base_dir = self.files_dir.resolve()
                    os.chdir(self.base_dir)
            else:
                self.logger.debug(f"Creating directory: {path}")
                path.mkdir(parents=True, exist_ok=True)
                self.files_dir = path
                self.base_dir = self.files_dir.resolve()
                os.chdir(self.base_dir)

        self.rundmark_dir = self.base_dir / ".rundmark"
        self.rundmark_dir.mkdir(exist_ok=True)
        (self.rundmark_dir / "results").mkdir(exist_ok=True)
        (self.rundmark_dir / "tmp").mkdir(exist_ok=True)

        self.last_file_store = self.rundmark_dir / ".last_file"
        if self.last_file_store.exists():
            self.last_opened_file = self.load_last_file()
        else:
            self.save_last_file(self.last_opened_file)
        self.logger.debug(f"Last opened file: {self.last_opened_file}")

# グローバルConfigインスタンス（後で初期化される）
_config: Optional[Config] = None


def get_config() -> Config:
    """グローバルConfigインスタンスを取得"""
    global _config
    if _config is None:
        raise RuntimeError("Config is not initialized. Call init_config() first.")
    return _config


def init_config(args: Optional[argparse.Namespace] = None) -> Config:
    """Configインスタンスを初期化"""
    global _config
    _config = Config(args)
    return _config
