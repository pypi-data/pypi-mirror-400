import asyncio
import logging
import os
import tempfile
import subprocess
from typing import Dict, Optional
from pathlib import Path
logger = logging.getLogger('tunnel_client')
class FrpClient:
    def __init__(self, tunnel_config: dict):
        self.tunnel_id = tunnel_config.get('id', 'default')
        self.endpoint = tunnel_config['endpoint']
        self.port = tunnel_config.get('port', 7000)
        self.token = tunnel_config.get('token', '')
        self.proxies: Dict[str, dict] = {}
        self.process: Optional[subprocess.Popen] = None
        self.config_file: Optional[str] = None
        self._lock = asyncio.Lock()
    async def add_proxy(self, proxy_config: dict) -> str:
        async with self._lock:
            name = proxy_config['name']
            self.proxies[name] = proxy_config
            await self._restart()
            return f"{self.endpoint}:{proxy_config.get('remote_port', 0)}"
    async def remove_proxy(self, name: str):
        async with self._lock:
            if name in self.proxies:
                del self.proxies[name]
                if self.proxies:
                    await self._restart()
                else:
                    await self.stop()
    async def stop(self):
        if self.process:
            logger.info(f"[{self.tunnel_id}] Stopping frpc")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        if self.config_file and os.path.exists(self.config_file):
            os.remove(self.config_file)
            self.config_file = None
    async def _restart(self):
        await self.stop()
        await self._start()
    async def _start(self):
        if not self.proxies:
            return
        config = self._generate_config()
        fd, self.config_file = tempfile.mkstemp(suffix='.toml', prefix='frpc_')
        with os.fdopen(fd, 'w') as f:
            f.write(config)
        logger.info(f"[{self.tunnel_id}] Starting frpc with {len(self.proxies)} proxies")
        logger.info(f"[{self.tunnel_id}] Config file: {self.config_file}")
        logger.info(f"[{self.tunnel_id}] Config:\n{config}")
        try:
            self.process = subprocess.Popen(
                ['frpc', '-c', self.config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await asyncio.sleep(2)
            if self.process.poll() is not None:
                stdout = self.process.stdout.read().decode() if self.process.stdout else ''
                stderr = self.process.stderr.read().decode() if self.process.stderr else ''
                logger.error(f"[{self.tunnel_id}] frpc exit code: {self.process.returncode}")
                logger.error(f"[{self.tunnel_id}] frpc stdout: {stdout}")
                logger.error(f"[{self.tunnel_id}] frpc stderr: {stderr}")
                raise RuntimeError(f"frpc failed to start: {stderr or stdout}")
            logger.info(f"[{self.tunnel_id}] frpc started, pid={self.process.pid}")
        except FileNotFoundError:
            raise RuntimeError("frpc not found. Please install frp client.")
    def _generate_config(self) -> str:
        lines = [
            f'serverAddr = "{self.endpoint}"',
            f'serverPort = {self.port}',
        ]
        if self.token:
            lines.append(f'auth.token = "{self.token}"')
        lines.append('')
        for name, proxy in self.proxies.items():
            lines.append(f'[[proxies]]')
            lines.append(f'name = "{name}"')
            lines.append(f'type = "{proxy.get("protocol", "tcp")}"')
            if proxy.get('remote_port'):
                lines.append(f'remotePort = {proxy["remote_port"]}')
            if proxy.get('plugin'):
                lines.append(f'[proxies.plugin]')
                lines.append(f'type = "{proxy["plugin"]}"')
            else:
                lines.append(f'localIP = "127.0.0.1"')
                lines.append(f'localPort = {proxy["local_port"]}')
            if proxy.get('tunnel_group'):
                lines.append(f'group = "{proxy["tunnel_group"]}"')
                lines.append(f'groupKey = "{proxy.get("group_key", "")}"')
            lines.append('')
        return '\n'.join(lines)
    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None
class TunnelClientManager:
    def __init__(self):
        self.clients: Dict[str, FrpClient] = {}
        self._lock = asyncio.Lock()
    async def add_mapping(self, tunnel_config: dict, proxy_config: dict) -> str:
        async with self._lock:
            tunnel_id = tunnel_config.get('id', 'default')
            if tunnel_id not in self.clients:
                self.clients[tunnel_id] = FrpClient(tunnel_config)
            client = self.clients[tunnel_id]
            return await client.add_proxy(proxy_config)
    async def remove_mapping(self, tunnel_id: str, proxy_name: str):
        async with self._lock:
            if tunnel_id in self.clients:
                client = self.clients[tunnel_id]
                await client.remove_proxy(proxy_name)
                if not client.proxies:
                    del self.clients[tunnel_id]
    async def stop_all(self):
        async with self._lock:
            for client in self.clients.values():
                await client.stop()
            self.clients.clear()
    def get_status(self) -> dict:
        return {
            tunnel_id: {
                'running': client.is_running,
                'proxies': list(client.proxies.keys())
            }
            for tunnel_id, client in self.clients.items()
        }