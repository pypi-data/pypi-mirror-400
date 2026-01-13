import importlib

import pytest

slide_service = importlib.import_module("fcbyk.commands.slide.service")
SlideService = slide_service.SlideService


def test_display_env_is_set_on_import():
    # service 模块在 import 时会确保 DISPLAY 存在
    assert "DISPLAY" in slide_service.os.environ


def test_static_resources_constant():
    assert "socket.io.min.js" in SlideService.STATIC_RESOURCES
    assert SlideService.SOCKETIO_VERSION in SlideService.STATIC_RESOURCES["socket.io.min.js"]


def test_init_sets_failsafe_false(monkeypatch):
    # 确保 __init__ 会设置 pyautogui.FAILSAFE=False
    monkeypatch.setattr(slide_service.pyautogui, "FAILSAFE", True)
    SlideService(password="p")
    assert slide_service.pyautogui.FAILSAFE is False


def test_verify_password():
    s = SlideService(password="p")
    assert s.verify_password("p") is True
    assert s.verify_password("x") is False


def test_next_prev_home_end_slide_success(monkeypatch):
    calls = []

    monkeypatch.setattr(slide_service.pyautogui, "press", lambda key: calls.append(key))

    s = SlideService(password="p")

    assert s.next_slide() == (True, None)
    assert s.prev_slide() == (True, None)
    assert s.home_slide() == (True, None)
    assert s.end_slide() == (True, None)

    assert calls == ["right", "left", "home", "end"]


def test_prev_slide_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("bad")

    monkeypatch.setattr(slide_service.pyautogui, "press", _boom)

    s = SlideService(password="p")
    ok, err = s.prev_slide()
    assert ok is False
    assert "bad" in err


def test_home_slide_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("bad")

    monkeypatch.setattr(slide_service.pyautogui, "press", _boom)

    s = SlideService(password="p")
    ok, err = s.home_slide()
    assert ok is False
    assert "bad" in err


def test_end_slide_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("bad")

    monkeypatch.setattr(slide_service.pyautogui, "press", _boom)

    s = SlideService(password="p")
    ok, err = s.end_slide()
    assert ok is False
    assert "bad" in err


def test_move_mouse_success(monkeypatch):
    monkeypatch.setattr(slide_service.pyautogui, "position", lambda: (10, 20))

    moved = {}

    def _move_to(x, y, duration=0):
        moved.update({"x": x, "y": y, "duration": duration})

    monkeypatch.setattr(slide_service.pyautogui, "moveTo", _move_to)

    s = SlideService(password="p")
    assert s.move_mouse(3, -5) == (True, None)
    assert moved == {"x": 13, "y": 15, "duration": 0}


def test_move_mouse_error(monkeypatch):
    monkeypatch.setattr(slide_service.pyautogui, "position", lambda: (0, 0))

    def _boom(*a, **k):
        raise RuntimeError("move failed")

    monkeypatch.setattr(slide_service.pyautogui, "moveTo", _boom)

    s = SlideService(password="p")
    ok, err = s.move_mouse(1, 1)
    assert ok is False
    assert "move failed" in err


def test_click_mouse_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("click failed")

    monkeypatch.setattr(slide_service.pyautogui, "click", _boom)

    s = SlideService(password="p")
    ok, err = s.click_mouse()
    assert ok is False
    assert "click failed" in err


def test_right_click_mouse_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("right failed")

    monkeypatch.setattr(slide_service.pyautogui, "rightClick", _boom)

    s = SlideService(password="p")
    ok, err = s.right_click_mouse()
    assert ok is False
    assert "right failed" in err


def test_click_mouse_right_click_mouse_success(monkeypatch):
    clicked = {"left": 0, "right": 0}

    monkeypatch.setattr(slide_service.pyautogui, "click", lambda: clicked.__setitem__("left", clicked["left"] + 1))
    monkeypatch.setattr(slide_service.pyautogui, "rightClick", lambda: clicked.__setitem__("right", clicked["right"] + 1))

    s = SlideService(password="p")
    assert s.click_mouse() == (True, None)
    assert s.right_click_mouse() == (True, None)
    assert clicked == {"left": 1, "right": 1}


def test_scroll_mouse_clamps_and_skips_zero(monkeypatch):
    scrolled = {"v": [], "h": []}

    monkeypatch.setattr(slide_service.pyautogui, "scroll", lambda n: scrolled["v"].append(n))
    monkeypatch.setattr(slide_service.pyautogui, "hscroll", lambda n: scrolled["h"].append(n))

    s = SlideService(password="p")

    # dy/dx 会 round + clamp
    assert s.scroll_mouse(dx=1000.2, dy=-1000.2) == (True, None)
    assert scrolled["v"] == [-100]
    assert scrolled["h"] == [100]

    # 0 不应触发调用
    scrolled["v"].clear()
    scrolled["h"].clear()
    assert s.scroll_mouse(dx=0, dy=0) == (True, None)
    assert scrolled == {"v": [], "h": []}


def test_scroll_mouse_rounds_to_zero_skips(monkeypatch):
    scrolled = {"v": [], "h": []}

    monkeypatch.setattr(slide_service.pyautogui, "scroll", lambda n: scrolled["v"].append(n))
    monkeypatch.setattr(slide_service.pyautogui, "hscroll", lambda n: scrolled["h"].append(n))

    s = SlideService(password="p")

    # round(0.4)=0 => 不调用 scroll/hscroll
    assert s.scroll_mouse(dx=0.4, dy=-0.4) == (True, None)
    assert scrolled == {"v": [], "h": []}


def test_scroll_mouse_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("scroll failed")

    monkeypatch.setattr(slide_service.pyautogui, "scroll", _boom)

    s = SlideService(password="p")
    ok, err = s.scroll_mouse(dx=0, dy=1)
    assert ok is False
    assert "scroll failed" in err
