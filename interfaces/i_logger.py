from typing import Protocol, Any

class ILogger(Protocol):
    def info(self, msg: str, **kwargs: Any) -> None:
        ...

    def error(self, msg: str, exc: Exception, **kwargs: Any) -> None:
        ...