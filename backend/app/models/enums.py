# app/models/enums.py
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    WORKER = "WORKER"

    def __str__(self) -> str:
        return self.value
