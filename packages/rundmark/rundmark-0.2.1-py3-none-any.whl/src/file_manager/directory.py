from fastapi import HTTPException, Depends
from typing import Dict
from pathlib import Path

# srcからappをインポート
from src import app
# app.pyから必要な依存関係をインポート
from app import resolve_safe_path, require_session
from src.config import get_config
from src.helpers import to_relative_path
from src.requests import DirectoryRequest, DirectoryRenameRequest

config = get_config()

# ディレクトリ CRUD
@app.get("/api/dirs")
async def list_directories(path: str = "", session: Dict = Depends(require_session)):
    """指定ディレクトリ直下のディレクトリ一覧を取得"""
    try:
        target_dir = resolve_safe_path(path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")

        directories = []
        for entry in target_dir.iterdir():
            if entry.is_dir():
                stat = entry.stat()
                directories.append({
                    "name": entry.name,
                    "path": to_relative_path(entry),
                    "modified": stat.st_mtime,
                })
        directories.sort(key=lambda x: x["name"])
        return {"directories": directories, "path": to_relative_path(target_dir)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list directories: {str(e)}")


@app.post("/api/dirs")
async def create_directory(request: DirectoryRequest, session: Dict = Depends(require_session)):
    """ディレクトリを作成"""
    if not request.path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    dir_path = resolve_safe_path(request.path)
    try:
        dir_path.mkdir(parents=True, exist_ok=False)
        return {
            "message": "Directory created successfully",
            "path": to_relative_path(dir_path),
        }
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Directory already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")


@app.put("/api/dirs/{dir_path:path}")
async def rename_directory(dir_path: str, request: DirectoryRenameRequest, session: Dict = Depends(require_session)):
    """ディレクトリ名を変更"""
    if not request.new_name:
        raise HTTPException(status_code=400, detail="New name is required")

    target_dir = resolve_safe_path(dir_path)
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    # 新しい名前にパストラバーサルを含めない
    if any(part in ("..", "") for part in Path(request.new_name).parts) or "/" in request.new_name or "\\" in request.new_name:
        raise HTTPException(status_code=400, detail="Invalid directory name")

    new_path = target_dir.parent / request.new_name
    new_path_resolved = resolve_safe_path(to_relative_path(new_path))

    if new_path_resolved.exists():
        raise HTTPException(status_code=400, detail="Target directory already exists")

    try:
        target_dir.rename(new_path_resolved)
        return {
            "message": "Directory renamed successfully",
            "path": to_relative_path(new_path_resolved),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename directory: {str(e)}")


@app.delete("/api/dirs/{dir_path:path}")
async def delete_directory(dir_path: str, session: Dict = Depends(require_session)):
    """ディレクトリを削除（空ディレクトリのみ）"""
    target_dir = resolve_safe_path(dir_path)
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    if any(target_dir.iterdir()):
        raise HTTPException(status_code=400, detail="Directory is not empty")

    try:
        target_dir.rmdir()
        return {
            "message": "Directory deleted successfully",
            "path": to_relative_path(target_dir),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete directory: {str(e)}")

@app.get("/api/dirs/last")
async def get_last_directory(session: Dict = Depends(require_session)):
    """最後に開いたディレクトリパスを取得"""
    if config.last_opened_directory:
        # ディレクトリが存在するか確認
        dir_path = resolve_safe_path(config.last_opened_directory)
        if dir_path.exists() and dir_path.is_dir():
            return {"path": config.last_opened_directory}
        else:
            # ディレクトリが存在しない場合はクリア
            config.last_opened_directory = None
    
    return {"path": None}


@app.post("/api/dirs/last")
async def set_last_directory(request: dict, session: Dict = Depends(require_session)):
    """最後に開いたディレクトリパスを保存"""
    
    path = request.get('path')
    if path is None:
        raise HTTPException(status_code=400, detail="Path is required")
    
    # 空文字列の場合はNoneとして保存（ルートディレクトリ）
    if path == "":
        config.last_opened_directory = ""
        return {
            "message": "Last directory saved successfully",
            "path": "",
        }
    
    # パスを検証
    try:
        dir_path = resolve_safe_path(path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        config.last_opened_directory = path
        return {
            "message": "Last directory saved successfully",
            "path": path,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save last directory: {str(e)}")
