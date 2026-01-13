from enum import Enum


class TeamMemberRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
