from fastapi import HTTPException, Depends
from typing import Dict
from pathlib import Path
import subprocess
import os
import asyncio
import threading
import json
import uuid
from datetime import datetime
from src.config import get_config
from src.requests import ExecuteRequest, StopRequest, InputRequest
from src import app
from app import require_session, find_latest_task_id, get_result_files, monitor_log_files
from enum import Enum
from typing import Optional
from src.executor import Executor
from src.helpers import get_result_dir
from fastapi.responses import StreamingResponse
from src.requests import ExecutionStatus
import logging

config = get_config()
run_block_logger = logging.getLogger(__name__)

async def execute_code_async(
    task_id: str,
    code: str,
    language: str,
    tag: str,
    wrap: Optional[str] = None,
    timeout: int = config.timeout_seconds,
    interactive: bool = False,
    image: Optional[str] = None,
    wrapper_script_opts: Optional[list] = None
):
    """非同期でコードを実行"""
    executor = Executor(
        task_id=task_id,
        code=code,
        language=language,
        tag=tag,
        language_configs=config.language_configs,
        wrappers=config.wrappers,
        timeout=timeout,
        sudo_enabled=False,
        running_tasks=config.running_tasks,
        execution_status=ExecutionStatus,
        get_result_dir_func=get_result_dir,
        get_result_files_func=get_result_files,
        monitor_log_files_func=monitor_log_files,
        wrap=wrap,
        sudo=False,
        password=None,
        interactive=interactive,
        image=image,
        wrapper_script_opts=wrapper_script_opts
    )
    # executorインスタンスをrunning_tasksに保存（停止処理で使用）
    if task_id in config.running_tasks:
        config.running_tasks[task_id]['executor'] = executor
    await executor.execute()

@app.post("/api/execute")
async def execute_code(request: ExecuteRequest, session: Dict = Depends(require_session)):
    """コードを非同期で実行開始"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code is required")

    language = request.language.lower()
    if language not in config.language_configs:
        raise HTTPException(
            status_code=400,
            detail=f'Unsupported language: {language}. Supported languages: {", ".join(config.language_configs.keys())}'
        )

    python_path = os.environ.get("PYTHONPATH", None)
    if python_path is None:
        os.environ["PYTHONPATH"] = str(Path.cwd())

    # Generate task ID if not provided
    task_id = request.task_id or str(uuid.uuid4())

    # Initialize task status
    config.running_tasks[task_id] = {
        'status': ExecutionStatus.PENDING,
        'output': None,
        'error': None,
        'process': None,
        'stream_queue': asyncio.Queue(),
        'stdin_lock': threading.Lock(),
        'interactive': request.interactive if hasattr(request, 'interactive') else False,
        'tag': request.tag,
    }

    timeout = request.timeout or config.timeout_seconds
    run_block_logger.debug(f"[{task_id}] Timeout setting: request.timeout={request.timeout}, TIMEOUT_SECONDS={config.timeout_seconds}, final timeout={timeout}")
    wrap = request.wrap or None
    image = request.image if hasattr(request, 'image') else None
    wrapper_script_opts = request.wrapper_script_opts if hasattr(request, 'wrapper_script_opts') else None
    
    # Start execution in background
    asyncio.create_task(execute_code_async(
        task_id, 
        request.code, 
        language,
        request.tag,
        wrap=wrap,
        timeout=timeout,
        interactive=request.interactive if hasattr(request, 'interactive') else False,
        image=image,
        wrapper_script_opts=wrapper_script_opts
    ))

    return {
        "task_id": task_id,
        "status": ExecutionStatus.PENDING,
        "message": "Execution started"
    }


@app.get("/api/execute/{task_id}")
async def get_execution_status(
    task_id: str,
    tag: str,
    session: Dict = Depends(require_session)
):
    """実行状態を取得"""
    # task_idが"latest"の場合は、tagから最新のtask_idを取得
    if task_id == "latest":
        task_id = find_latest_task_id(tag)
        run_block_logger.debug(f"[{task_id}] Latest task ID found for tag: {tag}")
        if not task_id:
            raise HTTPException(status_code=404, detail="No task found for tag")

    result_files = get_result_files(task_id, tag)
    stdout = ""
    stderr = ""
    try:
        if result_files['stdout'].exists():
            with open(result_files['stdout'], 'r', encoding='utf-8') as f:
                stdout = f.read()
        if result_files['stderr'].exists():
            with open(result_files['stderr'], 'r', encoding='utf-8') as f:
                stderr = f.read()
    except Exception as e:
        run_block_logger.error(f"Error reading log files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read log files: {e}")

    # return-codeファイルが存在しない場合は、タスクがまだ開始されていない
    if not result_files['return_code'].exists():
        # running_tasksに存在する場合は、その情報を返す
        if task_id in config.running_tasks:
            response = {
                "task_id": task_id,
                "status": ExecutionStatus.RUNNING,
                "output": stdout,
                "error": stderr,
                "stdout": stdout,
            }
            return response
        else:
            run_block_logger.debug(f"[{task_id}] Task not found in running_tasks")
            raise HTTPException(status_code=404, detail="Task not found")
    
    # return-codeファイルからreturncodeを読み取る
    try:
        with open(result_files['return_code'], 'r', encoding='utf-8') as f:
            returncode_str = f.read().strip()
            returncode = int(returncode_str) if returncode_str else -1
    except Exception as e:
        run_block_logger.error(f"Error reading return-code file: {result_files['return_code']}")
        raise HTTPException(status_code=500, detail=f"Failed to read return-code file: {e}")
    
    # return-codeファイルの更新時刻を取得
    finish_time = None
    try:
        if result_files['return_code'].exists():
            mtime = result_files['return_code'].stat().st_mtime
            finish_time = datetime.fromtimestamp(mtime).isoformat()
    except Exception as e:
        run_block_logger.error(f"Error getting return-code file mtime: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get return-code file mtime: {e}")
        
    response = {
        "task_id": task_id,
    }
    if returncode == 0:
        response["status"] = ExecutionStatus.COMPLETED
        response["output"] = stdout
        response["result"] = stdout
    else:
        response["status"] = ExecutionStatus.FAILED
        response["error"] = stderr
        response["output"] = stdout
    
    # finish_timeを追加
    if finish_time:
        response["finish_time"] = finish_time
    
    return response


@app.get("/api/execute/stream/{task_id}")
async def stream_execution_output(
    task_id: str,
    tag: str,
    session: Dict = Depends(require_session)
):
    """実行中の出力をストリーミング（SSE）"""
    # task_idが"latest"の場合は、tagから最新のtask_idを取得
    if task_id == "latest":
        task_id = find_latest_task_id(tag)
        if not task_id:
            raise HTTPException(status_code=404, detail="No task found for tag")
    
    # タスクがrunning_tasksに存在する場合は、既存のキューを使用
    # 存在しない場合は、ファイルから直接読み取る
    task = config.running_tasks.get(task_id)
    stream_queue = None
    read_positions = {}
    
    if task:
        stream_queue = task.get('stream_queue')
        read_positions = task.get('read_positions', {})
    else:
        # 新しいキューを作成
        stream_queue = asyncio.Queue()
        read_positions = {}
        # ファイル監視タスクを開始
        asyncio.create_task(monitor_log_files(task_id, tag, stream_queue, read_positions))

    if not stream_queue:
        raise HTTPException(status_code=400, detail="Streaming not available for this task")

    async def generate():
        """SSEイベントを生成"""
        try:
            while True:
                try:
                    # タイムアウト付きでキューから読み取る
                    stream_type, data = await asyncio.wait_for(stream_queue.get(), timeout=0.5)
                    
                    if stream_type == 'status':
                        # 最終状態を送信して終了
                        yield f"data: {json.dumps({'type': 'status', 'status': data['status'], 'output': data.get('output', ''), 'error': data.get('error', '')})}\n\n"
                        break
                    else:
                        # 出力データを送信
                        yield f"data: {json.dumps({'type': stream_type, 'data': data})}\n\n"
                        
                except asyncio.TimeoutError:
                    # タイムアウト時はタスクの状態を確認
                    if task and task['status'] in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                        # 残りの出力を処理
                        while not stream_queue.empty():
                            stream_type, data = await stream_queue.get()
                            if stream_type == 'status':
                                yield f"data: {json.dumps({'type': 'status', 'status': data['status'], 'output': data.get('output', ''), 'error': data.get('error', '')})}\n\n"
                                break
                            else:
                                yield f"data: {json.dumps({'type': stream_type, 'data': data})}\n\n"
                        # 最終状態を送信
                        if task:
                            yield f"data: {json.dumps({'type': 'status', 'status': task['status'], 'output': task.get('output', ''), 'error': task.get('error', '')})}\n\n"
                        break
                    continue

        except Exception as e:
            run_block_logger.exception(f"Error in stream generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/execute/stop")
async def stop_execution(request: StopRequest, session: Dict = Depends(require_session)):
    """実行を停止"""
    task_id = request.task_id

    if task_id not in config.running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = config.running_tasks[task_id]

    if task['status'] not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        return {
            "task_id": task_id,
            "status": task['status'],
            "message": "Task is not running"
        }

    # Executerのstopメソッドを呼び出して停止処理を実行
    executor = task.get('executor')
    if executor:
        executor.stop()
    else:
        # executorが存在しない場合はエラー
        run_block_logger.warning(f"[{task_id}] Executor not found for task")
        task['status'] = ExecutionStatus.CANCELLED
        task['error'] = "Execution cancelled by user"

    return {
        "task_id": task_id,
        "status": ExecutionStatus.CANCELLED,
        "message": "Execution stopped"
    }


@app.post("/api/execute/{task_id}/input")
async def send_input(task_id: str, request: InputRequest, session: Dict = Depends(require_session)):
    """実行中のプロセスにtmux send-keysで入力を送信"""
    if task_id not in config.running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = config.running_tasks[task_id]
    
    # インタラクティブモードでない場合はエラー
    if not task.get('interactive', False):
        raise HTTPException(status_code=400, detail="Task is not in interactive mode")
    
    # tmuxセッション名
    session_name = f"rundmark-{task_id}"
    
    # tmuxセッションが存在するか確認
    check_result = subprocess.run(
        ['tmux', 'has-session', '-t', session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if check_result.returncode != 0:
        # より詳細なエラーメッセージを返す
        run_block_logger.warning(f"[{task_id}] Tmux session '{session_name}' not found for input")
        raise HTTPException(status_code=400, detail=f"Tmux session '{session_name}' not found. Task may have completed or not started yet.")

    try:
        # 入力を送信（改行を追加）
        input_data = request.input
        if input_data.endswith('\n'):
            input_data = input_data[:-1]
        
        # テキストを送信してからEnterを送信
        subprocess.run(['tmux', 'send-keys', '-t', session_name, '-l', input_data], check=True, timeout=5)
        subprocess.run(['tmux', 'send-keys', '-t', session_name, 'Enter'], check=True, timeout=5)
        
        return {
            "task_id": task_id,
            "message": "Input sent successfully",
            "input_length": len(request.input)
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to send input via tmux: {str(e)}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout while sending input via tmux")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send input: {str(e)}")


@app.delete("/api/execute/{task_id}")
async def cleanup_task(task_id: str, session: Dict = Depends(require_session)):
    """タスクをクリーンアップ"""
    if task_id in config.running_tasks:
        task = config.running_tasks[task_id]
        
        # Executerのstopメソッドを呼び出して停止処理を実行
        executor = task.get('executor')
        if executor:
            executor.stop()
        
        del config.running_tasks[task_id]
        return {"message": "Task cleaned up"}
    return {"message": "Task not found"}
