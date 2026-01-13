"""Utils Library"""

import re
from collections.abc import Callable, Iterable
from datetime import date, datetime, timezone
from decimal import Decimal
from functools import lru_cache
from itertools import islice
from os import environ
from pathlib import Path
from typing import Any
from uuid import UUID

import tomllib
from loguru import logger

# --------------------------------------------------------------------------------------------------

DEBUG = environ.get("DEBUG")

# --------------------------------------------------------------------------------------------------


def isTrue(target: object, typeClass: Any) -> bool:
    """检查对象是否为真"""

    # 常见布尔类型:
    #
    #     Boolean     bool            False
    #     Numbers     int/float       0/0.0
    #     String      str             ""
    #     List        list/tuple/set  []/()/{}
    #     Dictionary  dict            {}
    #     Set         set             set()
    #
    # 查看变量类型: type(x)
    #
    # 判断变量类型: isinstance(x, str)
    #
    # 函数使用 callable(func) 判断
    #
    # 判断多个类型:
    #
    #   isTrue("abc", (str, int))
    #   isTrue("abc", (str | int))
    #
    # all() 用于检查一个可迭代对象(如列表、元组、集合等)中的 所有 元素是否为 真值 (truthy), 所有元素为真, 返回 True
    # any() 用于检查一个可迭代对象(如列表、元组、集合等)中的 某个 元素是否为 真值 (truthy), 某个元素为真, 返回 True
    # 与 all() 作用相反的 not any(), 可以用来检查所有元素是否为 假值 (falsy), any() 中所有元素为假, not any() 返回 True
    #
    # return target not in [False, None, 0, 0.0, '', (), [], {}, set(), {*()}, {*[]}, {*{}}, {*set()}]

    try:

        if isinstance(target, typeClass) and target:
            return True

        return False

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return False


# --------------------------------------------------------------------------------------------------


def load_toml_file(file: str) -> dict:
    """Load TOML file"""

    info: str = "load toml file"

    try:

        logger.info(f"{info} [ start ]")

        # 不要加 encoding="utf-8" 参数, 否则会报错:
        # binary mode doesn't take an encoding argument
        with open(file, "rb") as _file:
            config = tomllib.load(_file)

        logger.success(f"{info} [ success ]")

        return config

    except Exception as e:

        logger.error(f"{info} [ error ]")

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return {}


# --------------------------------------------------------------------------------------------------


def map_filter(iterable: Iterable, func: Callable) -> list:
    """对 iterable 执行 func, 并保留为 True 的返回值"""

    try:

        return [x for x in map(func, iterable) if x]

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return []


# --------------------------------------------------------------------------------------------------


def check_dict_values_incorrect(
    data: dict[str, object],
    errors: object | Iterable[object] | None = None,
    include_keys: list[str] | None = None,
    exclude_keys: list[str] | None = None,
    regex: str | None = None,
) -> bool:
    """检查字典的值是否存在错误值"""

    # 支持:
    #
    #   target: 单值 或 多值（列表/元组）
    #   regex: 值是否匹配某正则表达式
    #   include_keys / exclude_keys: 指定检查的 key 范围
    #
    # 匹配规则(满足任一条件即可):
    #
    #   value 等于 target 或 在 target 列表里
    #   value 与 regex 匹配
    #
    # 参数:
    #
    #   data            dict[str, object]       待检查的字典
    #   errors          object|Iterable|None    指定匹配值或值列表
    #   include_keys    list[str]|None          只检查这些 key
    #   exclude_keys    list[str]|None          排除指定 key
    #   regex           str|None                正则匹配（自动转换成 re.Pattern）
    #
    # 返回:
    #
    #   bool
    #
    # 所有最终 keys 的值满足任一匹配条件返回 False, 否则 True

    try:

        # -----------------------
        # 处理 include / exclude 逻辑
        # -----------------------
        if include_keys is not None:
            keys = set(include_keys)
        else:
            keys = set(data.keys())

        if exclude_keys is not None:
            keys -= set(exclude_keys)

        # 若没有 key 需要检查 -> 默认 True
        if not keys:
            return False

        # -----------------------
        # 处理 target（单值 or 列表）
        # -----------------------
        if isinstance(errors, Iterable) and not isinstance(errors, (str, bytes)):
            error_set = set(errors)
        else:
            error_set = {errors}

        # -----------------------
        # 处理正则
        # -----------------------
        pattern = re.compile(regex) if regex else None

        # -----------------------
        # 核心检查逻辑
        # -----------------------
        for k in keys:

            value = data.get(k)

            # 匹配 target
            if value in error_set:
                return False

            # 匹配 类型
            # if isinstance(types, list) and types:
            #     if any(isinstance(value, type) for type in types):
            #         return False

            # 匹配正则
            if pattern is not None:
                if isinstance(value, str) and pattern.search(value):
                    return False

        return True

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return False


# --------------------------------------------------------------------------------------------------


def timestamp_to_datetime(timestamp: int | float, tz: timezone = timezone.utc) -> datetime | None:
    """Unix Timestamp 转换为 Datatime"""

    try:

        if not isinstance(timestamp, (int, float)):
            return None

        return (datetime.fromtimestamp(timestamp, tz=tz)).replace(tzinfo=None)

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return None


# --------------------------------------------------------------------------------------------------


@lru_cache(maxsize=None)
def compile_patterns(patterns: tuple[str, ...]) -> re.Pattern | None:
    """把 list 编译为一个超大正则 (带缓存)"""

    try:

        combined = "|".join(map(re.escape, patterns))

        return re.compile(combined)

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return None

    # 测试
    # a = compile_patterns(123)
    # if not a:
    #     logger.error("compile_patterns error")
    #     return None
    # print(a.match("a"))


# --------------------------------------------------------------------------------------------------


def json_safe(value: Any) -> Any:
    """将值转换为 JSON 可序列化类型"""
    # 处理日期和时间, 否则会报错:
    # Object of type datetime is not JSON serializable
    # 注意: datetime 要在 date 之前

    try:

        if isinstance(value, datetime):
            return value.isoformat(sep=" ")

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        if isinstance(value, UUID):
            return str(value)

        return value

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return value


# --------------------------------------------------------------------------------------------------


def list_split(data: list, number: int, equally: bool = False) -> list | None:
    """列表分割"""

    # 列表分割
    #
    # 默认: 将 list 以 number 个元素为一个子 list 分割
    #
    #   data = [1, 2, 3, 4, 5, 6, 7]                                奇数个元素
    #   list_split(data, 2) -> [[1, 2], [3, 4], [5, 6], [7]]        将 data 以 2个元素 为一个 list 分割
    #   list_split(data, 3) -> [[1, 2, 3], [4, 5, 6], [7]]          将 data 以 3个元素 为一个 list 分割
    #
    #   data = [1, 2, 3, 4, 5, 6, 7, 8]                             偶数个元素
    #   list_split(data, 2) -> [[1, 2], [3, 4], [5, 6], [7, 8]]     将 data 以 2个元素 为一个 list 分割
    #   list_split(data, 3) -> [[1, 2, 3], [4, 5, 6], [7, 8]]       将 data 以 3个元素 为一个 list 分割
    #
    # equally 为 True 时, 将 list 平均分成 number 个元素的子 list
    #
    #   data = [1, 2, 3, 4, 5, 6, 7]                                奇数个元素
    #   list_split(data, 2, True) -> [[1, 2, 3, 4], [5, 6, 7]]      将 data 平均分成 2个子list
    #   list_split(data, 3, True) -> [[1, 2, 3], [4, 5, 6], [7]]    将 data 平均分成 3个子list
    #
    #   data = [1, 2, 3, 4, 5, 6, 7, 8]                             偶数个元素
    #   list_split(data, 2, True) -> [[1, 2, 3, 4], [5, 6, 7, 8]]   将 data 平均分成 2个子list
    #   list_split(data, 3, True) -> [[1, 2, 3], [4, 5, 6], [7, 8]] 将 data 平均分成 3个子list

    try:

        # 要将列表平均分成 n 个子列表
        if equally:
            it = iter(data)
            chunk_size = (len(data) + number - 1) // number  # 每组至少多少个元素
            return [list(islice(it, chunk_size)) for _ in range(number)]

        # 将列表按每 n 个元素为一个列表进行分割
        it = iter(data)
        return [list(islice(it, number)) for _ in range((len(data) + number - 1) // number)]

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return None


# --------------------------------------------------------------------------------------------------


def list_print_by_step(data: list, step: int, separator: str = " ") -> bool:
    """根据 步长 和 分隔符 有规律的打印列表中的数据"""

    try:

        # 打印
        for i, v in enumerate(data):

            if i > 0 and i % step == 0:
                print()

            # 每行最后一个 或者 所有数据最后一个, 不打印分隔符
            if ((i % step) == (step - 1)) or ((i + 1) == len(data)):
                print(v, end="")
            else:
                print(v, end=separator)

        print()

        return True

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return False


# --------------------------------------------------------------------------------------------------


def check_file_type(file_object: str, file_type: str) -> bool:
    """检查文件类型"""

    try:

        _file_path = Path(file_object)

        # 文件不存在的情况
        if not _file_path.exists():
            return False

        # 根据 file_type 判断文件类型
        if file_type == "absolute":
            return _file_path.is_absolute()
        elif file_type == "block_device":
            return _file_path.is_block_device()
        elif file_type == "dir":
            return _file_path.is_dir()
        elif file_type == "fifo":
            return _file_path.is_fifo()
        elif file_type == "file":
            return _file_path.is_file()
        elif file_type == "mount":
            return _file_path.is_mount()
        elif file_type == "reserved":
            return _file_path.is_reserved()
        elif file_type == "socket":
            return _file_path.is_socket()
        elif file_type == "symlink":
            return _file_path.is_symlink()

        # 如果 file_type 不匹配任何已知类型，返回 False
        return False

    except Exception as e:

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return False
