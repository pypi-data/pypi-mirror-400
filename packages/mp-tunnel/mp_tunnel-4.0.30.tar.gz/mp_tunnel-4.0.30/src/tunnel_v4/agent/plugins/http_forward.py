import asyncio
import logging
from typing import Any, Optional
from urllib.parse import quote
import aiohttp
from .base import Plugin
class HTTPForwardPlugin(Plugin):
    def __init__(self, agent, service_config: dict):
        super().__init__(agent, service_config)
        target = service_config.get('target', {})
        self.target_host = target.get('host', '127.0.0.1')
        self.target_port = target.get('port')
        if not self.target_port:
            raise ValueError(f"HTTP forward service '{self.service_name}' missing target.port")
        self.target_url = f"http://{self.target_host}:{self.target_port}"
        self.session = None
        worker_ws_url = agent.config.get('worker_url', '')
        self.worker_url = worker_ws_url.replace('wss://', 'https://').replace('ws://', 'http://')
        if self.worker_url.endswith('/agent/connect'):
            self.worker_url = self.worker_url.replace('/agent/connect', '')
        self.large_file_threshold = 1024 * 1024
        self.logger.info(f"HTTP Forward: {self.service_name} -> {self.target_url}")
        self.logger.info(f"Cache upload URL: {self.worker_url}/api/cache-upload")
    async def initialize(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.websocket_sessions = {}
        self.logger.info("HTTP session initialized")
    async def _handle_websocket_upgrade(self, session_id: str, upgrade_data):
        try:
            self.logger.info(f"[WS-UPGRADE] Starting upgrade for session {session_id}")
            if isinstance(upgrade_data, str):
                import json
                upgrade_data = json.loads(upgrade_data)
            path = upgrade_data.get('path', '/')
            headers = upgrade_data.get('headers', {})
            self.logger.info(f"[WS-UPGRADE] Path: {path}, Headers count: {len(headers)}")
            if 'origin' in headers or 'Origin' in headers:
                origin = headers.get('origin') or headers.get('Origin')
                self.logger.info(f"[WS-UPGRADE] Origin: {origin}")
            if 'cookie' in headers or 'Cookie' in headers:
                cookie = headers.get('cookie') or headers.get('Cookie')
                self.logger.info(f"[WS-UPGRADE] Cookie: {cookie[:50] if cookie else 'None'}...")
            url = self.target_url.replace('http://', 'ws://').replace('https://', 'wss://') + path
            self.logger.info(f"[WS-UPGRADE] Connecting to {url}")
            import websockets
            extra_headers_list = []
            for key, value in headers.items():
                key_lower = key.lower()
                if key_lower not in ['host', 'upgrade', 'connection', 'sec-websocket-key', 
                                       'sec-websocket-version', 'sec-websocket-extensions',
                                       'sec-websocket-protocol']:
                    if key_lower == 'origin':
                        value = self.target_url.rstrip('/')
                        self.logger.info(f"[WS-UPGRADE] Modified Origin to: {value}")
                    extra_headers_list.append((key, value))
            self.logger.info(f"[WS-UPGRADE] Extra headers count: {len(extra_headers_list)}")
            ws = await websockets.connect(url, additional_headers=extra_headers_list if extra_headers_list else None)
            self.logger.info(f"[WS-UPGRADE] Connected successfully to {url}")
            if not hasattr(self, 'websocket_sessions'):
                self.websocket_sessions = {}
            self.websocket_sessions[session_id] = ws
            self.logger.info(f"[WS-UPGRADE] Session {session_id} saved")
            await self.send_to_worker({
                'service': self.service_name,
                'session_id': session_id,
                'transport': 'http',
                'category': 'control',
                'action': 'connected'
            })
            self.logger.info(f"[WS-UPGRADE] Sent 'connected' to Worker")
            asyncio.create_task(self._websocket_receive_loop(session_id, ws))
            self.logger.info(f"[WS-UPGRADE] Receive loop started for {session_id}")
        except Exception as e:
            self.logger.error(f"WebSocket upgrade failed: {e}")
            await self.send_to_worker({
                'service': self.service_name,
                'session_id': session_id,
                'transport': 'http',
                'category': 'control',
                'action': 'error'
            }, {'message': str(e)})
    async def _websocket_receive_loop(self, session_id: str, ws):
        self.logger.info(f"[WS-RECV-LOOP] Started for {session_id}")
        message_count = 0
        try:
            async for message in ws:
                message_count += 1
                self.logger.info(f"[WS-RECV] Message #{message_count}, type: {type(message)}, len: {len(message) if hasattr(message, '__len__') else 'N/A'}")
                data = message if isinstance(message, bytes) else message.encode('utf-8')
                await self.send_to_worker({
                    'service': self.service_name,
                    'session_id': session_id,
                    'transport': 'http',
                    'category': 'data',
                    'action': 'data'
                }, data)
                self.logger.info(f"[WS-RECV] Message #{message_count} forwarded to Worker")
        except Exception as e:
            self.logger.error(f"[WS-RECV-LOOP] Error: {e}")
        finally:
            await self.send_to_worker({
                'service': self.service_name,
                'session_id': session_id,
                'transport': 'http',
                'category': 'control',
                'action': 'close'
            })
    async def _handle_websocket_data(self, session_id: str, data: Any):
        self.logger.info(f"[WS-SEND] Received data from Worker, session: {session_id}, type: {type(data)}, len: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        if not hasattr(self, 'websocket_sessions'):
            self.logger.error(f"[WS-SEND] No websocket_sessions attribute!")
            return
        ws = self.websocket_sessions.get(session_id)
        if not ws:
            self.logger.warning(f"[WS-SEND] WebSocket session not found: {session_id}")
            return
        try:
            if isinstance(data, bytes):
                await ws.send(data)
                self.logger.info(f"[WS-SEND] Sent {len(data)} bytes to ttyd")
            else:
                await ws.send(str(data))
                self.logger.info(f"[WS-SEND] Sent {len(str(data))} chars to ttyd")
        except Exception as e:
            self.logger.error(f"[WS-SEND] Send error: {e}")
    async def _handle_websocket_close(self, session_id: str):
        if not hasattr(self, 'websocket_sessions'):
            return
        ws = self.websocket_sessions.get(session_id)
        if ws:
            try:
                await ws.close()
            except:
                pass
            del self.websocket_sessions[session_id]
            self.logger.info(f"WebSocket closed: {session_id}")
    async def cleanup(self):
        if self.session:
            await self.session.close()
            self.logger.info("HTTP session closed")
        if hasattr(self, 'websocket_sessions'):
            for session_id in list(self.websocket_sessions.keys()):
                await self._handle_websocket_close(session_id)
    async def handle_message(self, message: dict, payload: Optional[Any]):
        session_id = message.get('session_id')
        request_id = message.get('request_id')
        category = message.get('category')
        action = message.get('action')
        self.logger.debug(f"Received HTTP message: sess={session_id}, req={request_id}, cat={category}, act={action}")
        if request_id and not session_id:
            if category == 'control' and action == 'init':
                await self._handle_http_request(request_id, payload)
            else:
                self.logger.warning(f"Unknown HTTP request: category={category}, action={action}")
            return
        if session_id:
            if category == 'control' and action == 'ws_upgrade':
                await self._handle_websocket_upgrade(session_id, payload)
            elif category == 'data' and action == 'data':
                await self._handle_websocket_data(session_id, payload)
            elif category == 'control' and action == 'close':
                await self._handle_websocket_close(session_id)
            else:
                self.logger.warning(f"Unknown WebSocket message: category={category}, action={action}")
    async def _upload_to_cache(self, file_data: bytes, url_path: str, content_type: str):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url_path)
            clean_path = parsed.path
            if content_type in ('text/plain', 'application/octet-stream'):
                if clean_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif clean_path.endswith('.css'):
                    content_type = 'text/css'
                elif clean_path.endswith('.html'):
                    content_type = 'text/html'
                elif clean_path.endswith('.json'):
                    content_type = 'application/json'
                elif clean_path.endswith('.wasm'):
                    content_type = 'application/wasm'
            upload_url = (
                f"{self.worker_url}/api/cache-upload"
                f"?service={quote(self.service_name)}"
                f"&path={quote(clean_path)}"
                f"&content-type={quote(content_type)}"
            )
            self.logger.info(f"Uploading to cache: {url_path} ({len(file_data)} bytes)")
            headers = {
                'X-Node-ID': self.agent.node_id,
                'Content-Type': 'application/octet-stream'
            }
            timeout = aiohttp.ClientTimeout(total=120)
            async with self.session.post(upload_url, data=file_data, headers=headers, timeout=timeout) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.logger.info(
                        f"✅ Uploaded to cache successfully: {url_path} "
                        f"({result.get('size', 0)} bytes)"
                    )
                    return True
                else:
                    error_text = await resp.text()
                    self.logger.error(
                        f"❌ Cache upload failed: {resp.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"❌ Cache upload exception: {e}", exc_info=True)
            return False
    async def _handle_http_request(self, request_id: str, request_data):
        try:
            if isinstance(request_data, bytes):
                import json
                request_data = json.loads(request_data.decode('utf-8'))
            elif isinstance(request_data, str):
                import json
                request_data = json.loads(request_data)
            method = request_data.get('method', 'GET')
            path = request_data.get('path', '/')
            headers = request_data.get('headers', {})
            body = request_data.get('body')
            headers['host'] = f"{self.target_host}:{self.target_port}"
            if 'Host' in headers:
                headers['Host'] = f"{self.target_host}:{self.target_port}"
            self.logger.info(f"Headers after modification: {headers.get('host')} / {headers.get('Host')}")
            url = self.target_url + path
            self.logger.info(f"Forwarding {method} {url}")
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=body
            ) as resp:
                response_body = await resp.read()
                response_headers = dict(resp.headers)
                content_type = response_headers.get('content-type', '') or response_headers.get('Content-Type', '')
                if 'application/json' in content_type and response_body:
                    try:
                        text = response_body.decode('utf-8')
                        local_addr = f"127.0.0.1:{self.target_port}"
                        if local_addr in text:
                            text = text.replace(f"ws://{local_addr}", "{{__WS_PUBLIC__}}")
                            text = text.replace(f"http://{local_addr}", "{{__HTTP_PUBLIC__}}")
                            response_body = text.encode('utf-8')
                    except:
                        pass
                body_size = len(response_body) if response_body else 0
                self.logger.info(f"Response body size: {body_size} bytes")
                message = {
                    'service': self.service_name,
                    'request_id': request_id,
                    'transport': 'http',
                    'category': 'data',
                    'action': 'complete',
                    'response': {
                        'status': resp.status,
                        'statusText': resp.reason,
                        'headers': response_headers
                    }
                }
                await self.send_to_worker(message, response_body)
                self.logger.info(f"Response sent: {resp.status} {len(response_body)} bytes")
        except asyncio.TimeoutError:
            self.logger.error(f"HTTP request timeout: {request_id}")
            await self._send_error_response(request_id, 504, "Gateway Timeout")
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP client error: {e}")
            await self._send_error_response(request_id, 502, f"Bad Gateway: {e}")
        except Exception as e:
            self.logger.error(f"HTTP forward error: {e}", exc_info=True)
            await self._send_error_response(request_id, 500, f"Internal Error: {e}")
    async def _send_error_response(self, request_id: str, status: int, message: str):
        error_data = {
            'status': status,
            'statusText': message,
            'headers': {'Content-Type': 'text/plain'},
            'body': message
        }
        await self.send_to_worker({
            'service': self.service_name,
            'request_id': request_id,
            'transport': 'http',
            'category': 'error',
            'action': 'complete'
        }, error_data)