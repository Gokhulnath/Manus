from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageTask(Enum):
    CHAT = "chat"
    SUMMARIZE = "summarize"
    ANALYSE = "analyse"


class MessageStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"