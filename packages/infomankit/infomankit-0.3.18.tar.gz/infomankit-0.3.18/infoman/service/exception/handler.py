from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from tortoise.exceptions import (
    OperationalError,
    DoesNotExist,
    IntegrityError,
    ValidationError as MysqlValidationError,
)
from typing import List, Dict, Any, Type
import traceback

from infoman.service.exception.error import DatabaseError, RequestError, AppSystemError
from infoman.service.exception.exception import AppException
from infoman.logger import logger


def format_error_response(
    code: int, message: str, data: Any = None, details: Any = None
) -> Dict[str, Any]:
    response = {"code": code, "message": message, "data": data or {}}
    if details:
        response["details"] = details
    return response


def format_validation_errors(errors: List[Dict]) -> List[Dict[str, str]]:
    formatted_errors = []
    for error in errors:
        loc_path = " -> ".join([str(loc) for loc in error.get("loc", [])])
        formatted_errors.append(
            {
                "field": loc_path,
                "message": error.get("msg", "Unknown error"),
                "type": error.get("type", "unknown"),
                "input": str(error.get("input", "")) if "input" in error else None,
            }
        )
    return formatted_errors


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    """处理 HTTP 异常"""
    logger.warning(
        f"HTTP Exception: status={exc.status_code}, "
        f"detail={exc.detail}, path={request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(code=exc.status_code, message=exc.detail),
        headers=exc.headers,
    )


async def handle_app_exception(_: Request, exc: AppException) -> Response:
    """处理应用自定义异常"""
    logger.error(f"App Exception: code={exc.error_code}, message={exc.message}")
    return JSONResponse(
        format_error_response(code=exc.error_code, message=exc.message), status_code=200
    )


async def mysql_validation_error_handler(
    request: Request, exc: MysqlValidationError
) -> Response:
    """处理 MySQL 验证错误"""
    logger.error(
        f"MySQL Validation Error at {request.url.path}\n"
        f"Error: {exc}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    err = DatabaseError.VALIDATION_ERROR
    return JSONResponse(
        format_error_response(code=err.code, message=err.message, details=str(exc)),
        status_code=200,
    )


async def mysql_integrity_error_handler(
    request: Request, exc: IntegrityError
) -> Response:
    """处理 MySQL 完整性约束错误"""
    error_msg = str(exc)
    logger.error(
        f"MySQL Integrity Error at {request.url.path}\n"
        f"Error: {error_msg}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    # 提取更友好的错误信息
    friendly_message = DatabaseError.INTEGRITY_ERROR.message
    if "Duplicate entry" in error_msg:
        friendly_message = "数据已存在，请勿重复添加"
    elif "foreign key constraint" in error_msg.lower():
        friendly_message = "关联数据不存在或已被引用"

    err = DatabaseError.INTEGRITY_ERROR
    return JSONResponse(
        format_error_response(
            code=err.code, message=friendly_message, details=error_msg
        ),
        status_code=200,
    )


async def mysql_does_not_exist_handler(request: Request, exc: DoesNotExist) -> Response:
    """处理 MySQL 记录不存在错误"""
    logger.warning(f"MySQL Record Not Found at {request.url.path}: {exc}")
    err = DatabaseError.RECORD_NOT_FOUND
    return JSONResponse(
        format_error_response(code=err.code, message=err.message, details=str(exc)),
        status_code=200,
    )


async def mysql_operational_error_handler(
    request: Request, exc: OperationalError
) -> Response:
    """处理 MySQL 操作错误"""
    error_msg = str(exc)
    logger.error(
        f"MySQL Operational Error at {request.url.path}\n"
        f"Error: {error_msg}\n"
        f"Traceback: {traceback.format_exc()}"
    )

    # 提取更友好的错误信息
    friendly_message = DatabaseError.OPERATIONAL_ERROR.message
    if "Lost connection" in error_msg:
        friendly_message = "数据库连接已断开"
    elif "Deadlock" in error_msg:
        friendly_message = "数据库死锁，请稍后重试"

    err = DatabaseError.OPERATIONAL_ERROR
    return JSONResponse(
        format_error_response(
            code=err.code, message=friendly_message, details=error_msg
        ),
        status_code=200,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    """处理请求验证错误"""
    error_details = format_validation_errors(exc.errors())

    logger.warning(
        f"Request Validation Error at {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Errors: {error_details}"
    )

    err = RequestError.VALIDATION_ERROR
    if len(error_details) == 1:
        main_message = f"{error_details[0]['field']}: {error_details[0]['message']}"
    else:
        main_message = f"发现 {len(error_details)} 个验证错误"

    return JSONResponse(
        format_error_response(
            code=err.code, message=main_message, details=error_details
        ),
        status_code=200,
    )


async def pydantic_validation_handler(
    request: Request, exc: ValidationError
) -> Response:
    """处理 Pydantic 验证错误"""
    error_details = format_validation_errors(exc.errors())

    logger.warning(
        f"Pydantic Validation Error at {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Errors: {error_details}"
    )

    err = RequestError.VALIDATION_ERROR
    # 生成更友好的错误消息
    if len(error_details) == 1:
        main_message = f"{error_details[0]['field']}: {error_details[0]['message']}"
    else:
        main_message = f"数据验证失败，发现 {len(error_details)} 个错误"

    return JSONResponse(
        format_error_response(
            code=err.code, message=main_message, details=error_details
        ),
        status_code=200,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """处理未捕获的异常"""
    logger.error(
        f"Unhandled Exception at {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Exception Type: {type(exc).__name__}\n"
        f"Error: {str(exc)}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    err = AppSystemError.UNKNOWN_ERROR
    return JSONResponse(
        format_error_response(
            code=err.code,
            message="服务器内部错误，请稍后重试",
            details=str(exc) if logger.level == "DEBUG" else None,
        ),
        status_code=500,
    )


EXCEPTION_HANDLERS: Dict[Type[Exception], Any] = {
    # 应用异常
    AppException: handle_app_exception,
    # HTTP 异常
    HTTPException: http_exception_handler,
    # 请求验证异常
    RequestValidationError: validation_exception_handler,
    ValidationError: pydantic_validation_handler,
    # MySQL 异常
    DoesNotExist: mysql_does_not_exist_handler,
    IntegrityError: mysql_integrity_error_handler,
    MysqlValidationError: mysql_validation_error_handler,
    OperationalError: mysql_operational_error_handler,
    # 兜底异常
    Exception: unhandled_exception_handler,
}


def register_exception_handlers(app) -> None:
    for exception_class, handler_func in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler_func)
        # logger.info(f"Registered handler for {exception_class.__name__}")
