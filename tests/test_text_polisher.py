import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from text_polisher import TextPolisher


class TestPolisherNoApiKey:
    """无 API key 时的降级行为。"""

    def test_returns_original_text_when_no_client(self):
        with patch.dict(os.environ, {}, clear=True):
            polisher = TextPolisher(api_key=None)
            assert polisher._client is None
            result = polisher.polish("今天下午开会")
            assert result == "今天下午开会"

    def test_empty_text_returns_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            polisher = TextPolisher(api_key=None)
            assert polisher.polish("") == ""
            assert polisher.polish("   ") == "   "

    def test_none_api_key_falls_back_to_env(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_openai.return_value = MagicMock()
                polisher = TextPolisher(api_key=None)
                assert polisher._client is not None


class TestPolisherModes:
    """润色模式测试。"""

    def test_all_modes_have_prompts(self):
        modes = ["general", "meeting", "email", "social"]
        for mode in modes:
            assert mode in TextPolisher.SYSTEM_PROMPTS
            assert len(TextPolisher.SYSTEM_PROMPTS[mode]) > 20

    def test_invalid_mode_falls_back_to_general(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "润色结果"
        mock_client.chat.completions.create.return_value = mock_response

        polisher = TextPolisher.__new__(TextPolisher)
        polisher._client = mock_client

        result = polisher.polish("测试文本", mode="nonexistent_mode")
        call_args = mock_client.chat.completions.create.call_args
        system_msg = call_args[1]["messages"][0]["content"]
        assert "书面语" in system_msg  # general 模式的提示词


class TestPolisherWithMockApi:
    """Mock API 调用的润色测试。"""

    def _make_polisher_with_mock(self):
        mock_client = MagicMock()
        polisher = TextPolisher.__new__(TextPolisher)
        polisher._client = mock_client
        return polisher, mock_client

    def test_polish_returns_api_result(self):
        polisher, mock_client = self._make_polisher_with_mock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "今天下午三点，会议室将讨论需求方案。"
        mock_client.chat.completions.create.return_value = mock_response

        result = polisher.polish("今天下午三点会议室讨论需求方案")
        assert "下午" in result
        mock_client.chat.completions.create.assert_called_once()

    def test_polish_api_failure_returns_original(self):
        polisher, mock_client = self._make_polisher_with_mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")

        result = polisher.polish("原始文本")
        assert result == "原始文本"

    def test_polish_api_returns_empty_string(self):
        polisher, mock_client = self._make_polisher_with_mock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_client.chat.completions.create.return_value = mock_response

        result = polisher.polish("原始文本")
        assert result == "原始文本"

    def test_polish_uses_deepseek_model(self):
        polisher, mock_client = self._make_polisher_with_mock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "结果"
        mock_client.chat.completions.create.return_value = mock_response

        polisher.polish("测试")
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "deepseek-chat"

    def test_polish_temperature_is_low(self):
        polisher, mock_client = self._make_polisher_with_mock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "结果"
        mock_client.chat.completions.create.return_value = mock_response

        polisher.polish("测试")
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["temperature"] == 0.3
