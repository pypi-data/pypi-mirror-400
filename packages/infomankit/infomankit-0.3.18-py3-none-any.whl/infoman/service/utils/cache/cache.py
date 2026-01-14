from infoman.utils.log import logger
from functools import wraps
from typing import (
    Any,
    Callable,
    Optional,
    Type,
    TypeVar,
    get_type_hints,
    get_origin,
    get_args,
)
import json
from pydantic import BaseModel
import inspect


T = TypeVar("T")


def redis_cache(
    prefix: str,
    ttl: int = 3600,
    model: Optional[Type[BaseModel]] = None,  # ✅ 新增：指定返回模型
    auto_detect: bool = True,  # ✅ 新增：自动检测返回类型
):
    """
    Redis 缓存装饰器（支持 Pydantic 模型反序列化）

    Args:
        prefix: 缓存键前缀
        ttl: 过期时间（秒）
        model: 返回的 Pydantic 模型类（可选，如果指定则强制使用）
        auto_detect: 是否自动从函数签名检测返回类型

    Examples:
        # 方式 1：手动指定模型
        @redis_cache(prefix="config", ttl=3600, model=ConfigKeyLogSchema)
        async def get_config(pub_key: str):
            ...

        # 方式 2：自动检测（推荐）
        @redis_cache(prefix="config", ttl=3600)
        async def get_config(pub_key: str) -> ConfigKeyLogSchema:
            ...

        # 方式 3：列表类型
        @redis_cache(prefix="configs", ttl=3600)
        async def list_configs() -> list[ConfigKeyLogSchema]:
            ...
    """

    def decorator(func: Callable) -> Callable:
        # ✅ 自动检测返回类型
        return_type = model
        is_list = False

        if auto_detect and not return_type:
            type_hints = get_type_hints(func)
            if "return" in type_hints:
                hint = type_hints["return"]

                # 处理 Optional[Model]
                origin = get_origin(hint)
                if origin is Optional or str(origin) == "typing.Union":
                    args = get_args(hint)
                    for arg in args:
                        if arg is not type(None) and (
                            isinstance(arg, type) and issubclass(arg, BaseModel)
                        ):
                            return_type = arg
                            break
                elif origin is list:
                    args = get_args(hint)
                    if (
                        args
                        and isinstance(args[0], type)
                        and issubclass(args[0], BaseModel)
                    ):
                        return_type = args[0]
                        is_list = True

                # 直接是 Model
                elif isinstance(hint, type) and issubclass(hint, BaseModel):
                    return_type = hint

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 获取 Redis 客户端
            redis_client = _get_redis_client(args, kwargs)

            if not redis_client:
                logger.warning("Redis client not found, executing without cache")
                return await func(*args, **kwargs)

            # 构建缓存键
            cache_key = f"{prefix}:{_build_cache_key(func, args, kwargs)}"

            # ==================== 读取缓存 ====================
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    cached_data = json.loads(cached)
                    logger.debug(f"Cache HIT: {cache_key}")

                    if return_type:
                        if is_list:
                            return [return_type(**item) for item in cached_data]
                        else:
                            return return_type(**cached_data)
                    return cached_data

            except Exception as e:
                logger.error(f"Cache read error for {cache_key}: {e}")

            # ==================== 执行函数 ====================
            result = await func(*args, **kwargs)

            if result is None:
                return None

            # ==================== 写入缓存 ====================
            try:
                cache_data = _serialize_result(result)
                json_str = json.dumps(cache_data, default=str, ensure_ascii=False)
                await redis_client.setex(cache_key, ttl, json_str)
                logger.debug(f"Cache SET: {cache_key}")

            except Exception as e:
                logger.error(f"Cache write error for {cache_key}: {e}")

            return result

        return wrapper

    return decorator


def _serialize_result(result: Any) -> Any:
    """序列化结果"""
    if isinstance(result, BaseModel):
        return result.model_dump()
    elif isinstance(result, list):
        return [
            item.model_dump() if isinstance(item, BaseModel) else item
            for item in result
        ]
    elif isinstance(result, dict):
        return {
            k: v.model_dump() if isinstance(v, BaseModel) else v
            for k, v in result.items()
        }
    return result


def _get_redis_client(args: tuple, kwargs: dict):

    for arg in list(args) + list(kwargs.values()):
        if hasattr(arg, "app") and hasattr(arg.app, "state"):
            redis = getattr(arg.app.state, "redis_client", None)
            if redis:
                return redis

    return None


def _build_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """构建缓存键"""
    key_parts = [func.__name__]

    # 获取函数签名
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    # 处理位置参数（跳过 self 和 request）
    for i, arg in enumerate(args):
        if i == 0 and param_names and param_names[0] in ["self", "cls"]:
            continue
        if _is_cacheable_value(arg):
            key_parts.append(str(arg))

    # 处理关键字参数
    for k, v in sorted(kwargs.items()):
        if k not in ["req", "request"] and _is_cacheable_value(v):
            key_parts.append(f"{k}={v}")

    return ":".join(key_parts)


def _is_cacheable_value(value: Any) -> bool:
    """判断值是否可用于缓存键"""
    return isinstance(value, (str, int, float, bool))
