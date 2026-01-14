# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 23:21
# Author     ：Maxwell
# Description：
"""
import jwt
from datetime import timedelta, datetime
from enum import Enum
from typing import Optional, Dict, Any, TypeVar

from fastapi import Request, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt import PyJWTError
from pydantic import ValidationError, BaseModel

from infoman.config import settings as config
from infoman.service.exception import exception
from infoman.service.exception import error

T = TypeVar("T")


class SecurityConstants:
    REDIS_USER_KEY_PREFIX = "U_API_AUTH_KEY_"
    REDIS_OPEN_API_KEY_PREFIX = "O_API_AUTH_KEY_"
    REDIS_CACHE_EXPIRE = 3 * 3600


class TokenPayload(BaseModel):
    exp: Optional[datetime] = None
    user_id: Optional[int] = None


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    OPEN_API = "open_api"


class JWTHandler:

    @staticmethod
    def create_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        token_type: TokenType = TokenType.ACCESS,
    ) -> str:
        payload = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        elif token_type == TokenType.ACCESS:
            expire = datetime.utcnow() + timedelta(
                minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:
            expire = datetime.utcnow() + timedelta(days=365)
        payload.update({"exp": expire, "token_type": token_type})
        return jwt.encode(
            payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise exception.AppException(error.SecurityError.TOKEN_EXPIRED)
        except (jwt.InvalidTokenError, PyJWTError, ValidationError):
            raise exception.AppException(error.SecurityError.INVALID_CREDENTIALS)

    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        try:
            payload = JWTHandler.decode_token(token)
            token_data = TokenPayload(**payload)
            if token_data.exp and token_data.exp < datetime.utcnow():
                raise exception.AppException(error.SecurityError.TOKEN_EXPIRED)
            return token_data
        except ValidationError:
            raise exception.AppException(error.SecurityError.INVALID_TOKEN)


class TokenExtractor:

    @staticmethod
    def get_user_id(token: str) -> Optional[int]:
        try:
            payload = JWTHandler.decode_token(token)
            return payload.get("user_id")
        except Exception:
            return None

    @staticmethod
    def get_open_user_id(token: str) -> Optional[int]:
        try:
            payload = JWTHandler.decode_token(token)
            return payload.get("open_user_id")
        except Exception:
            return None
