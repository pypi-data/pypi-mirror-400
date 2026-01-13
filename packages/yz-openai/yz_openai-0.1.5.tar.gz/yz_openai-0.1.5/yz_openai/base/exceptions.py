"""
异常定义与错误码映射
"""
from typing import Optional
from enum import Enum


class YzOpenAIErrorCode(Enum):
    """YZ-OpenAI 错误码定义

    格式: (错误码, 错误信息)
    """
    # LLM 基础错误 (30000001-30000099)
    API_KEY_ERROR = (30000001, "API key 错误")
    API_ERROR = (30000002, "API 错误")
    TIMEOUT_ERROR = (30000003, "请求超时")
    AUTHENTICATION_ERROR = (30000004, "认证错误")
    RATE_LIMIT_ERROR = (30000005, "速率限制错误")
    INVALID_REQUEST_ERROR = (30000006, "无效请求错误")
    NO_PROVIDER_ERROR = (30000007, "无效provider错误")
    CONFIG_ERROR = (30000008, "配置错误")
    VOLCENGINE_CONFIG_ERROR = (30000009, "火山引擎配置错误")
    VOLCENGINE_JSON_DECODE_ERROR = (30000010, "火山引擎 JSON 解析错误")

    # Podcast TTS 相关错误 (30000100-30000199)
    PODCAST_ERROR = (30000100, "Podcast TTS 错误")
    PODCAST_CONNECTION_ERROR = (30000101, "Podcast 连接错误")
    PODCAST_ROUND_ERROR = (30000102, "Podcast 轮次处理错误")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class YzOpenAIException(Exception):
    """YZ-OpenAI 异常基类"""

    def __init__(
        self,
        error_code: YzOpenAIErrorCode,
        message: Optional[str] = None,
    ) -> None:
        """
        初始化 YZ-OpenAI 异常

        Args:
            error_code: 错误码枚举
            message: 自定义错误信息，如果不提供则使用默认信息
        """
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)
