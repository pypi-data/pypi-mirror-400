from fastapi import HTTPException
from pathlib import Path
from typing import Dict

from src.config import get_config

def resolve_safe_path(rel_path: str) -> Path:
    """相対パスをベースディレクトリ内の安全な絶対パスへ解決"""
    config = get_config()
    rel_path = (rel_path or "").strip()
    # 絶対パスとパストラバーサルを拒否
    if rel_path.startswith(("/", "\\")):
        rel_path = rel_path.lstrip("/\\")
    rel_parts = Path(rel_path).parts
    if ".." in rel_parts:
        raise HTTPException(status_code=400, detail="Invalid path")

    candidate = (config.base_dir / rel_path).resolve()
    base_resolved = config.base_dir
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise HTTPException(status_code=400, detail="Path escapes base directory")
    return candidate


def to_relative_path(path: Path) -> str:
    """ベースディレクトリからの相対パスを返す（POSIX形式）"""
    config = get_config()
    rel = path.resolve().relative_to(config.base_dir)
    rel_str = rel.as_posix()
    return "" if rel_str == "." else rel_str


def get_result_dir(tag: str) -> Path:
    """tagに基づいて結果ディレクトリのパスを返す"""
    config = get_config()
    # tag名の安全性をチェック（パストラバーサルを防ぐ）
    # スラッシュは許可するが、..は拒否
    if ".." in tag:
        raise HTTPException(status_code=400, detail="Invalid tag name")
    # パスを正規化して、ベースディレクトリから外に出ないようにする
    tag_parts = Path(tag).parts
    if any(part == ".." for part in tag_parts):
        raise HTTPException(status_code=400, detail="Invalid tag name")
    result_dir = config.rundmark_dir / "results" / tag
    # 結果ディレクトリがベースディレクトリ内にあることを確認
    try:
        resolved = result_dir.resolve()
        base_resolved = config.rundmark_dir.resolve()
        if base_resolved not in resolved.parents and resolved != base_resolved:
            raise HTTPException(status_code=400, detail="Invalid tag name")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tag name")
    return result_dir


def get_result_files(task_id: str, tag: str) -> Dict[str, Path]:
    """ログファイルとreturn-codeファイルのパスを返す"""
    result_dir = get_result_dir(tag)
    return {
        "stdout": result_dir / f"{task_id}-std.log",
        "stderr": result_dir / f"{task_id}-err.log",
        "return_code": result_dir / f"{task_id}-return-code",
    }
