from enum import Enum


class APIKeyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
