###############################
##  TOOLS
from langchain.agents import Tool
from langchain.tools import BaseTool
from langchain.tools import StructuredTool
import streamlit as st
from datetime import date
from dotenv import load_dotenv
import json
import re
import os
from app.security_logger import log_tool_call, log_tool_error

load_dotenv()

# Cache userId hợp lệ không còn cần thiết cho detection tại app nữa
def get_current_user(input: str):
    session_id = st.session_state.get("session_id", "unknown")
    from app.database import TransactionDb
    db = TransactionDb()
    user = db.get_user(1)
    db.close()
    log_tool_call(session_id, "GetCurrentUser", input)
    return user

get_current_user_tool = Tool(
    name='GetCurrentUser',
    func=get_current_user,
    description="Trả về người dùng hiện tại để truy vấn các giao dịch."
)

def get_transactions(userId: str):
    """Trả về các giao dịch liên kết với userId được cung cấp bằng cách chạy trấn vấn này: SELECT * FROM Transactions WHERE userId = ?."""
    session_id = st.session_state.get("session_id", "unknown")
    log_tool_call(session_id, "GetUserTransactions", userId)
    from app.database import TransactionDb
    try:
        db = TransactionDb(session_id=session_id)
        transactions = db.get_user_transactions(userId)
        db.close()
        return transactions
    except Exception as e:
        log_tool_error(session_id, "GetUserTransactions", str(e))
        return f"Error: {e}"

get_recent_transactions_tool = Tool(
    name='GetUserTransactions',
    func=get_transactions,
    description="Trả về các giao dịch liên kết với userId được cung cấp bằng cách chạy trấn vấn này: SELECT * FROM Transactions WHERE userId = provided_userId."
)