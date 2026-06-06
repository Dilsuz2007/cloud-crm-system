import os
import socket
import subprocess
import sys
import time


def check_port_free(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def run_project():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["PYTHONPATH"] = root_dir

    requirements = os.path.join(root_dir, "backend", "requirements.txt")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements])
    subprocess.check_call([sys.executable, "-m", "backend.app.init_db"])

    backend_port = 8000
    frontend_port = 3003
    if not check_port_free("127.0.0.1", backend_port):
        raise SystemExit(f"Port {backend_port} band.")
    if not check_port_free("127.0.0.1", frontend_port):
        raise SystemExit(f"Port {frontend_port} band.")

    backend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(backend_port),
        ],
        cwd=root_dir,
    )
    frontend = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=os.path.join(root_dir, "frontend"),
    )

    print(f"Frontend: http://127.0.0.1:{frontend_port}/")
    print(f"Backend docs: http://127.0.0.1:{backend_port}/docs")

    try:
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()


if __name__ == "__main__":
    run_project()
