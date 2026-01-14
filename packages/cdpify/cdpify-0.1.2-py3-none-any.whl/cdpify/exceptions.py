from typing import Any


class CDPException(Exception): ...


class CDPConnectionException(CDPException): ...


class CDPCommandException(CDPException):
    def __init__(self, error_data: dict[str, Any]) -> None:
        self.code: int = error_data.get("code", -1)
        self.message: str = error_data.get("message", "Unknown error")
        self.data: Any = error_data.get("data")
        super().__init__(f"CDP Error {self.code}: {self.message}")


class CDPTimeoutException(CDPException): ...
