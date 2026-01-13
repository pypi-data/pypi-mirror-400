"""
Middleware utilities for FastAPI
"""

import os
from typing import List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse
from starlette.requests import Request


class NextJSRouteMiddleware(BaseHTTPMiddleware):
    """
    处理 Next.js 静态导出的路由中间件

    当请求返回 404 时，尝试查找对应的 .html 文件
    """

    def __init__(
        self,
        app,
        static_dir: str,
        skip_prefixes: Optional[List[str]] = None,
        index_file: str = "index",
    ):
        """
        初始化中间件

        Args:
            app: ASGI 应用
            static_dir: 静态文件目录路径
            skip_prefixes: 要跳过的路径前缀列表，这些路径不会被处理
            index_file: 根路径对应的默认文件名（不含扩展名）
        """
        super().__init__(app)
        self.static_dir = static_dir
        self.skip_prefixes = skip_prefixes or []
        self.index_file = index_file

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        path = request.url.path

        # 跳过指定前缀的路由
        if any(path.startswith(prefix) for prefix in self.skip_prefixes):
            return await call_next(request)

        # 尝试直接处理
        response = await call_next(request)

        # 如果是 404 且不是 _next 静态资源，尝试查找 .html 文件
        if response.status_code == 404 and not path.startswith("/_next"):
            # 移除开头的斜杠
            clean_path = path.lstrip("/")
            if clean_path == "":
                clean_path = self.index_file

            html_file = os.path.join(self.static_dir, f"{clean_path}.html")

            if os.path.exists(html_file):
                return FileResponse(html_file, media_type="text/html")

        return response
