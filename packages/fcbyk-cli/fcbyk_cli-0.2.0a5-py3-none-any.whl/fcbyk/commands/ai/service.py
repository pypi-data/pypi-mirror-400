"""
ai 业务逻辑层

类:
- AIServiceError: 异常类，三种错误类型（network_error/api_key_error/backend_error）
- AIService: OpenAI 兼容的 Chat Completions 客户端
  - chat(req) -> JsonDict | Iterable[JsonDict]: 发起对话请求
  - _parse_response(resp) -> JsonDict: 解析非流式响应
  - _stream_chunks(resp) -> Generator: 解析流式响应

数据类:
- ChatRequest: 请求参数封装（messages, model, api_key, api_url, stream, timeout）

函数:
- extract_assistant_reply(response: JsonDict) -> str: 从非流式响应提取回复
- extract_assistant_reply_from_stream(chunks: Iterable[JsonDict]) -> str: 从流式响应拼接回复
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterable, List, Optional, Union

import requests


JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class ChatRequest:
    messages: List[JsonDict]
    model: str
    api_key: str
    api_url: str
    stream: bool = False
    timeout: int = 30


class AIServiceError(RuntimeError):
    
    @classmethod
    def network_error(cls):
        return cls("网络错误")
    
    @classmethod
    def api_key_error(cls):
        return cls("API Key 错误")
    
    @classmethod
    def backend_error(cls, detail: str = ""):
        msg = "后端逻辑错误"
        if detail:
            msg += f": {detail}"
        return cls(msg)


class AIService:

    def __init__(self, session: Optional[requests.Session] = None):
        self._session = session or requests.Session()

    def chat(self, req: ChatRequest) -> Union[JsonDict, Iterable[JsonDict]]:
        """发起对话请求，返回完整响应或流式 chunks"""
        
        if not req.api_key:
            raise AIServiceError.api_key_error()

        headers = {
            "Authorization": f"Bearer {req.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": req.model,
            "messages": req.messages,
            "stream": req.stream,
        }

        try:
            resp = self._session.post(
                req.api_url, headers=headers, json=payload,
                stream=req.stream, timeout=req.timeout
            )
            
            # 401/403 判定为 API Key 错误
            if resp.status_code in (401, 403):
                raise AIServiceError.api_key_error()
            
            resp.raise_for_status()

            if not req.stream:
                return self._parse_response(resp)
            return self._stream_chunks(resp)

        except (requests.Timeout, requests.ConnectionError):
            raise AIServiceError.network_error()
        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError.backend_error(str(e))

    def _parse_response(self, resp: requests.Response) -> JsonDict:
        try:
            data = resp.json()
            if 'error' in data:
                raise AIServiceError.backend_error(data['error'].get('message', ''))
            return data
        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError.backend_error(f"响应解析失败: {e}")

    def _stream_chunks(self, resp: requests.Response) -> Generator[JsonDict, None, None]:
        try:
            for line in resp.iter_lines():
                if not line:
                    continue

                text = line.decode('utf-8', errors='replace')
                if not text.startswith('data: '):
                    continue

                data = text[6:].strip()
                if data == '[DONE]':
                    break

                try:
                    chunk = json.loads(data)
                    if 'error' in chunk:
                        raise AIServiceError.backend_error(chunk['error'].get('message', ''))
                    yield chunk
                except json.JSONDecodeError:
                    continue
                except AIServiceError:
                    raise

        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError.backend_error(f"流式读取失败: {e}")


def extract_assistant_reply(response: JsonDict) -> str:
    return response['choices'][0]['message']['content']


def extract_assistant_reply_from_stream(chunks: Iterable[JsonDict]) -> str:
    reply = ""
    for chunk in chunks:
        delta = chunk['choices'][0]['delta'].get('content', '')
        reply += delta
    return reply