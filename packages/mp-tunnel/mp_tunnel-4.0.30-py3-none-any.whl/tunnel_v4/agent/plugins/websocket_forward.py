import asyncio
import logging
from typing import Any, Optional
import websockets
import aiohttp
from .base import Plugin
class WebSocketForwardPlugin(Plugin):
    def __init__(self, agent, service_config: dict):
        super().__init__(agent, service_config)
        target = service_config.get('target', {})
        self.target_host = target.get('host', '127.0.0.1')
        self.target_port = target.get('port')
        if not self.target_port:
            raise ValueError(f"WebSocket forward service '{self.service_name}' missing target.port")
        self.target_url = f"ws://{self.target_host}:{self.target_port}"
        self.http_url = f"http://{self.target_host}:{self.target_port}"
        self.sessions = {}
        self.http_session = None
        self.logger.info(f"WebSocket Forward: {self.service_name} -> {self.target_url}")
    async def initialize(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.http_session = aiohttp.ClientSession(timeout=timeout)
    async def handle_message(self, message: dict, payload: Optional[Any]):
        transport = message.get('transport')
        self.logger.info(f"handle_message: transport={transport}, keys={list(message.keys())}")
        if transport == 'http':
            await self._handle_http_request(message, payload)
            return
        session_id = message.get('session_id')
        category = message.get('category')
        action = message.get('action')
        if not session_id:
            self.logger.error("WebSocket message missing session_id")
            return
        if category == 'control':
            if action == 'init':
                await self._handle_connect(session_id, payload)
            elif action == 'close':
                await self._handle_close(session_id)
        elif category == 'data':
            await self._handle_message(session_id, payload)
    async def _handle_http_request(self, message: dict, payload: Optional[Any]):
        request_id = message.get('request_id')
        self.logger.info(f"_handle_http_request called, request_id={request_id}")
        if not self.http_session:
            self.logger.info("Creating http_session")
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(timeout=timeout)
        try:
            self.logger.info(f"Parsing payload: type={type(payload)}")
            if isinstance(payload, str):
                import json
                request_data = json.loads(payload)
            elif isinstance(payload, dict):
                request_data = payload
            else:
                request_data = {}
            method = request_data.get('method', 'GET')
            path = request_data.get('path', '/')
            headers = request_data.get('headers', {})
            body = request_data.get('body')
            url = self.http_url + path
            self.logger.info(f"Sending HTTP request: {method} {url}")
            async with self.http_session.request(
                method=method,
                url=url,
                headers={k: v for k, v in headers.items() if k.lower() not in ['host', 'content-length']},
                data=body if body else None
            ) as resp:
                self.logger.info(f"Got response: status={resp.status}")
                response_body = await resp.read()
                response_headers = dict(resp.headers)
                self.logger.info(f"Sending response back, size={len(response_body)}")
                await self.send_to_worker({
                    'service': self.service_name,
                    'request_id': request_id,
                    'transport': 'http',
                    'category': 'response',
                    'response': {
                        'status': resp.status,
                        'headers': response_headers
                    }
                }, response_body)
                self.logger.info("Response sent successfully")
        except Exception as e:
            self.logger.error(f"HTTP request failed: {e}", exc_info=True)
            await self.send_to_worker({
                'service': self.service_name,
                'request_id': request_id,
                'transport': 'http',
                'category': 'response',
                'response': {
                    'status': 502,
                    'headers': {'content-type': 'text/plain'}
                }
            }, f"Proxy error: {e}".encode())
    async def _handle_connect(self, session_id: str, init_data):
        try:
            if isinstance(init_data, str):
                import json
                init_data = json.loads(init_data)
            path = init_data.get('path', '/') if init_data else '/'
            url = self.target_url + path
            ws = await websockets.connect(url)
            self.sessions[session_id] = ws
            self.logger.info(f"WebSocket connected: {session_id}")
            await self.send_control(session_id, 'ready')
            asyncio.create_task(self._read_loop(session_id, ws))
        except Exception as e:
            self.logger.error(f"WebSocket connect failed: {e}")
            await self.send_error(session_id, f"Connect failed: {e}")
    async def _handle_message(self, session_id: str, data: Any):
        if session_id not in self.sessions:
            self.logger.warning(f"Session not found: {session_id}")
            return
        ws = self.sessions[session_id]
        try:
            self.logger.info(f"Forwarding message to target: {type(data)} {len(str(data))} bytes")
            if isinstance(data, str):
                await ws.send(data)
            elif isinstance(data, bytes):
                await ws.send(data)
            elif isinstance(data, (list, bytearray)):
                await ws.send(bytes(data))
            else:
                await ws.send(str(data))
        except Exception as e:
            self.logger.error(f"WebSocket send error: {e}")
            await self._handle_close(session_id)
    async def _handle_close(self, session_id: str):
        if session_id not in self.sessions:
            self.logger.debug(f"Session already closed: {session_id}")
            return
        ws = self.sessions[session_id]
        try:
            await ws.close()
        except:
            pass
        try:
            del self.sessions[session_id]
            self.logger.info(f"WebSocket closed: {session_id}")
        except KeyError:
            self.logger.debug(f"Session already removed: {session_id}")
    async def _read_loop(self, session_id: str, ws):
        try:
            async for message in ws:
                await self.send_data(session_id, message)
        except Exception as e:
            self.logger.error(f"WebSocket read error: {e}")
        finally:
            await self.send_control(session_id, 'close')
            await self._handle_close(session_id)
    async def cleanup(self):
        for session_id in list(self.sessions.keys()):
            await self._handle_close(session_id)
        if self.http_session:
            await self.http_session.close()