# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/1/12 10:27
# Author     ：Maxwell
# Description：
"""
import time
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from infoman.logger import logger
from infoman.utils.http.info import ClientInfoExtractor
from starlette.responses import StreamingResponse, FileResponse


class LoggingMiddleware(BaseHTTPMiddleware):

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f}MB"

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        client_ip = ClientInfoExtractor.client_ip(request=request)
        path = request.url.path[:200]

        try:
            response = await call_next(request)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            # ===== 1. 检测特殊响应类型 =====
            if isinstance(response, (StreamingResponse, FileResponse)):
                content_length = response.headers.get("content-length", "unknown")
                logger.info(
                    f"Req: ip={client_ip}, elapsed_ms={elapsed_ms}, "
                    f"path={path}, status={response.status_code}, "
                    f"type=streaming, size={content_length}"
                )
                return response

            # ===== 2. 检测 Content-Length =====
            content_length = response.headers.get("content-length")
            if content_length:
                response_size = int(content_length)
                logger.info(
                    f"Req: ip={client_ip}, elapsed_ms={elapsed_ms}, "
                    f"path={path}, status={response.status_code}, "
                    f"size={self.format_size(response_size)}"
                )
                return response

            # ===== 3. 读取内容计算大小 =====
            response_body = b""
            async for chunk in response.body:
                response_body += chunk

            response_size = len(response_body)

            logger.info(
                f"Req: ip={client_ip}, elapsed_ms={elapsed_ms}, "
                f"path={path}, status={response.status_code}, "
                f"size={self.format_size(response_size)}"
            )

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            logger.error(
                f"Global error: ip={client_ip}, path={path}, "
                f"traceback={traceback.format_exc()}"
            )
            return Response(content="Server error.", status_code=500)
