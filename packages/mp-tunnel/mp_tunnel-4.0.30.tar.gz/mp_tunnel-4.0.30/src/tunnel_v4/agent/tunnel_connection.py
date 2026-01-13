import json
import asyncio
import re
import logging
from typing import Any, Optional, Tuple, Callable
logger = logging.getLogger('tunnel_connection')
class TunnelConnection:
    INLINE_THRESHOLD = 64 * 1024
    CHUNK_SIZE = 512 * 1024
    def __init__(self, ws):
        self.ws = ws
        self.pending_binary_frame = None
        self.closed = False
        self.message_handlers = []
        logger.debug(f'TunnelConnection initialized, ws={ws}')
    def on_message(self, handler: Callable):
        self.message_handlers.append(handler)
    async def send(self, message: dict, payload: Any = None) -> None:
        if self.closed:
            logger.warning(f'[CONN:DIAG] Attempt to send on closed connection: {message.get("type", message.get("action"))}')
            raise ConnectionError('Connection is closed')
        try:
            session_id = message.get('session_id', 'N/A')
            action = message.get('action', 'N/A')
            payload_size = len(payload) if payload else 0
            if payload is None:
                logger.info(f'[CONN:SEND] session={session_id[-8:] if len(session_id) > 8 else session_id}, action={action}')
            if payload is None:
                logger.debug(f'[CONN:DIAG] Sending control message: type={message.get("type")}, action={message.get("action")}')
                await self.ws.send(json.dumps(message))
                return
            if isinstance(payload, dict) and self._contains_bytes(payload):
                payload = self._prepare_dict_for_json(payload)
            payload_bytes = self._to_bytes(payload)
            payload_size = len(payload_bytes)
            if payload_size < self.INLINE_THRESHOLD:
                message['payload'] = {
                    'encoding': self._detect_encoding(payload_bytes),
                    'inline': True,
                    'data': self._encode(payload_bytes)
                }
                await self.ws.send(json.dumps(message))
                return
            if payload_size <= self.CHUNK_SIZE:
                message['payload'] = {
                    'encoding': 'binary',
                    'inline': False,
                    'size': payload_size
                }
                await self.ws.send(json.dumps(message))
                await self.ws.send(payload_bytes)
            else:
                import uuid
                transfer_id = str(uuid.uuid4())
                total_chunks = (payload_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
                message['payload'] = {
                    'encoding': 'binary',
                    'inline': False,
                    'chunked': True,
                    'transfer_id': transfer_id,
                    'total_size': payload_size,
                    'chunk_size': self.CHUNK_SIZE,
                    'total_chunks': total_chunks
                }
                await self.ws.send(json.dumps(message))
                for chunk_index in range(total_chunks):
                    start = chunk_index * self.CHUNK_SIZE
                    end = min(start + self.CHUNK_SIZE, payload_size)
                    chunk_data = payload_bytes[start:end]
                    chunk_msg = {
                        'type': 'chunk',
                        'transfer_id': transfer_id,
                        'chunk_index': chunk_index,
                        'chunk_size': len(chunk_data)
                    }
                    await self.ws.send(json.dumps(chunk_msg))
                    await self.ws.send(chunk_data)
        except (OSError, ConnectionError, RuntimeError) as e:
            logger.error(f'[CONN:DIAG] Send failed (connection error): {e}')
            self.closed = True
            raise ConnectionError(f'Failed to send message: {e}')
        except Exception as e:
            logger.error(f'[CONN:DIAG] Send failed (unexpected): {e}')
            self.closed = True
            raise ConnectionError(f'Unexpected error sending message: {e}')
    async def receive(self) -> Tuple[dict, Optional[Any]]:
        if self.closed:
            logger.warning('[CONN:DIAG] Attempt to receive on closed connection')
            raise ConnectionError('Connection is closed')
        try:
            data = await self.ws.recv()
            logger.debug(f'[CONN:DIAG] Received data: type={type(data).__name__}, len={len(data) if data else 0}')
        except Exception as e:
            logger.error(f'[CONN:DIAG] Receive failed: {e}')
            self.closed = True
            raise ConnectionError(f'Failed to receive: {e}')
        if isinstance(data, str):
            return await self._handle_json_message(data)
        elif isinstance(data, bytes):
            if len(data) == 1 and data[0] == 0:
                return {'type': 'heartbeat'}, None
            return self._handle_binary_message(data)
        else:
            raise ValueError(f'Unknown message type: {type(data)}')
    async def _handle_json_message(self, json_str: str) -> Tuple[dict, Optional[Any]]:
        message = json.loads(json_str)
        if 'payload' not in message:
            return message, None
        payload_desc = message['payload']
        if payload_desc.get('inline'):
            payload = self._decode_inline(payload_desc)
            return message, payload
        if self.pending_binary_frame:
            import logging
            logging.warning('Previous binary frame not received, overwriting')
        self.pending_binary_frame = message
        try:
            binary_data = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
        except asyncio.TimeoutError:
            self.pending_binary_frame = None
            raise ValueError('Timeout waiting for binary frame')
        if not isinstance(binary_data, bytes):
            self.pending_binary_frame = None
            raise ValueError(f'Expected binary frame, got {type(binary_data)}')
        expected_size = payload_desc['size']
        actual_size = len(binary_data)
        if actual_size != expected_size:
            import logging
            logging.warning(f'Binary frame size mismatch: expected {expected_size}, got {actual_size}')
        message = self.pending_binary_frame
        self.pending_binary_frame = None
        return message, binary_data
    def _handle_binary_message(self, data: bytes) -> Tuple[dict, bytes]:
        if not self.pending_binary_frame:
            raise ValueError('Unexpected binary frame without JSON header')
        message = self.pending_binary_frame
        self.pending_binary_frame = None
        return message, data
    def _to_bytes(self, data: Any) -> bytes:
        if isinstance(data, bytes):
            return data
        if isinstance(data, bytearray):
            return bytes(data)
        if isinstance(data, str):
            return data.encode('utf-8')
        if isinstance(data, (dict, list)):
            if self._contains_bytes(data):
                raise TypeError(f'Dict/list contains bytes, should be handled by send() method')
            return json.dumps(data).encode('utf-8')
        raise TypeError(f'Cannot convert to bytes: {type(data)}')
    def _contains_bytes(self, obj) -> bool:
        if isinstance(obj, bytes):
            return True
        if isinstance(obj, dict):
            return any(self._contains_bytes(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._contains_bytes(v) for v in obj)
        return False
    def _prepare_dict_for_json(self, obj):
        import base64
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('ascii')
        elif isinstance(obj, dict):
            return {k: self._prepare_dict_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_dict_for_json(v) for v in obj]
        else:
            return obj
    def _detect_encoding(self, data: bytes) -> str:
        try:
            text = data.decode('utf-8')
            if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', text):
                return 'binary'
            return 'utf8'
        except UnicodeDecodeError:
            return 'binary'
    def _encode(self, data: bytes):
        encoding = self._detect_encoding(data)
        if encoding == 'utf8':
            return data.decode('utf-8')
        else:
            return list(data)
    def _decode_inline(self, payload: dict) -> Any:
        encoding = payload.get('encoding', 'utf8')
        data = payload['data']
        if encoding == 'utf8':
            return data
        elif encoding == 'json':
            return data
        elif isinstance(data, list):
            return bytes(data)
        else:
            return data
    async def close(self):
        if not self.closed:
            logger.debug('[CONN:DIAG] Closing connection')
            self.closed = True
            try:
                await self.ws.close()
                logger.debug('[CONN:DIAG] Connection closed successfully')
            except (RuntimeError, ConnectionError, OSError) as e:
                logger.debug(f'[CONN:DIAG] Close error (ignored): {e}')