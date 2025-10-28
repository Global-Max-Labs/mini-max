#!/usr/bin/env python3
"""
Command-line interface for the multi-service application.
"""

import click
import multiprocessing
import time
import signal
import sys
import os
from pathlib import Path
import logging

# Import your existing modules
from minimax.app.stt.src.main import run_listener
import uvicorn
from minimax.mqtt_worker import start_mqtt
from minimax.mqtt_utils import ensure_mosquitto_docker, ensure_ffmpeg
from minimax import __version__
from minimax.app.scripts.init_mini_max import remove_init, initialize
import lancedb
from minimax.app.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("minimax")

# Global process tracking
running_processes = []


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    click.echo("\n🛑 Shutting down services...")
    for process in running_processes:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
    click.echo("👋 All services stopped")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Multi-service application with API, MQTT, and STT components."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--host", default="0.0.0.0", help="API host")
@click.option("--port", default=8000, type=int, help="API port")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def api(ctx, host, port, reload):
    """Start the FastAPI server."""
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        click.echo(f"[FASTAPI] Starting API server on {host}:{port}")

    try:
        uvicorn.run(
            "minimax.app.main:app",  # Use string import instead of imported object
            host=host,
            port=port,
            reload=reload,
            log_level="info" if verbose else "warning",
        )
    except Exception as e:
        click.echo(f"❌ API Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--skip-setup", is_flag=True, help="Skip Docker/FFmpeg setup checks")
@click.option("--plugins-dir", type=click.Path(exists=True, file_okay=False), help="Path to custom MQTT plugins directory")
@click.pass_context
def mqtt(ctx, skip_setup, plugins_dir):
    """Start the MQTT worker."""
    verbose = ctx.obj.get("verbose", False)

    if not skip_setup:
        if verbose:
            click.echo("[MQTT] Ensuring broker is available...")
        ensure_mosquitto_docker()

        if verbose:
            click.echo("[FFMPEG] Ensuring FFMPEG is available...")
        ensure_ffmpeg()

    if verbose:
        click.echo("[MQTT] Starting MQTT worker...")
        if plugins_dir:
            click.echo(f"[MQTT] Using plugins dir: {plugins_dir}")

    try:
        start_mqtt(plugins_dir=plugins_dir)
    except Exception as e:
        click.echo(f"❌ MQTT Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stt(ctx):
    """Start the Speech-to-Text worker."""
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        click.echo("[STT] Starting STT worker...")

    try:
        run_listener()
    except Exception as e:
        click.echo(f"❌ STT Error: {e}", err=True)
        sys.exit(1)


def _initialize_database_if_needed(init_file_path=None, verbose=False):
    """Initialize the database with the specified init file if needed."""
    try:
        # Use the provided init_file_path or fall back to settings
        current_init_file = init_file_path or settings.INIT_FILE

        if verbose:
            click.echo(
                f"[DB] Checking database initialization with: {current_init_file}"
            )

        # Connect to LanceDB
        db = lancedb.connect(settings.DB_PATH)

        # Check if table exists and has data
        table_exists = "init_qa_action" in db.table_names()
        needs_reinit = True
        # needs_reinit = False

        # if table_exists:
        #     table = db.open_table("init_qa_action")
        #     count = table.count_rows()

        #     # Reinitialize if empty or if we're using a different init file than test_text.csv
        #     if count == 0 or init_file_path:
        #         needs_reinit = True
        # else:
        #     needs_reinit = True

        if needs_reinit:
            if verbose:
                click.echo("[DB] Initializing database...")
            remove_init()
            initialize(current_init_file)
            if verbose:
                click.echo("[DB] Database initialization complete")
        else:
            if verbose:
                click.echo("[DB] Database already initialized")

    except Exception as e:
        if verbose:
            click.echo(f"[DB] Database initialization error: {e}")
        raise


@cli.command()
@click.option("--api-host", default="0.0.0.0", help="API host")
@click.option("--api-port", default=8000, type=int, help="API port")
@click.option("--skip-mqtt-setup", is_flag=True, help="Skip MQTT Docker/FFmpeg setup")
@click.option(
    "--services",
    "-s",
    multiple=True,
    type=click.Choice(["api", "mqtt", "stt"]),
    help="Specific services to run (default: all)",
)
@click.option(
    "--init_file",
    type=click.Path(exists=True),
    help="Path to custom initialization CSV file",
)
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False),
    help="Path to custom MQTT plugins directory",
)
@click.pass_context
def start(ctx, api_host, api_port, skip_mqtt_setup, services, init_file, plugins_dir):
    """Start all services (or specified services) in parallel."""
    verbose = ctx.obj.get("verbose", True)

    if init_file:
        # Convert to absolute path if relative
        init_file_path = os.path.abspath(init_file)
        os.environ["MINIMAX_INIT_FILE"] = init_file_path
        if verbose:
            print(f"Using custom init file: {init_file_path}")
            click.echo(f"Using custom init file: {init_file_path}")

    # Initialize database before starting services
    try:
        _initialize_database_if_needed(init_file, verbose)
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}", err=True)
        sys.exit(1)

    # Default to all services if none specified
    if not services:
        # services = ['api']
        services = ["api", "mqtt", "stt"]

    global running_processes
    processes = []

    if "api" in services:
        if verbose:
            click.echo(f"[FASTAPI] Starting API server on {api_host}:{api_port}")
            logger.info(f"Using custom init file: {init_file}")
        p_api = multiprocessing.Process(
            target=_run_api_process, args=(api_host, api_port, verbose, init_file)
        )
        processes.append(("API", p_api))

    if "mqtt" in services:
        if verbose:
            click.echo("[MQTT] Starting MQTT worker...")
            if plugins_dir:
                click.echo(f"[MQTT] Using plugins dir: {plugins_dir}")
            logger.info(f"Using custom init file: {init_file}")
        p_mqtt = multiprocessing.Process(
            target=_run_mqtt_process, args=(skip_mqtt_setup, verbose, plugins_dir)
        )
        processes.append(("MQTT", p_mqtt))

    if "stt" in services:
        if verbose:
            click.echo("[STT] Starting STT worker...")
            logger.info(f"Using custom init file: {init_file}")
        p_stt = multiprocessing.Process(target=_run_stt_process, args=(verbose,))
        processes.append(("STT", p_stt))

    # Start all processes
    for name, process in processes:
        process.start()
        running_processes.append(process)
        if verbose:
            click.echo(f"✅ {name} service started (PID: {process.pid})")

        # Small delay between starts
        if name == "API":
            time.sleep(1)  # Give API a head start

    click.echo(f"🚀 Started {len(processes)} service(s). Press Ctrl+C to stop all.")

    # Wait for all processes
    try:
        for name, process in processes:
            process.join()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


@cli.command()
def setup():
    """Set up dependencies (Docker, FFmpeg, etc.)."""
    click.echo("🔧 Setting up dependencies...")

    try:
        click.echo("[DOCKER] Ensuring Mosquitto MQTT broker...")
        ensure_mosquitto_docker()
        click.echo("✅ MQTT broker ready")

        click.echo("[FFMPEG] Ensuring FFmpeg is available...")
        ensure_ffmpeg()
        click.echo("✅ FFmpeg ready")

        click.echo("🎉 Setup complete!")

    except Exception as e:
        click.echo(f"❌ Setup failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Check the status of services and dependencies."""
    click.echo("=== Service Status ===")

    # Check if processes are running (this is basic - you might want more sophisticated checks)
    import psutil

    # Check for FastAPI (look for uvicorn processes)
    fastapi_running = any("uvicorn" in p.name() for p in psutil.process_iter(["name"]))
    click.echo(f"FastAPI: {'🟢 Running' if fastapi_running else '🔴 Not running'}")

    # Check Docker containers
    try:
        import subprocess

        result = subprocess.run(
            ["docker", "ps", "--filter", "name=iot-mosquitto", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        mqtt_running = "iot-mosquitto" in result.stdout
        click.echo(f"MQTT Broker: {'🟢 Running' if mqtt_running else '🔴 Not running'}")
    except:
        click.echo("MQTT Broker: ❓ Unable to check")

    # Check FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        click.echo("FFmpeg: ✅ Available")
    except:
        click.echo("FFmpeg: ❌ Not available")


@cli.command()
def stop():
    """Stop all running services."""
    click.echo("🛑 Stopping services...")

    # Stop Docker containers
    try:
        import subprocess

        subprocess.run(["docker", "stop", "iot-mosquitto"], capture_output=True)
        click.echo("✅ Stopped MQTT broker")
    except:
        pass

    # Kill uvicorn processes (be careful with this in production!)
    try:
        import psutil

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if "uvicorn" in proc.info["name"] or any(
                "uvicorn" in cmd for cmd in proc.info["cmdline"] or []
            ):
                proc.terminate()
        click.echo("✅ Stopped API server")
    except:
        pass

    click.echo("👋 Services stopped")


# Helper functions for multiprocessing
def _run_api_process(host, port, verbose, init_file=None):
    """Run API in a separate process."""
    if init_file:
        # Convert to absolute path if relative
        init_file_path = os.path.abspath(init_file)
        os.environ["MINIMAX_INIT_FILE"] = init_file_path
        if verbose:
            print(f"[API] Using custom init file: {init_file_path}")

    uvicorn.run(
        "minimax.app.main:app",  # Use string import instead of imported object
        host=host,
        port=port,
        log_level="info" if verbose else "warning",
    )


def _run_mqtt_process(skip_setup, verbose, plugins_dir=None):
    """Run MQTT worker in a separate process."""
    if not skip_setup:
        ensure_mosquitto_docker()
        ensure_ffmpeg()
    start_mqtt(plugins_dir=plugins_dir)


def _run_stt_process(verbose):
    """Run STT worker in a separate process."""
    run_listener()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
