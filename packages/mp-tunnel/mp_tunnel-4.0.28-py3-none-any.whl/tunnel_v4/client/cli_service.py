import aiohttp
import asyncio
import socket
import json
import os
import sys
def get_current_node_id():
    node_id = os.getenv('TUNNEL_NODE_ID')
    if node_id:
        return node_id
    state_file = '/tmp/tunnel-agent-state.json'
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                state = json.load(f)
                return state.get('node_id')
        except:
            pass
    return socket.gethostname()
def parse_service(service_str):
    if service_str.startswith('@'):
        return {
            'name': service_str,
            'port': None,
            'protocol': None,
            'builtin': True
        }
    else:
        parts = service_str.split(':')
        if len(parts) < 2:
            raise ValueError(f'Invalid service format: {service_str} (expected name:port:protocol)')
        name = parts[0]
        port = int(parts[1])
        protocol = parts[2] if len(parts) >= 3 else 'http'
        return {
            'name': name,
            'port': port,
            'protocol': protocol,
            'builtin': False
        }
async def run_add_service(services, node_id, nodes, worker_url):
    try:
        if nodes:
            target_nodes = [n.strip() for n in nodes.split(',')]
        elif node_id:
            target_nodes = [node_id]
        else:
            target_nodes = [get_current_node_id()]
        service_configs = []
        for svc_str in services:
            try:
                service_configs.append(parse_service(svc_str))
            except ValueError as e:
                print(f'✗ {e}', file=sys.stderr)
                return 1
        async with aiohttp.ClientSession() as session:
            for target_node in target_nodes:
                if len(target_nodes) > 1:
                    print(f'\n=== Node: {target_node} ===')
                else:
                    print(f'Node: {target_node}')
                for svc in service_configs:
                    try:
                        async with session.post(
                            f'{worker_url}/api/service/add',
                            json={
                                'node_id': target_node,
                                'service_name': svc['name'],
                                'port': svc['port'],
                                'protocol': svc['protocol'],
                                'builtin': svc['builtin']
                            },
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as resp:
                            result = await resp.json()
                            if result.get('success'):
                                if svc['builtin']:
                                    print(f"  ✓ Builtin service added: {svc['name']}")
                                else:
                                    print(f"  ✓ Service added: {svc['name']}")
                                    if result.get('url'):
                                        print(f"    URL: {result['url']}")
                            else:
                                error = result.get('error', 'Unknown error')
                                print(f"  ✗ Failed to add {svc['name']}: {error}", file=sys.stderr)
                    except asyncio.TimeoutError:
                        print(f"  ✗ Timeout adding {svc['name']}", file=sys.stderr)
                    except Exception as e:
                        print(f"  ✗ Error adding {svc['name']}: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return 1
async def run_remove_service(services, node_id, nodes, worker_url):
    try:
        if nodes:
            target_nodes = [n.strip() for n in nodes.split(',')]
        elif node_id:
            target_nodes = [node_id]
        else:
            target_nodes = [get_current_node_id()]
        async with aiohttp.ClientSession() as session:
            for target_node in target_nodes:
                if len(target_nodes) > 1:
                    print(f'\n=== Node: {target_node} ===')
                else:
                    print(f'Node: {target_node}')
                for svc_name in services:
                    try:
                        async with session.post(
                            f'{worker_url}/api/service/remove',
                            json={
                                'node_id': target_node,
                                'service_name': svc_name
                            },
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as resp:
                            result = await resp.json()
                            if result.get('success'):
                                print(f"  ✓ Service removed: {svc_name}")
                            else:
                                error = result.get('error', 'Unknown error')
                                print(f"  ✗ Failed to remove {svc_name}: {error}", file=sys.stderr)
                    except asyncio.TimeoutError:
                        print(f"  ✗ Timeout removing {svc_name}", file=sys.stderr)
                    except Exception as e:
                        print(f"  ✗ Error removing {svc_name}: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return 1
async def run_list_services(node_id, worker_url):
    try:
        if not node_id:
            node_id = get_current_node_id()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{worker_url}/api/service/list',
                params={'node_id': node_id},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                result = await resp.json()
                if not result.get('success'):
                    error = result.get('error', 'Unknown error')
                    print(f'✗ Error: {error}', file=sys.stderr)
                    return 1
                print(f"\nNode: {node_id} ({get_current_node_id() == node_id and 'current' or 'remote'})")
                print(f"Status: online")
                services = result.get('services', [])
                builtin_services = [s for s in services if s.get('builtin')]
                forwarding_services = [s for s in services if not s.get('builtin')]
                if builtin_services:
                    print(f"\nBuiltin Services:")
                    for svc in builtin_services:
                        svc_type = f"[{svc.get('type', 'static')}]"
                        print(f"  ✓ {svc['name']:<20} {svc_type}")
                if forwarding_services:
                    print(f"\nPort Forwarding:")
                    for svc in forwarding_services:
                        svc_type = f"[{svc.get('type', 'static')}]"
                        port_info = f"{svc.get('port', 'N/A')}:{svc.get('protocol', 'N/A')}"
                        print(f"  ✓ {svc['name']:<20} {port_info:<15} {svc_type}")
                        if svc.get('url'):
                            print(f"    URL: {svc['url']}")
                total = result.get('total', 0)
                static = result.get('static', 0)
                dynamic = result.get('dynamic', 0)
                print(f"\nTotal: {total} services ({static} static, {dynamic} dynamic)")
        return 0
    except asyncio.TimeoutError:
        print('✗ Timeout', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return 1
async def select_node_interactive(worker_url, tags=None):
    try:
        async with aiohttp.ClientSession() as session:
            url = f'{worker_url}/api/v1/nodes'
            if tags:
                url += f'?tags={tags}'
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    print('✗ Failed to fetch nodes', file=sys.stderr)
                    return None
                result = await resp.json()
                if not result.get('success'):
                    print(f'✗ Error: {result.get("error")}', file=sys.stderr)
                    return None
                nodes = result.get('nodes', [])
                if not nodes:
                    print('⚠️  No nodes available')
                    return None
                online_nodes = [n for n in nodes if n.get('status') == 'online']
                if not online_nodes:
                    print('⚠️  No online nodes')
                    return None
                print()
                print('可用节点：')
                for i, node in enumerate(online_nodes, 1):
                    node_id = node.get('node_id')
                    tags = node.get('tags', [])
                    tag_str = f" ({', '.join(tags[:3])})" if tags else ""
                    print(f"  {i}) {node_id}{tag_str}")
                print()
                try:
                    choice = input(f'请选择节点 (1-{len(online_nodes)}): ').strip()
                    if not choice:
                        return None
                    idx = int(choice) - 1
                    if 0 <= idx < len(online_nodes):
                        return online_nodes[idx]['node_id']
                    else:
                        print('✗ Invalid choice', file=sys.stderr)
                        return None
                except (ValueError, KeyboardInterrupt):
                    print()
                    return None
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return None
async def run_list_nodes(worker_url, show_offline=False):
    from tunnel_v4.config import get_worker_url
    if not worker_url:
        worker_url = get_worker_url()
    try:
        async with aiohttp.ClientSession() as session:
            params = {}
            if show_offline:
                params['show_offline'] = 'true'
            url = f'{worker_url}/api/v1/nodes'
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    print('✗ Failed to fetch nodes', file=sys.stderr)
                    return 1
                result = await resp.json()
                if not result.get('success'):
                    print(f'✗ Error: {result.get("error")}', file=sys.stderr)
                    return 1
                nodes = result.get('nodes', [])
                if not nodes:
                    print('⚠️  No nodes available')
                    return 0
                print()
                print('节点列表：')
                print()
                for node in nodes:
                    node_id = node.get('node_id')
                    status = node.get('status')
                    services_count = node.get('services_count', 0)
                    tags = node.get('tags', [])
                    status_icon = '✓' if status == 'online' else '✗'
                    status_text = 'online' if status == 'online' else 'offline'
                    print(f"  {status_icon} {node_id} ({status_text})")
                    if services_count > 0:
                        print(f"    Services: {services_count}")
                    if tags:
                        tag_str = ', '.join(tags)
                        print(f"    Tags: {tag_str}")
                    print()
                print(f'Total: {len(nodes)} nodes')
                return 0
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return 1
async def run_list_services_query(node_id, all_nodes, worker_url):
    from tunnel_v4.config import get_worker_url
    if not worker_url:
        worker_url = get_worker_url()
    if all_nodes:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{worker_url}/api/v1/nodes',
                    params={'show_offline': 'true'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        print('✗ Failed to fetch nodes', file=sys.stderr)
                        return 1
                    result = await resp.json()
                    nodes = result.get('nodes', [])
                    if not nodes:
                        print('⚠️  No nodes available')
                        return 0
                    for node in nodes:
                        node_id = node.get('node_id')
                        print(f"\n{'='*60}")
                        print(f"Node: {node_id}")
                        print('='*60)
                        await run_list_services(node_id, worker_url)
                    return 0
        except Exception as e:
            print(f'✗ Error: {e}', file=sys.stderr)
            return 1
    elif node_id:
        return await run_list_services(node_id, worker_url)
    else:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{worker_url}/api/v1/nodes',
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        print('✗ Failed to fetch nodes', file=sys.stderr)
                        return 1
                    data = await resp.json()
                    nodes = data.get('nodes', [])
                    if not nodes:
                        print('⚠️  No online nodes available')
                        return 0
                    first_node = nodes[0]['node_id']
                    print(f"Using first online node: {first_node}")
                    return await run_list_services(first_node, worker_url)
        except Exception as e:
            print(f'✗ Error: {e}', file=sys.stderr)
            return 1
async def run_remove_local_service(services):
    print('⚠️  Local service removal requires Agent restart')
    print()
    print('To remove services:')
    print('  1. Stop current Agent (Ctrl+C)')
    print(f'  2. Restart Agent without: {", ".join(services)}')
    print()
    print('Services to remove:', ', '.join(services))
    return 1
async def run_list_local_services():
    print('⚠️  Local service listing requires Agent control interface')
    print()
    print('To view local services:')
    print('  - Check Agent startup output')
    print('  - Or use: tunnel list services --node <your-node-id>')
    print()
    return 1