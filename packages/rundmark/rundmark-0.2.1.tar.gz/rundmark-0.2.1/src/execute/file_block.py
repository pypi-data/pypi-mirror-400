from fastapi import HTTPException, Depends
from typing import Dict
from pathlib import Path
import subprocess
import os
import tempfile
import logging
from src.config import get_config
from src.requests import FileRequest
from src import app
from app import require_session

config = get_config()
file_block_logger = logging.getLogger(__name__)

def command_execute(cmd: list[str], password: str):
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    process.stdin.write(password + '\n')
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def create_file_with_sudo(file_path: Path, tmp_file_path: str, password: str):
    # 親ディレクトリが存在しない場合は作成（常に実行、既に存在する場合はエラーにならない）
    parent_dir = file_path.parent
    file_block_logger.debug(f"Creating parent directory: {parent_dir}")
    mkdir_cmd = ['sudo', '-S', 'mkdir', '-p', str(parent_dir)]
    file_block_logger.debug(f"Running command: {' '.join(mkdir_cmd)}")
    mkdir_stdout, mkdir_stderr, mkdir_returncode = command_execute(mkdir_cmd, password)
    file_block_logger.debug(f"mkdir returncode: {mkdir_returncode}, stdout: {mkdir_stdout}, stderr: {mkdir_stderr}")
    
    if mkdir_returncode != 0:
        raise Exception(f"Failed to create directory: {mkdir_stderr}")
    
    # sudo cp でファイルをコピー
    file_block_logger.debug(f"Copying file from {tmp_file_path} to {file_path}")
    cp_cmd = ['sudo', '-S', 'cp', tmp_file_path, str(file_path)]
    file_block_logger.debug(f"Running command: {' '.join(cp_cmd)}")
    cp_stdout, cp_stderr, cp_returncode = command_execute(cp_cmd, password)
    file_block_logger.debug(f"cp returncode: {cp_returncode}, stdout: {cp_stdout}, stderr: {cp_stderr}")
    
    if cp_returncode != 0:
        raise Exception(f"Failed to create file: {cp_stderr}")


def create_file_without_sudo(file_path: Path, content: str):
    # 親ディレクトリが存在することを確認
    parent_dir = file_path.parent
    if not parent_dir.exists():
        # 親ディレクトリを作成
        parent_dir.mkdir(parents=True, exist_ok=True)
    
    # ファイルを作成
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_temporary_file(content: str):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    return tmp_file_path


@app.post("/api/file")
async def create_file(request: FileRequest, session: Dict = Depends(require_session)):
    """ファイルを作成"""
    file_block_logger.debug(f"create_file called: path={request.path}, sudo={request.sudo}, password={'*' * len(request.password) if request.password else None}")
    
    if not request.path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # sudo実行のチェック
    if request.sudo:
        if not config.sudo_enabled:
            raise HTTPException(status_code=403, detail="Sudo execution is not enabled. Start server with -s option.")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required for sudo file creation.")
    
    file_path = Path(request.path).resolve()

    try:
        tmp_file_path = None
        if request.sudo:
            tmp_file_path = create_temporary_file(request.content)
            create_file_with_sudo(file_path, tmp_file_path, request.password)
        else:
            create_file_without_sudo(file_path, request.content)
    except Exception as e:
        file_block_logger.exception(f"Error creating file with sudo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create file with sudo: {str(e)}")
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                file_block_logger.debug(f"Removing temporary file: {tmp_file_path}")
                os.unlink(tmp_file_path)
            except Exception as e:
                file_block_logger.warning(f"Failed to remove temporary file: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to remove temporary file: {str(e)}")

    file_block_logger.debug(f"File created successfully: {file_path}")
    return {
        "message": "File created successfully",
        "path": str(file_path)
    }
