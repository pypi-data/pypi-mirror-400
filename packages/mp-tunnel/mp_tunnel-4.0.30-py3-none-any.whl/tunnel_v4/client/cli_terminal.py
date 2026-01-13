import asyncio
import websockets
import sys
import tty
import termios
import os
import signal
import struct
import fcntl
import logging
import warnings
import ssl
import atexit
import json
import time
warnings.filterwarnings("ignore", category=DeprecationWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
_original_terminal_settings = None
_stdin_fd = None
def _restore_terminal():
    global _original_terminal_settings, _stdin_fd
    if _original_terminal_settings and _stdin_fd is not None:
        try:
            termios.tcsetattr(_stdin_fd, termios.TCSANOW, _original_terminal_settings)
        except:
            pass
atexit.register(_restore_terminal)
DEBUG = os.environ.get('TUNNEL_DEBUG', '').lower() in ('1', 'true', 'yes')
def set_debug(enabled):
    global DEBUG
    DEBUG = enabled
def get_terminal_size():
    try:
        winsize = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b'\x00' * 8)
        rows, cols = struct.unpack('HH', winsize[:4])
        return rows, cols
    except:
        return 24, 80
async def run_terminal_client(node_id: str, worker_url: str, token: str) -> int:
    print(f"🔌 连接到远程终端: {node_id}")
    print("   (退出: ~. 或 Ctrl+D x3)")
    if DEBUG:
        print(f"[DEBUG] Starting, is_tty will be checked", file=sys.stderr, flush=True)
    if not worker_url.startswith('ws'):
        worker_url = 'wss://' + worker_url.replace('https://', '').replace('http://', '')
    global _original_terminal_settings, _stdin_fd
    stdin_fd = sys.stdin.fileno()
    _stdin_fd = stdin_fd
    is_tty = os.isatty(stdin_fd)
    if is_tty:
        old_settings = termios.tcgetattr(stdin_fd)
        _original_terminal_settings = old_settings
    else:
        old_settings = None
    ws = None
    connected = False
    user_exit = False
    exit_flag = asyncio.Event()
    last_char = [b'']
    ctrl_d_count = [0]
    current_size = [get_terminal_size()]
    last_activity = [time.time()]
    IDLE_TIMEOUT = 900
    async def connect():
        nonlocal ws, connected
        rows, cols = get_terminal_size()
        url = f"{worker_url}/ws/term?node_id={node_id}&token={token}&rows={rows}&cols={cols}"
        try:
            ws = await asyncio.wait_for(
                websockets.connect(url, ping_interval=None, ping_timeout=None),
                timeout=10.0
            )
            connected = True
            return True
        except Exception as e:
            if DEBUG:
                print(f"\r❌ 连接失败: {e}")
            connected = False
            return False
    async def ensure_connected():
        nonlocal connected
        if ws and connected:
            try:
                await ws.ping()
                return True
            except:
                connected = False
        print("\r🔄 重连中...", end="", flush=True)
        if await connect():
            print("\r✅ 已重连    \r", end="", flush=True)
            return True
        else:
            print("\r❌ 重连失败  \r", end="", flush=True)
            return False
    print("🔄 正在连接...")
    if not await connect():
        print("❌ 连接失败")
        return 1
    print("✅ 已连接\n")
    if is_tty:
        tty.setraw(stdin_fd)
    resize_queue = asyncio.Queue()
    def handle_resize(signum, frame):
        new_size = get_terminal_size()
        if new_size != current_size[0]:
            current_size[0] = new_size
            try:
                resize_queue.put_nowait(new_size)
            except:
                pass
    if is_tty:
        signal.signal(signal.SIGWINCH, handle_resize)
    async def send_resize():
        while not exit_flag.is_set():
            try:
                size = await asyncio.wait_for(resize_queue.get(), timeout=1.0)
                if connected and ws:
                    rows, cols = size
                    msg = json.dumps({"type": "resize", "rows": rows, "cols": cols})
                    await ws.send(b'\x01' + msg.encode('utf-8'))
            except asyncio.TimeoutError:
                continue
            except:
                pass
    async def read_from_stdin():
        nonlocal user_exit, connected
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        try:
            while not exit_flag.is_set():
                try:
                    data = os.read(stdin_fd, 1024)
                    if not data:
                        await asyncio.sleep(0.01)
                        continue
                    if data == b'\x04':
                        ctrl_d_count[0] += 1
                        if ctrl_d_count[0] >= 3:
                            if DEBUG:
                                print(f"\r[DEBUG] Ctrl+D x3 exit", file=sys.stderr, flush=True)
                            user_exit = True
                            exit_flag.set()
                            return
                    else:
                        ctrl_d_count[0] = 0
                    for byte in data:
                        char = bytes([byte])
                        if last_char[0] in (b'', b'\r', b'\n') and char == b'~':
                            last_char[0] = b'~'
                            if DEBUG:
                                import datetime
                                print(f"\r[DEBUG {datetime.datetime.now().strftime('%H:%M:%S')}] ~ detected", file=sys.stderr, flush=True)
                        elif last_char[0] == b'~' and char == b'.':
                            if DEBUG:
                                import datetime
                                print(f"\r[DEBUG {datetime.datetime.now().strftime('%H:%M:%S')}] ~. exit", file=sys.stderr, flush=True)
                            user_exit = True
                            exit_flag.set()
                            return
                        else:
                            last_char[0] = char
                    last_activity[0] = time.time()
                    try:
                        if not connected:
                            if not await ensure_connected():
                                continue
                        asyncio.create_task(ws.send(data))
                    except:
                        connected = False
                except BlockingIOError:
                    await asyncio.sleep(0.01)
                except Exception as e:
                    if DEBUG:
                        import traceback
                        traceback.print_exc()
                    await asyncio.sleep(0.01)
        except Exception as e:
            if DEBUG:
                import traceback
                print(f"\r[DEBUG] read_from_stdin outer exception: {e}", file=sys.stderr, flush=True)
                traceback.print_exc()
            exit_flag.set()
    async def read_from_ws():
        nonlocal connected
        heartbeat_reply_count = [0]
        recv_count = [0]
        while not exit_flag.is_set():
            try:
                if not connected or not ws:
                    await asyncio.sleep(0.1)
                    continue
                data = await asyncio.wait_for(ws.recv(), timeout=1.0)
                if isinstance(data, str):
                    data = data.encode('utf-8')
                if len(data) == 1 and data[0] == 0:
                    heartbeat_reply_count[0] += 1
                    if DEBUG:
                        print(f"\r[DEBUG] Heartbeat reply #{heartbeat_reply_count[0]} received", file=sys.stderr, flush=True)
                    continue
                recv_count[0] += 1
                if DEBUG:
                    print(f"\r[DEBUG] CLI recv #{recv_count[0]}: {len(data)} bytes", file=sys.stderr, flush=True)
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed as e:
                if DEBUG:
                    print(f"\r[DEBUG] WebSocket closed: {e}")
                connected = False
                exit_flag.set()
            except Exception as e:
                if DEBUG:
                    print(f"\r[DEBUG] read_from_ws error: {e}")
                connected = False
                exit_flag.set()
    async def heartbeat():
        nonlocal connected
        heartbeat_count = [0]
        heartbeat_fail_count = [0]
        while not exit_flag.is_set():
            await asyncio.sleep(30)
            heartbeat_count[0] += 1
            idle_time = time.time() - last_activity[0]
            if idle_time > IDLE_TIMEOUT:
                if DEBUG:
                    print(f"\r[DEBUG] Idle timeout after {idle_time:.0f}s", file=sys.stderr, flush=True)
                exit_flag.set()
                return
            if connected and ws:
                try:
                    await ws.send(b'\x00')
                    heartbeat_fail_count[0] = 0
                    if DEBUG:
                        print(f"\r[DEBUG] Heartbeat #{heartbeat_count[0]}, idle: {idle_time:.0f}s")
                except Exception as e:
                    heartbeat_fail_count[0] += 1
                    if DEBUG:
                        print(f"\r[DEBUG] Heartbeat failed ({heartbeat_fail_count[0]}): {e}")
                    connected = False
                    if heartbeat_fail_count[0] >= 3:
                        print("\r🔄 连接断开，正在重连...")
                        if await ensure_connected():
                            print("\r✅ 重连成功")
                            heartbeat_fail_count[0] = 0
                        else:
                            print("\r❌ 重连失败")
    try:
        if DEBUG:
            print("[DEBUG] Starting tasks...", file=sys.stderr, flush=True)
        tasks = [
            asyncio.create_task(read_from_stdin()),
            asyncio.create_task(read_from_ws()),
            asyncio.create_task(heartbeat()),
            asyncio.create_task(send_resize()),
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        if DEBUG:
            for task in done:
                try:
                    exc = task.exception()
                except:
                    exc = None
                print(f"[DEBUG] Task completed: {task.get_name()}, exception: {exc}", file=sys.stderr, flush=True)
        exit_flag.set()
        for task in tasks:
            task.cancel()
        if ws:
            try:
                await asyncio.wait_for(ws.close(), timeout=0.2)
            except:
                pass
    finally:
        if old_settings:
            try:
                termios.tcsetattr(stdin_fd, termios.TCSANOW, old_settings)
                _original_terminal_settings = None
            except:
                pass
        print("\r\n👋 终端已断开")
    return 0