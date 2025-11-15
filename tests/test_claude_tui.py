import pytest
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from claude_tui import clear_screen, load_components_registry


def test_clear_screen():
    # 测试清屏函数不会抛出异常
    try:
        clear_screen()
        assert True
    except Exception as e:
        assert False, f"clear_screen() raised exception: {e}"


def test_load_components_registry():
    # 测试加载组件注册表函数
    registry = load_components_registry()
    assert isinstance(registry, dict)
    assert 'components' in registry
    assert isinstance(registry['components'], dict)
