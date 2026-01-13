"""AI 子命令：service 层单元测试

目标：覆盖 fcbyk.commands.ai.service 中 AIService 的主要逻辑分支，
包括：
- 基础解析函数 extract_assistant_reply / extract_assistant_reply_from_stream
- chat() 的参数校验、HTTP 状态码处理、网络异常转换
- 非流式响应解析（含 error 字段与 json 解析失败）
- 流式响应解析（SSE data: 行解析、[DONE]、坏 JSON 跳过、error 字段、iter_lines 异常）

说明：
- 这里不发起真实网络请求，使用 _FakeSession/_FakeResponse 模拟 requests.Session/Response。
- 测试只关注本项目逻辑，不测试 requests 本身。
"""

import pytest
import requests

from fcbyk.commands.ai.service import (
    AIService,
    AIServiceError,
    ChatRequest,
    extract_assistant_reply,
    extract_assistant_reply_from_stream,
)


class _FakeResponse:
    """最小化模拟 requests.Response。

    只实现本项目用到的字段/方法：status_code/json()/raise_for_status()/iter_lines()。
    """

    def __init__(
        self,
        status_code=200,
        json_data=None,
        lines=None,
        raise_for_status_exc=None,
    ):
        self.status_code = status_code
        self._json_data = json_data if json_data is not None else {}
        self._lines = lines if lines is not None else []
        self._raise_for_status_exc = raise_for_status_exc

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._raise_for_status_exc is not None:
            raise self._raise_for_status_exc

    def iter_lines(self):
        # requests 在 stream 模式下 iter_lines() 返回 bytes
        for line in self._lines:
            yield line


class _FakeSession:
    """最小化模拟 requests.Session，记录 post() 入参以便断言。"""

    def __init__(self, response=None, post_exc=None):
        self._response = response
        self._post_exc = post_exc
        self.last_post = None

    def post(self, url, headers=None, json=None, stream=False, timeout=None):
        self.last_post = {
            "url": url,
            "headers": headers,
            "json": json,
            "stream": stream,
            "timeout": timeout,
        }
        if self._post_exc is not None:
            raise self._post_exc
        return self._response


def _make_req(**kwargs):
    """创建默认 ChatRequest，并允许通过 kwargs 覆盖字段。"""

    base = dict(
        messages=[{"role": "user", "content": "hi"}],
        model="deepseek-chat",
        api_key="k",
        api_url="https://example.com/v1/chat/completions",
        stream=False,
        timeout=30,
    )
    base.update(kwargs)
    return ChatRequest(**base)


def test_extract_assistant_reply():
    """非流式响应：从 response 中提取 assistant 的 message.content。"""

    resp = {"choices": [{"message": {"content": "hello"}}]}
    assert extract_assistant_reply(resp) == "hello"


def test_extract_assistant_reply_from_stream():
    """流式响应：将每个 chunk 的 delta.content 拼接为完整回复。"""

    chunks = [
        {"choices": [{"delta": {"content": "he"}}]},
        {"choices": [{"delta": {"content": "llo"}}]},
    ]
    assert extract_assistant_reply_from_stream(chunks) == "hello"


def test_chat_missing_api_key_raises_api_key_error():
    """api_key 为空时应直接报错，不发起请求。"""

    service = AIService(session=_FakeSession())
    req = _make_req(api_key="")
    with pytest.raises(AIServiceError, match="API Key 错误"):
        service.chat(req)


def test_chat_non_stream_success_parses_json_and_sends_payload():
    """非流式成功请求：验证 payload/header/stream 参数与解析结果。"""

    fake_resp = _FakeResponse(
        status_code=200,
        json_data={"choices": [{"message": {"content": "ok"}}]},
    )
    sess = _FakeSession(response=fake_resp)
    service = AIService(session=sess)

    req = _make_req(stream=False)
    data = service.chat(req)

    assert data["choices"][0]["message"]["content"] == "ok"

    assert sess.last_post["url"] == req.api_url
    assert sess.last_post["headers"]["Authorization"] == f"Bearer {req.api_key}"
    assert sess.last_post["json"]["model"] == req.model
    assert sess.last_post["json"]["messages"] == req.messages
    assert sess.last_post["json"]["stream"] is False
    assert sess.last_post["stream"] is False


def test_chat_401_403_raises_api_key_error():
    """后端返回 401/403 时，统一视为 API Key 错误。"""

    for code in (401, 403):
        fake_resp = _FakeResponse(status_code=code)
        sess = _FakeSession(response=fake_resp)
        service = AIService(session=sess)
        with pytest.raises(AIServiceError, match="API Key 错误"):
            service.chat(_make_req())


def test_chat_timeout_or_connection_error_raises_network_error():
    """requests.Timeout/ConnectionError 转换为 network_error。"""

    for exc in (requests.Timeout(), requests.ConnectionError()):
        sess = _FakeSession(post_exc=exc)
        service = AIService(session=sess)
        with pytest.raises(AIServiceError, match="网络错误"):
            service.chat(_make_req())


def test_parse_response_error_field_raises_backend_error():
    """非流式响应中包含 error 字段时，报后端逻辑错误。"""

    fake_resp = _FakeResponse(
        status_code=200,
        json_data={"error": {"message": "bad"}},
    )
    service = AIService(session=_FakeSession(response=fake_resp))
    with pytest.raises(AIServiceError, match=r"后端逻辑错误: bad"):
        service.chat(_make_req(stream=False))


def test_parse_response_json_raises_backend_error():
    """resp.json() 解析异常应包装为 backend_error(响应解析失败)。"""

    class _BadJsonResp(_FakeResponse):
        def json(self):
            raise ValueError("no json")

    fake_resp = _BadJsonResp(status_code=200)
    service = AIService(session=_FakeSession(response=fake_resp))

    with pytest.raises(AIServiceError, match=r"后端逻辑错误: 响应解析失败:"):
        service.chat(_make_req(stream=False))


def test_chat_raise_for_status_other_http_error_becomes_backend_error():
    """raise_for_status() 抛 HTTPError 时，应进入 backend_error。"""

    fake_resp = _FakeResponse(
        status_code=500,
        raise_for_status_exc=requests.HTTPError("server error"),
    )
    service = AIService(session=_FakeSession(response=fake_resp))

    with pytest.raises(AIServiceError, match=r"后端逻辑错误: server error"):
        service.chat(_make_req(stream=False))


def test_stream_chunks_happy_path_and_done():
    """流式响应：解析 data: {...} 行并在 [DONE] 处结束。"""

    lines = [
        b"data: {\"choices\":[{\"delta\":{\"content\":\"he\"}}]}",
        b"data: {\"choices\":[{\"delta\":{\"content\":\"llo\"}}]}",
        b"data: [DONE]",
    ]
    fake_resp = _FakeResponse(status_code=200, lines=lines)
    sess = _FakeSession(response=fake_resp)
    service = AIService(session=sess)

    chunks = list(service.chat(_make_req(stream=True)))
    assert extract_assistant_reply_from_stream(chunks) == "hello"

    assert sess.last_post["stream"] is True
    assert sess.last_post["json"]["stream"] is True


def test_stream_chunks_skips_non_data_and_bad_json_lines():
    """流式响应：跳过非 data: 行；坏 JSON 行忽略继续。"""

    lines = [
        b"event: ping",
        b"data: {bad json}",
        b"data: {\"choices\":[{\"delta\":{\"content\":\"ok\"}}]}",
        b"data: [DONE]",
    ]
    fake_resp = _FakeResponse(status_code=200, lines=lines)
    service = AIService(session=_FakeSession(response=fake_resp))

    chunks = list(service.chat(_make_req(stream=True)))
    assert extract_assistant_reply_from_stream(chunks) == "ok"


def test_chat_stream_iter_lines_unexpected_exception_becomes_backend_error():
    """iter_lines() 过程中出现异常时，应包装为 backend_error(流式读取失败)。"""

    class _BadStreamResp(_FakeResponse):
        def iter_lines(self):
            raise RuntimeError("broken")

    fake_resp = _BadStreamResp(status_code=200)
    service = AIService(session=_FakeSession(response=fake_resp))

    with pytest.raises(AIServiceError, match=r"后端逻辑错误: 流式读取失败: broken"):
        list(service.chat(_make_req(stream=True)))


def test_stream_chunks_error_field_raises_backend_error():
    """流式 chunk 中出现 error 字段时，应立即报后端逻辑错误。"""

    lines = [
        b"data: {\"error\":{\"message\":\"boom\"}}",
    ]
    fake_resp = _FakeResponse(status_code=200, lines=lines)
    service = AIService(session=_FakeSession(response=fake_resp))

    with pytest.raises(AIServiceError, match=r"后端逻辑错误: boom"):
        list(service.chat(_make_req(stream=True)))
