# tlnr

> **too long; no need to read** — Real-time terminal command education

[![License](https://img.shields.io/badge/License-AGPL_v3-blue)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passing-brightgreen)](#performance)
[![Performance](https://img.shields.io/badge/Performance-0.24ms%20avg-blue)](#performance)

**tlnr** (pronounced "tee-el-en-are") gives you instant command explanations as you type — no context switching, no waiting, no interruptions.

## Why tlnr?

The name says it all: **"too long; no need to read"** → `tlnntr` → `tlnr` (the 'nt' is silent, like in "knight")

- **tldr**: "too long; didn't read" — you already stopped to look it up
- **tlnr**: "too long; no need to read" — you never stopped typing

## What Makes tlnr Different?

| Feature | tlnr | tldr | cheat.sh | man pages | explainshell |
|---------|------|------|----------|-----------|--------------|
| **Real-time** | ✅ As you type | ❌ Lookup | ❌ Lookup | ❌ Lookup | ❌ Lookup |
| **Speed** | 0.24ms avg | N/A | >100ms | >50ms | >500ms |
| **Context switching** | ✅ Zero | ❌ Yes | ❌ Yes | ❌ Yes | ❌ Browser |
| **Installation** | `pip install tlnr` | `pip install tldr` | `curl` | Built-in | Web only |
| **Coverage** | 32,000+ commands | 1,000+ | 1,000+ | System-dependent | Limited |

**The difference:** Every other tool makes you stop typing. tlnr doesn't.

## Installation

### 🐳 Try It Now (Docker - No Install Required)

**Fastest way to try tlnr** — works on any platform:

```bash
docker run -it --rm jatinmayekar/tlnr
```

You'll drop into a Zsh shell with tlnr pre-installed. Just start typing!

---

### Quick Start (Recommended)

**Using pipx (isolated, recommended):**

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install tlnr
pipx install tlnr

# Install shell integration (Zsh required for real-time)
tlnr install

# Restart shell
exec zsh
```

**Using pip (alternative):**

```bash
# System-wide (may require --break-system-packages on some systems)
pip install tlnr

# Or user install
pip install --user tlnr

# Then install shell integration
tlnr install
exec zsh
```

**From source:**

```bash
git clone https://github.com/yourusername/tlnr.git
cd tlnr
pip install -e .
tlnr install
```

## Usage

Once installed, just start typing. tlnr shows explanations automatically:

```bash
$ git sta█
🟢 SAFE git status - Show the working tree status
```

### Manual Commands

```bash
# Get command explanation
tlnr predict "git status"

# Natural language search
tlnr ask "how to list files"

# Debug with performance metrics
tlnr debug "docker"

# Control real-time predictions
tlnr enable    # Turn on
tlnr disable   # Turn off
tlnr status    # Check current state
```

## Features

### ⚡ Real-Time Predictions (Zsh)
- **Keystroke-by-keystroke** command education
- **0.24ms average** response time (20,931 ops/sec)
- **Zero latency** — never notice it's running

### 🧠 Intelligent Fuzzy Matching
- State-of-the-art algorithm with exponential position decay
- Context-aware recommendations
- FZF-inspired smart scoring

### 🛡️ Safety First
- **🟢 SAFE** / **🟡 CAUTION** / **🔴 DANGEROUS** risk levels
- Warns before destructive commands
- Explains what commands actually do

### 🗣️ Natural Language Search
```bash
$ tlnr ask "how to find large files"
find - 🟢 SAFE - Search for files in a directory hierarchy
```

### 📊 32,000+ Commands
- Git, Docker, Kubernetes, AWS, system utilities
- Updated from tldr-pages community database
- Add custom commands via `~/.tlnr_custom_commands.json`

## Performance

```
Unit Tests:        40/40 PASSED ✅
Edge Case Tests:   ALL PASSED ✅
Average Response:  0.24ms
Throughput:        20,931 ops/sec
```

## Architecture

tlnr achieves sub-millisecond performance through:

1. **Daemon Mode**: Eliminates Python startup overhead (~50ms → ~0.2ms)
2. **Unix Socket IPC**: Fast local communication
3. **Trie-Based Search**: O(k) lookups where k = command length
4. **Zero External Deps**: No API calls, no network latency

## Platform Support

| Platform | Real-Time | Manual Commands |
|----------|-----------|-----------------|
| **macOS** (Zsh) | ✅ Full support | ✅ |
| **Linux** (Zsh) | ✅ Full support | ✅ |
| **Other shells** (Bash/Fish) | ⚠️ Manual only | ✅ |

**Note:** Windows/WSL2 support is planned but not yet tested.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good First Issues:**
- Add new command descriptions
- Improve fuzzy matching algorithm
- Port to other shells (Fish, Bash)
- Performance optimizations

## License

**AGPL-3.0** — Free for personal and open-source use.

For commercial/enterprise use, the AGPL requires you to open-source any modifications. If you need a different license, please contact me.

## Why AGPL?

I'm on an H-1B visa and can't start a company or raise VC funding. Open source is my only path to building reputation and career leverage. The AGPL ensures:

1. **Individuals** can use tlnr freely
2. **Open-source projects** can integrate without restriction
3. **Companies** who want to use it internally must either:
   - Open-source their modifications (strengthens the project)
   - Contact me for dual licensing (creates career opportunities)

This isn't about making money — it's about building undeniable proof of product + technical skill to unlock opportunities at OpenAI, Anthropic, Google, or Meta.

---

**Built by Jatin Mayekar** | [GitHub](https://github.com/yourusername) | [Email](mailto:jatin@tlnr.dev)

⭐ Star on GitHub if tlnr saves you time!
