# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:58:56 UTC+08:00
"""

from ._structure import LoggerConfigStructure, LoggerRecordStructure
from ._registry import LoggerRegistry
from ._enums import LogLevelEnum


class Logger:

    def __init__(self, name: str, dirname: str = "", depth: int | None = None):
        self._name = name
        self._dirname = dirname
        self._depth = depth
        self._registry = LoggerRegistry.get_instance()

        if name:
            self._registry.register_logger_file(name, dirname)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dirname(self):
        return self._dirname

    def _emit(self, level: LogLevelEnum, msg: str, depth: int, **kwargs) -> None:
        if self._depth is not None:
            depth += self._depth

        record = LoggerRecordStructure(
            name=self._name,
            level=level.upper(),
            message=msg,
            depth=depth,
            extra=kwargs or {}
        )
        self._registry.route(record)

    def trace(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.TRACE, msg, depth, **kwargs)

    def debug(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.DEBUG, msg, depth, **kwargs)

    def info(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.INFO, msg, depth, **kwargs)

    def success(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.SUCCESS, msg, depth, **kwargs)

    def warning(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.WARNING, msg, depth, **kwargs)

    def error(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.ERROR, msg, depth, **kwargs)

    def critical(self, msg: str, depth: int = 0, **kwargs) -> None:
        self._emit(LogLevelEnum.CRITICAL, msg, depth, **kwargs)


class LogManager:
    _configured: bool = False

    @classmethod
    def configure(cls, config: LoggerConfigStructure) -> None:
        LoggerRegistry.get_instance().configure(config)
        cls._configured = True

    @classmethod
    def get_config(cls) -> LoggerConfigStructure:
        registry = LoggerRegistry.get_instance()
        if registry.config is None:
            raise RuntimeError("LoggerRegistry is not configured yet.")
        return registry.config

    @classmethod
    def get_logger(cls, name: str = "", /, *, dirname: str = "", depth: int = 0) -> Logger:
        if not cls._configured:
            LoggerRegistry.get_instance().ensure_default()
            cls._configured = True
        return Logger(name, dirname, depth)

    @classmethod
    def reset(cls) -> None:
        LoggerRegistry.reset()
        cls._configured = False

    @classmethod
    def set_level(cls, prefix: str, level: str) -> None:
        LoggerRegistry.get_instance().set_level(prefix, level)

    @classmethod
    def get_registry(cls) -> LoggerRegistry:
        return LoggerRegistry.get_instance()
