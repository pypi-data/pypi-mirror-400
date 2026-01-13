"""
YZ OpenAI 统一客户端
"""
from typing import Optional

from yz_openai.factory import get_client, get_voice_client

class YzOpenAI:
    """YZ OpenAI 统一客户端"""

    def __init__(
        self,
        provider: str,
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        access_key: Optional[str] = None
    ):
        """
        初始化 YZ OpenAI 客户端

        Args:
            provider: Provider 名称（litellm, volcengine）
            api_key: API 密钥（可选，优先从环境变量读取）
            app_id: voice 应用 ID（可选，仅 volcengine 支持）
            access_key: voice Access Key（可选，仅 volcengine 支持）

        Raises:
            YzOpenAIException: Provider 不存在
            YzOpenAIException: API 密钥未提供

        Examples:
            >>> # 仅使用 Chat 能力
            >>> client = YzOpenAI(provider="volcengine", api_key="xxx")
            >>> result = client.chat.completion(model="doubao-pro", messages=[...])
            >>>
            >>> # 同时使用 Chat 和 ASR/TTS 能力
            >>> client = YzOpenAI(
            ...     provider="volcengine",
            ...     api_key="xxx",
            ...     app_id="xxx",
            ...     access_key="xxx"
            ... )
            >>> chat_result = client.chat.completion(...)
            >>> asr_result = client.asr.transcribe(...)
        """
        self._provider = provider
        self._api_key = api_key

        # Chat 客户端（延迟初始化）
        self._client = None

        # Voice 客户端统一管理（延迟初始化）
        self._voice_clients = {}

        # Voice 配置（共享）
        self._voice_config = {
            "app_id": app_id,
            "access_key": access_key
        }
        
            
    def _get_voice_client(self, ability: str):
        """
        统一的 voice 客户端获取方法

        Args:
            ability: voice 能力类型（podcast, tts, asr 等）

        Returns:
            对应能力的客户端实例
        """
        if ability not in self._voice_clients:
            self._voice_clients[ability] = get_voice_client(
                provider=self._provider,
                ability=ability,
                **self._voice_config
            )
        return self._voice_clients[ability]

    @property
    def chat(self):
        """
        获取 Chat 功能

        Returns:
            Chat 客户端实例,提供 completion() 和 simple_completion() 方法

        Examples:
            非流式调用:
            >>> result = client.chat.completion(
            ...     model="doubao-pro",
            ...     messages=[{"role": "user", "content": "你好"}]
            ... )

            流式调用:
            >>> for chunk in client.chat.completion(
            ...     model="doubao-pro",
            ...     messages=[{"role": "user", "content": "你好"}],
            ...     stream=True
            ... ):
            ...     print(chunk["message"]["content"], end="")
        """
        # 延迟初始化（只在首次访问时创建）
        if self._client is None:
            self._client = get_client(self._provider, self._api_key)
        return self._client

    @property
    def podcast(self):
        """
        获取 Podcast TTS 功能 (暂不支持同步模式)

        Returns:
            Podcast 客户端实例，提供 generate() 方法

        Raises:
            YzOpenAIException: Podcast 功能使用 WebSocket，暂不支持同步模式
        """
        return self._get_voice_client('podcast')

    @property
    def tts(self):
        """
        获取 TTS (Text-to-Speech) 功能

        Returns:
            TTS 客户端实例，提供 synthesize() 方法

        Raises:
            YzOpenAIException: Provider 不支持 TTS 功能
            YzOpenAIException: TTS 认证信息未提供

        Examples:
            >>> result = client.tts.synthesize({
            ...     "text": "你好，我是豆包语音大模型",
            ...     "speaker": "zh_female_xiaohe_uranus_bigtts"
            ... })
            >>> print(f"音频已保存到: {result.audio_path}")
            >>> print(f"音频大小: {len(result.audio_data)} bytes")
        """
        return self._get_voice_client('tts')

    @property
    def asr(self):
        """
        获取 ASR (Automatic Speech Recognition) 功能

        Returns:
            ASR 客户端实例，提供 transcribe() 方法

        Raises:
            YzOpenAIException: Provider 不支持 ASR 功能
            YzOpenAIException: ASR 认证信息未提供

        Examples:
            >>> result = client.asr.transcribe({
            ...     "file_url": "https://example.com/audio.mp3"
            ... })
            >>> print(f"识别文本: {result.text}")
            >>> print(f"Token 使用: {result.usage}")
        """
        return self._get_voice_client('asr')

    def close(self):
        """关闭客户端，释放资源"""
        # 关闭 Chat 客户端
        if self._client and hasattr(self._client, 'close'):
            self._client.close()

        # 关闭所有 Voice 客户端
        for client in self._voice_clients.values():
            if hasattr(client, 'close'):
                client.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
