#!/usr/bin/env python3
"""
Sphinx CLI

Command-line interface for AI-powered Jupyter notebook interactions.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

import backoff
import questionary
import yaml
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)


SUPPORTED_SCHEMA_TYPES = ["string", "integer", "number", "float", "boolean"]


def _output_structured_error(error_message: str, error_code: str) -> None:
    """
    Output a structured JSON error to stdout for programmatic consumers.

    This matches the format used by the Node.js CLI for consistency.

    Args:
        error_message: Human-readable error message
        error_code: Machine-readable error code (e.g., 'invalid_schema', 'file_not_found')
    """
    error_output = {
        "_meta": {
            "success": False,
            "warnings": [error_message],
            "sphinxStatus": "error",
            "errorCode": error_code,
        }
    }
    print(json.dumps(error_output, indent=2))


def _parse_schema_content(content: str, file_ext: str) -> str:
    """
    Parse schema file content and return as JSON string.

    Args:
        content: Raw file content
        file_ext: File extension (lowercase, with leading dot)

    Returns:
        JSON string representation of the schema
    """
    if file_ext == ".json":
        parsed = json.loads(content)
        return json.dumps(parsed)

    if file_ext in (".yaml", ".yml"):
        parsed = yaml.safe_load(content)
        return json.dumps(parsed)

    # For .txt or unknown extensions, try JSON first, then YAML
    try:
        parsed = json.loads(content)
        return json.dumps(parsed)
    except json.JSONDecodeError:
        parsed = yaml.safe_load(content)
        return json.dumps(parsed)


def _validate_schema_structure(schema_json: str) -> None:
    """
    Validate that the schema structure is compatible with our schema parser.

    Args:
        schema_json: JSON string of the schema

    Raises:
        ValueError: If the schema structure is invalid
    """
    parsed = json.loads(schema_json)

    if not isinstance(parsed, dict):
        raise ValueError('Schema must be a JSON object, e.g., {"field": "string"}')

    if "_meta" in parsed:
        raise ValueError('"_meta" is a reserved field name')

    def validate_value(val: Any, path: str) -> None:
        if isinstance(val, str):
            if val.lower() not in SUPPORTED_SCHEMA_TYPES:
                raise ValueError(
                    f'Unsupported type "{val}" at "{path}". Supported types: {", ".join(SUPPORTED_SCHEMA_TYPES)}'
                )
            return

        if isinstance(val, list):
            if len(val) == 0:
                raise ValueError(f'Array at "{path}" must specify item type, e.g., ["string"]')
            validate_value(val[0], f"{path}[0]")
            return

        if isinstance(val, dict):
            # Check for explicit array type: {"type": "array", "items": ...}
            if isinstance(val.get("type"), str) and val["type"].lower() == "array" and "items" in val:
                validate_value(val["items"], f"{path}.items")
                return

            # Check for type definition: {"type": "string", "description": "..."}
            if "type" in val and isinstance(val.get("type"), str):
                allowed_keys = {"type", "description"}
                if set(val.keys()).issubset(allowed_keys):
                    if val["type"].lower() not in SUPPORTED_SCHEMA_TYPES:
                        raise ValueError(
                            f'Unsupported type "{val["type"]}" at "{path}". '
                            f"Supported types: {', '.join(SUPPORTED_SCHEMA_TYPES)}"
                        )
                    return

            # Nested object
            for key, nested_val in val.items():
                validate_value(nested_val, f"{path}.{key}" if path else key)
            return

        val_type = "null" if val is None else type(val).__name__
        raise ValueError(
            f'Invalid value at "{path}": {json.dumps(val)}. '
            f'Expected a type string (e.g., "string", "integer"), array, or object. Got {val_type}.'
        )

    for key, val in parsed.items():
        validate_value(val, key)


def resolve_output_schema(value: Optional[str]) -> Optional[str]:
    """
    Resolve output schema value - read from file if it's a path, otherwise return as-is.

    Supports auto-detection:
    - .json files: parsed as JSON
    - .yaml/.yml files: parsed as YAML, converted to JSON
    - .txt files or no extension: tries JSON first, then YAML
    - Otherwise: treated as inline JSON string

    Args:
        value: Either a JSON schema string or a path to a schema file

    Returns:
        The schema content as a JSON string, or None if value is None

    Raises:
        FileNotFoundError: If a recognized file path doesn't exist
        ValueError: If the schema format is invalid or uses unsupported types
    """
    if not value:
        return value

    path = Path(value)
    file_ext = path.suffix.lower()

    # Check if it looks like a file path based on extension
    if file_ext in (".json", ".yaml", ".yml", ".txt"):
        if path.exists():
            logger.info(f"Reading output schema from file: {path}")
            content = path.read_text()
            try:
                schema_json = _parse_schema_content(content, file_ext)
                _validate_schema_structure(schema_json)
                return schema_json
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in schema file {path}: {e}")
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in schema file {path}: {e}")
        raise FileNotFoundError(f"Output schema file not found: {path}")

    # Check if it's a path without recognized extension that exists
    if path.exists() and path.is_file():
        stripped = value.strip()
        if not stripped.startswith("{") and not stripped.startswith("["):
            logger.info(f"Reading output schema from file: {path}")
            content = path.read_text()
            try:
                schema_json = _parse_schema_content(content, file_ext)
                _validate_schema_structure(schema_json)
                return schema_json
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in schema file {path}: {e}")
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in schema file {path}: {e}")

    # Treat as inline JSON - validate structure
    try:
        _validate_schema_structure(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in output schema: {e}")

    return value


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages."""

    COLORS = {
        "DEBUG": "\033[32m",
        "INFO": "\033[36m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[31m",
    }
    RESET = "\033[0m"

    def format(self, record):
        formatted = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{formatted}{self.RESET}"


def setup_logging(verbose: bool = False, log_level: Optional[str] = None) -> None:
    """Set up logging configuration.

    Args:
        verbose: Show detailed info messages
        log_level: Log level to use when verbose is enabled (debug, info, warn, error, fatal).
                   Only takes effect if verbose is True. Defaults to info when verbose is True.
    """
    logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if verbose:
        # Verbose mode: use log_level if specified, otherwise default to info
        if log_level is not None:
            # Map headless log levels to Python logging levels
            level_map = {
                "fatal": logging.CRITICAL,
                "error": logging.ERROR,
                "warn": logging.WARNING,
                "info": logging.INFO,
                "debug": logging.DEBUG,
            }
            level = level_map.get(log_level.lower(), logging.INFO)
            logger.setLevel(level)
        else:
            logger.setLevel(logging.INFO)
    else:
        # Non-verbose mode: always ERROR
        logger.setLevel(logging.ERROR)

    logger.propagate = False


def setup_nodeenv() -> tuple[Path, Path, Path]:
    """
    Set up a persistent nodeenv environment and find the CLI file.

    Returns:
        tuple: (nodeenv_dir, node_exe, cjs_file) where:
               - nodeenv_dir is the persistent directory
               - node_exe is the path to the node executable
               - cjs_file is the path to the sphinx-cli.cjs file
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Look for the sphinx-cli.cjs file
    cjs_file = script_dir / "sphinx-cli.cjs"
    if not cjs_file.exists():
        raise FileNotFoundError("sphinx-cli.cjs not found")

    # Create a persistent directory for nodeenv
    nodeenv_dir = Path.home() / ".sphinx" / ".env.cli"
    nodeenv_dir.mkdir(parents=True, exist_ok=True)

    # Create nodeenv environment
    nodeenv_path = nodeenv_dir / "nodeenv"
    if not nodeenv_path.exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "nodeenv", str(nodeenv_path), "--node", "24.9.0"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error creating nodeenv: {e}")

    # Get the node executable path
    if os.name == "nt":  # Windows
        node_exe = nodeenv_path / "Scripts" / "node.exe"
    else:  # Unix-like
        node_exe = nodeenv_path / "bin" / "node"

    return nodeenv_dir, node_exe, cjs_file


def check_jupyter_dependencies() -> None:
    """Check if required Jupyter dependencies are installed."""
    missing_deps = []

    try:
        import jupyter_server  # noqa: F401
    except ImportError:
        missing_deps.append("jupyter-server")

    try:
        import ipykernel  # noqa: F401
    except ImportError:
        missing_deps.append("ipykernel")

    if missing_deps:
        deps_str = " ".join(missing_deps)
        raise ImportError(
            f"Missing required dependencies: {deps_str}\nPlease install them with: pip install {deps_str}\n"
        )


def run_sphinx_chat(
    notebook_filepath: Optional[str],
    prompt: str,
    *,
    sphinx_url: str = "https://api.prod.sphinx.ai",
    jupyter_server_url: Optional[str] = None,
    jupyter_server_token: Optional[str] = None,
    jupyter_server_port: int = 8888,
    verbose: bool = False,
    log_level: Optional[str] = None,
    no_memory_read: bool = False,
    no_memory_write: bool = False,
    no_package_installation: bool = False,
    no_collapse_exploratory_cells: bool = False,
    no_file_search: bool = False,
    no_ripgrep_installation: bool = False,
    no_web_search: bool = False,
    sphinx_rules_path: Optional[str] = None,
    output_schema: Optional[str] = None,
    on_thinking: Optional[callable] = None,
    on_output: Optional[callable] = None,
) -> int:
    """
    Run a Sphinx chat session with an embedded Jupyter server.

    Args:
        sphinx_url: The URL of the Sphinx service
        notebook_filepath: Path to the notebook file. If None, the CLI will auto-generate
            a notebook filename based on the prompt.
        prompt: Prompt to create a thread
        jupyter_server_url: URL of existing Jupyter server (if None, will start new server)
        jupyter_server_token: Token for existing Jupyter server (if None, will generate new token)
        jupyter_server_port: Port for the Jupyter server (only used if starting new server)
        verbose: Whether to show info-level messages
        log_level: Log level when verbose is enabled (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        no_memory_read: Disable memory read
        no_memory_write: Disable memory write
        no_package_installation: Disable package installation
        no_collapse_exploratory_cells: Disable collapsing exploratory cells
        no_file_search: Disable file search tools (grep, ls, read)
        no_ripgrep_installation: Disable automatic ripgrep binary installation
        no_web_search: Disable web search tools
        sphinx_rules_path: Path to Sphinx rules file
        output_schema: JSON schema for structured output. Can be either:
            - Inline JSON: '{"amount": "integer"}'
            - Path to a schema file (.json, .yaml, .yml, .txt)
            Supported types: string, integer, number, float, boolean.
            YAML files are automatically converted to JSON.

    Returns:
        Exit code from the headless CLI (0 for success)
    """
    setup_logging(verbose=verbose, log_level=log_level)

    if jupyter_server_url is None:
        logger.info("Checking dependencies...")
        try:
            check_jupyter_dependencies()
            logger.info("Dependencies available")
        except ImportError as e:
            logger.error(f"{e}")
            return 1

    jupyter_process = None
    temp_dir = None
    jupyter_token = None
    server_url = None

    try:
        if jupyter_server_url is not None:
            if not jupyter_server_url.startswith(("http://", "https://")):
                if ":" in jupyter_server_url:
                    server_url = f"http://{jupyter_server_url}"
                else:
                    server_url = f"http://{jupyter_server_url}:8888"
            else:
                server_url = jupyter_server_url

            jupyter_token = jupyter_server_token

            logger.info(f"Using existing server: {server_url}")
            if jupyter_token:
                logger.info(f"Using token: {jupyter_token[:8]}...")

            logger.info("Testing server connection...")

            def _probe(url: str) -> str:
                try:
                    with urllib.request.urlopen(url, timeout=10) as resp:
                        return f"OK {resp.status}"
                except urllib.error.HTTPError as e:
                    return f"HTTP {e.code}"
                except Exception as e:
                    return f"ERR {type(e).__name__}: {e}"

            test_url = f"{server_url}/api/status"
            if jupyter_token:
                test_url = f"{server_url}/api/status?token={jupyter_token}"

            logger.info(f"Testing: {test_url}")

            status_try = _probe(test_url)
            logger.info(f"Response: {status_try}")

            if not status_try.startswith("OK 200"):
                raise RuntimeError(
                    f"Server is not accessible: {status_try}\n"
                    f"Please check:\n"
                    f"1. Server is running at {server_url}\n"
                    f"2. Token is correct (if provided)\n"
                    f"3. Server allows connections from this host"
                )

            logger.info("Server is ready")
        else:
            logger.info("Starting server...")
            logger.info(f"Using Python: {sys.executable}")

            temp_dir = tempfile.mkdtemp(prefix="sphinx_jupyter_")

            import secrets

            jupyter_token = secrets.token_hex(32)

            jupyter_log_level = "INFO"  # Need INFO level to capture port information

            # Set Jupyter root to filesystem root so it can access any notebook path
            # If no notebook path provided, use current working directory as reference
            if notebook_filepath:
                notebook_abs = Path(notebook_filepath).resolve()
                jupyter_root_dir = f"{notebook_abs.drive}\\" if os.name == "nt" else "/"
            else:
                cwd_abs = Path.cwd().resolve()
                jupyter_root_dir = f"{cwd_abs.drive}\\" if os.name == "nt" else "/"

            server_cmd = [
                sys.executable,
                "-m",
                "jupyter",
                "server",
                "--no-browser",
                f"--port={jupyter_server_port}",
                f"--IdentityProvider.token={jupyter_token}",
                f"--ServerApp.log_level={jupyter_log_level}",
                f"--ServerApp.root_dir={jupyter_root_dir}",
            ]

            # Capture stderr to read which port the server actually uses
            jupyter_process = subprocess.Popen(
                server_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=temp_dir,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
            )

            def _probe(url: str) -> str:
                try:
                    with urllib.request.urlopen(url, timeout=5) as resp:
                        return f"OK {resp.status}"
                except urllib.error.HTTPError as e:
                    return f"HTTP {e.code}"
                except Exception as e:
                    return f"ERR {type(e).__name__}: {e}"

            actual_port = None
            port_detected = threading.Event()

            def read_server_output():
                nonlocal actual_port
                try:
                    for line in jupyter_process.stderr:
                        # Look for any URL with a port, e.g.:
                        # "http://localhost:8889/", "http://0.0.0.0:8889/", "http://some-host:8889/"
                        if actual_port is None:
                            # Match any http/https URL followed by :PORT
                            port_match = re.search(r"https?://[^:]+:(\d+)", line)
                            if port_match:
                                actual_port = int(port_match.group(1))
                                port_detected.set()
                                logger.info(f"Detected server started on port {actual_port}")
                                break
                except Exception:
                    pass

            # Start background thread to monitor server output
            output_thread = threading.Thread(target=read_server_output, daemon=True)
            output_thread.start()

            # Wait for port detection with timeout
            if not port_detected.wait(timeout=10):
                # Fallback: assume the requested port if we couldn't detect it
                actual_port = jupyter_server_port
                logger.warning(f"Could not detect port from server output, assuming {jupyter_server_port}")

            if actual_port != jupyter_server_port:
                logger.info(f"Port {jupyter_server_port} was busy, server started on port {actual_port}")

            base = f"http://localhost:{actual_port}"
            server_url = base

            @backoff.on_exception(backoff.expo, Exception, max_time=15)
            def check_ready():
                if jupyter_process.poll() is not None:
                    error_msg = f"Server exited early with code {jupyter_process.returncode}"
                    raise RuntimeError(error_msg)
                status_try = _probe(f"{base}/api/status?token={jupyter_token}")
                if not status_try.startswith("OK 200"):
                    raise Exception(f"Server is not ready: {status_try}")

            check_ready()

            logger.info(f"Server ready at {server_url}")

        # Set up nodeenv environment and get CLI file
        nodeenv_dir, node_exe, cjs_file = setup_nodeenv()

        node_args = [
            "chat",
            "--jupyter-server-url",
            server_url,
            "--sphinx-url",
            sphinx_url,
            "--prompt",
            prompt,
        ]

        # Only add notebook filepath if provided (otherwise Node.js CLI will auto-generate)
        if notebook_filepath:
            # Use forward slashes for cross-platform compatibility
            notebook_abs_path = str(Path(notebook_filepath).resolve()).replace("\\", "/")
            node_args.extend(["--notebook-filepath", notebook_abs_path])

        # Only add token if we have one
        if jupyter_token:
            node_args.extend(["--jupyter-server-token", jupyter_token])

        # Pass jupyter root dir if we started the server (we know its root_dir)
        # This is needed because the Node.js CLI uses this to compute relative paths
        if jupyter_process is not None:
            # We started the server, so we know the root_dir
            node_args.extend(["--jupyter-root-dir", jupyter_root_dir])

        if no_memory_read:
            node_args.append("--no-memory-read")

        if no_memory_write:
            node_args.append("--no-memory-write")

        if no_package_installation:
            node_args.append("--no-package-installation")

        if no_collapse_exploratory_cells:
            node_args.append("--no-collapse-exploratory-cells")

        if no_file_search:
            node_args.append("--no-file-search")

        if no_ripgrep_installation:
            node_args.append("--no-ripgrep-installation")

        if no_web_search:
            node_args.append("--no-web-search")

        if sphinx_rules_path:
            node_args.append(f"--sphinx-rules-path={sphinx_rules_path}")

        if output_schema:
            try:
                resolved_schema = resolve_output_schema(output_schema)
                node_args.extend(["--output-schema", resolved_schema])
            except FileNotFoundError as e:
                error_message = str(e)
                logger.error(error_message)
                _output_structured_error(error_message, "file_not_found")
                return 1
            except ValueError as e:
                error_message = str(e)
                if "Unsupported type" in error_message:
                    error_code = "unsupported_type"
                elif "Invalid JSON" in error_message:
                    error_code = "invalid_json"
                else:
                    # Use invalid_schema for YAML errors and other schema issues
                    error_code = "invalid_schema"
                logger.error(error_message)
                _output_structured_error(error_message, error_code)
                return 1

        if verbose:
            node_args.append("--verbose")

        if log_level:
            node_args.extend(["--log-level", log_level])

        cmd = [str(node_exe), str(cjs_file)] + node_args

        # Set up environment variables
        env = os.environ.copy()
        if on_thinking:  # Only in interactive mode
            env["SPHINX_CLI_INTERACTIVE_MODE"] = "true"

        # Reading both stdout and stderr concurrently in an async fashion prevents potential deadlocks.
        async def stream_subprocess():
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env
            )
            output_lines: list[str] = []
            stderr_lines: list[str] = []
            show_stderr = not output_schema or verbose
            output_started = False

            async def read_stdout():
                nonlocal output_started
                async for line in proc.stdout:
                    decoded = line.decode(errors="replace").rstrip("\n\r")

                    # Handle thinking marker from Node.js CLI
                    if decoded == "[SPHINX_THINKING]":
                        if on_thinking:
                            on_thinking()
                        output_started = False  # Reset for next output
                        continue  # Don't print the marker

                    # Skip empty lines right after thinking (Node.js adds \n before output)
                    if not output_started and not decoded:
                        continue

                    # This is actual output (not a marker) - notify once that output is coming
                    if not output_started:
                        if on_output:
                            on_output()
                        output_started = True

                    print(decoded)
                    output_lines.append(decoded)

            async def read_stderr():
                async for line in proc.stderr:
                    decoded = line.decode(errors="replace").rstrip("\n\r")
                    stderr_lines.append(decoded)
                    if show_stderr:
                        print(decoded, file=sys.stderr)

            await asyncio.gather(read_stdout(), read_stderr())
            return await proc.wait(), output_lines, stderr_lines

        return_code, output_lines, stderr_lines = asyncio.run(stream_subprocess())
        logger.info(f"return code: {return_code}")

        # If process failed and we have no output, provide helpful error info
        if return_code != 0 and not output_lines:
            logger.error(f"Process failed with exit code {return_code}")
            logger.error("No output was captured. This might indicate:")
            logger.error("1. The sphinx-cli.cjs file is not executable")
            logger.error("2. Node.js is not properly installed in the nodeenv")
            logger.error("3. The CLI command failed silently")
            logger.info(f"Command that failed: {' '.join(cmd)}")
            logger.info(f"Working directory: {os.getcwd()}")
            if stderr_lines:
                logger.error(f"Stderr output: {chr(10).join(stderr_lines)}")

            # In structured output mode, provide JSON error when process fails with no output
            if output_schema:
                error_message = f"Process failed with exit code {return_code}"
                if stderr_lines:
                    error_message = f"{error_message}: {stderr_lines[-1]}"
                _output_structured_error(error_message, "unknown_error")

        return return_code

    except subprocess.CalledProcessError as e:
        logger.error(f"Headless CLI failed with exit code {e.returncode}")
        if output_schema:
            _output_structured_error(f"Headless CLI failed with exit code {e.returncode}", "unknown_error")
        return e.returncode
    except FileNotFoundError as e:
        error_message = str(e)
        logger.error(f"Error: {error_message}")
        if output_schema:
            _output_structured_error(error_message, "file_not_found")
        return 1
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error: {error_message}")
        if output_schema:
            _output_structured_error(error_message, "unknown_error")
        return 1
    finally:
        # Cleanup - only stop server if we started it
        if jupyter_process:
            logger.info("Stopping Jupyter server...")
            try:
                jupyter_process.terminate()
                jupyter_process.stdout.close()
                jupyter_process.stderr.close()
                jupyter_process.wait(timeout=10)
            except Exception as e:
                logger.warning(f"Warning: Error stopping Jupyter server: {e}")
                try:
                    jupyter_process.kill()
                except:  # noqa: E722
                    pass

        if temp_dir:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Warning: Error cleaning up temp directory: {e}")

        logger.info("Cleanup completed")


def run_login(verbose: bool = False, log_level: Optional[str] = None) -> int:
    """Run the login command."""
    try:
        # Set up logging
        setup_logging(verbose=verbose, log_level=log_level)

        # Set up nodeenv environment and get CLI file
        nodeenv_dir, node_exe, cjs_file = setup_nodeenv()

        # Run the login command
        cmd = [str(node_exe), str(cjs_file), "login"]

        # Run the command and stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
        )

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
        # Wait for process to complete and get return code
        process.stdout.close()
        return_code = process.wait()
        return return_code

    except Exception as e:
        logger.error(f"Login error: {e}")
        return 1


def run_logout(verbose: bool = False, log_level: Optional[str] = None) -> int:
    """Run the logout command."""
    try:
        # Set up logging
        setup_logging(verbose=verbose, log_level=log_level)

        # Set up nodeenv environment and get CLI file
        nodeenv_dir, node_exe, cjs_file = setup_nodeenv()

        # Run the logout command
        cmd = [str(node_exe), str(cjs_file), "logout"]

        # Run the command and stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
        )

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Wait for process to complete and get return code
        process.stdout.close()
        return_code = process.wait()
        return return_code

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return 1


def run_status(verbose: bool = False, log_level: Optional[str] = None) -> int:
    """Run the status command."""
    try:
        # Set up logging
        setup_logging(verbose=verbose, log_level=log_level)

        # Set up nodeenv environment and get CLI file
        nodeenv_dir, node_exe, cjs_file = setup_nodeenv()

        # Run the status command
        cmd = [str(node_exe), str(cjs_file), "status"]

        # Run the command and stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
        )

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Wait for process to complete and get return code
        process.stdout.close()
        return_code = process.wait()
        return return_code

    except Exception as e:
        logger.error(f"Status error: {e}")
        return 1


# fmt: off
THINKING_VERBS = [ # Thinking/working verbs that cycle during processing
    # Core thinking verbs (24 total - 48 seconds of unique content)
    "Thinking", "Analyzing", "Processing", "Working", "Computing",
    "Calculating", "Evaluating", "Considering", "Examining",
    "Investigating", "Exploring", "Researching", "Studying",
    "Reviewing", "Assessing", "Contemplating", "Deliberating",
    "Reflecting", "Pondering", "Musing", "Reasoning", "Deducing",
    "Inferring", "Concluding",
    # Extended verbs for longer interactions (48 total - 96 seconds)
    "Brainstorming", "Conceptualizing", "Synthesizing", "Formulating",
    "Deconstructing", "Interpreting", "Extrapolating", "Generalizing",
    "Abstracting", "Categorizing", "Correlating", "Hypothesizing",
    "Speculating", "Theorizing", "Modeling", "Simulating", "Optimizing",
    "Refactoring", "Debugging", "Troubleshooting", "Diagnosing",
    "Resolving", "Integrating", "Consolidating", "Streamlining", "Refining",
] # fmt: on


def find_notebooks(directory: Optional[str] = None) -> list[Path]:
    """Find all .ipynb files in the given directory or current directory."""
    search_dir = Path(directory) if directory else Path.cwd()
    return list(search_dir.glob("**/*.ipynb"))


def create_spinner_text(verb: str, dot_count: int) -> str:
    """Create spinner text with verb and animated dots.

    Args:
        verb: The thinking verb to display
        dot_count: Number of dots (1-3)
    """
    dots = "." * dot_count
    # Use dim cyan color to differentiate from Sphinx output
    # ANSI codes: \x1b[36m = cyan, \x1b[2m = dim, \x1b[0m = reset
    return f"\x1b[2m\x1b[36m{verb}{dots}\x1b[0m"


def run_interactive_chat(
    notebook_filepath: Optional[str] = None,
    *,
    sphinx_url: str = "https://api.prod.sphinx.ai",
    jupyter_server_url: Optional[str] = None,
    jupyter_server_token: Optional[str] = None,
    jupyter_server_port: int = 8888,
    verbose: bool = False,
    log_level: Optional[str] = None,
    no_memory_read: bool = False,
    no_memory_write: bool = False,
    no_package_installation: bool = False,
    no_collapse_exploratory_cells: bool = False,
    no_file_search: bool = False,
    no_ripgrep_installation: bool = False,
    no_web_search: bool = False,
    sphinx_rules_path: Optional[str] = None,
) -> int:
    """
    Run an interactive Sphinx chat session with a beautiful terminal UI.
    """
    console = Console()

    try:
        # Welcome message
        console.print(
            Panel.fit(
                "[bold blue]Welcome to the Sphinx CLI![/bold blue]\n\n"
                "This mode allows you to:\n"
                "• Select notebooks from your current directory\n"
                "• Chat with Sphinx in a conversational interface\n"
                "• See real-time processing status\n\n"
                "[dim]Press Ctrl+C at any time to exit[/dim]",
                border_style="blue",
            )
        )

        # Notebook selection
        if not notebook_filepath:
            console.print("\n[bold]Scanning for notebooks...[/bold]")
            notebooks = find_notebooks()

            if not notebooks:
                # No notebooks found - offer to create one
                console.print("[yellow]No .ipynb files found in current directory or subdirectories.[/yellow]")

                create_new = questionary.confirm("Would you like to create a new notebook?", default=True).ask()

                if not create_new:
                    console.print("[yellow]Session cancelled.[/yellow]")
                    return 0

                # Prompt for notebook name
                notebook_name = questionary.text("Enter notebook name:").ask()

                if not notebook_name:
                    console.print("[yellow]Session cancelled.[/yellow]")
                    return 0

                # Ensure .ipynb extension
                if not notebook_name.endswith(".ipynb"):
                    notebook_name += ".ipynb"

                notebook_filepath = str(Path.cwd() / notebook_name)
                console.print(f"[green]Creating new notebook: {notebook_name}[/green]")

            else:
                # Convert to relative paths for display
                notebook_choices = []
                for nb in notebooks:
                    try:
                        rel_path = nb.relative_to(Path.cwd())
                        notebook_choices.append({"name": str(rel_path), "value": str(nb.resolve())})
                    except ValueError:
                        # Can't make relative, use absolute
                        notebook_choices.append({"name": str(nb), "value": str(nb.resolve())})

                selected_notebook = questionary.select(
                    "",  # Empty message to remove indentation
                    choices=[choice["name"] for choice in notebook_choices],
                    qmark="",  # No prompt text
                    pointer="›",  # Use simple pointer
                ).ask()

                if not selected_notebook:
                    console.print("[yellow]Selection cancelled.[/yellow]")
                    return 0

                # Find the corresponding full path
                notebook_filepath = next(
                    choice["value"] for choice in notebook_choices if choice["name"] == selected_notebook
                )

                # Clear the "Scanning for notebooks..." message
                import sys

                sys.stdout.write("\033[F")  # Move cursor up one line
                sys.stdout.write("\033[K")  # Clear line
                sys.stdout.flush()

                # Print the selected notebook
                console.print(f"[green]Selected notebook: {selected_notebook}[/green]")

        # Set up chat session
        console.print("\n[bold green]Session started![/bold green]")
        console.print("[dim]Type your questions or requests below. Type 'exit' to end the session.[/dim]\n")

        while True:
            try:
                # Get user input with simple > prompt (keep prompting until non-empty)
                import sys

                while True:
                    sys.stdout.write("> ")
                    sys.stdout.flush()
                    user_input_raw = input()  # Don't strip yet - need to count newlines
                    user_input = user_input_raw.strip()

                    if user_input:  # Only break if input is non-empty
                        break
                    # If empty, move cursor up to show > again
                    sys.stdout.write("\033[F")

                if user_input.lower() == "exit":
                    console.print("[yellow]Session ended. Goodbye![/yellow]")
                    break

                # Clear the input prompt line
                # After input() returns, cursor is on the next line
                # We just need to move up once and clear the "> [input]" line
                # Note: input() only captures single lines, but if user pastes
                # multiline text, we count those newlines

                # Calculate terminal lines used:
                # The input line(s) plus the prompt ">"
                terminal_width = shutil.get_terminal_size().columns
                prompt_len = 2  # "> "

                # Count how many terminal lines the input actually spans
                # accounting for line wrapping
                lines_used = 1  # Start with the prompt line
                current_line_len = prompt_len

                for char in user_input_raw:
                    if char == "\n":
                        lines_used += 1
                        current_line_len = 0
                    else:
                        current_line_len += 1
                        if current_line_len > terminal_width:
                            lines_used += 1
                            current_line_len = 1  # First character of new line

                # Clear all the lines
                for _ in range(lines_used):
                    sys.stdout.write("\033[F")  # Move cursor up one line
                    sys.stdout.write("\033[K")  # Clear line
                sys.stdout.flush()

                # Display the user's prompt with > prefix
                console.print(f"> [bold]{user_input}[/bold]")
                console.print()  # Add blank line after prompt

                # Show thinking indicator while processing
                import random
                import sys

                # Calculate max line length once
                max_verb_length = max(len(v) for v in THINKING_VERBS)
                max_line_length = max_verb_length + 3  # verb + "..."

                # Simple spinner state
                spinner_stop_event = threading.Event()
                current_spinner_thread = None

                def run_spinner(verb):
                    """Run spinner with given verb until stopped."""
                    dot_count = 1
                    last_update = time.time()

                    while not spinner_stop_event.is_set():
                        # Update dots every 0.5 seconds
                        if time.time() - last_update >= 0.5:
                            dot_count = (dot_count % 3) + 1
                            last_update = time.time()

                        # Write spinner
                        spinner_text = create_spinner_text(verb, dot_count)
                        sys.stdout.write("\r" + " " * max_line_length + "\r" + spinner_text)
                        sys.stdout.flush()

                        time.sleep(0.1)

                def start_spinner():
                    """Start spinner with random verb."""
                    nonlocal current_spinner_thread
                    stop_spinner()  # Stop any existing spinner
                    spinner_stop_event.clear()
                    verb = random.choice(THINKING_VERBS)
                    current_spinner_thread = threading.Thread(target=run_spinner, args=(verb,), daemon=True)
                    current_spinner_thread.start()

                def stop_spinner():
                    """Stop and clear spinner."""
                    nonlocal current_spinner_thread
                    if current_spinner_thread and current_spinner_thread.is_alive():
                        spinner_stop_event.set()
                        current_spinner_thread.join(timeout=0.5)
                        # Clear line
                        sys.stdout.write("\r" + " " * max_line_length + "\r")
                        sys.stdout.flush()
                        current_spinner_thread = None

                # Start spinner - will run until first output
                start_spinner()

                def handle_thinking():
                    """Restart spinner for follow-up thinking."""
                    start_spinner()

                def handle_output():
                    """Stop spinner when output arrives."""
                    stop_spinner()

                try:
                    # Run the chat command with callbacks
                    exit_code = run_sphinx_chat(
                        notebook_filepath=notebook_filepath,
                        prompt=user_input,
                        sphinx_url=sphinx_url,
                        jupyter_server_url=jupyter_server_url,
                        jupyter_server_token=jupyter_server_token,
                        jupyter_server_port=jupyter_server_port,
                        verbose=verbose,
                        log_level=log_level,
                        no_memory_read=no_memory_read,
                        no_memory_write=no_memory_write,
                        no_package_installation=no_package_installation,
                        no_collapse_exploratory_cells=no_collapse_exploratory_cells,
                        no_file_search=no_file_search,
                        no_ripgrep_installation=no_ripgrep_installation,
                        no_web_search=no_web_search,
                        sphinx_rules_path=sphinx_rules_path,
                        on_thinking=handle_thinking,  # Restart spinner on thinking markers
                        on_output=handle_output,  # Stop spinner when output arrives
                    )

                    if exit_code != 0:
                        console.print(f"\n[red]Command failed with exit code {exit_code}[/red]")

                finally:
                    # Ensure spinner is stopped
                    stop_spinner()
                    console.print()  # New line for next prompt

            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Session ended. Goodbye![/yellow]")
                break

        return 0

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def main():
    """The Sphinx CLI."""
    parser = argparse.ArgumentParser(
        description="Sphinx CLI - Start Jupyter server and invoke Sphinx from your command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat (default - requires authentication)
  sphinx-cli
  sphinx-cli --notebook-filepath ./notebook.ipynb

  # Authentication commands
  sphinx-cli login
  sphinx-cli logout
  sphinx-cli status

  # Chat commands (requires authentication)
  # Auto-generate notebook (creates a descriptively-named notebook based on prompt)
  sphinx-cli chat --prompt "Analyze sales data and create a forecast"

  # With explicit notebook path
  sphinx-cli chat --notebook-filepath ./notebook.ipynb --prompt "Create a model to predict y from x"
  sphinx-cli chat --notebook-filepath ./notebook.ipynb --prompt "Analyze this data" --jupyter-server-url http://localhost:8888 --jupyter-server-token your_token_here

  # Using existing Jupyter server (URL formats supported):
  # - localhost:8888 (will be converted to http://localhost:8888)
  # - http://localhost:8888
  # - https://your-server.com:8888
        """,
    )

    # Add arguments for default interactive mode
    parser.add_argument(
        "--notebook-filepath", help="Path to notebook file (optional - will prompt for selection if not provided)"
    )
    parser.add_argument("--sphinx-url", default="https://api.prod.sphinx.ai", help="Sphinx service URL")
    parser.add_argument("--jupyter-server-url", help="Existing Jupyter server URL (optional)")
    parser.add_argument("--jupyter-server-token", help="Jupyter server token (if using existing server)")
    parser.add_argument("--no-memory-read", action="store_true", help="Disable memory read (default: enabled)")
    parser.add_argument("--no-memory-write", action="store_true", help="Disable memory write (default: enabled)")
    parser.add_argument(
        "--no-package-installation", action="store_true", help="Disable package installation (default: enabled)"
    )
    parser.add_argument(
        "--no-collapse-exploratory-cells",
        action="store_true",
        help="Disable collapsing exploratory cells (default: enabled)",
    )
    parser.add_argument(
        "--no-file-search",
        action="store_true",
        help="Disable file search tools (grep, ls, read) (default: enabled)",
    )
    parser.add_argument(
        "--no-ripgrep-installation",
        action="store_true",
        help="Disable automatic ripgrep binary installation (default: enabled)",
    )
    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search tools (default: enabled)",
    )
    parser.add_argument("--sphinx-rules-path", help="Path to rules file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed messages")
    parser.add_argument(
        "-l",
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warn", "error", "fatal"],
        help="Log level when verbose is enabled (default: info)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    login_parser = subparsers.add_parser("login", help="Authenticate with Sphinx")
    login_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed messages")
    login_parser.add_argument(
        "-l",
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warn", "error", "fatal"],
        help="Log level when verbose is enabled (default: info)",
    )

    logout_parser = subparsers.add_parser("logout", help="Clear authentication")
    logout_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed messages")
    logout_parser.add_argument(
        "-l",
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warn", "error", "fatal"],
        help="Log level when verbose is enabled (default: info)",
    )

    status_parser = subparsers.add_parser("status", help="Check authentication status")
    status_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed messages")
    status_parser.add_argument(
        "-l",
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warn", "error", "fatal"],
        help="Log level when verbose is enabled (default: info)",
    )

    chat_parser = subparsers.add_parser("chat", help="Start a chat session")

    chat_parser.add_argument("--notebook-filepath", help="Path to notebook file (if not provided, will auto-generate based on prompt)")
    chat_parser.add_argument("--prompt", required=True, help="Chat prompt")

    chat_parser.add_argument("--sphinx-url", default="https://api.prod.sphinx.ai", help="Sphinx service URL")

    chat_parser.add_argument("--jupyter-server-url", help="Existing Jupyter server URL (optional)")

    chat_parser.add_argument("--jupyter-server-token", help="Jupyter server token (if using existing server)")

    chat_parser.add_argument("--no-memory-read", action="store_true", help="Disable memory read (default: enabled)")

    chat_parser.add_argument("--no-memory-write", action="store_true", help="Disable memory write (default: enabled)")

    chat_parser.add_argument(
        "--no-package-installation", action="store_true", help="Disable package installation (default: enabled)"
    )

    chat_parser.add_argument(
        "--no-collapse-exploratory-cells",
        action="store_true",
        help="Disable collapsing exploratory cells (default: enabled)",
    )

    chat_parser.add_argument(
        "--no-file-search",
        action="store_true",
        help="Disable file search tools (grep, ls, read) (default: enabled)",
    )

    chat_parser.add_argument(
        "--no-ripgrep-installation",
        action="store_true",
        help="Disable automatic ripgrep binary installation (default: enabled)",
    )

    chat_parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search tools (default: enabled)",
    )

    chat_parser.add_argument("--sphinx-rules-path", help="Path to rules file")

    chat_parser.add_argument(
        "--output-schema",
        help="JSON schema for structured output. Can be inline JSON or a file path (.json, .yaml, .yml, .txt). "
        'Simple: \'{"amount": "integer"}\'. '
        'With descriptions: \'{"metric": {"type": "number", "description": "explanation"}}\'. '
        "File: './schema.json'. Supported types: string, integer, number, float, boolean.",
    )

    chat_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed messages")
    chat_parser.add_argument(
        "-l",
        "--log-level",
        type=str.lower,
        choices=["debug", "info", "warn", "error", "fatal"],
        help="Log level when verbose is enabled (default: info)",
    )

    args = parser.parse_args()

    if args.command == "login":
        try:
            exit_code = run_login(verbose=args.verbose, log_level=args.log_level)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    elif args.command == "logout":
        try:
            exit_code = run_logout(verbose=args.verbose, log_level=args.log_level)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    elif args.command == "status":
        try:
            exit_code = run_status(verbose=args.verbose, log_level=args.log_level)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    elif args.command == "chat":
        try:
            exit_code = run_sphinx_chat(
                sphinx_url=args.sphinx_url,
                notebook_filepath=args.notebook_filepath,
                prompt=args.prompt,
                jupyter_server_url=args.jupyter_server_url,
                jupyter_server_token=args.jupyter_server_token,
                verbose=args.verbose,
                log_level=args.log_level,
                no_memory_read=args.no_memory_read,
                no_memory_write=args.no_memory_write,
                no_package_installation=args.no_package_installation,
                no_collapse_exploratory_cells=args.no_collapse_exploratory_cells,
                no_file_search=args.no_file_search,
                no_ripgrep_installation=args.no_ripgrep_installation,
                no_web_search=args.no_web_search,
                sphinx_rules_path=args.sphinx_rules_path,
                output_schema=args.output_schema,
            )
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    else:
        # Default: run interactive mode
        try:
            exit_code = run_interactive_chat(
                notebook_filepath=args.notebook_filepath,
                sphinx_url=args.sphinx_url,
                jupyter_server_url=args.jupyter_server_url,
                jupyter_server_token=args.jupyter_server_token,
                verbose=args.verbose,
                log_level=args.log_level,
                no_memory_read=args.no_memory_read,
                no_memory_write=args.no_memory_write,
                no_package_installation=args.no_package_installation,
                no_collapse_exploratory_cells=args.no_collapse_exploratory_cells,
                no_file_search=args.no_file_search,
                no_ripgrep_installation=args.no_ripgrep_installation,
                no_web_search=args.no_web_search,
                sphinx_rules_path=args.sphinx_rules_path,
            )
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
