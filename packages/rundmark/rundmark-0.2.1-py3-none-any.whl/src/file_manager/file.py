from fastapi import HTTPException, Depends
from typing import Dict, Optional

# srcからappをインポート
from src import app
# app.pyから必要な依存関係をインポート
import app as app_module
from app import resolve_safe_path, require_session
from src.config import get_config
from src.helpers import to_relative_path
from src.requests import MarkdownFileRequest

config = get_config()

# MarkdownファイルのCRUD API
@app.get("/api/files")
async def list_files(path: str = "", session: Dict = Depends(require_session)):
    """指定パス直下のMarkdownファイルとディレクトリ一覧を取得"""
    try:
        target_dir = resolve_safe_path(path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")

        files = []
        directories = []

        for entry in target_dir.iterdir():
            if entry.is_dir():
                stat = entry.stat()
                directories.append({
                    "name": entry.name,
                    "path": to_relative_path(entry),
                    "modified": stat.st_mtime,
                })
            elif entry.is_file() and entry.suffix == ".md":
                stat = entry.stat()
                files.append({
                    "filename": entry.name,
                    "path": to_relative_path(entry),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })

        directories.sort(key=lambda x: x["name"])
        files.sort(key=lambda x: x["filename"])
        return {"directories": directories, "files": files, "path": to_relative_path(target_dir)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/api/files/last")
async def get_last_file(session: Dict = Depends(require_session)):
    """最後に開いたファイル名を取得"""
    if config.last_opened_file:
        # ファイルが存在するか確認
        file_path = resolve_safe_path(config.last_opened_file)
        if file_path.exists():
            return {"filename": config.last_opened_file}
        else:
            # ファイルが存在しない場合はクリア
            config.save_last_file(None)  # 永続化ファイルもクリア
    
    return {"filename": None}


@app.post("/api/files/last")
async def set_last_file(request: dict, session: Dict = Depends(require_session)):
    """最後に開いたファイル名を保存"""
    filename = request.get('filename')
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # パスを検証
    file_path = resolve_safe_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    config.save_last_file(filename)  # 永続化
    return {
        "message": "Last file saved successfully",
        "filename": filename,
    }


@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str, session: Dict = Depends(require_session)):
    """Markdownファイルを読み込む"""
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        stat = resolved_path.stat()
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "filename": to_relative_path(resolved_path),
            "content": content,
            "mtime": stat.st_mtime,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@app.post("/api/files")
async def save_file(request: MarkdownFileRequest, session: Dict = Depends(require_session)):
    """Markdownファイルを保存（作成または更新）"""
    if not request.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    filename = request.filename
    if not filename.endswith('.md'):
        filename += '.md'

    file_path = resolve_safe_path(filename)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
        return {
            "message": "File saved successfully",
            "filename": to_relative_path(file_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.put("/api/files/{file_path:path}")
async def update_file(file_path: str, request: MarkdownFileRequest, session: Dict = Depends(require_session)):
    """Markdownファイルを更新"""
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
        return {
            "message": "File updated successfully",
            "filename": to_relative_path(resolved_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")


@app.delete("/api/files/{file_path:path}")
async def delete_file(file_path: str, session: Dict = Depends(require_session)):
    """Markdownファイルを削除"""
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        resolved_path.unlink()
        
        # 削除したファイルが最後に開いたファイルの場合、キャッシュをクリア
        if config.last_opened_file == file_path or config.last_opened_file == to_relative_path(resolved_path):
            config.save_last_file(None)  # 永続化ファイルもクリア
        
        return {
            "message": "File deleted successfully",
            "filename": to_relative_path(resolved_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
