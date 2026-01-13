import asyncio
import struct
import socket
import logging
from typing import Dict, Any
from .base import Plugin
class SOCKS5Plugin(Plugin):
    SOCKS_VERSION = 0x05
    AUTH_NO_AUTH = 0x00
    AUTH_NO_ACCEPTABLE = 0xFF
    CMD_CONNECT = 0x01
    CMD_BIND = 0x02
    CMD_UDP_ASSOCIATE = 0x03
    ATYP_IPV4 = 0x01
    ATYP_DOMAIN = 0x03
    ATYP_IPV6 = 0x04
    REP_SUCCESS = 0x00
    REP_GENERAL_FAILURE = 0x01
    REP_CONN_NOT_ALLOWED = 0x02
    REP_NETWORK_UNREACHABLE = 0x03
    REP_HOST_UNREACHABLE = 0x04
    REP_CONN_REFUSED = 0x05
    REP_TTL_EXPIRED = 0x06
    REP_CMD_NOT_SUPPORTED = 0x07
    REP_ATYP_NOT_SUPPORTED = 0x08
    def __init__(self, agent, service_config: dict):
        super().__init__(agent, service_config)
        self.sessions = {}
    async def initialize(self):
        self.logger.info("SOCKS5 plugin initialized")
    async def handle_message(self, message: dict, payload: Any):
        try:
            session_id = message.get('session_id')
            if not session_id:
                self.logger.error("Message missing session_id")
                return
            if message.get('category') == 'control':
                action = message.get('action')
                if action == 'init':
                    self.logger.info(f"Session init: {session_id}")
                    return
                elif action == 'close':
                    self.logger.info(f"Session close: {session_id}")
                    await self._cleanup_session(session_id)
                    return
                else:
                    return
            if payload is None:
                if session_id in self.sessions:
                    self.logger.info(f"Client disconnected: {session_id}")
                    await self._cleanup_session(session_id)
                return
            if isinstance(payload, str):
                data = payload.encode('utf-8')
            elif isinstance(payload, bytes):
                data = payload
            else:
                self.logger.error(f"Unexpected payload type: {type(payload)}")
                return
            await self._handle_socks5_data(session_id, data)
        except Exception as e:
            self.logger.error(f"Error in SOCKS5 handle_message: {e}", exc_info=True)
            if 'session_id' in locals() and session_id:
                try:
                    await self._cleanup_session(session_id)
                except Exception:
                    pass
    async def _handle_socks5_data(self, session_id: str, data: bytes):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'state': 'handshake',
                'buffer': b'',
                'reader': None,
                'writer': None,
                'target_task': None
            }
            self.logger.info(f"SOCKS5 session created: {session_id}")
        session = self.sessions[session_id]
        if session['state'] == 'connected':
            if session['writer']:
                try:
                    session['writer'].write(data)
                    await session['writer'].drain()
                except Exception as e:
                    self.logger.error(f"Failed to send to target: {e}")
                    await self._cleanup_session(session_id)
        else:
            session['buffer'] += data
            if session['state'] == 'handshake':
                await self._handle_handshake(session_id, session)
            elif session['state'] == 'request':
                await self._handle_request(session_id, session)
    async def _handle_handshake(self, session_id: str, session: dict):
        buf = session['buffer']
        if len(buf) < 2:
            return
        version = buf[0]
        nmethods = buf[1]
        if len(buf) < 2 + nmethods:
            return
        if version != self.SOCKS_VERSION:
            self.logger.error(f"Unsupported SOCKS version: {version}")
            await self._cleanup_session(session_id)
            return
        response = struct.pack('!BB', self.SOCKS_VERSION, self.AUTH_NO_AUTH)
        await self.send(session_id, response)
        session['buffer'] = buf[2 + nmethods:]
        session['state'] = 'request'
        if session['buffer']:
            await self._handle_request(session_id, session)
    async def _handle_request(self, session_id: str, session: dict):
        buf = session['buffer']
        if len(buf) < 4:
            return
        version = buf[0]
        cmd = buf[1]
        atyp = buf[3]
        if version != self.SOCKS_VERSION:
            self.logger.error(f"Invalid version in request: {version}")
            await self._cleanup_session(session_id)
            return
        if cmd != self.CMD_CONNECT:
            self.logger.warning(f"Unsupported command: {cmd}")
            response = struct.pack('!BBBBIH', self.SOCKS_VERSION, self.REP_CMD_NOT_SUPPORTED, 0, 1, 0, 0)
            await self.send(session_id, response)
            await self._cleanup_session(session_id)
            return
        if atyp == self.ATYP_IPV4:
            if len(buf) < 10:
                return
            addr = socket.inet_ntoa(buf[4:8])
            port = struct.unpack('!H', buf[8:10])[0]
            session['buffer'] = buf[10:]
        elif atyp == self.ATYP_DOMAIN:
            if len(buf) < 5:
                return
            addr_len = buf[4]
            if len(buf) < 5 + addr_len + 2:
                return
            addr = buf[5:5+addr_len].decode('utf-8')
            port = struct.unpack('!H', buf[5+addr_len:7+addr_len])[0]
            session['buffer'] = buf[7+addr_len:]
        elif atyp == self.ATYP_IPV6:
            if len(buf) < 22:
                return
            addr = socket.inet_ntop(socket.AF_INET6, buf[4:20])
            port = struct.unpack('!H', buf[20:22])[0]
            session['buffer'] = buf[22:]
        else:
            self.logger.error(f"Unsupported address type: {atyp}")
            response = struct.pack('!BBBBIH', self.SOCKS_VERSION, self.REP_ATYP_NOT_SUPPORTED, 0, 1, 0, 0)
            await self.send(session_id, response)
            await self._cleanup_session(session_id)
            return
        self.logger.info(f"Connecting to {addr}:{port}")
        try:
            reader, writer = await asyncio.open_connection(addr, port)
            session['reader'] = reader
            session['writer'] = writer
            session['state'] = 'connected'
            response = struct.pack('!BBBBIH', self.SOCKS_VERSION, self.REP_SUCCESS, 0, 1, 0, 0)
            await self.send(session_id, response)
            session['target_task'] = asyncio.create_task(
                self._read_from_target(session_id, session)
            )
            self.logger.info(f"Connected to {addr}:{port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to {addr}:{port}: {e}")
            response = struct.pack('!BBBBIH', self.SOCKS_VERSION, self.REP_HOST_UNREACHABLE, 0, 1, 0, 0)
            await self.send(session_id, response)
            await self._cleanup_session(session_id)
    async def _read_from_target(self, session_id: str, session: dict):
        reader = session['reader']
        try:
            while True:
                data = await reader.read(8192)
                if not data:
                    break
                await self.send(session_id, data)
        except Exception as e:
            self.logger.error(f"Error reading from target: {e}")
        finally:
            await self._cleanup_session(session_id)
    async def send(self, session_id: str, data: bytes):
        await self.agent.connection.send({
            'service': 'socks5',
            'session_id': session_id,
            'transport': 'websocket',
            'category': 'data'
        }, data)
    async def _cleanup_session(self, session_id: str):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        if session.get('target_task'):
            try:
                session['target_task'].cancel()
                try:
                    await session['target_task']
                except asyncio.CancelledError:
                    pass
            except Exception:
                pass
        if session.get('writer'):
            try:
                session['writer'].close()
            except Exception:
                pass
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Session cleaned up: {session_id}")
        else:
            self.logger.debug(f"Session {session_id} already cleaned up")
    async def cleanup(self):
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            try:
                await self._cleanup_session(session_id)
            except Exception as e:
                self.logger.error(f"Error cleaning up SOCKS5 session {session_id}: {e}")
        self.logger.info("SOCKS5 plugin cleanup completed")