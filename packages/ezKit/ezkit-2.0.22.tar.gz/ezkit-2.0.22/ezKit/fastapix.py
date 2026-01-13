# FastAPI Extensions
# pylint: disable=W0613

import logging
import sys
from datetime import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# --------------------------------------------------------------------------------------------------


def setup_logger(*, debug: bool = False, log_dir: str = "logs"):
    """
    全局日志初始化（幂等、安全、不重复）
    """

    # 1. 确保全局日志只初始化一次
    # 2. 避免日志重复输出

    # 确保日志目录存在
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 移除默认控制台日志器
    # ⭐ 关键：先清空所有 handler，防止重复
    logger.remove()

    # ---------- 控制台日志 ----------
    if debug:
        logger.add(
            sys.stdout,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
            enqueue=True,
            colorize=True,
        )

    # ---------- 文件日志 ----------
    logger.add(
        sink=f"{log_dir}/{'debug' if debug else 'app'}.log",  # 日志文件
        level="DEBUG" if debug else "INFO",  # 记录等级
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function} | {message}",  # 日志格式
        # rotation="200 MB",  # 文件达到 100MB 自动轮转
        rotation=time(0, 0),  # 每天 00:00 切割
        # retention="30 days",  # 保留 7 天日志
        compression="zip",  # 超过的日志自动压缩
        encoding="utf-8",  # 文件编码
        enqueue=True,  # 多线程、多进程安全
        backtrace=True,  # 捕获堆栈追踪
        diagnose=debug,  # 显示变量值, 生产环境建议 False
    )


# --------------------------------------------------------------------------------------------------


def CORS(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=["*"],
    )


# --------------------------------------------------------------------------------------------------


def Response(code: int = 200, data: Any = None, message: str | None = None, status_code: int = 200):
    return JSONResponse(content={"code": code, "data": data, "message": message}, status_code=status_code)


# --------------------------------------------------------------------------------------------------


def exceptions(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP Exception: {exc.detail}")
        return Response(code=exc.status_code, message=f"HTTP Exception: {exc.detail}", status_code=exc.status_code)
        # return JSONResponse(content={"code": exc.status_code, "data": None, "message": exc.detail}, status_code=exc.status_code)

    # 参数验证错误
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request Validation Error: {exc.errors()}")
        return Response(code=422, message=f"Request Validation Error: {exc.errors()}")

    # 参数验证错误
    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"Pydantic Validation Error: {exc.errors()}")
        return Response(code=422, message=f"Pydantic Validation Error: {exc.errors()}")

    # 内部服务错误
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Internal Server Error: {exc}")
        return Response(code=500, message=f"Internal Server Error: {exc}")


# --------------------------------------------------------------------------------------------------


# 兼容 FastAPI/Uvicorn 的 logging（重要）
class InterceptHandler(logging.Handler):
    """Intercept Handler"""

    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

    def write(self, message: str):
        if message.strip():
            logger.info(message.strip())

    def flush(self):
        pass
