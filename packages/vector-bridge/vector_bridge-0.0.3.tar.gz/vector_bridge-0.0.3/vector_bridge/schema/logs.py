from datetime import datetime

from pydantic import BaseModel


class LogMessage(BaseModel):
    error_traceback: str
    log_messages: str


class Log(BaseModel):
    integration_id: str
    user_id: str
    api_key_hash: str
    timestamp: datetime
    method: str
    url: str
    status_code: int
    process_time: float
    log_message: LogMessage
    expire_at: datetime


class PaginatedLogs(BaseModel):
    logs: list[Log]
    limit: int
    last_evaluated_key: str | None
    has_more: bool
