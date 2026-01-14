"""Shell integration installer."""

import os
import shutil
import sys
from pathlib import Path

# Import for package resource access
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources


class ShellInstaller:
    """Install and manage shell integration."""

    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".config" / "tlnr"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _detect_current_shell(self):
        """Detect the currently running shell.

        Returns the shell name (e.g., 'zsh', 'bash', 'fish') by checking:
        1. Parent process name (most reliable for manual shell switches)
        2. SHELL environment variable (fallback)
        """
        # First try to detect current running shell via parent process
        # This is more reliable than SHELL env var when user switches shells
        try:
            import subprocess
            result = subprocess.run(['ps', '-p', str(os.getppid()), '-o', 'comm='],
                                  capture_output=True, text=True, timeout=1)
            current_shell = result.stdout.strip().lower()
        except Exception:
            current_shell = ''

        # Fall back to SHELL environment variable
        env_shell = os.environ.get('SHELL', '').lower()

        # Prefer current shell over env shell
        return current_shell if current_shell else env_shell

    def get_shell_config_file(self):
        """Detect and return the appropriate shell config file."""
        shell = self._detect_current_shell()

        if 'zsh' in shell:
            return self.home / '.zshrc'
        elif 'fish' in shell:
            fish_config = self.home / '.config' / 'fish' / 'config.fish'
            # Create fish config directory if it doesn't exist
            fish_config.parent.mkdir(parents=True, exist_ok=True)
            return fish_config
        else:  # Default to bash
            bashrc = self.home / '.bashrc'
            bash_profile = self.home / '.bash_profile'
            return bashrc if bashrc.exists() else bash_profile

    def get_shell_integration_code(self):
        """Get the shell integration code."""
        shell = self._detect_current_shell()

        if 'zsh' in shell:
            return self._get_zsh_realtime_integration()
        else:
            return self._get_bash_integration()

    def _get_zsh_realtime_integration(self):
        """Get advanced Zsh real-time integration."""
        try:
            # Use importlib.resources to access package files
            # This works correctly when installed via pip/uv/pipx
            if sys.version_info >= (3, 9):
                # Python 3.9+ API
                zsh_content = resources.files('tlnr').joinpath('zsh_integration.zsh').read_text()
            else:
                # Python 3.7-3.8 compatibility
                zsh_content = resources.read_text('tlnr', 'zsh_integration.zsh')

            return f'\n# tlnr Integration - Start\n{zsh_content}\n# tlnr Integration - End\n'
        except Exception as e:
            # Fallback to bash integration if file not found
            print(f"⚠️  Warning: Could not load Zsh integration ({e})")
            print("   Falling back to basic integration")
            return self._get_bash_integration()

    def _get_bash_integration(self):
        """Get basic Bash/universal integration."""
        return '''
# tlnr Integration - Start

# Simple real-time prediction via trap DEBUG
function tt_predict_live() {
    local cmd="$BASH_COMMAND"

    # Skip our internal commands
    [[ "$cmd" =~ ^(tt_|terminal-tutor) ]] && return

    # Only show predictions for commands we recognize, silently ignore others
    if [[ "$TT_LIVE_MODE" == "enabled" ]]; then
        local prediction=""
        if command -v tlnr >/dev/null 2>&1; then
            prediction=$(tlnr explain --no-confirm "$cmd" 2>/dev/null)
        fi

        # Only show if we have a real match (not "not found")
        if [[ -n "$prediction" && "$prediction" != *"not found"* ]]; then
            echo -e "\\033[90m$prediction\\033[0m"
        fi
    fi
}

function tt_explain() {
    local cmd="$1"
    shift
    local full_cmd="$cmd $@"

    # Show live prediction if enabled
    if [[ "$TT_LIVE_MODE" == "enabled" ]]; then
        local prediction=""
        if command -v tlnr >/dev/null 2>&1; then
            prediction=$(tlnr explain --no-confirm "$full_cmd" 2>/dev/null)
        fi

        if [[ -n "$prediction" ]]; then
            echo -e "\\033[90m$prediction\\033[0m"
        fi
    fi

    # Use the installed tlnr command directly (cleaner than python -m)
    if command -v tlnr >/dev/null 2>&1; then
        tlnr explain --no-confirm "$cmd" "$@"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m tlnr.cli explain --no-confirm "$cmd" "$@"
    elif command -v python >/dev/null 2>&1; then
        python -m tlnr.cli explain --no-confirm "$cmd" "$@"
    else
        echo "Error: tlnr not found and no python interpreter available"
        return 1
    fi

    # Check exit status for dangerous commands
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Command explanation failed or cancelled."
        return 1
    fi

    # Ask for confirmation
    echo -n "Execute command? [Y/n]: "
    read -r response
    case "$response" in
        [nN][oO]|[nN])
            echo "Command cancelled."
            return 1
            ;;
        *)
            "$cmd" "$@"
            ;;
    esac
}

# Create aliases for common commands
alias kubectl='tt_explain kubectl'
alias docker='tt_explain docker'
alias git='tt_explain git'
alias systemctl='tt_explain systemctl'
alias rm='tt_explain rm'
alias chmod='tt_explain chmod'
alias chown='tt_explain chown'
alias iptables='tt_explain iptables'
alias ufw='tt_explain ufw'

# Note: Use 'tlnr enable/disable/toggle' to control TLNR
# tlnr Integration - End
'''

    def install(self):
        """Install shell integration."""
        config_file = self.get_shell_config_file()
        integration_code = self.get_shell_integration_code()

        # Check if already installed
        if config_file.exists():
            content = config_file.read_text()
            if "tlnr Integration" in content:
                print("✅ TLNR is already installed!")
                return True
        else:
            # Create the config file if it doesn't exist
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                config_file.touch()
                print(f"📝 Created {config_file}")
            except PermissionError:
                print(f"❌ Cannot create {config_file}: Permission denied")
                print("   Try: sudo chmod 755 $(dirname {})".format(config_file))
                return False
            except Exception as e:
                print(f"❌ Cannot create {config_file}: {e}")
                return False

        # Append integration code
        try:
            with open(config_file, 'a') as f:
                f.write('\n')
                f.write(integration_code)
        except PermissionError:
            print(f"❌ Cannot write to {config_file}: Permission denied")
            print("   Try: chmod 644 {}".format(config_file))
            return False
        except Exception as e:
            print(f"❌ Cannot write to {config_file}: {e}")
            return False

        # Verify installation succeeded
        content = config_file.read_text()
        if "tlnr Integration" not in content:
            print("❌ Installation verification failed!")
            print("   The integration code was not written correctly.")
            return False

        # Auto-restart daemon (which triggers background download)
        try:
            from .daemon import TerminalTutorDaemon
            daemon = TerminalTutorDaemon()
            if daemon.is_running():
                daemon.stop()
            daemon.start()
        except Exception as e:
            # Non-fatal: daemon is optional for basic functionality
            print(f"⚠️  Daemon not started: {e}")
            print("   Predictions will still work, but may be slower.")

        print("✅ TLNR installed successfully!")
        print(f"Run 'source {config_file}' to activate TLNR")
        print("")
        return True



    def install_local_llm_deps(self, silent: bool = False) -> bool:
        """Install dependencies for Local LLM features."""
        try:
            import subprocess
            
            if not silent:
                print("   🔨 Installing missing AI dependencies (this may take a moment)...")
            
            # Try standard install first (silent)
            cmd = [sys.executable, "-m", "pip", "install", "llama-cpp-python", "huggingface-hub"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            
            # Check for externally managed environment error
            if "externally-managed-environment" in result.stderr:
                cmd.append("--break-system-packages")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True
            
            # Only print on FAILURE
            if not silent:
                print(f"❌ Dependency install failed: {result.returncode}")
                if result.stderr:
                    print(f"   {result.stderr.strip()}")
            return False

        except Exception as e:
            if not silent:
                print(f"❌ Setup error: {e}")
            return False

    def uninstall(self):
        """Uninstall shell integration and clean up all tlnr files."""
        # Step 0: Stop daemon if running
        try:
            from .daemon import TerminalTutorDaemon
            daemon = TerminalTutorDaemon()
            if daemon.is_running():
                print("🛑 Stopping daemon...")
                daemon.stop()
                # Give daemon time to fully stop and release resources
                import time
                time.sleep(0.5)
        except Exception:
            pass  # Daemon module might not be available

        # Step 1: Remove shell integration
        config_file = self.get_shell_config_file()

        if not config_file.exists():
            print("❌ No shell configuration file found.")
        else:
            content = config_file.read_text()

            # Remove integration code
            lines = content.split('\n')
            filtered_lines = []
            skip = False

            for line in lines:
                if "tlnr Integration - Start" in line:
                    skip = True
                    continue
                elif "tlnr Integration - End" in line:
                    skip = False
                    continue

                if not skip:
                    filtered_lines.append(line)

            # Write back the filtered content
            config_file.write_text('\n'.join(filtered_lines))

        # Step 2: Remove all data files and directories
        files_to_remove = [
            self.home / '.config' / 'tlnr',
            self.home / '.tlnr',  # Config directory (core.py ConfigurationManager)
            self.home / '.tlnr_openai_key',
            self.home / '.tlnr_mode',
            self.home / '.tlnr_auto_detect',
            self.home / '.tlnr_usage',
            self.home / '.tlnr_premium',
            self.home / '.tlnr_custom_commands.json',
            self.home / '.tlnr_token',
            self.home / '.tlnr_local_history',  # Command history (zsh_integration)
            self.home / '.terminal_tutor',  # LLM models directory (~650MB)
            self.home / '.terminal_tutor_local_history',  # Old history file name
            self.home / '.terminal_tutor_openai_key',  # Old API key file name
            Path('/tmp') / 'tt_disabled',
        ]

        removed_count = 0
        failed_files = []
        for file_path in files_to_remove:
            try:
                if file_path.exists():
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                        removed_count += 1
                    else:
                        file_path.unlink()
                        removed_count += 1
            except Exception as e:
                # Track files that couldn't be removed
                failed_files.append((file_path.name, str(e)))

        # Step 3: Force cleanup of daemon socket/pid (may have been recreated)
        for socket_file in [self.home / '.tlnr.sock', self.home / '.tlnr.pid']:
            try:
                if socket_file.exists():
                    socket_file.unlink()
                    removed_count += 1
            except Exception as e:
                failed_files.append((socket_file.name, str(e)))

        print("✅ TLNR shell integration removed!")
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} file(s) and directory(ies)")
        if failed_files:
            print(f"⚠️  Could not remove {len(failed_files)} file(s):")
            for filename, error in failed_files:
                print(f"   - {filename}: {error}")
            print("💡 Run manual cleanup: see docs/TROUBLESHOOTING.md")
        print("")
        print("📦 To fully remove TLNR, also run:")
        print("   pipx uninstall tlnr")
        print("")
        print("🔄 Restart your terminal: exec zsh")