import asyncio
import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .tunnel_connection import TunnelConnection
from .tunnel_client import TunnelClientManager
def get_agents_dir() -> Path:
    import sys
    import os
    cmd = os.path.basename(sys.argv[0]) if sys.argv else ''
    is_dev = cmd == 'tunnel4'
    subdir = 'agents-dev' if is_dev else 'agents'
    return Path.home() / '.tunnel' / subdir
def write_agent_file(node_id: str, data: dict):
    agents_dir = get_agents_dir()
    agents_dir.mkdir(parents=True, exist_ok=True)
    filepath = agents_dir / f'{node_id}.json'
    filepath.write_text(json.dumps(data, indent=2))
def remove_agent_file(node_id: str):
    filepath = get_agents_dir() / f'{node_id}.json'
    if filepath.exists():
        filepath.unlink()
class Agent:
    def __init__(self, config: dict):
        self.config = config
        self.connection: Optional[TunnelConnection] = None
        self.plugins: Dict[str, Any] = {}
        self.running = False
        self.node_id = config.get('node_id', self._generate_node_id())
        self.connection_monitor_task = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.tunnel_manager = TunnelClientManager()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('agent')
    async def start(self):
        self.running = True
        self.logger.info('Starting agent...')
        try:
            await self.connect_to_worker()
            await self.load_plugins()
            await self.register_services()
            self._write_discovery_file()
            self.logger.info('Agent started successfully')
            await self.message_loop()
        except KeyboardInterrupt:
            self.logger.info('Received interrupt signal')
        except Exception as e:
            self.logger.error(f'CRITICAL: Agent crashed with error: {e}', exc_info=True)
            import traceback
            self.logger.error(f'Full traceback: {traceback.format_exc()}')
            await asyncio.sleep(2)
        finally:
            self.logger.info('Agent stopping...')
            await self.stop()
    async def connect_to_worker(self):
        try:
            import websockets
        except ImportError:
            raise RuntimeError('websockets library not found. Install it with: pip install websockets')
        worker_url = self.config['worker_url']
        self.logger.info(f'Connecting to {worker_url}')
        if not worker_url.endswith('/agent/connect'):
            if not worker_url.endswith('/'):
                worker_url += '/'
            worker_url += 'agent/connect'
        ws = await websockets.connect(worker_url)
        self.connection = TunnelConnection(ws)
        self.logger.info('Connected to worker')
    async def load_plugins(self):
        services = self.config.get('services', [])
        for service_config in services:
            service_type = service_config['type']
            service_name = service_config['name']
            try:
                plugin = await self._load_plugin(service_type, service_config)
                self.plugins[service_name] = plugin
                await plugin.initialize()
                self.logger.info(f'Loaded plugin: {service_name} ({service_type})')
            except Exception as e:
                self.logger.error(f'Failed to load plugin {service_name}: {e}', exc_info=True)
    async def _load_plugin(self, service_type: str, service_config: dict):
        if service_type == 'forward':
            transport = service_config.get('transport', 'http')
            if transport == 'http':
                from .plugins.http_forward import HTTPForwardPlugin
                return HTTPForwardPlugin(self, service_config)
            elif transport == 'tcp':
                from .plugins.tcp_forward import TCPForwardPlugin
                return TCPForwardPlugin(self, service_config)
            elif transport == 'websocket':
                from .plugins.websocket_forward import WebSocketForwardPlugin
                return WebSocketForwardPlugin(self, service_config)
            else:
                raise ValueError(f"Unknown transport: {transport}")
        elif service_type == 'builtin':
            service_name = service_config['name']
            plugin_config = service_config.get('config', {})
            if service_name == '@exec':
                from .plugins.exec import ExecPlugin
                return ExecPlugin(self, service_config)
            elif service_name == '@socks5':
                from .plugins.socks5 import SOCKS5Plugin
                return SOCKS5Plugin(self, service_config)
            elif service_name == '@term':
                from .plugins.terminal import TerminalPlugin
                return TerminalPlugin(self, service_config)
            else:
                raise ValueError(f"Unknown builtin service: {service_name}")
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    async def register_services(self):
        services = []
        for service_config in self.config.get('services', []):
            service_type = service_config['type']
            if service_type == 'forward':
                transport = service_config.get('transport', 'http')
                if transport == 'websocket':
                    service_type = 'ws'
                elif transport == 'tcp':
                    service_type = 'tcp'
                else:
                    service_type = 'http'
            services.append({
                'name': service_config['name'],
                'type': service_type,
                'transport': service_config.get('transport'),
                'target': service_config.get('target')
            })
        register_msg = {
            'type': 'register',
            'node_id': self.node_id,
            'services': services,
            'tags': self.config.get('tags', {}),
            'ip_info': self.config.get('ip_info', {})
        }
        await self.connection.send(register_msg)
        self.logger.info(f'Registered {len(services)} services')
        tags = self.config.get('tags', {})
        if tags:
            simple_tags = tags.get('simpleTags', [])
            if simple_tags:
                self.logger.info(f'Tags: {", ".join(simple_tags)}')
    async def message_loop(self):
        message_count = 0
        last_status_time = asyncio.get_event_loop().time()
        while self.running:
            try:
                message, payload = await self.connection.receive()
                message_count += 1
                current_time = asyncio.get_event_loop().time()
                if current_time - last_status_time >= 60:
                    self.logger.debug(f'[AGENT:DIAG] Status: messages={message_count}, plugins={list(self.plugins.keys())}, connection_closed={self.connection.closed}')
                    last_status_time = current_time
                if message.get('type') == 'heartbeat':
                    continue
                if message.get('type') == 'register_ack':
                    self.logger.info(f'Registration confirmed, node_id: {message.get("node_id")}')
                    dynamic_services = message.get('dynamic_services', [])
                    if dynamic_services and self.config.get('restore_services', True):
                        await self._restore_dynamic_services(dynamic_services)
                    continue
                await self.handle_message(message, payload)
            except ConnectionError as e:
                self.logger.error(f'[AGENT:DIAG] Connection error in message_loop: {e}, messages_processed={message_count}')
                await self.reconnect()
            except Exception as e:
                self.logger.error(f'CRITICAL: Error in message loop: {e}', exc_info=True)
                import traceback
                self.logger.error(f'Message loop traceback: {traceback.format_exc()}')
                await asyncio.sleep(1)
    async def handle_message(self, message: dict, payload: Any):
        try:
            msg_type = message.get('type')
            service = message.get('service')
            session_id = message.get('session_id')
            self.logger.info(f"Agent received message: type={msg_type}, service={service}, session_id={session_id}")
            if msg_type == 'add_service':
                await self.handle_add_service(message)
                return
            elif msg_type == 'remove_service':
                await self.handle_remove_service(message)
                return
            elif msg_type == 'exec_command':
                await self.handle_exec_command(message)
                return
            elif msg_type == 'exec_command_async':
                await self.handle_exec_command_async(message)
                return
            elif msg_type == 'mapping_add':
                await self.handle_mapping_add(message)
                return
            elif msg_type == 'mapping_remove':
                await self.handle_mapping_remove(message)
                return
            if not service:
                self.logger.error(f'Missing service field in message: {message}')
                return
            plugin = self.plugins.get(service)
            if not plugin:
                self.logger.error(f'No plugin for service: {service}')
                self.logger.error(f'Available plugins: {list(self.plugins.keys())}')
                await self.send_error(message, f'Service {service} not found')
                return
            self.logger.info(f"Forwarding to plugin: {service}")
            await plugin.handle_message(message, payload)
        except Exception as e:
            self.logger.error(f'Error handling message: {e}', exc_info=True)
            await self.send_error(message, str(e))
    async def send_error(self, original_message: dict, error_message: str):
        error_response = {
            'service': original_message.get('service'),
            'session_id': original_message.get('session_id'),
            'request_id': original_message.get('request_id'),
            'category': 'error',
            'action': 'error'
        }
        error_data = {
            'code': 'PLUGIN_ERROR',
            'message': error_message
        }
        await self.connection.send(error_response, error_data)
    async def reconnect(self):
        retry_count = 0
        max_retries = 10
        self.logger.info(f'[AGENT:DIAG] Starting reconnect, current state: running={self.running}, plugins={list(self.plugins.keys())}')
        while retry_count < max_retries and self.running:
            try:
                self.logger.info(f'[AGENT:DIAG] Reconnecting... (attempt {retry_count + 1}/{max_retries})')
                if self.connection:
                    self.logger.debug(f'[AGENT:DIAG] Closing old connection, closed={self.connection.closed}')
                    await self.connection.close()
                await self.connect_to_worker()
                await self.register_services()
                self.logger.info(f'[AGENT:DIAG] Reconnected successfully after {retry_count + 1} attempts')
                return
            except Exception as e:
                self.logger.error(f'[AGENT:DIAG] Reconnect attempt {retry_count + 1} failed: {e}')
                retry_count += 1
                delay = min(30, 2 ** retry_count)
                await asyncio.sleep(delay)
        self.logger.error('Max retries reached, giving up')
        self.running = False
    async def stop(self):
        self.running = False
        self.logger.info('Stopping agent...')
        remove_agent_file(self.node_id)
        if self.connection_monitor_task:
            self.connection_monitor_task.cancel()
            try:
                await self.connection_monitor_task
            except (asyncio.CancelledError, RuntimeError):
                pass
            self.logger.info('Connection monitor stopped')
        for plugin in self.plugins.values():
            try:
                await plugin.cleanup()
            except Exception as e:
                self.logger.error(f'Error cleaning up plugin: {e}')
        try:
            await self.tunnel_manager.stop_all()
            self.logger.info('Tunnel clients stopped')
        except Exception as e:
            self.logger.error(f'Error stopping tunnel clients: {e}')
        if self.connection:
            try:
                await self.connection.close()
            except (RuntimeError, ConnectionError, OSError) as e:
                self.logger.debug(f'Connection close error (ignored): {e}')
    async def _connection_monitor(self):
        while self.running:
            try:
                await asyncio.sleep(300)
                if not self.running:
                    break
                if not self.connection:
                    self.logger.warning("Connection object is None")
                    await self._handle_connection_error("Connection object lost")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f'Connection monitor error: {e}')
                await asyncio.sleep(300)
    def _is_connection_alive(self):
        try:
            if not self.connection:
                return False
            if hasattr(self.connection, 'ws'):
                ws = self.connection.ws
                if ws is None:
                    return False
                if hasattr(ws, 'closed') and ws.closed:
                    return False
                if hasattr(ws, 'state'):
                    if ws.state != 1:
                        return False
            return True
        except Exception:
            return False
        except Exception:
            return False
    async def _handle_connection_error(self, error):
        if not self.running:
            return
        self.reconnect_attempts += 1
        if self.reconnect_attempts > self.max_reconnect_attempts:
            self.logger.error(f"Max reconnect attempts ({self.max_reconnect_attempts}) reached, giving up")
            self.running = False
            return
        delay = min(60, 2 ** (self.reconnect_attempts - 1))
        error_str = str(error).lower()
        if any(x in error_str for x in ['connection closed', 'websocket', 'hibernation']):
            self.logger.debug(f"Connection closed (likely DO hibernation): {error}")
            self.logger.info(f"Reconnecting #{self.reconnect_attempts} in {delay}s...")
        else:
            self.logger.warning(f"Connection error: {error}")
            self.logger.info(f"Attempting reconnect #{self.reconnect_attempts} in {delay}s...")
        try:
            await asyncio.sleep(delay)
            if not self.running:
                return
            await self.reconnect()
            self.reconnect_attempts = 0
            self.logger.info("Reconnection successful")
        except Exception as e:
            self.logger.error(f"Reconnect attempt #{self.reconnect_attempts} failed: {e}")
        self.logger.info('Agent stopped')
    def _generate_node_id(self) -> str:
        import socket
        hostname = socket.gethostname()
        return f'node-{hostname}'
    def _write_discovery_file(self):
        import time
        write_agent_file(self.node_id, {
            'pid': os.getpid(),
            'node_id': self.node_id,
            'worker_url': self.config.get('worker_url'),
            'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
    async def handle_add_service(self, message: dict):
        request_id = message.get('request_id')
        service_name = message.get('service_name')
        port = message.get('port')
        protocol = message.get('protocol', 'http')
        builtin = message.get('builtin', False)
        try:
            if service_name in self.plugins:
                await self.connection.send({
                    'type': 'response',
                    'request_id': request_id,
                    'success': False,
                    'error': 'Service already exists'
                })
                return
            service_config = {
                'name': service_name,
                'port': port,
                'protocol': protocol,
                'builtin': builtin
            }
            if builtin:
                service_config['type'] = 'builtin'
                service_config['name'] = service_name
            else:
                service_config['type'] = 'forward'
                service_config['transport'] = protocol
                service_config['target'] = {
                    'host': '127.0.0.1',
                    'port': port
                }
            plugin = await self._load_plugin(service_config['type'], service_config)
            self.plugins[service_name] = plugin
            await plugin.initialize()
            self.logger.info(f'✓ Service added: {service_name}')
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': True,
                'service_name': service_name
            })
        except Exception as e:
            self.logger.error(f'Failed to add service {service_name}: {e}', exc_info=True)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': False,
                'error': str(e)
            })
    async def handle_remove_service(self, message: dict):
        request_id = message.get('request_id')
        service_name = message.get('service_name')
        try:
            if service_name not in self.plugins:
                await self.connection.send({
                    'type': 'response',
                    'request_id': request_id,
                    'success': False,
                    'error': 'Service not found'
                })
                return
            plugin = self.plugins[service_name]
            await plugin.cleanup()
            del self.plugins[service_name]
            self.logger.info(f'✓ Service removed: {service_name}')
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': True,
                'service_name': service_name
            })
        except Exception as e:
            self.logger.error(f'Failed to remove service {service_name}: {e}', exc_info=True)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': False,
                'error': str(e)
            })
    async def _restore_dynamic_services(self, services: list):
        import socket
        if not services:
            return
        self.logger.info(f'Restoring {len(services)} dynamic services...')
        for svc in services:
            name = svc.get('name')
            port = svc.get('port')
            protocol = svc.get('protocol', 'http')
            if name in self.plugins:
                self.logger.info(f'  ✓ {name} (already loaded)')
                continue
            if port:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('127.0.0.1', port))
                    sock.close()
                    if result != 0:
                        self.logger.warning(f'  ⚠ {name}:{port} (port not available, skipped)')
                        continue
                except Exception as e:
                    self.logger.warning(f'  ⚠ {name}:{port} (check failed: {e}, skipped)')
                    continue
            try:
                service_config = {
                    'name': name,
                    'type': 'forward',
                    'transport': protocol,
                    'target': {'host': '127.0.0.1', 'port': port}
                }
                plugin = await self._load_plugin('forward', service_config)
                self.plugins[name] = plugin
                await plugin.initialize()
                self.logger.info(f'  ✓ {name}:{port} (restored)')
            except Exception as e:
                self.logger.warning(f'  ⚠ {name}:{port} (load failed: {e})')
    async def handle_exec_command(self, message: dict):
        import subprocess
        import time
        request_id = message.get('request_id')
        command = message.get('command')
        try:
            self.logger.info(f'Executing: {command}')
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = time.time() - start_time
            try:
                await self.connection.send({
                    'type': 'response',
                    'request_id': request_id,
                    'success': True,
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'duration': duration
                })
            except (OSError, ConnectionError, RuntimeError):
                pass
            self.logger.info(f'Command completed: exit_code={result.returncode}, duration={duration:.2f}s')
        except subprocess.TimeoutExpired:
            self.logger.error('Command timeout')
            try:
                await self.connection.send({
                    'type': 'response',
                    'request_id': request_id,
                    'success': False,
                    'error': 'Command timeout'
                })
            except (OSError, ConnectionError, RuntimeError):
                pass
        except Exception as e:
            self.logger.error(f'Command execution failed: {e}', exc_info=True)
            try:
                await self.connection.send({
                    'type': 'response',
                    'request_id': request_id,
                    'success': False,
                    'error': str(e)
                })
            except (OSError, ConnectionError, RuntimeError):
                pass
    async def handle_exec_command_async(self, message: dict):
        import subprocess
        task_id = message.get('task_id')
        command = message.get('command')
        try:
            self.logger.info(f'Executing async: {command} (task_id={task_id})')
            async def run_command():
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    await self.connection.send({
                        'type': 'task_completed',
                        'task_id': task_id,
                        'exit_code': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    })
                except Exception as e:
                    await self.connection.send({
                        'type': 'task_failed',
                        'task_id': task_id,
                        'error': str(e)
                    })
            asyncio.create_task(run_command())
        except Exception as e:
            self.logger.error(f'Failed to start async command: {e}', exc_info=True)
    async def handle_mapping_add(self, message: dict):
        request_id = message.get('request_id')
        tunnel_config = message.get('tunnel', {})
        proxy_config = message.get('proxy', {})
        try:
            self.logger.info(f'Adding tunnel mapping: {proxy_config.get("name")}')
            self.logger.info(f'Tunnel config: {tunnel_config}')
            self.logger.info(f'Proxy config: {proxy_config}')
            endpoint = await self.tunnel_manager.add_mapping(tunnel_config, proxy_config)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': True,
                'endpoint': endpoint,
                'status': 'connected'
            })
            self.logger.info(f'Tunnel mapping added: {proxy_config.get("name")} -> {endpoint}')
        except Exception as e:
            self.logger.error(f'Failed to add tunnel mapping: {e}', exc_info=True)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': False,
                'error': str(e)
            })
    async def handle_mapping_remove(self, message: dict):
        request_id = message.get('request_id')
        tunnel_id = message.get('tunnel_id')
        proxy_name = message.get('proxy_name')
        try:
            self.logger.info(f'Removing tunnel mapping: {proxy_name}')
            await self.tunnel_manager.remove_mapping(tunnel_id, proxy_name)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': True
            })
            self.logger.info(f'Tunnel mapping removed: {proxy_name}')
        except Exception as e:
            self.logger.error(f'Failed to remove tunnel mapping: {e}', exc_info=True)
            await self.connection.send({
                'type': 'response',
                'request_id': request_id,
                'success': False,
                'error': str(e)
            })
async def main():
    config = {
        'worker_url': 'ws://localhost:8787/agent/connect',
        'node_id': 'test-node-1',
        'services': [
            {
                'name': 'test-service',
                'type': 'builtin'
            }
        ],
        'tags': {
            'env': 'dev',
            'region': 'local'
        }
    }
    agent = Agent(config)
    await agent.start()
if __name__ == '__main__':
    asyncio.run(main())