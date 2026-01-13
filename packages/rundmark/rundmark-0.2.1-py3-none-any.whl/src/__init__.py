from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # Startup処理（必要に応じて追加）
    yield
    # Shutdown処理
    # configとapp_loggerは後で設定される
    from src.config import get_config
    import logging
    
    config = get_config()
    app_logger = logging.getLogger(__name__)
    
    app_logger.info("Shutting down: terminating all running tasks...")
    
    # 実行中のすべてのタスクを終了
    for task_id, task in list(config.running_tasks.items()):
        try:
            # Executorのstopメソッドを呼び出して停止処理を実行
            executor = task.get('executor')
            if executor:
                executor.stop()
            else:
                app_logger.warning(f"[{task_id}] Executor not found, skipping stop")
        except Exception as e:
            app_logger.error(f"Error during shutdown cleanup for task {task_id}: {e}")
    
    app_logger.info(f"Shutdown complete: {len(config.running_tasks)} task(s) processed")

# FastAPIアプリケーションを作成
app = FastAPI(lifespan=lifespan)
