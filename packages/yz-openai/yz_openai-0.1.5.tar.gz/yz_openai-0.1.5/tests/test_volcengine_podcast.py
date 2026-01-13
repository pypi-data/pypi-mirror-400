"""
Podcast TTS pytest 测试
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
async def test_nlp_texts():
    """测试 Podcast TTS 语音合成功能"""
    print("\n" + "=" * 60)
    print("测试 Podcast TTS: 使用自定义 NLP 文本")
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
        # 调用 Podcast TTS
        result = await client.podcast.generate({
            "speakers": [
                "zh_male_dayixiansheng_v2_saturn_bigtts",
                "zh_female_mizaitongxue_v2_saturn_bigtts"
            ],
            "action": 3,
            "nlp_texts": [
                {
                    "speaker": "zh_male_dayixiansheng_v2_saturn_bigtts",
                    "text": "今天呢我们要聊的呢是火山引擎在这个 FORCE 原动力大会上面的一些比较重磅的发布。"
                },
                {
                    "speaker": "zh_female_mizaitongxue_v2_saturn_bigtts",
                    "text": "来看看都有哪些亮点哈。"
                }
            ],
            "audio_format": "mp3",
            "sample_rate": 24000,
            "speech_rate": 0,  # 正常语速
            "use_head_music": False,
            "use_tail_music": False,
            "return_audio_url": True,
            "only_nlp_text": False,
            "max_retries": 5
        })

        # 验证结果
        assert result is not None, "播客生成结果不能为空"
        assert result.total_rounds > 0, "播客轮次必须大于0"
        assert result.audio_url is not None, "音频 URL 不能为空"
        assert len(result.texts) > 0, "文本列表不能为空"

        print(f"✅ 播客生成成功！")
        print(f"   音频格式: mp3")
        print(f"   采样率: 24000 Hz")
        print(f"   总轮次: {result.total_rounds}")
        print(f"   audio_url: {result.audio_url}")
        print(f"   usage: {result.usage}")

    finally:
        client.close()

