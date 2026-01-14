import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def _log(msg: str, err: bool = False):
    """Print weaverun status message."""
    stream = sys.stderr if err else sys.stdout
    print(f"\033[36mweaverun:\033[0m {msg}", file=stream)


def _load_dotenv() -> list[str]:
    """Load .env file from current directory if it exists. Returns list of base URL env keys found in .env."""
    env_path = Path.cwd() / ".env"
    found_keys = []
    if env_path.exists():
        load_dotenv(env_path)
        _log(f"Loaded {env_path}")
        # Check if .env has any base URL keys which may conflict
        try:
            with open(env_path) as f:
                content = f.read()
                # Check for common base URL env keys
                for key in ["OPENAI_BASE_URL", "OPENAI_API_BASE", "LLM_BASE_URL", "API_BASE_URL"]:
                    if key in content:
                        found_keys.append(key)
        except Exception:
            pass
    return found_keys


def _find_free_port(host: str = "127.0.0.1", start: int = 7777, attempts: int = 100) -> int:
    """Find available port starting from `start`."""
    for offset in range(attempts):
        port = start + offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free port found (tried {start}-{start + attempts})")


def _wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Block until port accepts connections."""
    # For 0.0.0.0, connect to localhost to check
    connect_host = "127.0.0.1" if host == "0.0.0.0" else host
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((connect_host, port))
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.05)
    return False


def _start_proxy(host: str, port: int):
    """Run uvicorn server."""
    config = uvicorn.Config(
        "weaverun.proxy:app",
        host=host,
        port=port,
        log_level="error",
    )
    uvicorn.Server(config).run()


def _run_proxy_with_command(
    cmd: list[str],
    host: str = "127.0.0.1",
    proxy_all: bool = False,
    debug: bool = False,
):
    """Core logic to start proxy and run command."""
    from .config import get_config
    
    env_found_keys = _load_dotenv()
    if env_found_keys:
        _log(f"⚠️  Warning: .env contains {', '.join(env_found_keys)} which may override proxy settings")
        _log("   For Next.js/Node apps, consider removing these from .env temporarily")

    # Enable debug mode in the config before starting the proxy
    if debug:
        from .config import set_debug_mode
        set_debug_mode(True)
        _log("Debug mode: observing traffic without Weave logging")

    try:
        proxy_port = _find_free_port(host=host)
    except RuntimeError as e:
        _log(f"Error: {e}", err=True)
        sys.exit(1)

    _log(f"Starting proxy on {host}:{proxy_port}...")
    
    proxy_thread = threading.Thread(target=_start_proxy, args=(host, proxy_port), daemon=True)
    proxy_thread.start()

    if not _wait_for_port(host, proxy_port, timeout=10.0):
        _log("Error: Proxy failed to start", err=True)
        sys.exit(1)

    _log("Proxy ready")
    _log(f"Dashboard: http://{host}:{proxy_port}/__weaverun__")

    env = os.environ.copy()
    
    # Get configured base URL env keys from config
    config = get_config()
    base_url_keys = config.base_url_env_keys
    
    # Preserve original base URLs for forwarding
    for key in base_url_keys:
        original_value = env.get(key)
        if original_value:
            env[f"WEAVE_ORIGINAL_{key}"] = original_value

    # Route SDK traffic through proxy (use localhost for local connections)
    proxy_url_host = "127.0.0.1" if host == "0.0.0.0" else host
    proxy_url = f"http://{proxy_url_host}:{proxy_port}"
    
    # Set all configured base URL env keys to point to proxy
    for key in base_url_keys:
        env[key] = proxy_url
    
    if len(base_url_keys) > 1:
        _log(f"Routing via: {', '.join(base_url_keys)}")
    
    env["WEAVE_RUN_ID"] = str(uuid.uuid4())
    env["WEAVE_APP_NAME"] = cmd[0]
    
    # Debug mode - pass to child process as well
    if debug:
        env["WEAVERUN_DEBUG"] = "1"

    # For apps that hardcode base_url, use HTTP_PROXY to intercept
    if proxy_all:
        _log("Proxy mode: ALL HTTP traffic (--proxy-all)")
        env["HTTP_PROXY"] = f"http://{proxy_url_host}:{proxy_port}"
        env["HTTPS_PROXY"] = f"http://{proxy_url_host}:{proxy_port}"
        # Only exclude the proxy itself from proxying
        env["NO_PROXY"] = f"{proxy_url_host}:{proxy_port}"

    _log(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, env=env)
        exit_code = result.returncode
    except KeyboardInterrupt:
        exit_code = 130
    except Exception as e:
        _log(f"Error: {e}", err=True)
        exit_code = 1

    _log(f"Done (exit code: {exit_code})")
    sys.exit(exit_code)


def _run_setup(args: list[str]):
    """Handle the setup subcommand."""
    force = False
    for arg in args:
        if arg in ("-f", "--force"):
            force = True
        elif arg == "--help":
            print("""
Run the interactive setup wizard to configure Weave credentials.

Usage: weaverun setup [OPTIONS]

Options:
  -f, --force    Reconfigure even if all variables are already set
  --help         Show this message and exit
""".strip())
            sys.exit(0)
    
    from .setup import run_setup_wizard
    success = run_setup_wizard(force=force)
    sys.exit(0 if success else 1)


def _print_help():
    """Print help message."""
    help_text = """
\033[1mweaverun\033[0m - Wrap a command and log OpenAI-compatible API calls to Weave.

\033[1mUsage:\033[0m
  weaverun [OPTIONS] <command> [args...]
  weaverun setup [--force]

\033[1mOptions:\033[0m
  -h, --host TEXT     Host IP to bind the proxy server (e.g., 0.0.0.0 for all interfaces)
                      [default: 127.0.0.1]
  -p, --proxy-all     Route ALL HTTP traffic through proxy (for apps with hardcoded base_url)
  -d, --debug         Debug mode: observe all traffic without logging to Weave
  --help              Show this message and exit

\033[1mCommands:\033[0m
  setup               Run the interactive setup wizard to configure Weave credentials

\033[1mExamples:\033[0m
  weaverun python app.py
  weaverun -h 0.0.0.0 npm start
  weaverun --debug python test.py
  weaverun setup
"""
    print(help_text.strip())


def main():
    """Main entry point with custom argument parsing."""
    args = sys.argv[1:]
    
    # Handle no arguments
    if not args:
        _print_help()
        sys.exit(0)
    
    # Check if first non-option arg is a known subcommand
    # Find first non-option argument
    first_positional = None
    for arg in args:
        if not arg.startswith("-"):
            first_positional = arg
            break
    
    # Handle setup subcommand
    if first_positional == "setup":
        # Pass remaining args after 'setup'
        setup_args = args[args.index("setup") + 1:]
        _run_setup(setup_args)
        return
    
    # Handle --help
    if "--help" in args and not any(not a.startswith("-") for a in args):
        _print_help()
        sys.exit(0)
    
    # Parse our own options for the default run behavior
    host = "127.0.0.1"
    proxy_all = False
    debug = False
    cmd: list[str] = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ("-h", "--host"):
            if i + 1 >= len(args):
                print("Error: --host requires a value", file=sys.stderr)
                sys.exit(1)
            host = args[i + 1]
            i += 2
            continue
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]
            i += 1
            continue
        elif arg in ("-p", "--proxy-all"):
            proxy_all = True
            i += 1
            continue
        elif arg in ("-d", "--debug"):
            debug = True
            i += 1
            continue
        elif arg == "--help":
            _print_help()
            sys.exit(0)
        elif arg.startswith("-"):
            # Unknown option - might be part of the command
            cmd = args[i:]
            break
        else:
            # First positional arg starts the command
            cmd = args[i:]
            break
    
    if not cmd:
        _print_help()
        sys.exit(0)
    
    _run_proxy_with_command(cmd, host=host, proxy_all=proxy_all, debug=debug)


if __name__ == "__main__":
    main()
