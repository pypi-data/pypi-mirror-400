"""
火山引擎 TTS (Text-to-Speech) 客户端
"""
import asyncio
import json
import logging
import uuid
import os
import time
import base64
import httpx
import websockets
from typing import Dict, Any, Optional
from pathlib import Path

from yz_openai.base.exceptions import YzOpenAIErrorCode, YzOpenAIException
from yz_openai.base.types import TTSResult, Usage
from yz_openai.providers.volcengine.websocket_protocol import (
    full_client_request,
    receive_message,
    MsgType,
    EventType
)

logger = logging.getLogger(__name__)


class VolcengineTTS:
    """
    火山引擎 TTS (Text-to-Speech) 客户端

    功能:
    - 文本转语音合成
    - 支持多种音色和语速控制
    - 支持 WebSocket 和 HTTPS 两种传输方式
    """

    # 内部类属性：控制使用哪种传输方式（不对外暴露）
    _use_protocol: str = "wss"  # "wss" 或 "https"

    def __init__(
        self,
        app_id: str,
        access_key: str,
        resource_id: str = "seed-tts-2.0",
        app_key: Optional[str] = None,
        endpoint: str = None,
        protocol: str = None,
    ):
        """
        初始化 Volcengine TTS 客户端

        Args:
            app_id: 火山引擎控制台获取的 APP ID
            access_key: 火山引擎控制台获取的 Access Key
            resource_id: 资源 ID，默认 "seed-tts-2.0"
            app_key: APP Key（可选）
            endpoint: 端点地址，WebSocket 或 HTTPS 地址
            protocol: 协议类型，"wss" 或 "https"，默认 "https"
        """
        self.app_id = app_id
        self.access_key = access_key
        self.resource_id = resource_id
        self.app_key = app_key
        self.endpoint = endpoint

        # 设置类属性（内部控制协议类型）
        VolcengineTTS._use_protocol = protocol

    async def synthesize(self, params: Dict[str, Any]) -> TTSResult:
        """
        合成语音

        Args:
            params: 请求参数字典，包含以下字段：
                必需参数：
                - text (str): 要合成的文本内容
                - speaker (str): 说话人/音色

                可选参数：
                - audio_format (str): 音频格式，默认 "mp3"
                - sample_rate (int): 采样率，默认 24000
                - enable_timestamp (bool): 是否启用时间戳，默认 True
                - disable_markdown_filter (bool): 是否禁用 Markdown 过滤，默认 False
                - uid (str): 用户 ID，默认自动生成
                - audio_path (str): 音频保存路径，默认自动生成到当前工作目录/tmp/audio_[timestamp].[format]

        Returns:
            TTSResult: 语音合成结果，包含音频数据、文件路径和使用统计

        Raises:
            YzOpenAIException: 参数错误
            YzOpenAIException: 火山引擎 API 调用异常
            YzOpenAIException: 连接超时

        Examples:
            >>> client = VolcengineTTS(app_id="xxx", access_key="xxx")
            >>> result = await client.synthesize({
            ...     "text": "你好，我是豆包语音大模型",
            ...     "speaker": "zh_female_xiaohe_uranus_bigtts"
            ... })
            >>> print(f"音频已保存到: {result.audio_path}")
        """
        # 根据内部协议类型调用不同的实现
        if self._use_protocol == "https":
            return await self.synthesize_of_https(params)
        else:
            return await self.synthesize_of_wss(params)

    async def synthesize_of_wss(self, params: Dict[str, Any]) -> TTSResult:
        """
        使用 WebSocket 协议创建语音合成

        Args:
            params: 请求参数字典

        Returns:
            TTSResult: 语音合成结果
        """
        # 1. 验证必需参数
        if "text" not in params or not params["text"]:
            raise LLMException("缺少必需参数: text")

        if "speaker" not in params or not params["speaker"]:
            raise LLMException("缺少必需参数: speaker")

        # 2. 提取参数
        text = params["text"]
        speaker = params["speaker"]
        audio_format = params.get("audio_format", "mp3")
        sample_rate = params.get("sample_rate", 24000)
        enable_timestamp = params.get("enable_timestamp", True)
        disable_markdown_filter = params.get("disable_markdown_filter", False)
        uid = params.get("uid", str(uuid.uuid4()))

        # 3. 准备 WebSocket 连接头
        headers = {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Connect-Id": str(uuid.uuid4()),
            "X-Control-Require-Usage-Tokens-Return": "*",  # 请求返回使用统计
        }

        logger.info(f"Connecting to {self.endpoint}")

        try:
            # 4. 建立 WebSocket 连接
            websocket = await websockets.connect(
                self.endpoint,
                additional_headers=headers,
                max_size=10 * 1024 * 1024  # 10MB
            )

            logid = websocket.response.headers.get('x-tt-logid', 'N/A')
            logger.info(f"WebSocket connected, Logid: {logid}")

            try:
                # 5. 准备请求负载
                request = {
                    "user": {
                        "uid": uid,
                    },
                    "req_params": {
                        "speaker": speaker,
                        "audio_params": {
                            "format": audio_format,
                            "sample_rate": sample_rate,
                            "enable_timestamp": enable_timestamp,
                        },
                        "text": text,
                        "additions": json.dumps({
                            "disable_markdown_filter": disable_markdown_filter,
                        }),
                    },
                }

                # 6. 发送请求
                logger.info(f"Sending TTS request: speaker={speaker}, text_len={len(text)}")
                await full_client_request(websocket, json.dumps(request).encode())

                # 7. 接收音频数据
                audio_data = bytearray()
                usage_data = None

                while True:
                    msg = await receive_message(websocket)

                    if msg.type == MsgType.FullServerResponse:
                        if msg.event == EventType.SessionFinished:
                            logger.info("TTS session finished")
                            # 解析 usage 数据
                            if msg.payload:
                                try:
                                    payload_str = msg.payload.decode('utf-8')
                                    payload_json = json.loads(payload_str)
                                    if "usage" in payload_json:
                                        usage_info = payload_json["usage"]
                                        # 提取 token 使用统计
                                        usage_data = Usage(
                                            prompt_tokens=usage_info.get("text_words", 0),
                                            completion_tokens=0,  # TTS 没有 completion tokens
                                            total_tokens=usage_info.get("text_words", 0)
                                        )
                                        logger.info(f"Usage data: {usage_data}")
                                except Exception as e:
                                    logger.warning(f"Failed to parse usage data: {e}")
                            break
                        elif msg.event == EventType.SessionFailed:
                            error_msg = msg.payload.decode('utf-8') if msg.payload else "Unknown error"
                            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"TTS synthesis failed: {error_msg}")

                    elif msg.type == MsgType.AudioOnlyServer:
                        # 接收音频数据片段
                        audio_data.extend(msg.payload)

                    elif msg.type == MsgType.Error:
                        error_msg = msg.payload.decode('utf-8') if msg.payload else "Unknown error"
                        raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"TTS error: {error_msg}")

                    else:
                        logger.warning(f"Unknown message type: {msg.type}")

                # 8. 检查是否接收到音频数据
                if not audio_data:
                    raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, "No audio data received")

                # 9. 生成音频文件路径
                audio_path = params.get("audio_path")
                if not audio_path:
                    # 自动生成路径: 当前工作目录/tmp/audio_[timestamp].[format]
                    timestamp = int(time.time())
                    # 使用当前工作目录作为项目根目录
                    project_root = Path.cwd()
                    audio_path = str(project_root / "tmp" / f"audio_{timestamp}.{audio_format}")

                # 10. 确保目录存在
                audio_dir = os.path.dirname(audio_path)
                if audio_dir:
                    os.makedirs(audio_dir, exist_ok=True)

                # 11. 保存音频文件
                with open(audio_path, "wb") as f:
                    f.write(audio_data)

                logger.info(f"TTS synthesis completed, audio size: {len(audio_data)} bytes, saved to: {audio_path}")

                # 12. 返回 TTSResult
                return TTSResult(
                    audio_data=bytes(audio_data),
                    audio_path=audio_path,
                    usage=usage_data
                )

            finally:
                # 13. 关闭 WebSocket 连接
                await websocket.close()
                logger.info("WebSocket connection closed")

        except websockets.exceptions.WebSocketException as e:
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"WebSocket connection failed: {str(e)}")
        except asyncio.TimeoutError:
            raise YzOpenAIException(YzOpenAIErrorCode.TIMEOUT_ERROR, "TTS request timeout")
        except Exception as e:
            if isinstance(e, (YzOpenAIException, YzOpenAIException, YzOpenAIException)):
                raise
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"TTS synthesis failed: {str(e)}")

    async def synthesize_of_https(self, params: Dict[str, Any]) -> TTSResult:
        """
        使用 HTTPS 协议创建语音合成

        Args:
            params: 请求参数字典

        Returns:
            TTSResult: 语音合成结果
        """
        # 1. 验证必需参数
        if "text" not in params or not params["text"]:
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, "缺少必需参数: text")

        if "speaker" not in params or not params["speaker"]:
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, "缺少必需参数: speaker")

        # 2. 提取参数
        text = params["text"]
        speaker = params["speaker"]
        audio_format = params.get("audio_format", "mp3")
        sample_rate = params.get("sample_rate", 24000)
        enable_timestamp = params.get("enable_timestamp", True)
        disable_markdown_filter = params.get("disable_markdown_filter", False)
        uid = params.get("uid", str(uuid.uuid4()))

        # 3. 准备 HTTPS 请求头
        headers = {
            "X-Api-App-Id": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": self.resource_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "X-Control-Require-Usage-Tokens-Return": "*",  # 请求返回使用统计
        }

        # 4. 准备请求负载
        payload = {
            "user": {
                "uid": uid,
            },
            "req_params": {
                "text": text,
                "speaker": speaker,
                "audio_params": {
                    "format": audio_format,
                    "sample_rate": sample_rate,
                    "enable_timestamp": enable_timestamp,
                },
                "additions": json.dumps({
                    "disable_markdown_filter": disable_markdown_filter,
                }),
            },
        }

        logger.info(f"Sending HTTPS TTS request: speaker={speaker}, text_len={len(text)}")

        try:
            # 5. 发送 HTTPS 流式请求
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", self.endpoint, headers=headers, json=payload) as response:
                    # 检查响应状态
                    if response.status_code != 200:
                        raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"HTTP request failed with status {response.status_code}")

                    logid = response.headers.get('X-Tt-Logid', 'N/A')
                    logger.info(f"HTTPS request sent, Logid: {logid}")

                    # 6. 接收音频数据
                    audio_data = bytearray()
                    usage_data = None

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            data = json.loads(line)

                            # 解析音频数据
                            if data.get("code", 0) == 0 and "data" in data and data["data"]:
                                chunk_audio = base64.b64decode(data["data"])
                                audio_data.extend(chunk_audio)
                                continue

                            # 解析句子信息（可选）
                            if data.get("code", 0) == 0 and "sentence" in data and data["sentence"]:
                                logger.debug(f"Sentence data: {data}")
                                continue

                            # 合成完成
                            if data.get("code", 0) == 20000000:
                                if "usage" in data:
                                    try:
                                        usage_info = data["usage"]
                                        usage_data = Usage(
                                            prompt_tokens=usage_info.get("text_words", 0),
                                            completion_tokens=0,  # TTS 没有 completion tokens
                                            total_tokens=usage_info.get("text_words", 0)
                                        )
                                        logger.info(f"Usage data: {usage_data}")
                                    except Exception as e:
                                        logger.warning(f"Failed to parse usage data: {e}")
                                break

                            # 错误响应
                            if data.get("code", 0) > 0:
                                error_msg = data.get("message", "Unknown error")
                                raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"TTS synthesis failed: {error_msg}")

                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON line: {e}")
                            continue

            # 7. 检查是否接收到音频数据
            if not audio_data:
                raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, "No audio data received")

            # 8. 生成音频文件路径
            audio_path = params.get("audio_path")
            if not audio_path:
                # 自动生成路径: 当前工作目录/tmp/audio_[timestamp].[format]
                timestamp = int(time.time())
                # 使用当前工作目录作为项目根目录
                project_root = Path.cwd()
                audio_path = str(project_root / "tmp" / f"audio_{timestamp}.{audio_format}")

            # 9. 确保目录存在
            audio_dir = os.path.dirname(audio_path)
            if audio_dir:
                os.makedirs(audio_dir, exist_ok=True)

            # 10. 保存音频文件
            with open(audio_path, "wb") as f:
                f.write(audio_data)

            logger.info(f"TTS synthesis completed, audio size: {len(audio_data)} bytes, saved to: {audio_path}")

            # 11. 返回 TTSResult
            return TTSResult(
                audio_data=bytes(audio_data),
                audio_path=audio_path,
                usage=usage_data
            )

        except httpx.HTTPError as e:
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"HTTPS request failed: {str(e)}")
        except asyncio.TimeoutError:
            raise YzOpenAIException(YzOpenAIErrorCode.TIMEOUT_ERROR, "TTS request timeout")
        except Exception as e:
            raise YzOpenAIException(YzOpenAIErrorCode.API_ERROR, f"TTS synthesis failed: {str(e)}")

    async def close(self):
        """关闭客户端，释放资源"""
        # TTS 客户端是无状态的，每次请求都会创建新连接
        # 因此这里不需要做任何清理工作
        pass
