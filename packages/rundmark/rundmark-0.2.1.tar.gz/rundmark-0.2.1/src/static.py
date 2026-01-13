from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

def setup_static(app: FastAPI, STATIC_DIR: Path):
    # 静的ファイル（JS, CSS, 画像など）を配信
    if STATIC_DIR.exists():
        app.mount(
            "/notebook/assets",
            StaticFiles(directory=STATIC_DIR / "assets"),
            name="static_assets"
        )
        
        # faviconなどのルートレベルの静的ファイル
        @app.get("/notebook/favicon.ico")
        async def favicon():
            favicon_path = STATIC_DIR / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(favicon_path)
            raise HTTPException(status_code=404)
        
        @app.get("/notebook")
        @app.get("/notebook/{path:path}")
        async def serve_frontend(path: str = ""):
            """フロントエンドを配信（SPA用）"""
            # 静的ファイルのリクエスト（拡張子がある場合）
            if path and "." in path and not path.endswith(".html"):
                file_path = STATIC_DIR / path
                if file_path.exists() and file_path.is_file():
                    return FileResponse(file_path)
            
            # SPA用: すべてのルートをindex.htmlにフォールバック
            index_path = STATIC_DIR / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Frontend not built. Run 'npm run build' first."
                )
    else:
        @app.get("/notebook")
        @app.get("/notebook/{path:path}")
        async def frontend_not_built():
            raise HTTPException(
                status_code=503,
                detail="Frontend not built. Run 'npm run build' first."
            )
