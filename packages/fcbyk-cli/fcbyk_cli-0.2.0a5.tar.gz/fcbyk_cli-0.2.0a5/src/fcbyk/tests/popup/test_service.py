import importlib
from unittest.mock import MagicMock

popup_service_mod = importlib.import_module("fcbyk.commands.popup.service")
PopupService = popup_service_mod.PopupService
PopupOptions = popup_service_mod.PopupOptions


def test_show_one_creates_and_configures_tk_window(monkeypatch):
    # Mock the entire tkinter module within the service module
    mock_tk = MagicMock()
    monkeypatch.setattr(popup_service_mod, "tk", mock_tk)

    # The mock for the Tk() instance
    mock_window = mock_tk.Tk.return_value
    mock_window.winfo_screenwidth.return_value = 1920
    mock_window.winfo_screenheight.return_value = 1080

    service = PopupService()
    service.show_one("Test Title", ["Test Tip"])

    mock_tk.Tk.assert_called_once()
    mock_window.title.assert_called_with("Test Title")
    mock_window.geometry.assert_called_once()

    mock_tk.Label.assert_called_once()
    mock_tk.Label.return_value.pack.assert_called_once()

    mock_window.attributes.assert_called_with("-topmost", True)
    mock_window.mainloop.assert_called_once()


def test_spawn_many_creates_threads(monkeypatch):
    # Mock threading.Thread and time.sleep
    created_kwargs = []

    def mock_thread_constructor(*args, **kwargs):
        # 真实调用形式是 Thread(target=..., args=(...,...))，所以从 kwargs 里取
        created_kwargs.append(kwargs)
        instance = MagicMock()
        return instance

    monkeypatch.setattr(popup_service_mod.threading, "Thread", mock_thread_constructor)
    monkeypatch.setattr(popup_service_mod.time, "sleep", lambda *_: None)

    service = PopupService()
    opts = PopupOptions(numbers=5, tips=["a"])
    threads = service.spawn_many(opts)

    assert len(threads) == 5
    assert len(created_kwargs) == 5

    # 每个线程 target 都应为 show_one
    assert all(k["target"] == service.show_one for k in created_kwargs)
    assert all(k["args"][0] == opts.title for k in created_kwargs)
    assert all(list(k["args"][1]) == ["a"] for k in created_kwargs)

    # 每个线程都应 start 一次
    for t in threads:
        t.start.assert_called_once()
