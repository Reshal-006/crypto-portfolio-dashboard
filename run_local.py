import os
import signal
import socket
import subprocess
import sys
import time
from typing import Optional, Tuple


def _is_port_available(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) != 0
    except OSError:
        return True


def _pick_port(host: str, preferred: int, fallback_range: range) -> int:
    if _is_port_available(host, preferred):
        return preferred
    for port in fallback_range:
        if _is_port_available(host, port):
            return port
    return preferred


def _start_process(args: list[str], env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        args,
        env=env,
        cwd=str(os.getcwd()),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def _pick_python_executable() -> str:
    """Prefer the workspace .venv interpreter to avoid mixed Python installs on Windows."""
    cwd = os.getcwd()
    candidates = [
        os.path.join(cwd, ".venv", "Scripts", "python.exe"),
        os.path.join(cwd, "venv", "Scripts", "python.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return sys.executable


def main() -> int:
    host = "127.0.0.1"

    backend_script = os.path.abspath(os.path.join(os.getcwd(), "backend", "app.py"))
    frontend_script = os.path.abspath(os.path.join(os.getcwd(), "frontend", "app.py"))
    if not os.path.exists(backend_script):
        print(f"ERROR: backend script not found: {backend_script}")
        return 2
    if not os.path.exists(frontend_script):
        print(f"ERROR: frontend script not found: {frontend_script}")
        return 2

    try:
        with open(frontend_script, "r", encoding="utf-8") as f:
            frontend_text = f.read()
        has_manage = "Manage Holdings" in frontend_text and "holdings-table" in frontend_text
    except Exception:
        has_manage = False

    backend_port = _pick_port(host, 8000, range(8001, 8011))
    frontend_port = _pick_port(host, 8051, range(8052, 8061))

    api_url = f"http://{host}:{backend_port}/api"

    base_env = os.environ.copy()

    backend_env = base_env.copy()
    backend_env["BACKEND_HOST"] = host
    backend_env["BACKEND_PORT"] = str(backend_port)

    frontend_env = base_env.copy()
    frontend_env["API_URL"] = api_url
    frontend_env["DASH_PORT"] = str(frontend_port)

    py = _pick_python_executable()

    print(f"Using Python: {py}")
    print(f"Backend script:  {backend_script}")
    print(f"Frontend script: {frontend_script}")
    print(f"Frontend has Manage Holdings UI: {has_manage}")
    print(f"Backend:  http://{host}:{backend_port}/api/health")
    print(f"Frontend: http://{host}:{frontend_port}/")
    print("Press Ctrl+C to stop both.")

    backend = None
    frontend = None

    try:
        backend = _start_process([py, backend_script], backend_env)
        time.sleep(0.8)
        frontend = _start_process([py, frontend_script], frontend_env)

        while True:
            if backend.poll() is not None:
                print("Backend exited.")
                return int(backend.returncode or 1)
            if frontend.poll() is not None:
                print("Frontend exited.")
                return int(frontend.returncode or 1)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for proc in (frontend, backend):
            if proc is None:
                continue
            try:
                if os.name == "nt":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                    time.sleep(0.2)
                proc.terminate()
            except Exception:
                pass

        # Give them a moment then force kill
        time.sleep(0.5)
        for proc in (frontend, backend):
            if proc is None:
                continue
            try:
                if proc.poll() is None:
                    proc.kill()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
