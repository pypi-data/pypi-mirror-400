"""
测试火山引擎 TTS (Text-to-Speech) 功能
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
async def test_tts_synthesis():
    """测试 TTS 语音合成功能"""
    print("\n" + "=" * 60)
    print("测试 TTS 语音合成")
    print("=" * 60)

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
        # 测试参数
        test_text = "你好，我是豆包语音大模型，很高兴为您服务！"
        speaker = "zh_female_xiaohe_uranus_bigtts"

        # 调用 TTS 合成
        result = await client.tts.synthesize({
            "text": test_text,
            "speaker": speaker,
            "audio_format": "wav"
        })

        # 验证结果
        assert result is not None, "TTS 合成结果不能为空"
        assert len(result.audio_data) > 0, "音频数据不能为空"
        assert result.audio_path is not None, "音频路径不能为空"

        print(f"✅ TTS 合成成功！")
        print(f"   音频大小: {len(result.audio_data)} bytes")
        print(f"   音频路径: {result.audio_path}")

        if result.usage:
            print(f"   使用统计:")
            print(f"     - 输入文本字数: {result.usage.prompt_tokens}")
            print(f"     - 总计: {result.usage.total_tokens}")

    finally:
        client.close()
