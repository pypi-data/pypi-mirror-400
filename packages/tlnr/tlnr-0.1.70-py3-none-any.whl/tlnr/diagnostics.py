#!/usr/bin/env python3
"""
Terminal Tutor Diagnostic System
Automated diagnostics for installation and configuration issues.
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .daemon import query_daemon, is_daemon_running, SOCKET_PATH, PID_FILE


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    name: str
    passed: bool
    message: str
    fix_suggestions: List[str]
    details: Optional[str] = None


class SystemDiagnostics:
    """Automated diagnostic system for tlnr installation"""

    # Expected ZLE widgets
    EXPECTED_WIDGETS = [
        'tt_predict_realtime',
        'tt_cleanup_on_accept',
        'tt_handle_backward_delete',
        'tt_handle_cancel',
        'tt_self_insert_and_predict'
    ]

    # Expected keybindings
    EXPECTED_KEYBINDINGS = [
        ('^M', 'tt_cleanup_on_accept'),      # Enter
        ('^?', 'tt_handle_backward_delete'),  # Backspace
        ('^C', 'tt_handle_cancel'),           # Ctrl+C
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[DiagnosticResult] = []
        self.current_shell_has_widgets = False  # Track current shell state

    def run_all_diagnostics(self) -> List[DiagnosticResult]:
        """Run all diagnostic checks"""
        self.results = []

        # Run checks in order
        self.results.append(self.check_shell())
        self.results.append(self.check_installation())
        self.results.append(self.check_terminal_tutor_command())
        self.results.append(self.check_zle_widgets())
        self.results.append(self.check_keybindings())
        self.results.append(self.check_functional())
        self.results.append(self.check_performance())
        self.results.append(self.check_daemon_status())
        self.results.append(self.check_daemon_performance())

        return self.results

    def check_shell(self) -> DiagnosticResult:
        """Check if current shell is Zsh"""
        # Try multiple methods to detect shell
        shell = os.environ.get('SHELL', '')

        # If SHELL not set, try detecting from parent process
        if not shell or 'zsh' not in shell.lower():
            try:
                result = subprocess.run(
                    ['ps', '-p', str(os.getppid()), '-o', 'comm='],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                parent_shell = result.stdout.strip()
                if parent_shell:
                    shell = parent_shell
            except:
                pass

        # If still not found, check ZSH_VERSION env var
        if not shell or 'zsh' not in shell.lower():
            if os.environ.get('ZSH_VERSION'):
                shell = 'zsh'

        if 'zsh' in shell.lower():
            return DiagnosticResult(
                name="Shell Check",
                passed=True,
                message="Using Zsh (real-time predictions supported)",
                fix_suggestions=[],
                details=f"Shell: {shell}"
            )
        else:
            return DiagnosticResult(
                name="Shell Check",
                passed=False,
                message=f"Using {shell} (Zsh required for real-time predictions)",
                fix_suggestions=[
                    "Switch to Zsh: zsh",
                    "Install tlnr in Zsh: tlnr install",
                    "Note: Bash/Fish only support manual predictions"
                ],
                details=f"Current shell: {shell}"
            )

    def check_installation(self) -> DiagnosticResult:
        """Check if integration is added to shell config"""
        config_file = Path.home() / '.zshrc'

        if not config_file.exists():
            return DiagnosticResult(
                name="Installation Check",
                passed=False,
                message=".zshrc not found",
                fix_suggestions=[
                    "Create .zshrc: touch ~/.zshrc",
                    "Run installation: tlnr install"
                ]
            )

        content = config_file.read_text()

        # Check for integration markers (both old and new format, case insensitive)
        content_lower = content.lower()
        zsh_marker_lower = "# tlnr integration - start"
        bash_marker_lower = "# terminal tutor integration - start"

        has_zsh_markers = zsh_marker_lower in content_lower
        has_bash_markers = bash_marker_lower in content_lower
        
        if has_zsh_markers or has_bash_markers:
            return DiagnosticResult(
                name="Installation Check",
                passed=True,
                message="Integration found in ~/.zshrc",
                fix_suggestions=[],
                details="Integration markers found"
            )
        else:
            return DiagnosticResult(
                name="Installation Check",
                passed=False,
                message="Integration markers not found in ~/.zshrc",
                fix_suggestions=[
                    "Run installation: tlnr install",
                    "If already installed, try: tlnr install --force"
                ]
            )

    def check_terminal_tutor_command(self) -> DiagnosticResult:
        """Check if tlnr command is accessible"""
        try:
            result = subprocess.run(
                ['which', 'tlnr'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                path = result.stdout.strip()
                return DiagnosticResult(
                    name="Command Check",
                    passed=True,
                    message="tlnr command found in PATH",
                    fix_suggestions=[],
                    details=f"Location: {path}"
                )
            else:
                return DiagnosticResult(
                    name="Command Check",
                    passed=False,
                    message="tlnr command not found",
                    fix_suggestions=[
                        "Reinstall: pip install tlnr",
                        "Or with pipx: pipx install tlnr",
                        "Check PATH: echo $PATH"
                    ]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Command Check",
                passed=False,
                message=f"Error checking command: {str(e)}",
                fix_suggestions=["Reinstall tlnr"]
            )

    def check_zle_widgets(self) -> DiagnosticResult:
        """Check if ZLE widgets are registered"""
        try:
            # Check current shell first (non-interactive check)
            try:
                current_result = subprocess.run(
                    ['zle', '-la'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    shell=False
                )
                current_widgets = current_result.stdout if current_result.returncode == 0 else ""
                self.current_shell_has_widgets = any(w in current_widgets for w in self.EXPECTED_WIDGETS)
            except:
                self.current_shell_has_widgets = False

            # Run zle -la in interactive Zsh to list widgets (test what WILL work after restart)
            result = subprocess.run(
                ['zsh', '-i', '-c', 'zle -la | grep tt_'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # grep returns 0 if found, 1 if not found. Both are valid executions.
            # Only >1 is an error.
            if result.returncode <= 1:
                widgets = result.stdout.strip().split('\n')
                widgets = [w.strip() for w in widgets if w.strip()]

                # Check which expected widgets are present
                found_widgets = [w for w in self.EXPECTED_WIDGETS if w in widgets]
                missing_widgets = [w for w in self.EXPECTED_WIDGETS if w not in widgets]

                if len(found_widgets) == len(self.EXPECTED_WIDGETS):
                    return DiagnosticResult(
                        name="ZLE Widgets",
                        passed=True,
                        message=f"All {len(found_widgets)}/5 widgets registered",
                        fix_suggestions=[],
                        details=f"Widgets: {', '.join(found_widgets)}"
                    )
                elif len(found_widgets) > 0:
                    return DiagnosticResult(
                        name="ZLE Widgets",
                        passed=False,
                        message=f"Partial widgets registered ({len(found_widgets)}/5)",
                        fix_suggestions=[
                            "Restart shell: exec zsh",
                            "If issue persists: tlnr install --force",
                            f"Missing widgets: {', '.join(missing_widgets)}"
                        ],
                        details=f"Found: {', '.join(found_widgets)}"
                    )
                else:
                    return DiagnosticResult(
                        name="ZLE Widgets",
                        passed=False,
                        message="No ZLE widgets registered (0/5)",
                        fix_suggestions=[
                            "1. Restart shell: exec zsh",
                            "2. Source config manually: source ~/.zshrc",
                            "3. If still broken, reinstall: tlnr install --force"
                        ]
                    )
            else:
                return DiagnosticResult(
                    name="ZLE Widgets",
                    passed=False,
                    message="Unable to check ZLE widgets",
                    fix_suggestions=[
                        "Ensure you're running in Zsh: zsh",
                        "Try restarting shell: exec zsh"
                    ]
                )
        except subprocess.TimeoutExpired:
            return DiagnosticResult(
                name="ZLE Widgets",
                passed=False,
                message="Timeout checking ZLE widgets",
                fix_suggestions=["Zsh may be hanging, check your .zshrc for errors"]
            )
        except Exception as e:
            return DiagnosticResult(
                name="ZLE Widgets",
                passed=False,
                message=f"Error: {str(e)}",
                fix_suggestions=["Check Zsh installation and configuration"]
            )

    def check_keybindings(self) -> DiagnosticResult:
        """Check if keybindings are set"""
        try:
            # Run bindkey in interactive Zsh
            result = subprocess.run(
                ['zsh', '-i', '-c', 'bindkey | grep tt_'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode <= 1:
                bindings = result.stdout.strip()
                
                # Filter out empty lines if grep returned nothing (exit code 1)
                binding_lines = [b for b in bindings.split('\n') if b.strip()]

                if binding_lines:
                    return DiagnosticResult(
                        name="Keybindings",
                        passed=True,
                        message=f"{len(binding_lines)} keybindings set",
                        fix_suggestions=[],
                        details=bindings if self.verbose else f"{len(binding_lines)} bindings"
                    )
                else:
                    return DiagnosticResult(
                        name="Keybindings",
                        passed=False,
                        message="No keybindings found",
                        fix_suggestions=[
                            "ZLE widgets may not be loaded",
                            "Restart shell: exec zsh"
                        ]
                    )
            else:
                return DiagnosticResult(
                    name="Keybindings",
                    passed=False,
                    message="Unable to check keybindings",
                    fix_suggestions=["Ensure Zsh is running: zsh"]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Keybindings",
                passed=False,
                message=f"Error: {str(e)}",
                fix_suggestions=["Check Zsh configuration"]
            )

    def check_functional(self) -> DiagnosticResult:
        """Check if predict command works"""
        try:
            result = subprocess.run(
                ['tlnr', 'predict', 'git status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                return DiagnosticResult(
                    name="Functional Test",
                    passed=True,
                    message="Predict command working",
                    fix_suggestions=[],
                    details=output[:100] if self.verbose else "Command returns output"
                )
            else:
                return DiagnosticResult(
                    name="Functional Test",
                    passed=False,
                    message="Predict command failed or returned no output",
                    fix_suggestions=[
                        "Check command database: ls -lh ~/.local/share/terminal_tutor/commands.json",
                        "Reinstall: pip install --force-reinstall tlnr"
                    ]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Functional Test",
                passed=False,
                message=f"Error: {str(e)}",
                fix_suggestions=["Check tlnr installation"]
            )

    def check_performance(self) -> DiagnosticResult:
        """Check prediction performance (<50ms target)"""
        try:
            start = time.perf_counter()
            result = subprocess.run(
                ['tlnr', 'predict', 'git status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            if result.returncode == 0:
                target_ms = 50
                if elapsed_ms < target_ms:
                    percentage_under = ((target_ms - elapsed_ms) / target_ms) * 100
                    return DiagnosticResult(
                        name="Performance",
                        passed=True,
                        message=f"{elapsed_ms:.1f}ms ({percentage_under:.0f}% under target)",
                        fix_suggestions=[],
                        details=f"Target: <{target_ms}ms"
                    )
                else:
                    return DiagnosticResult(
                        name="Performance",
                        passed=False,
                        message=f"{elapsed_ms:.1f}ms (exceeds {target_ms}ms target)",
                        fix_suggestions=[
                            "Performance degraded, check system resources",
                            "Large command database may impact speed"
                        ],
                        details=f"Target: <{target_ms}ms"
                    )
            else:
                return DiagnosticResult(
                    name="Performance",
                    passed=False,
                    message="Unable to measure performance (command failed)",
                    fix_suggestions=["Fix functional test first"]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Performance",
                passed=False,
                message=f"Error: {str(e)}",
                fix_suggestions=["Check system performance"]
            )

    def check_daemon_status(self) -> DiagnosticResult:
        """Check if the daemon is running for instant predictions."""
        try:
            if is_daemon_running():
                # Get PID for details
                pid = None
                if PID_FILE.exists():
                    try:
                        pid = int(PID_FILE.read_text().strip())
                    except (ValueError, OSError):
                        pass

                return DiagnosticResult(
                    name="Daemon Status",
                    passed=True,
                    message="Daemon running (instant predictions enabled)",
                    fix_suggestions=[],
                    details=f"PID: {pid}, Socket: {SOCKET_PATH}" if pid else f"Socket: {SOCKET_PATH}"
                )
            else:
                return DiagnosticResult(
                    name="Daemon Status",
                    passed=False,
                    message="Daemon not running (slower predictions)",
                    fix_suggestions=[
                        "Start daemon: tlnr daemon start",
                        "Daemon provides <5ms predictions vs ~50ms without",
                        "Daemon auto-starts on shell init after 'tlnr install'"
                    ]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Daemon Status",
                passed=False,
                message=f"Error checking daemon: {str(e)}",
                fix_suggestions=["Try: tlnr daemon status"]
            )

    def check_daemon_performance(self) -> DiagnosticResult:
        """Check daemon response time (<5ms target)."""
        if not is_daemon_running():
            return DiagnosticResult(
                name="Daemon Performance",
                passed=False,
                message="Skipped (daemon not running)",
                fix_suggestions=["Start daemon first: tlnr daemon start"]
            )

        try:
            # Measure daemon response time
            test_command = "git status"
            start = time.perf_counter()
            response = query_daemon(test_command, timeout=2.0)
            daemon_ms = (time.perf_counter() - start) * 1000

            if not response:
                return DiagnosticResult(
                    name="Daemon Performance",
                    passed=False,
                    message="Daemon returned empty response",
                    fix_suggestions=[
                        "Restart daemon: tlnr daemon stop && tlnr daemon start",
                        "Check daemon logs if available"
                    ]
                )

            # Target is <5ms for daemon
            target_ms = 5
            if daemon_ms < target_ms:
                return DiagnosticResult(
                    name="Daemon Performance",
                    passed=True,
                    message=f"{daemon_ms:.1f}ms (target <{target_ms}ms)",
                    fix_suggestions=[],
                    details=f"Response: {response[:50]}..." if len(response) > 50 else f"Response: {response}"
                )
            elif daemon_ms < 50:  # Still acceptable but not optimal
                return DiagnosticResult(
                    name="Daemon Performance",
                    passed=True,
                    message=f"{daemon_ms:.1f}ms (acceptable, target <{target_ms}ms)",
                    fix_suggestions=[
                        "Performance slightly degraded",
                        "Consider restarting daemon: tlnr daemon stop && tlnr daemon start"
                    ],
                    details=f"Expected <{target_ms}ms, got {daemon_ms:.1f}ms"
                )
            else:
                return DiagnosticResult(
                    name="Daemon Performance",
                    passed=False,
                    message=f"{daemon_ms:.1f}ms (too slow, target <{target_ms}ms)",
                    fix_suggestions=[
                        "Daemon is not providing expected speedup",
                        "Restart daemon: tlnr daemon stop && tlnr daemon start",
                        "Check system resources"
                    ]
                )
        except Exception as e:
            return DiagnosticResult(
                name="Daemon Performance",
                passed=False,
                message=f"Error: {str(e)}",
                fix_suggestions=["Check daemon status: tlnr daemon status"]
            )

    def generate_report(self) -> str:
        """Generate formatted diagnostic report"""
        if not self.results:
            self.run_all_diagnostics()

        # Header
        lines = []
        lines.append("")
        lines.append("🔍 tlnr Diagnostic Report")
        lines.append("═" * 40)
        lines.append("")

        # Results
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        for result in self.results:
            icon = "✅" if result.passed else "❌"
            lines.append(f"{icon} {result.name}: {result.message}")

            if self.verbose and result.details:
                lines.append(f"   Details: {result.details}")

            lines.append("")

        # Summary
        lines.append("─" * 40)
        lines.append(f"Summary: {passed_count}/{total_count} checks passed")
        lines.append("")

        # Fix suggestions (only for failed checks)
        failed_checks = [r for r in self.results if not r.passed and r.fix_suggestions]
        if failed_checks:
            lines.append("🔧 Recommended Fixes:")
            lines.append("")
            for result in failed_checks:
                lines.append(f"  {result.name}:")
                for i, fix in enumerate(result.fix_suggestions, 1):
                    lines.append(f"    {i}. {fix}")
                lines.append("")

        # Overall status
        if passed_count == total_count:
            # Check if current shell has widgets vs new shell
            if not self.current_shell_has_widgets:
                lines.append("✅ All checks passed in test shell")
                lines.append("⚠️  Current shell needs restart for real-time predictions")
                lines.append("🔄 Run: exec zsh")
            else:
                lines.append("✨ All systems operational! Real-time predictions working now.")
        else:
            lines.append("⚠️  Issues detected. Follow the recommended fixes above.")

        lines.append("")

        return "\n".join(lines)

    def get_overall_status(self) -> bool:
        """Return True if all diagnostics passed"""
        return all(r.passed for r in self.results)


def run_diagnostics(verbose: bool = False) -> Tuple[str, bool]:
    """
    Run all diagnostics and return (report, success)

    Args:
        verbose: Show detailed diagnostic information

    Returns:
        Tuple of (formatted report string, overall success boolean)
    """
    diagnostics = SystemDiagnostics(verbose=verbose)
    diagnostics.run_all_diagnostics()
    report = diagnostics.generate_report()
    success = diagnostics.get_overall_status()

    return report, success


if __name__ == "__main__":
    # Allow running diagnostics directly
    report, success = run_diagnostics(verbose=True)
    print(report)
    sys.exit(0 if success else 1)
