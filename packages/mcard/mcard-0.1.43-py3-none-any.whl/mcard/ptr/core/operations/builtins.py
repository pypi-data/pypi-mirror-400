"""
Core builtin operations for PythonRuntime.
"""

import json
from typing import Any, Dict

from mcard import MCard


def op_identity(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """Identity operation - returns target content unchanged."""
    return target.get_content()


def op_transform(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """Transform operation - applies a named transformation."""
    transforms = {
        'upper_case': lambda t: t.get_content().decode('utf-8').upper().encode('utf-8'),
        'count_bytes': lambda t: len(t.get_content()),
    }
    func = impl.get('transform_function')
    return transforms.get(func, lambda t: t.get_content())(target)


def op_arithmetic(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """Arithmetic operation on numeric target content."""
    params = {**impl.get('params', {}), **ctx}
    op, operand = params.get('op'), params.get('operand')
    
    try:
        val = float(target.get_content().decode('utf-8'))
    except ValueError:
        return "Error: Target content is not a valid number"
    
    ops = {
        'add': lambda x, y: x + y,
        'sub': lambda x, y: x - y,
        'mul': lambda x, y: x * y,
        'div': lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    return ops.get(op, lambda x, y: f"Error: Unknown operation '{op}'")(val, operand)


def op_string(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """String operation on target content."""
    params = {**impl.get('params', {}), **ctx}
    func = params.get('func')
    s = target.get_content().decode('utf-8')
    
    ops = {
        'reverse': lambda: s[::-1],
        'len': lambda: len(s),
        'split': lambda: s.split(params.get('delimiter', ' '))
    }
    return ops.get(func, lambda: f"Error: Unknown function '{func}'")()


def op_fetch_url(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """Fetch content from a URL."""
    import urllib.request
    url = target.get_content().decode('utf-8').strip()
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.read().decode('utf-8')[:1000]
    except Exception as e:
        return f"Error fetching URL: {e}"


def op_session_record(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """P2P Session Recording operation."""
    config = impl.get('config', {})
    ctx_params = ctx.get('params', {})
    
    # Extract session_id from various sources
    session_id = ctx.get('sessionId') or ctx_params.get('sessionId')
    
    # Check config with potential interpolation
    if not session_id and 'sessionId' in config:
        val = config['sessionId']
        if isinstance(val, str) and val.startswith('${') and val.endswith('}'):
            key = val[9:-1]  # strip '${params.' and '}'
            if '.' in key:
                key = key.split('.')[-1]
            session_id = ctx.get(key) or ctx_params.get(key)
        else:
            session_id = val

    # Fallback to target content inspection
    if not session_id:
        try:
            content = target.get_content().decode('utf-8')
            data = json.loads(content)
            if isinstance(data, dict):
                session_id = data.get('sessionId')
        except:
            pass
    
    if not session_id:
        return {'success': False, 'error': 'session_id is required'}
        
    return {'success': True, 'session_id': session_id, 'recorded': True}


def op_static_server(impl: Dict, target: MCard, ctx: Dict) -> Any:
    """
    Execute static_server builtin - manages HTTP static file server.
    
    Actions: deploy, status, stop
    Config: root_dir, port, host
    """
    import os
    import signal
    import socket
    import subprocess
    import time
    
    config = impl.get('config', {})
    action = ctx.get('action') or config.get('action', 'status')
    port = int(ctx.get('port') or config.get('port', 8080))
    host = ctx.get('host') or config.get('host', 'localhost')
    root_dir = ctx.get('root_dir') or config.get('root_dir', '.')
    
    # Resolve root_dir relative to project root
    project_root = os.getcwd()
    if not os.path.isabs(root_dir):
        root_dir = os.path.normpath(os.path.join(project_root, root_dir))
    
    pid_file = os.path.join(project_root, f'.static_server_{port}.pid')
    
    def is_port_in_use(p: int) -> bool:
        # Use lsof to check if port is in use (handles both IPv4 and IPv6)
        try:
            result = subprocess.run(['lsof', '-ti', f':{p}'], capture_output=True, text=True)
            return result.returncode == 0 and result.stdout.strip() != ''
        except Exception:
            # Fallback to socket check
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', p)) == 0
    
    def get_pid_on_port(p: int):
        try:
            result = subprocess.run(
                ['lsof', '-ti', f':{p}'],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        return None
    
    if action == 'deploy':
        # Check if already running
        if is_port_in_use(port):
            pid = get_pid_on_port(port)
            return {
                "success": True,
                "message": "Server already running",
                "pid": pid,
                "port": port,
                "url": f"http://{host}:{port}",
                "status": "already_running"
            }
        
        # Verify root_dir exists
        if not os.path.isdir(root_dir):
            return {"success": False, "error": f"Directory not found: {root_dir}"}
        
        # Start Python HTTP server as background process
        try:
            process = subprocess.Popen(
                ['python3', '-m', 'http.server', str(port), '--bind', host, '--directory', root_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Save PID
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for server to start
            time.sleep(1.0)
            
            if is_port_in_use(port):
                return {
                    "success": True,
                    "message": "Server deployed successfully",
                    "pid": process.pid,
                    "port": port,
                    "url": f"http://{host}:{port}",
                    "root_dir": root_dir,
                    "status": "running"
                }
            else:
                return {"success": False, "error": "Server started but not responding"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to start server: {e}"}
    
    elif action == 'status':
        is_running = is_port_in_use(port)
        pid = get_pid_on_port(port)
        
        saved_pid = None
        if os.path.isfile(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    saved_pid = int(f.read().strip())
            except Exception:
                pass
        
        return {
            "success": True,
            "running": is_running,
            "pid": pid,
            "saved_pid": saved_pid,
            "port": port,
            "url": f"http://{host}:{port}" if is_running else None,
            "status": "running" if is_running else "stopped"
        }
    
    elif action == 'stop':
        pid = get_pid_on_port(port)
        
        if not pid:
            if os.path.isfile(pid_file):
                os.remove(pid_file)
            return {
                "success": True,
                "message": "No server running on this port",
                "port": port,
                "status": "stopped"
            }
        
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            
            if is_port_in_use(port):
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
            
            if os.path.isfile(pid_file):
                os.remove(pid_file)
            
            return {
                "success": True,
                "message": "Server stopped",
                "pid": pid,
                "port": port,
                "status": "stopped"
            }
        except ProcessLookupError:
            if os.path.isfile(pid_file):
                os.remove(pid_file)
            return {
                "success": True,
                "message": "Server was not running",
                "port": port,
                "status": "stopped"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to stop server: {e}"}
    
    else:
        return {"success": False, "error": f"Unknown action: {action}"}
