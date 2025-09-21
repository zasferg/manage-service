from enums import Enum
from typing import Any
from pydantic_core import (
    CoreSchema,
    PydanticSerializationError,
    PydanticCustomError,
    SchemaSerializer,
    SchemaValidator,
    core_schema,
)


class RolesEnum(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class TaskStatuses(str, Enum):
    OPENED = "opened"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @classmethod
    def check_for_value(cls, value):
        if isinstance(value, str) and value in (
            cls.OPENED,
            cls.IN_PROGRESS,
            cls.COMPLETED,
        ):
            return True


class Events(str, Enum):
    TASK = "task"
    MEETING = "meeting"
