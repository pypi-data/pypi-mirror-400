from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecuteRequest(BaseModel):
    code: str
    language: str = "bash"
    tag: str
    task_id: Optional[str] = None
    wrap: Optional[str] = None
    timeout: int = 0
    interactive: bool = False
    image: Optional[str] = None  # 画像の拡張子（例: "png"）
    wrapper_script_opts: Optional[List[str]] = None  # ラッパースクリプトに渡す引数


class StopRequest(BaseModel):
    task_id: str


class InputRequest(BaseModel):
    input: str


class FileRequest(BaseModel):
    path: str
    content: str
    sudo: bool = False
    password: Optional[str] = None


class MarkdownFileRequest(BaseModel):
    filename: str
    content: str


class DirectoryRequest(BaseModel):
    path: str


class DirectoryRenameRequest(BaseModel):
    new_name: str

