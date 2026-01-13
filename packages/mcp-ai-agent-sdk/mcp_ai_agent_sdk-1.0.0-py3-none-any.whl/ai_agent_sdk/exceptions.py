"""
AI Agent SDK 异常类
"""


class AIAgentError(Exception):
    """AI Agent SDK 基础异常"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(AIAgentError):
    """认证错误（API Key 无效）"""
    pass


class DatabaseError(AIAgentError):
    """数据库连接或操作错误"""
    pass


class QueryError(AIAgentError):
    """SQL 查询错误"""
    pass


class RateLimitError(AIAgentError):
    """请求频率超限"""
    pass


class ValidationError(AIAgentError):
    """参数验证错误"""
    pass
