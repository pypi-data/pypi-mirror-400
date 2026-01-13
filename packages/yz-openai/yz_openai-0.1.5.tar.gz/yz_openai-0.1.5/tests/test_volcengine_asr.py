"""
火山引擎 ASR 基础功能测试
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from yz_openai import YzOpenAI

# 加载环境变量
_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(_ENV_FILE)


@pytest.mark.asyncio
async def test_asr_with_url():
    """测试使用 URL 进行语音识别"""
    # 检查环境变量
    app_id = os.getenv("VOLCENGINE_APP_ID")
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY")

    if not app_id or not access_key:
        pytest.skip("未设置 VOLCENGINE_APP_ID 和 VOLCENGINE_ACCESS_KEY 环境变量")

    # 创建客户端
    client = YzOpenAI(
        provider="volcengine",
        app_id=app_id,
        access_key=access_key
    )

    try:
        result = await client.asr.transcribe({
            "file_url": "https://img01.yzcdn.cn/upload_files/2025/12/10/Fj0Jkr1noqE20OLAipd3QxtaCYt6.mp3"
        })

        assert result is not None
        assert result.text is not None
        assert len(result.text) > 0
        print(f"\n识别文本: {result.text}")

        if result.usage:
            print(f"Usage: {result.usage}")
    finally:
        client.close()


@pytest.mark.asyncio
async def test_asr_with_local_file():
    """测试使用本地文件进行语音识别"""
    # 检查环境变量
    app_id = os.getenv("VOLCENGINE_APP_ID")
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY")

    if not app_id or not access_key:
        pytest.skip("未设置 VOLCENGINE_APP_ID 和 VOLCENGINE_ACCESS_KEY 环境变量")

    # 使用项目中的测试音频文件
    test_audio_path = "/Users/zhouyuexing/project/zlx/ai-platform/packages/yz_openai/tmp/audio_1765281109.mp3"

    if not os.path.exists(test_audio_path):
        pytest.skip(f"测试音频文件不存在: {test_audio_path}")

    # 创建客户端
    client = YzOpenAI(
        provider="volcengine",
        app_id=app_id,
        access_key=access_key
    )

    try:
        result = await client.asr.transcribe({
            "file_path": test_audio_path
        })

        assert result is not None
        assert result.text is not None
        assert len(result.text) > 0
        print(f"\n识别文本: {result.text}")

        if result.words:
            print(f"词级别信息数量: {len(result.words)}")
    finally:
        client.close()