"""tlnr Daemon - Unix socket server for fast predictions.

This daemon eliminates Python startup overhead by keeping CommandTutor
loaded in memory and responding to predictions via Unix socket.

Performance:
- Without daemon: 50-100ms per prediction (Python startup overhead)
- With daemon: <5ms per prediction (socket communication only)

Usage:
    terminal-tutor daemon start   # Start daemon in background
    terminal-tutor daemon stop    # Stop daemon
    terminal-tutor daemon status  # Check if daemon is running
"""

import os
import sys
import signal
import socket
import threading
import time
from pathlib import Path


# Socket and PID file paths
SOCKET_PATH = Path.home() / ".tlnr.sock"
PID_FILE = Path.home() / ".tlnr.pid"


class TerminalTutorDaemon:
    """Unix socket daemon for fast command predictions."""

    def __init__(self):
        self.socket_path = SOCKET_PATH
        self.pid_file = PID_FILE
        self.running = False
        self.tutor = None
        self.server_socket = None

    def _load_tutor(self):
        """Load CommandTutor once - the whole point of the daemon."""
        from .core import CommandTutor
        self.tutor = CommandTutor()
        
        # Pre-load Local LLM if configured (crucial for performance)
        # Pre-load Local LLM if configured or auto-detected (crucial for performance)
        provider = self.tutor.config_manager.get_provider()
        
        should_preload = False
        if provider == 'local':
            should_preload = True
        elif provider == 'auto':
            # Only preload in auto mode if the model is actually there (don't spam logs otherwise)
            try:
                from .local_llm import LocalLLMManager
                llm = LocalLLMManager()
                if llm.is_model_downloaded():
                    should_preload = True
            except ImportError:
                should_preload = False

        # Start background download thread if needed (Silent Setup)
        if provider == 'local' or provider == 'auto':
            threading.Thread(target=self._background_download, daemon=True).start()
                
        return self.tutor

    def _background_download(self):
        """Silently setup dependencies and download model."""
        lock_file = Path.home() / ".terminal-tutor.download.lock"
        
        try:
            from .installer import ShellInstaller
            installer = ShellInstaller()
            
            # 1. Create Lock Immediately
            print("⬇️  Daemon: Starting background setup...")
            lock_file.touch()

            # 2. auto-heal dependencies (Silent)
            # This ensures we have huggingface_hub before importing local_llm
            installer.install_local_llm_deps(silent=True)
            
            # 3. Now safe to import LocalLLMManager
            from .local_llm import LocalLLMManager
            llm = LocalLLMManager()
            
            # 4. Check if needed
            if not llm.is_model_downloaded():
                # Download!
                llm.download_model()
                # Preload
                llm.load_model()
                print("✅ Daemon: Background setup complete.")
            
            elif provider == 'local':
                 llm.load_model()

        except Exception as e:
            print(f"❌ Daemon background task failed: {e}")
        
        finally:
            # Always remove lock
            if lock_file.exists():
                lock_file.unlink()

    def _cleanup_socket(self):
        """Remove stale socket file if exists."""
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass

    def _write_pid(self):
        """Write PID file for daemon management."""
        self.pid_file.write_text(str(os.getpid()))

    def _remove_pid(self):
        """Remove PID file on shutdown."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except OSError:
                pass

    def _handle_client(self, conn):
        """Handle a single client connection."""
        try:
            # Set timeout to prevent hanging
            conn.settimeout(5.0)

            # Receive command (max 4KB should be plenty)
            data = conn.recv(4096)
            if not data:
                return

            command = data.decode('utf-8').strip()

            # Get prediction (fastest path)
            if self.tutor and command:
                try:
                    # Use realtime method which includes risk level and bucket matching O(1)
                    response = self.tutor.get_description_realtime(command)
                    if not response:
                        response = ""
                except Exception:
                    response = ""
            else:
                response = ""

            # Send response
            conn.sendall(response.encode('utf-8'))

        except socket.timeout:
            pass
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    def _signal_handler(self, _signum, _frame):
        """Handle shutdown signals gracefully."""
        self.running = False

    def start(self, foreground=False):
        """Start the daemon.

        Args:
            foreground: If True, run in foreground (for debugging).
                       If False, daemonize (default).
        """
        # Check if already running
        if self.is_running():
            print("Daemon is already running.")
            return False

        if not foreground:
            # Fork to background
            try:
                pid = os.fork()
                if pid > 0:
                    # Parent process - wait a moment then exit
                    time.sleep(0.5)
                    if self.is_running():
                        #print(f"Daemon started (PID: {pid})")
                        return True
                    else:
                        #print("Failed to start daemon")
                        return False
            except OSError as e:
                #print(f"Fork failed: {e}")
                return False

            # Child process continues
            os.setsid()

            # Second fork to prevent zombie processes
            try:
                pid = os.fork()
                if pid > 0:
                    os._exit(0)
            except OSError:
                os._exit(1)

            # Redirect standard file descriptors
            sys.stdin = open(os.devnull, 'r')
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Cleanup any stale socket
        self._cleanup_socket()

        # Load CommandTutor (the expensive part - only done once!)
        try:
            self._load_tutor()
        except Exception as e:
            if foreground:
                print(f"Failed to load CommandTutor: {e}")
            return False

        # Create Unix socket
        try:
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(str(self.socket_path))
            self.server_socket.listen(10)
            self.server_socket.settimeout(1.0)  # Allow periodic shutdown check
        except Exception as e:
            if foreground:
                print(f"Failed to create socket: {e}")
            self._cleanup_socket()
            return False

        # Write PID file
        self._write_pid()
        self.running = True

        if foreground:
            print(f"Daemon running on {self.socket_path}")
            print("Press Ctrl+C to stop")

        # Main server loop
        try:
            while self.running:
                try:
                    conn, _ = self.server_socket.accept()
                    # Handle each connection in a thread for concurrency
                    thread = threading.Thread(target=self._handle_client, args=(conn,))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue
                except Exception:
                    if self.running:
                        continue
                    break
        finally:
            self._shutdown()

        return True

    def _shutdown(self):
        """Clean shutdown of daemon."""
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        self._cleanup_socket()
        self._remove_pid()

    def stop(self):
        """Stop the running daemon."""
        pid = self.get_pid()
        if pid is None:
            print("Daemon is not running.")
            return False

        try:
            os.kill(pid, signal.SIGTERM)
            # Wait for daemon to stop
            for _ in range(20):  # Wait up to 2 seconds
                time.sleep(0.1)
                if not self.is_running():
                    print("Daemon stopped.")
                    return True
            print("Daemon did not stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
            self._cleanup_socket()
            self._remove_pid()
            print("Daemon killed.")
            return True
        except ProcessLookupError:
            print("Daemon process not found, cleaning up...")
            self._cleanup_socket()
            self._remove_pid()
            return True
        except PermissionError:
            print("Permission denied to stop daemon.")
            return False

    def get_pid(self):
        """Get PID of running daemon, or None if not running."""
        if not self.pid_file.exists():
            return None
        try:
            pid = int(self.pid_file.read_text().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            return pid
        except (ValueError, ProcessLookupError, PermissionError):
            return None

    def is_running(self):
        """Check if daemon is running."""
        # Check both PID and socket
        pid = self.get_pid()
        socket_exists = self.socket_path.exists()

        if pid and socket_exists:
            return True

        # Cleanup stale files
        if not pid and socket_exists:
            self._cleanup_socket()
        if pid is None and self.pid_file.exists():
            self._remove_pid()

        return False

    def status(self):
        """Print daemon status."""
        if self.is_running():
            pid = self.get_pid()
            print(f"Daemon is running (PID: {pid})")
            print(f"Socket: {self.socket_path}")
            return True
        else:
            print("Daemon is not running.")
            return False


def query_daemon(command: str, timeout: float = 1.0) -> str:
    """Query the daemon for a prediction.

    Args:
        command: The command to get prediction for
        timeout: Socket timeout in seconds

    Returns:
        Prediction string, or empty string if daemon not available
    """
    if not SOCKET_PATH.exists():
        return ""

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(str(SOCKET_PATH))
            sock.sendall(command.encode('utf-8'))
            response = sock.recv(4096)
            return response.decode('utf-8')
    except Exception:
        return ""


def is_daemon_running() -> bool:
    """Quick check if daemon is running."""
    return SOCKET_PATH.exists() and PID_FILE.exists()


# CLI interface when run directly
if __name__ == "__main__":
    daemon = TerminalTutorDaemon()

    if len(sys.argv) < 2:
        print("Usage: python -m terminal_tutor.daemon [start|stop|status|foreground]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "start":
        daemon.start(foreground=False)
    elif cmd == "foreground":
        daemon.start(foreground=True)
    elif cmd == "stop":
        daemon.stop()
    elif cmd == "status":
        daemon.status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
