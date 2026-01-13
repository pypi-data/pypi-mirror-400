from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
import subprocess
import tempfile
import os
import asyncio
import sys
import secrets
import socket
import shutil
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
import logging
from src.static import setup_static
from src import app
from src.config import init_config
from src.helpers import get_result_dir, get_result_files, resolve_safe_path
from src.requests import ExecutionStatus

# 引数をパースしてConfigを初期化
config = init_config()
app_logger = logging.getLogger(__name__)

def find_latest_task_id(tag: str) -> Optional[str]:
    """results/tag ディレクトリ内で最新のtask_idを返す（std.logファイルの更新時刻で判定）"""
    result_dir = get_result_dir(tag)
    if not result_dir.exists():
        return None
    
    latest_task_id = None
    latest_mtime = 0
    
    # std.logファイルを探す
    for file_path in result_dir.glob("*-std.log"):
        try:
            mtime = file_path.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
                # ファイル名からtask_idを抽出: <task_id>-std.log
                latest_task_id = file_path.stem.replace("-std", "")
        except Exception:
            continue
    
    return latest_task_id


async def monitor_log_files(
    task_id: str,
    tag: str,
    stream_queue: asyncio.Queue,
    read_positions: Dict[str, int]
):
    """ログファイルを監視して新しい内容をキューに追加"""
    result_files = get_result_files(task_id, tag)
    stdout_file = result_files['stdout']
    stderr_file = result_files['stderr']
    return_code_file = result_files['return_code']
    
    loop = asyncio.get_event_loop()
    
    # 読み取り位置を初期化
    if 'stdout' not in read_positions:
        read_positions['stdout'] = 0
    if 'stderr' not in read_positions:
        read_positions['stderr'] = 0
    
    while True:
        try:
            # stdoutファイルを監視
            if stdout_file.exists():
                current_size = stdout_file.stat().st_size
                if current_size > read_positions['stdout']:
                    with open(stdout_file, 'r', encoding='utf-8') as f:
                        f.seek(read_positions['stdout'])
                        new_content = f.read()
                        if new_content:
                            await stream_queue.put(('output', new_content))
                        read_positions['stdout'] = f.tell()
            
            # stderrファイルを監視
            if stderr_file.exists():
                current_size = stderr_file.stat().st_size
                if current_size > read_positions['stderr']:
                    with open(stderr_file, 'r', encoding='utf-8') as f:
                        f.seek(read_positions['stderr'])
                        new_content = f.read()
                        if new_content:
                            await stream_queue.put(('error', new_content))
                        read_positions['stderr'] = f.tell()
            
            # return-codeファイルが存在するかチェック（プロセス完了の判定）
            if return_code_file.exists():
                # プロセスが完了したことを示す
                try:
                    with open(return_code_file, 'r', encoding='utf-8') as f:
                        returncode_str = f.read().strip()
                        returncode = int(returncode_str) if returncode_str else -1
                    
                    # 最終的な出力を読み取る
                    stdout = ""
                    stderr = ""
                    if stdout_file.exists():
                        with open(stdout_file, 'r', encoding='utf-8') as f:
                            stdout = f.read()
                    if stderr_file.exists():
                        with open(stderr_file, 'r', encoding='utf-8') as f:
                            stderr = f.read()
                    
                    # ステータスを決定
                    if returncode == 0:
                        status = ExecutionStatus.COMPLETED
                    elif returncode == -1:
                        status = ExecutionStatus.FAILED
                    else:
                        status = ExecutionStatus.FAILED
                    
                    await stream_queue.put(('status', {
                        'status': status,
                        'output': stdout,
                        'error': stderr
                    }))
                    break
                except Exception as e:
                    app_logger.error(f"Error reading return-code file: {e}")
            
            # 0.1秒待機してから再チェック
            await asyncio.sleep(0.1)
            
        except Exception as e:
            app_logger.error(f"Error monitoring log files: {e}")
            await stream_queue.put(('error', f"File monitoring error: {e}\n"))
            break

def load_last_file() -> Optional[str]:
    """永続化された最後に開いたファイルを読み込む"""
    return config.load_last_file()


def save_last_file(filename: Optional[str]) -> None:
    """最後に開いたファイルを永続化"""
    config.save_last_file(filename)

# Language configurations
def create_session(token: str) -> str:
    """セッションを生成し、メモリに保存"""
    session_id = secrets.token_urlsafe(32)
    config.sessions[session_id] = {
        "token": token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(seconds=config.session_ttl_seconds),
    }
    return session_id


def validate_session(session_id: Optional[str]) -> Optional[Dict]:
    """セッションIDから有効なセッションを取得"""
    if not session_id:
        return None
    session = config.sessions.get(session_id)
    if not session:
        return None
    if session["expires_at"] < datetime.utcnow():
        # 期限切れセッションをクリーンアップ
        config.sessions.pop(session_id, None)
        return None
    return session


def has_active_session() -> bool:
    """有効なセッションが存在するかを確認。期限切れは同時に掃除。"""
    expired_ids = [sid for sid, s in config.sessions.items() if s["expires_at"] < datetime.utcnow()]
    for sid in expired_ids:
        config.sessions.pop(sid, None)
    return any(config.sessions.values())


def is_unix_socket_request(request: Request) -> bool:
    """リクエストがUnix domain socket経由かどうかを判定"""
    # Unix domain socket経由の場合、clientはNoneまたはタプルでNoneを含む
    client = request.scope.get("client")
    if client is None:
        return True
    # Unix domain socketの場合、clientはタプルで最初の要素がNone
    if isinstance(client, tuple) and len(client) > 0:
        # Unix domain socketの場合、client[0]はNone
        if client[0] is None:
            return True
    # server情報も確認（Unix domain socketの場合、server[0]はNoneまたはパス文字列）
    server = request.scope.get("server")
    if isinstance(server, tuple) and len(server) > 0:
        # Unix domain socketの場合、server[0]はNoneまたはパス文字列
        if server[0] is None or (isinstance(server[0], str) and server[0].startswith("/")):
            return True
    return False


async def require_session(request: Request) -> Dict:
    """セッション認証が必要なエンドポイントで使用する依存関係"""
    # Unix domain socket経由の場合は認証をスキップ
    if is_unix_socket_request(request):
        # ダミーセッションを返す（認証済みとして扱う）
        return {"token": "unix_socket", "created_at": datetime.utcnow(), "expires_at": datetime.utcnow() + timedelta(days=365)}
    
    session_id = request.cookies.get(config.session_cookie_name)
    session = validate_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session not found or expired")
    return session


@app.get("/images/{tag:path}")
async def get_image(tag: str, session: Dict = Depends(require_session)):
    """画像ファイルを取得（tagから最新の画像を取得）"""
    # URLデコード（FastAPIは自動的にデコードするが、念のため）
    from urllib.parse import unquote
    tag = unquote(tag)
    
    # tag名の安全性をチェック（パストラバーサルを防ぐ）
    # tagはget_result_dirで処理されるので、基本的なチェックのみ
    if ".." in tag:
        raise HTTPException(status_code=400, detail="Invalid tag name")
    
    # 画像ファイルのパス: .rundmark/results/<tag>/
    result_dir = get_result_dir(tag)
    
    if not result_dir.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 画像ファイルの拡張子リスト
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']
    
    # 最新の画像ファイルを探す（更新時刻でソート）
    latest_image = None
    latest_mtime = 0
    
    for file_path in result_dir.iterdir():
        if file_path.is_file() and file_path.suffix in extensions:
            try:
                mtime = file_path.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_image = file_path
            except Exception:
                continue
    
    if not latest_image or not latest_image.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(latest_image)



@app.get("/auth/login")
async def login_with_token(request: Request, token: str, redirect: Optional[str] = None):
    """
    トークンで認証し、セッションを発行してフロントエンドへリダイレクト
    無限ループ防止のため、既に有効なセッションがある場合はリダイレクトのみ行う
    Unix domain socket経由の場合はトークンチェックをスキップ
    """
    target_url = redirect or "/notebook/?session=1"
    existing_session = validate_session(request.cookies.get(config.session_cookie_name))
    if existing_session:
        return RedirectResponse(url=target_url, status_code=302)

    # Unix domain socket経由の場合はトークンチェックをスキップ
    if not is_unix_socket_request(request):
        # グローバルに有効なセッションが存在する場合は新規発行を拒否
        if has_active_session():
            raise HTTPException(status_code=403, detail="Another active session already exists")

        if token != config.access_token:
            raise HTTPException(status_code=401, detail="Invalid token")

    session_id = create_session(token or "unix_socket")
    response = RedirectResponse(url=target_url, status_code=302)
    response.set_cookie(
        key=config.session_cookie_name,
        value=session_id,
        httponly=True,
        max_age=config.session_ttl_seconds,
        secure=False,
        samesite="lax",
    )
    return response


@app.get("/auth/session")
async def session_status(request: Request):
    """セッションが有効かを確認（Unix domain socket経由の場合は常に認証済み）"""
    # Unix domain socket経由の場合は常に認証済みとして扱う
    if is_unix_socket_request(request):
        return {"status": "authenticated"}
    
    session = validate_session(request.cookies.get(config.session_cookie_name))
    if not session:
        raise HTTPException(status_code=401, detail="Session not found or expired")
    return {"status": "authenticated"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(...),
    sudo: bool = Form(False),
    password: Optional[str] = Form(None),
    session: Dict = Depends(require_session)
):
    """バイナリファイルをアップロード（multipart/form-data）"""
    app_logger.debug(f"upload_file called: path={path}, sudo={sudo}, filename={file.filename}, password={'*' * len(password) if password else None}")
    
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required")
    
    # sudo実行のチェック
    if sudo:
        app_logger.debug(f"SUDO_ENABLED={config.sudo_enabled}")
        if not config.sudo_enabled:
            raise HTTPException(status_code=403, detail="Sudo execution is not enabled. Start server with -s option.")
        
        if not password:
            raise HTTPException(status_code=400, detail="Password is required for sudo file upload.")
    
    try:
        # パスの正規化とセキュリティチェック
        file_path = resolve_safe_path(path)
        app_logger.debug(f"Resolved file_path: {file_path}")
        
        if sudo:
            # sudoでファイルをアップロード
            # 一時ファイルに内容を書き込み、sudoでコピー
            tmp_file_path = None
            file_size = 0
            try:
                # 一時ファイルにバイナリデータを書き込む
                app_logger.debug("Creating temporary file")
                content = await file.read()
                file_size = len(content)
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                app_logger.debug(f"Temporary file created: {tmp_file_path}")
                
                # 親ディレクトリが存在しない場合はエラーを返す
                parent_dir = file_path.parent
                app_logger.debug(f"Creating parent directory: {parent_dir}")
                mkdir_cmd = ['sudo', '-S', 'mkdir', '-p', str(parent_dir)]
                app_logger.debug(f"Running command: {' '.join(mkdir_cmd)}")
                mkdir_process = subprocess.Popen(
                    mkdir_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                mkdir_process.stdin.write(password + '\n')
                mkdir_stdout, mkdir_stderr = mkdir_process.communicate()
                app_logger.debug(f"mkdir returncode: {mkdir_process.returncode}, stdout: {mkdir_stdout}, stderr: {mkdir_stderr}")
                
                if mkdir_process.returncode != 0:
                    raise Exception(f"Failed to create directory: {mkdir_stderr}")
                
                # sudo cp でファイルをコピー
                app_logger.debug(f"Copying file from {tmp_file_path} to {file_path}")
                cp_cmd = ['sudo', '-S', 'cp', tmp_file_path, str(file_path)]
                app_logger.debug(f"Running command: {' '.join(cp_cmd)}")
                cp_process = subprocess.Popen(
                    cp_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                cp_process.stdin.write(password + '\n')
                cp_stdout, cp_stderr = cp_process.communicate()
                app_logger.debug(f"cp returncode: {cp_process.returncode}, stdout: {cp_stdout}, stderr: {cp_stderr}")
                
                if cp_process.returncode != 0:
                    raise Exception(f"Failed to upload file: {cp_stderr}")
                
                # ファイルのパーミッションを設定（必要に応じて）
                app_logger.debug(f"Setting permissions on {file_path}")
                chmod_cmd = ['sudo', '-S', 'chmod', '644', str(file_path)]
                app_logger.debug(f"Running command: {' '.join(chmod_cmd)}")
                chmod_process = subprocess.Popen(
                    chmod_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                chmod_process.stdin.write(password + '\n')
                chmod_stdout, chmod_stderr = chmod_process.communicate()
                app_logger.debug(f"chmod returncode: {chmod_process.returncode}, stdout: {chmod_stdout}, stderr: {chmod_stderr}")
                
                if chmod_process.returncode != 0:
                    # chmodの失敗は警告として扱う（ファイルは作成されている）
                    app_logger.warning(f"chmod failed but file was uploaded: {chmod_stderr}")
            finally:
                # 一時ファイルを削除
                if tmp_file_path and os.path.exists(tmp_file_path):
                    try:
                        app_logger.debug(f"Removing temporary file: {tmp_file_path}")
                        os.unlink(tmp_file_path)
                    except Exception as e:
                        app_logger.warning(f"Failed to remove temporary file: {e}")
        else:
            # 通常のファイルアップロード
            app_logger.debug("Uploading file without sudo")
            # 親ディレクトリが存在しない場合は作成
            parent_dir = file_path.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # バイナリファイルを保存
            content = await file.read()
            file_size = len(content)
            with open(file_path, 'wb') as f:
                f.write(content)
        
        app_logger.debug(f"File uploaded successfully: {file_path}")
        return {
            "message": "File uploaded successfully",
            "path": str(file_path),
            "filename": file.filename,
            "size": file_size
        }
    except Exception as e:
        app_logger.exception(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


def is_port_available(host: str, port: int) -> bool:
    """ポートが使用可能かどうかをチェック"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(host: str, start_port: int, max_attempts: int = 100) -> int:
    """使用可能なポートを見つける（npmのようにポート番号を加算）"""
    port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        if is_port_available(host, port):
            return port
        port += 1
        attempts += 1
    
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts (starting from {start_port})")


def setup_socket_mode():
    """Unix domain socketモードをセットアップ"""
    socket_path = config.rundmark_dir / "rundmark.socket"
    
    # 既存のソケットファイルを削除（存在する場合）
    if socket_path.exists():
        try:
            socket_path.unlink()
            app_logger.info(f"Removed existing socket file: {socket_path}")
        except Exception as e:
            app_logger.warning(f"Failed to remove existing socket file: {e}")
    
    # ソケットファイルの親ディレクトリを作成
    socket_path.parent.mkdir(parents=True, exist_ok=True)

    hostname = socket.gethostname()
    print(f"🔌 Unix domain socket mode is enabled")
    print(f"   Socket: {socket_path}")
    print(f"   Run: ssh -L localhost:8000:{socket_path} {hostname}")

    return socket_path


def copy_examples_to_current_dir():
    """Copy example files from the package examples directory to the current directory"""
    # Get the examples directory path
    # Try to find examples directory relative to app.py
    app_file = Path(__file__)
    examples_dir = app_file.parent / "examples"
    
    # If not found, try to find it using importlib.resources (for installed packages)
    if not examples_dir.exists():
        try:
            import importlib.resources
            with importlib.resources.path('rundmark', 'examples') as examples_path:
                examples_dir = Path(examples_path)
        except (ImportError, ModuleNotFoundError, TypeError):
            # If importlib.resources doesn't work, try another approach
            # Look for examples in common installation locations
            import site
            for site_dir in site.getsitepackages():
                examples_dir = Path(site_dir) / "rundmark" / "examples"
                if examples_dir.exists():
                    break
    
    if not examples_dir.exists():
        print(f"❌ Error: Examples directory not found")
        return False
    
    # Get current directory
    current_dir = Path.cwd() / "examples"
    current_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from examples directory to current directory
    copied_files = []
    for example_file in examples_dir.glob("*.md"):
        dest_file = current_dir / example_file.name
        try:
            shutil.copy2(example_file, dest_file)
            copied_files.append(example_file.name)
            print(f"✓ Copied: {example_file.name}")
        except Exception as e:
            print(f"❌ Error copying {example_file.name}: {e}")
            return False
    
    if copied_files:
        print(f"\n✓ Successfully copied {len(copied_files)} example file(s) to {current_dir}")
        return True
    else:
        print("❌ No example files found")
        return False


def main():
    """Main entry point for the application"""
    import uvicorn

    args = config.args
    
    # Handle -f option: run runner.py and exit
    if args.file:
        if not args.path:
            print("❌ Error: File path is required when using -f option")
            sys.exit(1)
        import src.runner as runner
        runner.from_rundmark(args.path, debug=args.debug, keep_going=args.keep_going)
        return
    
    setup_static(app, config.static_dir)
    config.set_global_variables(args.path)
    
    # Handle -e option: copy examples and exit
    if args.examples:
        if not copy_examples_to_current_dir():
            sys.exit(1)
    
    # -uと-pが同時に指定された場合はエラー
    if args.unix_socket and args.port is not None:
        print("❌ Error: Cannot specify both -u and -p options")
        sys.exit(1)
    
    # ホストはlocalhostのみを許可
    host = "localhost"
    port = config.port_option if config.port_option is not None else 8000

    # Unix domain socketモードの場合（デフォルト、または-uオプションが指定された場合）
    socket_path = None
    if config.unix_socket_mode:
        socket_path = setup_socket_mode()

    # 動的ポートに合わせてCORS設定を更新
    # 既存のCORSミドルウェアを削除（存在する場合）
    cors_middleware_index = None
    for i, middleware in enumerate(app.user_middleware):
        if middleware.cls == CORSMiddleware:
            cors_middleware_index = i
            break
    
    if cors_middleware_index is not None:
        app.user_middleware.pop(cors_middleware_index)
    
    # 動的に見つかったポートとlocalhostに合わせてCORSを制限
    # Unix domain socketモードの場合はポート8000を使用（表示用）
    base_url = f"http://{host}:{port}/notebook"
    allowed_origins = [
        base_url,
    ]
    if args.debug:
        allowed_origins.append("http://localhost:5173")
    
    # 環境変数で追加のオリジンを指定可能
    cors_origins_env = os.environ.get("CORS_ORIGINS", None)
    if cors_origins_env:
        allowed_origins.extend([origin.strip() for origin in cors_origins_env.split(",")])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Cookie"],
        expose_headers=["Content-Type"],
    )
    
    # トークンを含むURLを生成
    token_url = f"{base_url}/notebook/?token={config.access_token}"
    
    if socket_path:
        print(f"📓 Notebook UI: {base_url}")
    else:
        print(f"📓 Notebook UI: {token_url}")

    if config.debug_mode:
        print(f"📓 Dev Notebook UI: http://localhost:5173/notebook/?token={config.access_token}")
        print("🐛 Debug mode is ENABLED (-d option)")
    if config.sudo_enabled:
        print("⚠️  Sudo execution is ENABLED (-s option)")
    else:
        print("ℹ️  Sudo execution is disabled. Use -s option to enable.")

    if socket_path:
        uvicorn.run(app, uds=str(socket_path), log_config=config.uvicorn_log_config)
    else:
        uvicorn.run(app, host=host, port=port, log_config=config.uvicorn_log_config)

# Endpoints
import src.file_manager.directory  # noqa: E402
import src.file_manager.file  # noqa: E402
import src.execute.run_block  # noqa: E402
import src.execute.file_block  # noqa: E402

if __name__ == "__main__":
    main()
