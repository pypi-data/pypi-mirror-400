import subprocess
from .base import Plugin
from typing import Any
class ExecPlugin(Plugin):
    def __init__(self, agent, service_config: dict):
        super().__init__(agent, service_config)
        self.sessions = {}
    async def initialize(self):
        self.logger.info("Exec plugin initialized (simple mode)")
    async def handle_request(self, message: dict, payload: Any):
        cmd = message.get('command', '')
        if not cmd and payload:
            cmd = payload.decode('utf-8').strip() if isinstance(payload, bytes) else str(payload).strip()
        if not cmd:
            return {'error': 'No command provided', 'exit_code': -1}
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Command timeout', 'exit_code': -1}
        except Exception as e:
            return {'error': str(e), 'exit_code': -1}
    async def handle_message(self, message: dict, payload: Any):
        session_id = message.get('session_id')
        if not session_id:
            return
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.logger.info(f"Exec received message: {message}")
        self.logger.info(f"Exec received payload type: {type(payload)}, content: {repr(payload)}")
        if payload and isinstance(payload, (str, bytes)):
            if isinstance(payload, bytes):
                cmd = payload.decode('utf-8').strip()
            else:
                cmd = str(payload).strip()
            self.logger.info(f"Raw command before cleaning: {repr(cmd)}")
            cmd = cmd.replace('{path:/}', '').strip()
            self.logger.info(f"Command after cleaning: {repr(cmd)}")
            if cmd:
                self.logger.info(f"Executing command: {repr(cmd)}")
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    output = result.stdout + result.stderr
                    if result.returncode != 0:
                        output += f"\nExit code: {result.returncode}\n"
                    await self.send_data(session_id, output.encode('utf-8'))
                except subprocess.TimeoutExpired:
                    await self.send_data(session_id, b"Error: Command timeout\n")
                except Exception as e:
                    await self.send_data(session_id, f"Error: {e}\n".encode('utf-8'))
            else:
                self.logger.warning("Empty command after cleaning")
                await self.send_data(session_id, b"Error: Empty command\n")
    async def send_data(self, session_id: str, data: bytes):
        await self.agent.connection.send({
            'service': 'exec',
            'session_id': session_id,
            'transport': 'websocket',
            'category': 'data'
        }, data)
    async def cleanup(self):
        self.sessions.clear()