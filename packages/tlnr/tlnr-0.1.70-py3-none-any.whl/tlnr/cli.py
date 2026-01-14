"""Command line interface for tlnr."""

import argparse
import os
import sys
import time
from pathlib import Path
from tlnr.core import CommandTutor

from tlnr.diagnostics import run_diagnostics
from tlnr.installer import ShellInstaller


# Lazy import for OpenAIKeyManager (only needed for config commands)
_openai_key_manager = None

def _get_openai_key_manager():
    """Lazy load OpenAI key manager."""
    global _openai_key_manager
    if _openai_key_manager is None:
        from .openai_manager import OpenAIKeyManager
        _openai_key_manager = OpenAIKeyManager
    return _openai_key_manager


def format_output(command: str, description: str, risk_level: str) -> str:
    """Format the command description output - lightning fast format with emoji indicators."""
    # Keep the full risk level with symbol (● SAFE, ▲ CAUTION, ✗ DANGEROUS)
    risk_display = risk_level if risk_level else "❓ UNKNOWN"
    return f"{risk_display} {command} - {description}"


def debug_command(command: str):
    """Debug command with timing and stats."""
    start_time = time.perf_counter()
    tutor = CommandTutor()

    # Get fuzzy suggestions first (always shows top 3 if available)
    suggestions = tutor.get_fuzzy_suggestions(command, max_results=3)

    # Check if there's an exact match
    exact_match = tutor.get_description(command)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000

    if suggestions and len(suggestions) > 1:
        # Multiple matches - show all as fuzzy
        print("───────────────────────────────────")
        for suggestion in suggestions:
            risk_level = suggestion['risk_level']
            cmd = suggestion['command']
            desc = suggestion['description']
            print(f"{risk_level} {cmd} - {desc}")
        print("───────────────────────────────────")
        match_type = "🎯 exact (+ related)" if exact_match else "🔍 fuzzy"
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 {len(suggestions)} matches | {match_type}")
    elif exact_match and len(suggestions) == 1:
        # Single exact match only - use matched command from suggestion for risk level
        suggestion = suggestions[0]
        matched_command = suggestion['command']
        risk_level = tutor.get_risk_level(matched_command)
        print("───────────────────────────────────")
        print(format_output(command, exact_match, risk_level))
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 1 match | 🎯 exact")
    elif suggestions and len(suggestions) == 1:
        # Single fuzzy match
        suggestion = suggestions[0]
        print("───────────────────────────────────")
        print(f"{suggestion['risk_level']} {suggestion['command']} - {suggestion['description']}")
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 1 match | 🔍 fuzzy")
    else:
        # No matches
        print("───────────────────────────────────")
        print(f"❓ No matches found for '{command}'")
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 0 matches")





def install_shell_hooks():
    """Install shell hooks for automatic command explanation."""
    installer = ShellInstaller()
    installer.install()


def uninstall_shell_hooks():
    """Uninstall shell hooks."""
    installer = ShellInstaller()
    installer.uninstall()


def live_command(action: str):
    """Manage real-time prediction status."""
    disable_file = "/tmp/tt_disabled"
    
    if action == "on":
        if os.path.exists(disable_file):
            os.remove(disable_file)
        print("🟢 Live predictions ON")
        
    elif action == "off":
        with open(disable_file, 'w') as f:
            f.write("disabled")
        print("🔴 Live predictions OFF")
        
    elif action == "status":
        if os.path.exists(disable_file):
            print("🔴 Live predictions: OFF")
        else:
            print("🟢 Live predictions: ON")


def show_history(limit: int = 20):
    """Show recent command history."""
    tutor = CommandTutor()
    history = tutor.history_manager.get_history(limit)
    
    if not history:
        print("No history record found.")
        print("   Commands are logged to ~/.terminal_tutor_local_history")
        return
        
    print(f"Recent History (last {len(history)}):")
    for entry in history:
        print(f"  {entry['time_str']}  {entry['command']}")


def show_stats():
    """Show usage statistics."""
    tutor = CommandTutor()
    stats = tutor.history_manager.get_stats()
    
    if stats['total_commands'] == 0:
        print("📊 No usage data available yet.")
        return
        
    print("📊 Terminal Usage Statistics")
    print(f"  Total Commands: {stats['total_commands']}")
    
    print("\n🏆 Top Commands:")
    for cmd, count in stats['top_commands']:
        print(f"  {cmd:<15} {count}")
        
    print("\n⏰ Busy Hours:")
    for hour, count in stats['busy_hours']:
        # Format 13 -> 1pm, 0 -> 12am
        time_suffix = "am" if hour < 12 else "pm"
        hour_12 = hour if hour <= 12 else hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        print(f"  {hour_12}{time_suffix:<2}        {count} commands")


def manage_config(action: str, config_type: str):
    """Manage configuration settings."""
    if config_type == 'api-key':
        key_manager = OpenAIKeyManager()

        if action == 'set':
            # Force prompt for new API key
            import getpass
            print("🔑 Enter your OpenAI API key")
            print("🔗 Get one here: https://platform.openai.com/api-keys\n")

            try:
                key = getpass.getpass("Enter your OpenAI API key (input hidden): ")
                key = key.strip()

                if not key:
                    print("❌ No key entered. Cancelled.")
                    return

                print("✅ Testing API key...", end=" ", flush=True)
                if key_manager._validate_key(key):
                    print("Valid!")
                    key_manager._save_key(key)
                else:
                    print("❌ Invalid!")
                    print("❌ API key validation failed. Please check your key and try again.")

            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled by user.")

        elif action == 'clear':
            key_manager.clear_key()

        elif action == 'status':
            if key_manager.key_file.exists():
                # Try to validate the stored key
                stored_key = key_manager._load_key_from_file()
                if stored_key:
                    print(f"🔑 API key stored at: {key_manager.key_file}")
                    print("✅ Testing stored key...", end=" ", flush=True)
                    if key_manager._validate_key(stored_key):
                        print("Valid!")
                    else:
                        print("❌ Invalid!")
                        print("💡 Run 'tlnr config api-key set' to update")
                else:
                    print(f"⚠️  Key file exists but is empty: {key_manager.key_file}")
                print("ℹ️  No API key configured")
                print("💡 Run 'tlnr config api-key set' to configure")


def _setup_local_provider(tutor):
    """Helper to configure local provider and trigger download."""
    tutor.config_manager.set_provider('local')
    print("✅ Provider set to: local")
    
    # Trigger download if needed
    try:
        # Lazy import to avoid loading heavy deps if not needed
        from .local_llm import LocalLLMManager
        manager = LocalLLMManager()
        if not manager.is_model_downloaded():
            print("\n📦 Local model not found. Downloading now...")
            if manager.download_model():
                print("✨ Setup complete! You can now use 'tlnr how' offline.")
            else:
                print("⚠️  Download failed. Please check your internet connection.")
                print("   You can retry by running this command again.")
        else:
            print("✨ Local model is already installed and ready.")
    except ImportError:
        print("\n⚠️  Local LLM dependencies not installed.")
        print("   Run: pip install tlnr[local-llm]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="tlnr - Command Education Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')



    # Predict command (for predictions)
    predict_parser = subparsers.add_parser('predict', help='Get command prediction (optimized for speed)')
    predict_parser.add_argument('cmd', nargs='+', help='Command to predict')
    predict_parser.add_argument('--fast', action='store_true', help='Ultra-fast prediction mode (default)')
    predict_parser.add_argument('--realtime', action='store_true', help='Legacy alias for --fast')

    # Install command
    install_parser = subparsers.add_parser('install', help='Install shell integration')

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall shell integration')

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version')

    # Live command (replaces enable/disable)
    live_parser = subparsers.add_parser('live', help='Manage real-time predictions')
    live_parser.add_argument('action', choices=['on', 'off', 'status'], help='Live mode action')
    
    # Local shortcut command
    local_parser = subparsers.add_parser('local', help='Switch to Local LLM provider (offline mode)')

    # Activate command (Commercial)
    activate_parser = subparsers.add_parser('activate', help='Activate a commercial license')
    activate_parser.add_argument('key', help='License key (TT-XXXX-XXXX-XXXX)')

    # How command (natural language command search)
    how_parser = subparsers.add_parser('how', help='Natural language command search (e.g. "how to list files")')
    how_parser.add_argument('query', nargs='+', help='Natural language query')
    how_parser.add_argument('--time', '-t', action='store_true', help='Show performance metrics')
    
    # Explain command (command explanation using Local LLM)
    explain_parser = subparsers.add_parser('explain', help='Explain a command using Local LLM')
    explain_parser.add_argument('cmd', nargs='+', help='Command to explain (e.g. "find . -name *.py")')

    # Debug command (unified command with timing and stats)
    debug_parser = subparsers.add_parser('debug', help='Debug command lookup with timing and stats')
    debug_parser.add_argument('cmd', nargs='+', help='Command to debug')

    # Diagnose command (installation diagnostics)
    diagnose_parser = subparsers.add_parser('diagnose', help='Run automated installation diagnostics')
    diagnose_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Show detailed diagnostic information')

    # Mode command (mode management)
    mode_parser = subparsers.add_parser('mode', help='Manage command modes for context-aware filtering')
    mode_subparsers = mode_parser.add_subparsers(dest='mode_action', help='Mode actions')

    # Mode list subcommand
    mode_list_parser = mode_subparsers.add_parser('list', help='List available modes')

    # Mode current subcommand
    mode_current_parser = mode_subparsers.add_parser('current', help='Show current mode')

    # Mode set subcommand
    mode_set_parser = mode_subparsers.add_parser('set', help='Set current mode')
    mode_set_parser.add_argument('mode_name', help='Mode to set (full, aws, docker, k8s, git)')

    # Mode auto subcommand
    mode_auto_parser = mode_subparsers.add_parser('auto', help='Manage auto-detection')
    mode_auto_parser.add_argument('action', choices=['enable', 'disable', 'status'],
                                 help='Auto-detection action')

    # Config command (configuration management)
    config_parser = subparsers.add_parser('config', help='Manage tlnr configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_type', help='Configuration type')

    # Config api-key subcommand
    config_apikey_parser = config_subparsers.add_parser('api-key', help='Manage OpenAI API key')
    config_apikey_parser.add_argument('action', choices=['set', 'clear', 'status'],
                                     help='API key action: set (configure new key), clear (remove key), status (check key)')

    # Config provider subcommand
    config_provider_parser = config_subparsers.add_parser('provider', help='Manage AI Provider (openai vs local)')
    config_provider_parser.add_argument('action', choices=['set', 'status'], help='Provider action')
    config_provider_parser.add_argument('value', nargs='?', choices=['openai', 'local'], help='Provider value (for set action)')

    # Daemon command (performance optimization - eliminates Python startup overhead)
    daemon_parser = subparsers.add_parser('daemon', help='Manage tlnr daemon for faster predictions')
    daemon_parser.add_argument('action', nargs='?', default='status',
                              choices=['start', 'stop', 'status', 'restart', 'foreground'],
                              help='Daemon action: start, stop, status, restart, or foreground (for debugging)')

    # History command
    history_parser = subparsers.add_parser('history', help='View recent command history')
    history_parser.add_argument('--limit', '-n', type=int, default=20, help='Number of entries to show')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='View command usage statistics')



    args = parser.parse_args()



    if args.command == 'predict':
        command = " ".join(args.cmd)

        # Try daemon first (fast path: <5ms)
        from .daemon import is_daemon_running, query_daemon
        if is_daemon_running():
            description = query_daemon(command)
            if description:
                print(description)
                return
            # Fall through if daemon returns empty (error case)

        # Fallback: create CommandTutor instance (slower: ~50ms)
        tutor = CommandTutor()

        # Get description (no rate limit anymore)
        description = tutor.get_description_realtime(command)
        usage_info = {"is_allowed": True} # Mock for compatibility if needed, or remove usage_info check

        if description:
            # For multi-line descriptions (fuzzy suggestions), print directly
            if '\n' in description:
                print(description)
            else:
                # For single descriptions that already include risk level, print directly
                if description.startswith(('● SAFE', '▲ CAUTION', '✗ DANGEROUS')):
                    print(description)
                else:
                    # Single line descriptions without risk level get the standard format
                    risk_level = tutor.get_risk_level(command)
                    print(format_output(command, description, risk_level))

        # For no description found, stay silent (real-time predictions)

    elif args.command == 'install':
        install_shell_hooks()
        # Auto-start daemon for fastest real-time predictions
        from .daemon import TerminalTutorDaemon
        daemon = TerminalTutorDaemon()
        if not daemon.is_running():
            #print("\n🚀 Starting daemon for instant predictions...")
            if daemon.start(foreground=False):
                print("✅ Installation successful")
                #print("✅ Daemon started - predictions will be lightning fast!")
            else:
                print("⚠️  Installation failed. Please try again")

    elif args.command == 'uninstall':
        uninstall_shell_hooks()

    elif args.command == 'version':
        from . import __version__
        print(f"tlnr v{__version__}")

    elif args.command == 'live':
        live_command(args.action)

    elif args.command == 'local':

        tutor = CommandTutor()
        _setup_local_provider(tutor)

    elif args.command == 'activate':
        try:
            from .licensing import LicenseManager
            manager = LicenseManager()
            success, message = manager.activate(args.key)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ Activation failed: {message}")
                sys.exit(1)
        except ImportError:
            print("❌ Feature not available. Please reinstall with correct dependencies.")
            print("   pip install 'tlnr[local-llm]'") # crypto is core now but good fallback msg

    elif args.command == 'how':

        query = " ".join(args.query)
        tutor = CommandTutor()
        
        start_time = time.perf_counter()
        result = tutor.natural_language_search(query)
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        if result:
            command = result['command']
            risk_level = result['risk_level']
            description = result['description']
            
            # Message Mode (Refusals/Conversational)
            if not command:
                print(description)
            # Standard Command Mode - UPDATED FORMAT: {Risk} {Command} - {Description}
            else:
                print(f"{risk_level} {command} - {description}")

            if args.time:
                print(f"⏱️  Time: {elapsed_ms:.1f}ms")
        else:
            # Only show error if setup is NOT in progress
            if not tutor.is_setup_in_progress():
                 print(f"Please enter a simple clear prompt or break it down into multiple prompts and try again")
            #print(f"❓ Could not find a command for: '{query}'")
            #print("💡 Try: 'terminal-tutor debug <partial_command>' for fuzzy matching")

    elif args.command == 'explain':
        tutor = CommandTutor()
        command = " ".join(args.cmd)
        print(f"🤔 Explaining: {command} ...")
        explanation = tutor.explain_command(command)
        if explanation:
            print("\n" + explanation)
        else:
            print("❌ Could not explain command.")

    elif args.command == 'debug':
        command = " ".join(args.cmd)
        debug_command(command)

    elif args.command == 'diagnose':
        report, success = run_diagnostics(verbose=args.verbose)
        print(report)
        sys.exit(0 if success else 1)

    elif args.command == 'mode':
        tutor = CommandTutor()
        mode_manager = tutor.mode_manager

        if args.mode_action == 'list':
            print("📋 Available Modes:")
            modes = mode_manager.list_modes()
            current_mode = mode_manager.get_effective_mode()

            for mode_name, description in modes.items():
                indicator = "👉" if mode_name == current_mode else "  "
                print(f"{indicator} {mode_name}: {description}")

            if mode_manager.auto_detect_enabled:
                print(f"\n🤖 Auto-detection: Enabled (effective mode: {current_mode})")
            else:
                print(f"\n🤖 Auto-detection: Disabled")

        elif args.mode_action == 'current':
            current_mode = mode_manager.current_mode
            effective_mode = mode_manager.get_effective_mode()

            if mode_manager.auto_detect_enabled and current_mode != effective_mode:
                print(f"📌 Set mode: {current_mode}")
                print(f"🤖 Auto-detected mode: {effective_mode}")
                print(f"✅ Effective mode: {effective_mode}")
            else:
                print(f"✅ Current mode: {current_mode}")

        elif args.mode_action == 'set':
            mode_name = args.mode_name
            if mode_manager.set_mode(mode_name):
                print(f"✅ Mode set to: {mode_name}")
                config = mode_manager.mode_configs.get(mode_name, {})
                if config.get("suppress_commands"):
                    print(f"🚫 Suppressed: {', '.join(config['suppress_commands'])}")
            else:
                print(f"❌ Invalid mode: {mode_name}")
                print("💡 Use 'tlnr mode list' to see available modes")

        elif args.mode_action == 'auto':
            action = args.action
            if action == 'enable':
                mode_manager.enable_auto_detect()
                print("🤖 Auto-detection enabled")
                detected_mode = mode_manager.detect_project_context()
                if detected_mode != "full":
                    print(f"📍 Detected context: {detected_mode} mode")
                else:
                    print("📍 No specific context detected, using full mode")

            elif action == 'disable':
                mode_manager.disable_auto_detect()
                print("🔒 Auto-detection disabled")
                print(f"📌 Using manual mode: {mode_manager.current_mode}")

            elif action == 'status':
                if mode_manager.auto_detect_enabled:
                    print("🤖 Auto-detection: Enabled")
                    detected_mode = mode_manager.detect_project_context()
                    print(f"📍 Current context: {detected_mode} mode")
                else:
                    print("🔒 Auto-detection: Disabled")
        else:
            print("Usage: tlnr mode {list,current,set,auto}")

    elif args.command == 'config':
        if args.config_type == 'api-key':
            manage_config(args.action, 'api-key')
        elif args.config_type == 'provider':

            tutor = CommandTutor()
            
            if args.action == 'set':
                value = args.value
                if value == 'local':
                    _setup_local_provider(tutor)
                else:
                    tutor.config_manager.set_provider(value)
                    print(f"✅ Provider set to: {value}")
                        
            elif args.action == 'status':
                provider = tutor.config_manager.get_provider()
                print(f"🤖 Current AI Provider: {provider}")
                
                if provider == 'local':
                    try:
                        from .local_llm import LocalLLMManager
                        manager = LocalLLMManager()
                        if manager.is_model_downloaded():
                            print("   ✅ Model installed: Qwen 2.5 0.5B")
                        else:
                            print("   ❌ Model missing. Run 'tlnr local' to download.")
                    except ImportError:
                        print("   ❌ Dependencies missing (pip install tlnr[local-llm])")

    elif args.command == 'daemon':
        from .daemon import TerminalTutorDaemon
        daemon = TerminalTutorDaemon()

        if args.action == 'start':
            print("🚀 Starting tlnr daemon...")
            print("   This eliminates Python startup overhead for ~25-50x faster predictions.")
            if daemon.start(foreground=False):
                print("✅ Daemon started successfully!")
                print("   Predictions will now use Unix socket for <5ms response time.")
            else:
                print("❌ Failed to start daemon.")
                sys.exit(1)

        elif args.action == 'stop':
            print("🛑 Stopping tlnr daemon...")
            if daemon.stop():
                print("✅ Daemon stopped.")
            else:
                sys.exit(1)

        elif args.action == 'restart':
            print("🔄 Restarting tlnr daemon...")
            daemon.stop()
            time.sleep(0.5)
            if daemon.start(foreground=False):
                print("✅ Daemon restarted successfully!")
            else:
                print("❌ Failed to restart daemon.")
                sys.exit(1)

        elif args.action == 'foreground':
            print("🔧 Starting daemon in foreground (for debugging)...")
            daemon.start(foreground=True)

        else:  # status (default)
            if daemon.is_running():
                pid = daemon.get_pid()
                print(f"✅ Daemon is running (PID: {pid})")
                print(f"   Socket: ~/.terminal-tutor.sock")
                print(f"   Predictions use Unix socket for <5ms response time.")
            else:
                print("⚪ Daemon is not running.")
                print("   Start with: tlnr daemon start")
                print("   Without daemon, predictions use subprocess (~50-100ms).")

    elif args.command == 'history':
        show_history(args.limit)

    elif args.command == 'stats':
        show_stats()



    else:
        parser.print_help()


if __name__ == "__main__":
    main()