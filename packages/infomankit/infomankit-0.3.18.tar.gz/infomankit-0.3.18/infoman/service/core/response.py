# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""
from infoman.service.exception.exception import AppError
from infoman.config import settings as config
from fastapi.responses import ORJSONResponse
import orjson


class ProRJSONResponse(ORJSONResponse):
    def render(self, content) -> bytes:
        return orjson.dumps(
            content,
            option=(
                orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_UTC_Z
            ),
        )


def response(code, msg, data=None):
    result = {"code": code, "message": msg, "data": data}
    return result


def success(data=None, msg=""):
    return response(200, msg, data)


def failed(error: AppError):
    msg = error.message_en
    if not config.DEFAULT_LANGUAGE_IS_EN:
        msg = error.message
    return response(code=error.code, msg=msg)
