from enum import Enum


class ClusterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

    def __str__(self) -> str:
        return str(self.value)
