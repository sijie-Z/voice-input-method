import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch
from command_engine import CommandEngine


def _make_engine(mode_setter=None):
    """创建 CommandEngine 实例，mock 掉 pyautogui 防止真实按键。"""
    with patch("command_engine.pyautogui"), \
         patch("command_engine.subprocess"), \
         patch("command_engine.webbrowser"):
        return CommandEngine(mode_setter=mode_setter)


class TestMatchExact:
    """精确匹配测试。"""

    def test_exact_match_returns_trigger_and_handler(self):
        engine = _make_engine()
        result = engine.match("换行")
        assert result is not None
        trigger, handler, arg = result
        assert trigger == "换行"
        assert arg is None

    def test_exact_match_all_commands(self):
        engine = _make_engine()
        exact_triggers = [
            "换行", "删除上一句", "全部删除", "全部复制",
            "粘贴", "撤销", "保存", "锁屏", "截屏", "大写切换", "打开记事本",
        ]
        for trigger in exact_triggers:
            result = engine.match(trigger)
            assert result is not None, f"'{trigger}' 应该匹配成功"
            assert result[0] == trigger
            assert result[2] is None

    def test_exact_match_with_mode_setter(self):
        setter = MagicMock()
        engine = _make_engine(mode_setter=setter)
        for trigger in ["润色模式", "会议模式", "邮件模式", "朋友圈模式"]:
            result = engine.match(trigger)
            assert result is not None, f"'{trigger}' 应该匹配成功"

    def test_exact_match_whitespace_not_matched(self):
        engine = _make_engine()
        assert engine.match("换行 ") is None or engine.match("换行 ")[0] != "换行"
        assert engine.match(" 换行") is None or engine.match(" 换行")[0] != "换行"


class TestMatchPrefix:
    """前缀匹配测试。"""

    def test_prefix_match_with_argument(self):
        engine = _make_engine()
        result = engine.match("搜索 七牛云")
        assert result is not None
        trigger, handler, arg = result
        assert trigger == "搜索"
        assert arg == "七牛云"

    def test_prefix_match_no_argument(self):
        engine = _make_engine()
        result = engine.match("搜索")
        assert result is not None
        trigger, handler, arg = result
        assert trigger == "搜索"
        assert arg == ""

    def test_prefix_match_extra_spaces(self):
        engine = _make_engine()
        result = engine.match("搜索   多余空格  ")
        assert result is not None
        assert result[0] == "搜索"
        assert result[2] == "多余空格"


class TestMatchPriority:
    """匹配优先级测试。"""

    def test_exact_over_prefix(self):
        engine = _make_engine()
        # "删除上一句" 是精确匹配，不应被 "删除" 前缀匹配截获
        result = engine.match("删除上一句")
        assert result is not None
        assert result[0] == "删除上一句"

    def test_no_match_returns_none(self):
        engine = _make_engine()
        assert engine.match("今天天气真好") is None
        assert engine.match("") is None
        assert engine.match(None) is None

    def test_longer_trigger_wins(self):
        engine = _make_engine()
        # "全部删除" 和 "全部复制" 都是精确匹配，不会冲突
        r1 = engine.match("全部删除")
        r2 = engine.match("全部复制")
        assert r1[0] == "全部删除"
        assert r2[0] == "全部复制"


class TestExecute:
    """指令执行测试。"""

    def test_execute_without_arg(self):
        engine = _make_engine()
        mock_handler = MagicMock()
        engine.execute(mock_handler, None)
        mock_handler.assert_called_once()

    def test_execute_with_arg(self):
        engine = _make_engine()
        mock_handler = MagicMock()
        engine.execute(mock_handler, "七牛云")
        mock_handler.assert_called_once_with("七牛云")
