"""
LLM 客户端工厂
"""
from typing import Dict, Optional
import os
import importlib

from yz_openai.base.exceptions import YzOpenAIErrorCode, YzOpenAIException

# Provider 注册表
_PROVIDER_REGISTRY: Dict[str, Dict] = {
    "litellm": {
        "module": "yz_openai.providers.litellm.chat",
        "class": "LiteLLMChat",
        "base_api": "https://litellm.prod.qima-inc.com",
        "env_key": "LITELLM_API_KEY"
    },
    "volcengine": {
        "module": "yz_openai.providers.volcengine.chat",
        "class": "VolcengineChat",
        "base_api": "https://ark.cn-beijing.volces.com",
        "env_key": "VOLCENGINE_API_KEY"
    }
}


def get_client(provider: str, api_key: Optional[str] = None):
    """
    获取 Provider 客户端（内部使用）

    Args:
        provider: Provider 名称（litellm, volcengine）
        api_key: API 密钥（可选，优先从环境变量读取）
        base_api: 自定义 API 地址（可选）

    Returns:
        Provider Chat 客户端实例

    Raises:
        YzOpenAIException: Provider 不存在
        YzOpenAIException: API 密钥未提供
    """
    # 1. 检查 provider 是否存在
    if provider not in _PROVIDER_REGISTRY:
        supported = ", ".join(_PROVIDER_REGISTRY.keys())
        raise YzOpenAIException(YzOpenAIErrorCode.NO_PROVIDER_ERROR, f"Unsupported provider: '{provider}'. Supported providers: {supported}")

    provider_cfg = _PROVIDER_REGISTRY[provider]

    # 2. 处理 api_key：入参优先，其次 env
    if api_key is None:
        env_key = provider_cfg.get("env_key")
        api_key = os.getenv(env_key)

    if not api_key:
        raise YzOpenAIException(YzOpenAIErrorCode.API_KEY_ERROR, f"请提供 api_key 或设置环境变量 {provider_cfg.get('env_key')}")

    # 3. 处理 base_api：入参优先，其次使用默认值
    final_base_api = provider_cfg.get("base_api")

    # 4. 动态导入并实例化客户端
    module = importlib.import_module(provider_cfg["module"])
    client_class = getattr(module, provider_cfg["class"])

    return client_class(base_api=final_base_api, api_key=api_key)


# Podcast Provider 注册表
_VOICE_PROVIDER_REGISTRY: Dict[str, Dict] = {
    "volcengine": {
        "podcast": {
            "module": "yz_openai.providers.volcengine.podcast",
            "class": "VolcenginePodcast",
            "app_id": "VOLCENGINE_APP_ID",
            "access_key": "VOLCENGINE_ACCESS_KEY",
            "resource_id": "volc.service_type.10050",
            "app_key": "aGjiRDfUWi",
            "endpoint": "wss://openspeech.bytedance.com/api/v3/sami/podcasttts",
        },
        "tts": {
            "module": "yz_openai.providers.volcengine.tts",
            "class": "VolcengineTTS",
            "app_id": "VOLCENGINE_APP_ID",
            "access_key": "VOLCENGINE_ACCESS_KEY",
            "resource_id": "seed-tts-2.0",
            "protocol": "wss",  # 协议类型: "wss" 或 "https"
            "endpoint": "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"
            
            # "protocol": "https",  # 协议类型: "wss" 或 "https"
            # "endpoint": "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
        },
        "asr": {
            "module": "yz_openai.providers.volcengine.asr",
            "class": "VolcengineASR",
            "app_id": "VOLCENGINE_APP_ID",
            "access_key": "VOLCENGINE_ACCESS_KEY",
            "resource_id": "volc.bigasr.auc_turbo",
            "endpoint": "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        }
    }
}

def get_voice_client(
    provider: str,
    ability: str,
    app_id: Optional[str] = None,
    access_key: Optional[str] = None
):
    """
    获取语音能力客户端（Podcast TTS 等）

    Args:
        provider: Provider 名称（目前仅支持 volcengine）
        ability: 能力类型（podcast）
        app_id: 应用 ID（可选，优先从环境变量读取）
        access_key: Access Key（可选）

    Returns:
        语音能力客户端实例

    Raises:
        YzOpenAIException: Provider 不存在或不支持指定能力
        YzOpenAIException: 必需的认证信息未提供

    Example:
        >>> # 从环境变量读取配置
        >>> client = get_voice_client("volcengine", "podcast")
        >>>
        >>> # 显式传递配置
        >>> client = get_voice_client(
        ...     "volcengine",
        ...     "podcast",
        ...     app_id="xxx",
        ...     access_key="xxx"
        ... )
    """
    # 1. 检查 provider 是否存在
    if provider not in _VOICE_PROVIDER_REGISTRY:
        supported = ", ".join(_VOICE_PROVIDER_REGISTRY.keys())
        raise YzOpenAIException(YzOpenAIErrorCode.NO_PROVIDER_ERROR, f"Provider '{provider}' 不支持语音能力。支持的 Provider: {supported}")

    # 2. 检查 provider 是否支持指定能力
    provider_abilities = _VOICE_PROVIDER_REGISTRY[provider]
    if ability not in provider_abilities:
        supported_abilities = ", ".join(provider_abilities.keys())
        raise YzOpenAIException(YzOpenAIErrorCode.NO_PROVIDER_ERROR, f"Provider '{provider}' 不支持 '{ability}' 能力。支持的能力: {supported_abilities}")

    ability_cfg = provider_abilities[ability]

    # 3. 处理认证信息：入参优先，其次环境变量
    env_app_id = ability_cfg.get("app_id")
    env_access_key = ability_cfg.get("access_key")

    if app_id is None:
        app_id = os.getenv(env_app_id) if env_app_id else None
    if access_key is None:
        access_key = os.getenv(env_access_key) if env_access_key else None

    # 4. 验证必需参数
    if not all([app_id, access_key]):
        missing = []
        if not app_id:
            missing.append(f"app_id (环境变量: {env_app_id})")
        if not access_key:
            missing.append(f"access_key (环境变量: {env_access_key})")

        raise YzOpenAIException(YzOpenAIErrorCode.API_KEY_ERROR, f"缺少必需的认证信息: {', '.join(missing)}")

    # 5. 动态导入并实例化客户端
    module = importlib.import_module(ability_cfg["module"])
    client_class = getattr(module, ability_cfg["class"])

    # 6. 准备实例化参数（包含配置中的其他参数）
    init_params = {
        "app_id": app_id,
        "access_key": access_key,
    }

    # 添加配置中的其他参数（如 resource_id, app_key, endpoint, protocol）
    for key in ["resource_id", "app_key", "endpoint", "protocol"]:
        if key in ability_cfg:
            init_params[key] = ability_cfg[key]

    return client_class(**init_params)
