#!/usr/bin/env python3
"""
Atlas Agent CLI - Simplified server monitoring

Usage:
    atlas setup     # Download binary, generate fingerprint, create config
    atlas start     # Start the monitoring daemon
    atlas stop      # Stop the daemon
    atlas status    # Check daemon status
    atlas logs      # View recent logs
    atlas claim     # Open dashboard to claim this server

No API key required. 30-day free trial. Auto-fixes common issues.
"""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import requests
import yaml

# Constants
BINARY_BASE_URL = "https://managedbyai.dev/bin"
RELAY_URL = "wss://atlas-ws.managedbyai.dev"
CONFIG_DIR = Path("/etc/atlas")
CONFIG_FILE = CONFIG_DIR / "config.yaml"
BINARY_PATH = Path("/usr/local/bin/atlas-agent")
SERVICE_NAME = "atlas-agent"
TRIAL_DAYS = 30


def get_fingerprint():
    """Generate unique fingerprint for this machine."""
    # Combine multiple hardware identifiers
    parts = []

    # Machine ID (Linux)
    machine_id_file = Path("/etc/machine-id")
    if machine_id_file.exists():
        parts.append(machine_id_file.read_text().strip())

    # Hostname
    parts.append(platform.node())

    # MAC address of first network interface
    try:
        import uuid as uuid_lib
        mac = ':'.join(['{:02x}'.format((uuid_lib.getnode() >> ele) & 0xff)
                       for ele in range(0, 48, 8)][::-1])
        parts.append(mac)
    except Exception:
        pass

    # Combine and hash
    combined = '-'.join(parts)
    fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:16]
    return f"atlas-{fingerprint}"


def get_binary_name():
    """Get the correct binary name for this platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map architecture
    arch_map = {
        'x86_64': 'amd64',
        'amd64': 'amd64',
        'aarch64': 'arm64',
        'arm64': 'arm64',
    }
    arch = arch_map.get(machine, machine)

    if system == 'darwin':
        return f"atlas-agent-darwin-{arch}"
    elif system == 'linux':
        return f"atlas-agent-linux-{arch}"
    else:
        raise RuntimeError(f"Unsupported platform: {system}/{machine}")


def check_root():
    """Check if running as root."""
    if os.geteuid() != 0:
        print("Error: This command requires root privileges.")
        print("Run with: sudo atlas <command>")
        sys.exit(1)


def cmd_setup(args):
    """Set up Atlas agent - download binary, generate config."""
    check_root()

    print("=" * 50)
    print("  ATLAS - AI-Powered Server Monitoring")
    print("  30-day free trial. No credit card required.")
    print("=" * 50)
    print()

    # Generate fingerprint
    fingerprint = get_fingerprint()
    print(f"Server ID: {fingerprint}")

    # Create directories
    print("\nCreating directories...")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    Path("/var/atlas/snapshots").mkdir(parents=True, exist_ok=True)
    Path("/usr/local/bin").mkdir(parents=True, exist_ok=True)

    # Download binary
    binary_name = get_binary_name()
    binary_url = f"{BINARY_BASE_URL}/{binary_name}"
    print(f"Downloading Atlas agent ({binary_name})...")

    try:
        response = requests.get(binary_url, stream=True, timeout=60)
        response.raise_for_status()

        with open(BINARY_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        os.chmod(BINARY_PATH, 0o755)
        print(f"  Installed: {BINARY_PATH}")
    except requests.RequestException as e:
        print(f"Error downloading binary: {e}")
        sys.exit(1)

    # Download auto-discover script
    discover_url = f"{BINARY_BASE_URL}/auto-discover.sh"
    discover_path = Path("/usr/local/bin/atlas-discover")

    try:
        response = requests.get(discover_url, timeout=30)
        response.raise_for_status()
        discover_path.write_text(response.text)
        os.chmod(discover_path, 0o755)
        print(f"  Installed: {discover_path}")
    except requests.RequestException:
        print("  Warning: Could not download auto-discover script")

    # Create config
    print("\nGenerating configuration...")
    trial_start = int(time.time())

    config = {
        'server_id': fingerprint,
        'relay_url': RELAY_URL,
        'trial_start': trial_start,
        'trial_days': TRIAL_DAYS,
        'hostname': platform.node(),
        'metrics': {
            'enabled': True,
            'interval_seconds': 30,
        },
        'log_watcher': {
            'enabled': True,
            'paths': [
                '/var/log/syslog',
                '/var/log/messages',
                '/var/log/nginx/error.log',
            ],
        },
        'playbooks': {
            'enabled': True,
        },
    }

    # Run auto-discovery if available
    if discover_path.exists():
        print("Running service discovery...")
        try:
            subprocess.run(
                [str(discover_path), str(CONFIG_FILE), fingerprint, RELAY_URL],
                check=True, timeout=60
            )
            # Merge with discovered config
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    discovered = yaml.safe_load(f)
                if discovered:
                    config.update(discovered)
        except (subprocess.SubprocessError, OSError):
            pass

    # Write config
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"  Config: {CONFIG_FILE}")

    # Create systemd service
    print("\nCreating systemd service...")
    service_content = f"""[Unit]
Description=Atlas Agent - AI-Powered Server Monitoring
Documentation=https://managedbyai.dev
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
ExecStart={BINARY_PATH} daemon -c {CONFIG_FILE}
Restart=always
RestartSec=10
Environment=ATLAS_SNAPSHOT_DIR=/var/atlas/snapshots
StandardOutput=journal
StandardError=journal
SyslogIdentifier=atlas-agent
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
"""

    service_path = Path(f"/etc/systemd/system/{SERVICE_NAME}.service")
    service_path.write_text(service_content)

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)

    print()
    print("=" * 50)
    print("  SETUP COMPLETE")
    print("=" * 50)
    print()
    print(f"Server ID: {fingerprint}")
    print()
    print("Next steps:")
    print("  1. Start monitoring:  sudo atlas start")
    print("  2. Check status:      sudo atlas status")
    print("  3. View logs:         sudo atlas logs")
    print()
    print(f"Trial: {TRIAL_DAYS} days free. Claim at https://managedbyai.dev/dashboard")
    print()


def cmd_start(args):
    """Start the Atlas daemon."""
    check_root()

    if not BINARY_PATH.exists():
        print("Error: Atlas not installed. Run 'sudo atlas setup' first.")
        sys.exit(1)

    print("Starting Atlas agent...")
    result = subprocess.run(["systemctl", "start", SERVICE_NAME])

    if result.returncode == 0:
        time.sleep(2)  # Give it time to start
        subprocess.run(["systemctl", "status", SERVICE_NAME, "--no-pager"])
    else:
        print("Failed to start. Check logs with: sudo atlas logs")
        sys.exit(1)


def cmd_stop(args):
    """Stop the Atlas daemon."""
    check_root()

    print("Stopping Atlas agent...")
    subprocess.run(["systemctl", "stop", SERVICE_NAME])
    print("Stopped.")


def cmd_status(args):
    """Check Atlas daemon status."""
    subprocess.run(["systemctl", "status", SERVICE_NAME, "--no-pager"])

    # Show trial info
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f)

        trial_start = config.get('trial_start', 0)
        trial_days = config.get('trial_days', TRIAL_DAYS)

        if trial_start:
            elapsed_days = (time.time() - trial_start) / 86400
            remaining = max(0, trial_days - elapsed_days)

            print()
            if remaining > 0:
                print(f"Trial: {remaining:.0f} days remaining")
            else:
                print("Trial: EXPIRED - Claim at https://managedbyai.dev/dashboard")


def cmd_logs(args):
    """View Atlas agent logs."""
    lines = args.lines if hasattr(args, 'lines') else 50
    subprocess.run(["journalctl", "-u", SERVICE_NAME, "-n", str(lines), "--no-pager"])


def cmd_claim(args):
    """Open dashboard to claim this server."""
    fingerprint = get_fingerprint()
    url = f"https://managedbyai.dev/dashboard?claim={fingerprint}"

    print(f"Server ID: {fingerprint}")
    print()
    print(f"To claim this server, visit:")
    print(f"  {url}")
    print()

    # Try to open browser
    try:
        import webbrowser
        webbrowser.open(url)
        print("(Opening in browser...)")
    except Exception:
        pass


def cmd_uninstall(args):
    """Uninstall Atlas agent."""
    check_root()

    print("Stopping Atlas agent...")
    subprocess.run(["systemctl", "stop", SERVICE_NAME], capture_output=True)
    subprocess.run(["systemctl", "disable", SERVICE_NAME], capture_output=True)

    print("Removing files...")
    files_to_remove = [
        BINARY_PATH,
        Path("/usr/local/bin/atlas-discover"),
        Path(f"/etc/systemd/system/{SERVICE_NAME}.service"),
    ]

    for f in files_to_remove:
        if f.exists():
            f.unlink()
            print(f"  Removed: {f}")

    # Keep config for now (user might reinstall)
    print()
    print("Uninstalled. Config preserved at /etc/atlas/")
    print("To fully remove: sudo rm -rf /etc/atlas /var/atlas")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Atlas Agent - AI-powered server monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup      Download binary, generate config (run first)
  start      Start the monitoring daemon
  stop       Stop the daemon
  status     Check daemon status and trial info
  logs       View recent logs
  claim      Open dashboard to claim this server
  uninstall  Remove Atlas agent

30-day free trial. No API key required.
https://managedbyai.dev
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # setup
    parser_setup = subparsers.add_parser('setup', help='Set up Atlas agent')
    parser_setup.set_defaults(func=cmd_setup)

    # start
    parser_start = subparsers.add_parser('start', help='Start daemon')
    parser_start.set_defaults(func=cmd_start)

    # stop
    parser_stop = subparsers.add_parser('stop', help='Stop daemon')
    parser_stop.set_defaults(func=cmd_stop)

    # status
    parser_status = subparsers.add_parser('status', help='Check status')
    parser_status.set_defaults(func=cmd_status)

    # logs
    parser_logs = subparsers.add_parser('logs', help='View logs')
    parser_logs.add_argument('-n', '--lines', type=int, default=50, help='Number of lines')
    parser_logs.set_defaults(func=cmd_logs)

    # claim
    parser_claim = subparsers.add_parser('claim', help='Claim this server')
    parser_claim.set_defaults(func=cmd_claim)

    # uninstall
    parser_uninstall = subparsers.add_parser('uninstall', help='Uninstall Atlas')
    parser_uninstall.set_defaults(func=cmd_uninstall)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
