import asyncio
import os
import pty
import struct
import fcntl
import termios
import signal
import logging
from typing import Dict, Any
from .base import Plugin
class TerminalPlugin(Plugin):
    def __init__(self, agent, service_config: dict):
        super().__init__(agent, service_config)
        self.sessions = {}
    async def initialize(self):
        self.logger.info("Terminal plugin initialized")
    async def handle_message(self, message: dict, payload: Any):
        session_id = None
        try:
            session_id = message.get('session_id')
            if not session_id:
                self.logger.error("Message missing session_id")
                return
            category = message.get('category')
            if category == 'control':
                action = message.get('action')
                if action == 'init':
                    await self._init_terminal(session_id, message)
                elif action == 'close':
                    await self._cleanup_session(session_id)
                return
            if payload is None:
                if session_id in self.sessions:
                    self.logger.info(f"Client disconnected: {session_id}, keeping shell alive for reconnection")
                return
            if isinstance(payload, str):
                data = payload.encode('utf-8')
            elif isinstance(payload, bytes):
                data = payload
            else:
                self.logger.error(f"Unexpected payload type: {type(payload)}")
                return
            if len(data) == 1 and data[0] == 0:
                return
            elif len(data) > 0 and data[0] == 0x01:
                try:
                    import json
                    msg = json.loads(data[1:].decode('utf-8'))
                    if msg.get('type') == 'resize':
                        await self._handle_resize(session_id, msg.get('rows', 24), msg.get('cols', 80))
                        return
                except Exception as e:
                    self.logger.debug(f"Failed to parse control message: {e}")
            await self._handle_input(session_id, data)
        except Exception as e:
            self.logger.error(f'CRITICAL: Terminal plugin error: {e}', exc_info=True)
            import traceback
            self.logger.error(f'Terminal plugin traceback: {traceback.format_exc()}')
            if session_id:
                try:
                    await self._cleanup_session(session_id)
                except Exception as cleanup_e:
                    self.logger.error(f'Terminal cleanup error: {cleanup_e}')
                    pass
    async def _init_terminal(self, session_id: str, message: dict):
        if session_id in self.sessions:
            self.logger.warning(f"Session already exists: {session_id}")
            return
        term_size = message.get('term_size', {})
        rows = term_size.get('rows', 24)
        cols = term_size.get('cols', 80)
        try:
            shell = os.environ.get('SHELL', '/bin/bash')
            pid, master_fd = pty.fork()
            if pid == 0:
                os.environ['TERM'] = 'xterm-256color'
                os.environ['LINES'] = str(rows)
                os.environ['COLUMNS'] = str(cols)
                os.execvp(shell, [shell])
            else:
                flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
                fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                winsize = struct.pack('HHHH', rows, cols, 0, 0)
                fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                self.logger.info(f"Terminal size: {rows}x{cols}")
                self.sessions[session_id] = {
                    'master_fd': master_fd,
                    'pid': pid,
                    'read_task': None
                }
                read_task = asyncio.create_task(
                    self._read_from_pty(session_id, master_fd)
                )
                self.sessions[session_id]['read_task'] = read_task
                self.logger.info(f"Terminal created: {session_id}, pid={pid}, shell={shell}")
                await self.send_control(session_id, 'ready')
        except Exception as e:
            self.logger.error(f"Failed to create terminal: {e}")
            import traceback
            traceback.print_exc()
    async def _handle_input(self, session_id: str, data: bytes):
        if session_id not in self.sessions:
            self.logger.warning(f"Session not found: {session_id}")
            return
        session = self.sessions[session_id]
        master_fd = session['master_fd']
        if data == b'\x00' or data == b'\\x00' or (isinstance(data, str) and data in ['\x00', '\\x00']):
            return
        data_str = data.decode('utf-8', errors='ignore').strip() if isinstance(data, bytes) else data.strip()
        if data_str == '~~exit':
            self.logger.info(f"Special exit command detected for session {session_id}")
            await self._cleanup_session(session_id)
            return
        if len(data) < 100:
            self.logger.debug(f"PTY input: {repr(data[:100])}")
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            os.write(master_fd, data)
        except OSError as e:
            self.logger.error(f"Failed to write to PTY: {e}")
            await self._cleanup_session(session_id)
    async def _handle_resize(self, session_id: str, rows: int, cols: int):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        master_fd = session['master_fd']
        try:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
            os.kill(session['pid'], signal.SIGWINCH)
            self.logger.info(f"Terminal resized: {rows}x{cols}")
        except Exception as e:
            self.logger.error(f"Failed to resize terminal: {e}")
    async def _read_from_pty(self, session_id: str, master_fd: int):
        total_bytes = 0
        message_count = 0
        try:
            while session_id in self.sessions:
                try:
                    data = os.read(master_fd, 8192)
                    if not data:
                        self.logger.info(f"Shell exited (EOF), sent {message_count} messages, {total_bytes} bytes")
                        break
                    total_bytes += len(data)
                    message_count += 1
                    if message_count % 100 == 0:
                        self.logger.info(f"PTY stats: {message_count} messages, {total_bytes} bytes")
                    asyncio.create_task(self.send_data(session_id, data))
                except BlockingIOError:
                    await asyncio.sleep(0.01)
                except OSError as e:
                    if e.errno == 5:
                        self.logger.info(f"Shell exited (PTY closed), sent {message_count} messages, {total_bytes} bytes")
                    else:
                        self.logger.error(f"PTY read error: {e}, sent {message_count} messages")
                    break
        except Exception as e:
            self.logger.error(f"Error reading from PTY: {e}, sent {message_count} messages")
        finally:
            self.logger.info(f"PTY read loop ended for {session_id}, total: {message_count} messages, {total_bytes} bytes")
            await self._cleanup_session(session_id)
    async def _cleanup_session(self, session_id: str):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        if session.get('read_task'):
            session['read_task'].cancel()
        try:
            os.close(session['master_fd'])
        except Exception:
            pass
        try:
            os.kill(session['pid'], signal.SIGTERM)
            try:
                os.waitpid(session['pid'], os.WNOHANG)
            except Exception:
                pass
        except Exception:
            pass
        del self.sessions[session_id]
        self.logger.info(f"Terminal session cleaned up: {session_id}")
    async def cleanup(self):
        for session_id in list(self.sessions.keys()):
            await self._cleanup_session(session_id)
        self.logger.info("Terminal plugin cleanup")