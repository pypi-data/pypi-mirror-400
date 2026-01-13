"""
火山引擎 ASR (语音识别) 客户端
"""
import asyncio
import json
import logging
import uuid
import base64
import httpx
from typing import Dict, Any

from yz_openai.base.exceptions import (
    YzOpenAIErrorCode, YzOpenAIException
)
from yz_openai.base.types import ASRResult, Usage

logger = logging.getLogger(__name__)


class VolcengineASR:
    """
    火山引擎 ASR (语音识别) 客户端

    功能:
    - 音频文件语音识别
    - 支持 URL 和本地文件两种输入方式
    - 支持多种音频格式（mp3, wav 等）
    """

    def __init__(
        self,
        app_id: str,
        access_key: str,
        resource_id: str = "volc.bigasr.auc_turbo",
        endpoint: str = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash",
    ):
        """
        初始化 Volcengine ASR 客户端

        Args:
            app_id: 火山引擎控制台获取的 APP ID
            access_key: 火山引擎控制台获取的 Access Key
            resource_id: 资源 ID，默认 "volc.bigasr.auc_turbo"
            endpoint: API 端点地址
        """
        if not app_id:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, "app_id 不能为空，请设置环境变量 VOLCENGINE_APP_ID 或传入有效的 app_id")
        if not access_key:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, "access_key 不能为空，请设置环境变量 VOLCENGINE_ACCESS_KEY 或传入有效的 access_key")
        
        self.app_id = app_id
        self.access_key = access_key
        self.resource_id = resource_id
        self.endpoint = endpoint

    def _file_to_base64(self, file_path: str) -> str:
        """
        将本地文件转换为 Base64

        Args:
            file_path: 本地文件路径

        Returns:
            Base64 编码的字符串
        """
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                base64_data = base64.b64encode(file_data).decode('utf-8')
            return base64_data
        except FileNotFoundError:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, f"文件不存在: {file_path}")
        except Exception as e:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, f"文件读取失败: {str(e)}")

    async def transcribe(self, params: Dict[str, Any]) -> ASRResult:
        """
        转录语音为文本

        Args:
            params: 请求参数字典，包含:
                必需参数（二选一）：
                - file_url (str): 音频文件 URL
                - file_path (str): 本地音频文件路径

                可选参数：
                - model_name (str): 模型名称，默认 "bigmodel"
                - enable_itn (bool): 是否启用逆文本规范化
                - enable_punc (bool): 是否启用标点符号
                - enable_ddc (bool): 是否启用脏词检测
                - enable_speaker_info (bool): 是否启用说话人识别
                - uid (str): 用户 ID，默认自动生成

        Returns:
            ASRResult: 语音识别结果

        Raises:
            YzOpenAIException: 参数错误
            YzOpenAIException: API 调用失败
            YzOpenAIException: 连接超时

        Examples:
            >>> client = VolcengineASR(app_id="xxx", access_key="xxx")
            >>> # 使用 URL
            >>> result = await client.transcribe({
            ...     "file_url": "https://example.com/audio.mp3"
            ... })
            >>> print(result.text)
            >>>
            >>> # 使用本地文件
            >>> result = await client.transcribe({
            ...     "file_path": "/path/to/audio.mp3"
            ... })
            >>> print(result.text)
        """
        # 1. 验证必需参数
        file_url = params.get("file_url")
        file_path = params.get("file_path")

        if not file_url and not file_path:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, "必须提供 file_url 或 file_path 其中之一")

        if file_url and file_path:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, "file_url 和 file_path 不能同时提供，请选择其一")

        # 2. 提取参数
        model_name = params.get("model_name", "bigmodel")
        enable_itn = params.get("enable_itn")
        enable_punc = params.get("enable_punc")
        enable_ddc = params.get("enable_ddc")
        enable_speaker_info = params.get("enable_speaker_info")
        uid = params.get("uid", self.app_id)

        # 3. 准备请求头
        headers = {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json",
        }

        # 4. 构建音频数据
        audio_data = None
        if file_url:
            audio_data = {"url": file_url}
            logger.info(f"Using audio URL: {file_url}")
        elif file_path:
            logger.info(f"Reading local file: {file_path}")
            base64_data = self._file_to_base64(file_path)
            audio_data = {"data": base64_data}
            logger.info(f"File converted to Base64, size: {len(base64_data)} chars")

        # 5. 构建请求体
        request_body = {
            "user": {
                "uid": uid
            },
            "audio": audio_data,
            "request": {
                "model_name": model_name,
            },
        }

        # 添加可选参数
        if enable_itn is not None:
            request_body["request"]["enable_itn"] = enable_itn
        if enable_punc is not None:
            request_body["request"]["enable_punc"] = enable_punc
        if enable_ddc is not None:
            request_body["request"]["enable_ddc"] = enable_ddc
        if enable_speaker_info is not None:
            request_body["request"]["enable_speaker_info"] = enable_speaker_info

        logger.info(f"Sending ASR request to {self.endpoint}")

        try:
            # 6. 发送 HTTPS POST 请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.endpoint,
                    json=request_body,
                    headers=headers
                )

                # 7. 检查响应头状态
                status_code = response.headers.get('X-Api-Status-Code')
                logid = response.headers.get('X-Tt-Logid', 'N/A')

                logger.info(f"Response status code: {status_code}, Logid: {logid}")

                if not status_code:
                    raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_CONFIG_ERROR, f"Missing X-Api-Status-Code in response headers")

                # 8. 解析响应
                if status_code == '20000000':  # 任务完成
                    try:
                        result_data = response.json()
                        logger.info(f"ASR recognition successful")

                        # 提取识别文本
                        text = ""
                        words = []

                        # 解析响应数据结构
                        if "result" in result_data:
                            result = result_data["result"]
                            # 直接获取完整文本
                            text = result.get("text", "")

                            # 提取词级别信息
                            if "utterances" in result:
                                for utterance in result["utterances"]:
                                    if "words" in utterance:
                                        words.extend(utterance["words"])

                        if not text:
                            logger.warning("No text extracted from response")

                        # 提取 usage 信息
                        usage = None
                        if "usage" in result_data:
                            usage_info = result_data["usage"]
                            usage = Usage(
                                prompt_tokens=usage_info.get("audio_duration", 0),
                                completion_tokens=usage_info.get("text_words", 0),
                                total_tokens=usage_info.get("total_tokens", 0)
                            )
                            logger.info(f"Usage data: {usage}")

                        return ASRResult(
                            text=text,
                            words=words if words else None,
                            usage=usage,
                            raw_response=result_data
                        )

                    except json.JSONDecodeError as e:
                        raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, f"Failed to parse JSON response: {str(e)}")

                elif status_code in ['20000001', '20000002']:  # 任务处理中
                    raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, f"Task is still processing (status: {status_code}). This should not happen with flash recognition.")

                else:  # 任务失败
                    error_message = response.headers.get('X-Api-Message', 'Unknown error')
                    logger.error(f"ASR failed: {error_message} (status: {status_code}, logid: {logid})")
                    raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, f"ASR recognition failed: {error_message} (code: {status_code})")

        except httpx.HTTPError as e:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, f"HTTP request failed: {str(e)}")
        except asyncio.TimeoutError:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, "ASR request timeout")
        except Exception as e:
            raise YzOpenAIException(YzOpenAIErrorCode.VOLCENGINE_ASR_ERROR, f"ASR recognition failed: {str(e)}")

    async def close(self):
        """关闭客户端，释放资源"""
        # ASR 客户端是无状态的，每次请求都会创建新连接
        # 因此这里不需要做任何清理工作
        pass
