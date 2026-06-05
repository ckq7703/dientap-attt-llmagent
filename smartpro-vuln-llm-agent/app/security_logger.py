"""
security_logger.py
------------------
Ghi toàn bộ hoạt động của LLM Agent ra file JSON (một dòng một event).
Không phân tích, không phân loại — để Wazuh đọc và xử lý.

Log file: LOG_DIR/app.log  (rotation 10MB × 5)
"""

import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

# ─── Cấu hình đường dẫn log ──────────────────────────────────────────────────
_preferred = os.environ.get("LLM_LOG_DIR", "/var/log/llm-agent")
try:
    os.makedirs(_preferred, exist_ok=True)
    _test = os.path.join(_preferred, ".write_test")
    open(_test, "w").close()
    os.remove(_test)
    LOG_DIR = _preferred
except (PermissionError, OSError):
    # Fallback: thư mục logs/ trong project khi chạy local
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(LOG_DIR, exist_ok=True)

APP_LOG = os.path.join(LOG_DIR, "app.log")

# ─── Logger ──────────────────────────────────────────────────────────────────
def _build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        APP_LOG, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s",
        json_ensure_ascii=False
    ))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


_logger = _build_logger("llm_agent")


# ─── Public API ───────────────────────────────────────────────────────────────

def new_session_id() -> str:
    """Sinh session ID mới để theo dõi theo cuộc hội thoại."""
    return uuid.uuid4().hex[:8]


def log_user_prompt(session_id: str, prompt: str) -> None:
    """Ghi lại câu hỏi thô của người dùng."""
    _logger.info("", extra={
        "event": "user_prompt",
        "session_id": session_id,
        "user_prompt": prompt[:2000],
        "app": "llm-agent",
    })


def log_tool_call(session_id: str, tool_name: str, tool_input: str) -> None:
    """Ghi lại mỗi lần agent gọi tool."""
    _logger.info("", extra={
        "event": "tool_call",
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": str(tool_input)[:1000],
        "app": "llm-agent",
    })


def log_tool_error(session_id: str, tool_name: str, error: str) -> None:
    """Ghi lại lỗi trả về từ tool."""
    _logger.info("", extra={
        "event": "tool_error",
        "session_id": session_id,
        "tool_name": tool_name,
        "error": str(error)[:1000],
        "app": "llm-agent",
    })


def log_sql_query(session_id: str, query: str) -> None:
    """Ghi lại câu SQL thực thi."""
    _logger.info("", extra={
        "event": "sql_query",
        "session_id": session_id,
        "sql_query": query[:2000],
        "app": "llm-agent",
    })


def log_agent_response(session_id: str, response: str,
                       intermediate_steps_count: int = 0) -> None:
    """Ghi lại câu trả lời cuối của agent."""
    _logger.info("", extra={
        "event": "agent_response",
        "session_id": session_id,
        "agent_response": response[:2000],
        "intermediate_steps": intermediate_steps_count,
        "app": "llm-agent",
    })
