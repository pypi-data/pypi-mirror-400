import argparse
import os
import sys
import subprocess
import time
import signal
import platform
import urllib.request

PID_FILE = os.path.expanduser("~/.greenrefactor_server.pid")

def save_pid(pid):
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))

def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return None

def remove_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

import socket

def is_server_running(host="localhost", port=8126):
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def start_server():
    # Check if already running
    if is_server_running():
        print("✅ Power Server is already running.")
        return None

    print(f"🔌 Starting Power Server...")
    
    cmd = [sys.executable, "-m", "greenrefactor.power_server"]
    
    # On macOS/Linux, we need sudo for hardware access (RAPL/Powermetrics)
    if platform.system() != "Windows":
        if os.geteuid() != 0:
            print("🔒 Requesting sudo privileges for hardware access...")
            cmd = ["sudo"] + cmd

    # Start in background
    log_file = os.path.expanduser("~/.greenrefactor.log")
    with open(log_file, "w") as f:
        # We must keep the file open for the subprocess? 
        # No, we can pass the file descriptor, but Popen needs the file object or fileno.
        # But we act like a daemon, so we shouldn't keep it open in the parent?
        # A clearer way is to pass the file object directly, Popen handles it.
        # But we need to ensure it persists.
        pass
    
    # We'll let Popen open it.
    log_f = open(log_file, "a")
    process = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    print(f"📄 Logs are being written to {log_file}")
    
    # Wait for it to be ready
    print("⏳ Waiting for Power Server to be ready...")
    for _ in range(10):
        if is_server_running():
            print("✅ Power Server is ready!")
            # Save a marker file (we can't reliably track sudo PIDs)
            save_pid(1)  # Dummy PID, we'll find real PID by port
            return process
        time.sleep(1)
    
    print("❌ Failed to start Power Server.")
    process.kill()
    sys.exit(1)

def stop_server():
    print("🛑 Stopping Power Server...")
    
    # Strategy 1: Try PID file first (most reliable)
    saved_pid = read_pid()
    if saved_pid:
        try:
            # Verify it's our process
            proc_name = subprocess.check_output(["ps", "-p", str(saved_pid), "-o", "comm="], text=True).strip()
            if "python" in proc_name.lower() or "greenrefactor" in proc_name.lower():
                # It's our process, kill it
                try:
                    os.kill(saved_pid, signal.SIGTERM)
                    print(f"✅ Power Server stopped (PID: {saved_pid})")
                    remove_pid_file()
                    return
                except PermissionError:
                    print(f"🔒 PID {saved_pid} requires sudo to kill...")
                    subprocess.run(["sudo", "kill", str(saved_pid)])
                    print(f"✅ Power Server stopped (PID: {saved_pid})")
                    remove_pid_file()
                    return
                except ProcessLookupError:
                    print(f"⚠️  Process {saved_pid} already gone.")
                    remove_pid_file()
                    return
        except subprocess.CalledProcessError:
            # Process doesn't exist, clean up PID file
            print(f"⚠️  Saved PID {saved_pid} not found. Cleaning up...")
            remove_pid_file()
    
    # Strategy 2: Port check (fallback, but avoid Docker processes)
    def find_pid_by_port(use_sudo=False):
        cmd = ["lsof", "-ti", ":8126"]
        if use_sudo:
            cmd = ["sudo"] + cmd
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        return None

    # Try normal user first
    pid = find_pid_by_port()
    
    # Try sudo if port is occupied but not visible
    if not pid and is_server_running():
        print("🔒 Port is occupied but PID not visible. Trying with sudo...")
        pid = find_pid_by_port(use_sudo=True)
    
    if pid:
        # Safety check: Verify it's a Python process (not Docker)
        try:
            proc_name = subprocess.check_output(["ps", "-p", str(pid), "-o", "comm="], text=True).strip()
            if "docker" in proc_name.lower():
                print(f"ℹ️  Port 8126 is being used by Docker (port forwarding).")
                print(f"   Attempting to find and stop the actual GreenRefactor server...")
                
                # Try to kill the actual server process
                try:
                    result = subprocess.run(
                        ["sudo", "pkill", "-f", "greenrefactor.power_server"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ Power Server stopped successfully")
                        remove_pid_file()
                        return
                    else:
                        print(f"⚠️  No active GreenRefactor server found to stop")
                        remove_pid_file()
                        return
                except Exception as e:
                    print(f"❌ Failed to stop server: {e}")
                    print(f"   Try manually: sudo pkill -f greenrefactor.power_server")
                    return
            elif "python" not in proc_name.lower() and "greenrefactor" not in proc_name.lower():
                print(f"⚠️  WARNING: Process on port 8126 (PID {pid}) seems to be '{proc_name}'.")
                print("   This does not look like the GreenRefactor server. Aborting stop command for safety.")
                return
        except Exception:
            pass

        # Kill the process
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ Power Server stopped (PID: {pid})")
        except PermissionError:
            print(f"🔒 PID {pid} requires sudo to kill...")
            subprocess.run(["sudo", "kill", str(pid)])
            print(f"✅ Power Server stopped (PID: {pid})")
        except ProcessLookupError:
             print(f"⚠️  Process {pid} already gone.")
             
        remove_pid_file()
    else:
        print("⚠️  No Power Server found running on port 8126")
        remove_pid_file()

def main():
    parser = argparse.ArgumentParser(description="GreenRefactor CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # 'server' command: The main command to start the metrics server
    subparsers.add_parser("server", help="Start the Power Metrics Server")

    # 'stop' command: Stop the server
    subparsers.add_parser("stop", help="Stop the Power Metrics Server")

    # 'dashboard' command: Optional helper to print Docker instructions
    subparsers.add_parser("dashboard", help="Show instructions to start the Dashboard")

    args = parser.parse_args()

    if args.command == "server":
        server_proc = start_server()
        if server_proc:
            print(f"🚀 GreenRefactor Server started in background")
            print(f"📊 Metrics available at http://localhost:8126")
            print(f"🛑 To stop: greenrefactor stop")
    
    elif args.command == "stop":
        stop_server()
                    
    elif args.command == "dashboard":
        print("\n📊 To start the Dashboard, run this Docker command:")
        print("\n    docker run -p 8123:8123 -p 8124:8124 rmcodeio/greenrefactor-dashboard\n")
        print("Make sure 'greenrefactor server' is running first!")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

