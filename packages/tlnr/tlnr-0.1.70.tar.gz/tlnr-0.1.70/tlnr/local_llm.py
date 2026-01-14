"""Local LLM Manager for tlnr.

Handles downloading required GGUF models and running inference using llama-cpp-python.
All data stays on the user's machine.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Default model configuration (Qwen 2.5 0.5B - Faster & Smarter)
DEFAULT_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
DEFAULT_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"

@contextmanager
def suppress_c_output():
    """Redirect C-level stdout/stderr to /dev/null to silence llama.cpp warnings."""
    with open(os.devnull, "w") as null_file:
        # Save original file descriptors
        original_stdout_fd = os.dup(sys.stdout.fileno())
        original_stderr_fd = os.dup(sys.stderr.fileno())
        
        try:
            # Redirect stdout/stderr to null file
            sys.stdout.flush()
            sys.stderr.flush()
            os.dup2(null_file.fileno(), sys.stdout.fileno())
            os.dup2(null_file.fileno(), sys.stderr.fileno())
            yield
        finally:
            # Restore original file descriptors
            os.dup2(original_stdout_fd, sys.stdout.fileno())
            os.dup2(original_stderr_fd, sys.stderr.fileno())
            os.close(original_stdout_fd)
            os.close(original_stderr_fd)

class LocalLLMManager:
    """Manages local LLM lifecycle: download, load, and inference."""

    def __init__(self):
        self.model_dir = Path.home() / ".terminal_tutor" / "models"
        self.model_path = self.model_dir / DEFAULT_FILENAME
        self._llm = None
        self._ensure_model_dir()

    def _ensure_model_dir(self):
        if not self.model_dir.exists():
            self.model_dir.mkdir(parents=True, exist_ok=True)

    def is_model_downloaded(self) -> bool:
        """Check if the model file exists."""
        return self.model_path.exists() and self.model_path.stat().st_size > 0

    def download_model(self):
        """Download the GGUF model from HuggingFace."""
        
        # Try to import, if fails, auto-heal (silently)
        try:
            import warnings
            # Suppress specific symlink warning from hf_hub_download
            warnings.filterwarnings("ignore", message=".*local_dir_use_symlinks.*")
            from huggingface_hub import hf_hub_download
        except ImportError:
            from .installer import ShellInstaller
            if ShellInstaller().install_local_llm_deps():
                try:
                    from huggingface_hub import hf_hub_download
                except ImportError:
                    print("❌ Setup failed. Please run: pip install terminal-tutor[local-llm]")
                    return False
            else:
                 return False

        print(f"⬇️  Downloading Local LLM ({DEFAULT_FILENAME})...")
        print("   This is a one-time download (~650MB).")
        
        try:
            # Download file directly to our target path
            downloaded_path = hf_hub_download(
                repo_id=DEFAULT_REPO,
                filename=DEFAULT_FILENAME,
                local_dir=str(self.model_dir),
                local_dir_use_symlinks=False
            )
            print(f"✅ Download complete: {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def load_model(self):
        """Load the model into memory (if not already loaded)."""
        if self._llm:
            return True

        if not self.is_model_downloaded():
            return False

        try:
            from llama_cpp import Llama
        except ImportError:
            from .installer import ShellInstaller
            if ShellInstaller().install_local_llm_deps():
                try:
                    from llama_cpp import Llama
                except ImportError:
                     print("❌ Setup failed. Please upgrade: pip install --upgrade terminal-tutor")
                     return False
            else:
                return False

        try:
            # Suppress C++ logging noise
            # We redirect stderr/stdout because the C library writes directly to them
            with suppress_c_output():
                self._llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=2048,
                    verbose=False, 
                    n_threads=os.cpu_count()
                )
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False

    def is_downloading(self) -> bool:
        """Check if model download is in progress."""
        lock_file = Path.home() / ".terminal-tutor.download.lock"
        return lock_file.exists()

    def query(self, user_query: str) -> Optional[str]:
        """
        Run inference to translate natural language to a command.
        
        Args:
            user_query: The user's natural language question.
            
        Returns:
            The predicted command string, or None if failed.
        """
        # Case 1: Active Setup
        if self.is_downloading():
            print("⏳ AI Model is setting up in background... check back in a minute.")
            return None

        # Case 2: Missing Setup -> Trigger Daemon
        if not self._llm and not self.is_model_downloaded():
            print("⏳ Missing AI engine. Starting background setup...")
            try:
                from .daemon import TerminalTutorDaemon
                d = TerminalTutorDaemon()
                if not d.is_running():
                    d.start()
                print("   Check back in a minute.")
            except Exception:
                print("❌ Failed to start setup. Run: terminal-tutor install")
            return None
            
        if not self._llm:
            if not self.load_model():
                return None

        # Use structured chat completion for better reliability
        # This handles the prompt template automatically
        try:
            import json
            
            system_prompt = (
                "You are a strict zsh command expert.\n"
                "INSTRUCTIONS:\n"
                "1. FIRST, check if the request is a valid terminal command or coding task.\n"
                "2. If NO (e.g. cooking, life advice, general knowledge), return command=\"\" and description=\"I can only help with terminal commands\".\n"
                "3. If YES, provide the best zsh command.\n"
                "4. Respond in JSON format with keys: 'command', 'description', 'risk_level'.\n"
                "5. risk_level MUST be one of: 'SAFE', 'CAUTION', 'DANGER'."
            )

            output = self._llm.create_chat_completion(
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {"role": "user", "content": "list files"},
                    {"role": "assistant", "content": "{\"command\": \"ls\", \"description\": \"List directory contents\", \"risk_level\": \"SAFE\"}"},
                    {"role": "user", "content": "bake a cake"},
                    {"role": "assistant", "content": "{\"command\": \"\", \"description\": \"I can only help with terminal commands\", \"risk_level\": \"SAFE\"}"},
                    {"role": "user", "content": "how to be happy"},
                    {"role": "assistant", "content": "{\"command\": \"\", \"description\": \"I can only help with terminal commands\", \"risk_level\": \"SAFE\"}"},
                    {"role": "user", "content": "check disk usage"},
                    {"role": "assistant", "content": "{\"command\": \"df -h\", \"description\": \"Display disk usage statistics\", \"risk_level\": \"SAFE\"}"},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=256, 
                stop=["</s>"],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            content = output['choices'][0]['message']['content'].strip()
            
            # Attempt to parse JSON
            try:
                # Handle potential markdown code blocks
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "")
                
                data = json.loads(content)
                return data # Return the dict directly
            except json.JSONDecodeError:
                # Fallback if model fails JSON constraint
                print(f"⚠️  LLM failed JSON format. Raw: {content}")
                return {
                    "command": content.strip().strip('"'), # Best effort
                    "description": "AI Generated (Parse Fail)",
                    "risk_level": "⚠️  UNVERIFIED"
                }

        except Exception as e:
            print(f"❌ Inference failed: {e}")
            return None

    def explain(self, command: str) -> Optional[str]:
        """
        Explain a complex command using a hybrid style (Summary + Breakdown).
        """
        # Case 1: Active Setup
        lock_file = Path.home() / ".terminal-tutor.download.lock"
        if lock_file.exists():
            print("AI Model is setting up in background... check back in a minute.")
            return None

        # Case 2: Missing Setup -> Trigger Daemon
        if not self._llm and not self.is_model_downloaded():
            print("Missing AI engine. Starting background setup...")
            try:
                from .daemon import TerminalTutorDaemon
                d = TerminalTutorDaemon()
                if not d.is_running():
                    d.start()
                print("   Check back in a minute.")
            except Exception:
                print("❌ Failed to start setup.")
            return None
            
        if not self._llm:
            if not self.load_model():
                return None

        prompt = (
            f"Explain this command: `{command}`\n\n"
            "Provide two parts:\n"
            "1. A simple, one-sentence summary of what it does.\n"
            "2. A bulleted list breaking down each flag/argument.\n\n"
            "Format:\n"
            "**Summary**: <text>\n"
            "**Breakdown**:\n"
            "* `<part>`: <explanation>\n"
        )

        try:
            output = self._llm.create_chat_completion(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful CLI tutor. Be concise, accurate, and educational."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
                temperature=0.7,
            )
            return output['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Explanation failed: {e}")
            return None
