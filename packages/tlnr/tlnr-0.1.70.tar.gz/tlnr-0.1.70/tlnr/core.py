"""Core functionality for command description lookup."""

import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from collections import Counter

# Lazy imports for performance - only loaded when needed
_requests = None
_openai_manager = None
_local_llm_manager = None

def _get_requests():
    """Lazy load requests module (only needed for natural language search)."""
    global _requests
    if _requests is None:
        import requests as req
        _requests = req
    return _requests


def _get_local_llm():
    """Lazy load local LLM manager."""
    global _local_llm_manager
    if _local_llm_manager is None:
        try:
            from .local_llm import LocalLLMManager
            _local_llm_manager = LocalLLMManager()
        except ImportError:
            # Should be handled by caller, but safe fallback
            return None
    return _local_llm_manager


def _get_openai_manager():
    """Lazy load OpenAI manager (only needed for ask mode)."""
    global _openai_manager
    if _openai_manager is None:
        from .openai_manager import OpenAIKeyManager
        _openai_manager = OpenAIKeyManager
    return _openai_manager


class ConfigurationManager:
    """Manages persistent configuration settings."""
    def __init__(self):
        self.config_dir = Path.home() / ".tlnr"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self.config = self._load_config()

    def _ensure_config_dir(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                return {}
        return {}

    def _save_config(self):
        self.config_file.write_text(json.dumps(self.config, indent=2))

    def set_provider(self, provider: str):
        self.config['provider'] = provider
        self._save_config()

    def get_provider(self) -> str:
        return self.config.get('provider', 'auto')


class ModeManager:
    """Manages command modes for context-aware filtering."""

    def __init__(self, commands_metadata: Dict[str, dict] = None):
        self.commands_metadata = commands_metadata or {}
        self.mode_file = Path.home() / ".tlnr_mode"
        self.auto_detect_file = Path.home() / ".tlnr_auto_detect"
        self.current_mode = self._load_current_mode()
        self.auto_detect_enabled = self._load_auto_detect_setting()
        self.mode_configs = self._get_mode_configs()

    def _get_mode_configs(self) -> Dict:
        """Define mode configurations with category-based filtering."""
        return {
            "full": {
                "name": "Full Mode",
                "description": "All commands available",
                "allowed_categories": ["*"],
                "suppress_categories": [],
                "context_files": [],
                "risk_multiplier": 1.0
            },
            "aws": {
                "name": "AWS Mode",
                "description": "Focus on AWS and cloud infrastructure commands",
                "allowed_categories": [
                    "aws-*",  # All AWS sub-categories
                    "git", "file-operations", "file-search", "network",
                    "text-processing", "utilities", "general", "editor",
                    "terminal", "compression"
                ],
                "suppress_categories": ["docker", "kubernetes", "nvidia-jetson"],
                "context_files": [".aws/", "terraform.tf", "cloudformation.yaml", "template.yaml"],
                "risk_multiplier": 1.5
            },
            "docker": {
                "name": "Docker Mode",
                "description": "Focus on Docker and containerization commands",
                "allowed_categories": [
                    "docker", "git", "file-operations", "file-search",
                    "network", "system", "system-info", "utilities",
                    "general", "editor", "terminal", "compression"
                ],
                "suppress_categories": ["kubernetes", "aws-*", "nvidia-jetson"],
                "context_files": ["Dockerfile", "docker-compose.yml", ".dockerignore", "docker-compose.yaml"],
                "risk_multiplier": 1.2
            },
            "k8s": {
                "name": "Kubernetes Mode",
                "description": "Focus on Kubernetes and orchestration commands",
                "allowed_categories": [
                    "kubernetes", "docker", "git", "network",
                    "system", "system-info", "utilities", "general",
                    "editor", "terminal", "compression", "file-operations"
                ],
                "suppress_categories": ["aws-*", "nvidia-jetson"],
                "context_files": ["*.yaml", "kustomization.yaml", ".kube/", "Chart.yaml"],
                "risk_multiplier": 2.0
            },
            "git": {
                "name": "Git Mode",
                "description": "Focus on Git version control commands",
                "allowed_categories": [
                    "git", "file-operations", "file-search", "text-processing",
                    "utilities", "general", "editor", "terminal", "compression"
                ],
                "suppress_categories": ["docker", "kubernetes", "aws-*", "nvidia-jetson", "system", "network"],
                "context_files": [".git/", ".gitignore", ".gitmodules"],
                "risk_multiplier": 0.8
            }
        }

    def _load_current_mode(self) -> str:
        """Load current mode from file."""
        if self.mode_file.exists():
            try:
                return self.mode_file.read_text().strip()
            except:
                pass
        return "full"

    def _load_auto_detect_setting(self) -> bool:
        """Load auto-detection setting."""
        return self.auto_detect_file.exists()

    def _save_current_mode(self, mode: str):
        """Save current mode to file."""
        try:
            self.mode_file.write_text(mode)
            self.current_mode = mode
        except Exception as e:
            print(f"Warning: Could not save mode setting: {e}")

    def _save_auto_detect_setting(self, enabled: bool):
        """Save auto-detection setting."""
        try:
            if enabled:
                self.auto_detect_file.touch()
            else:
                if self.auto_detect_file.exists():
                    self.auto_detect_file.unlink()
            self.auto_detect_enabled = enabled
        except Exception as e:
            print(f"Warning: Could not save auto-detect setting: {e}")

    def detect_project_context(self) -> str:
        """Auto-detect mode based on current directory context."""
        if not self.auto_detect_enabled:
            return self.current_mode

        cwd = Path.cwd()

        # Check each mode's context files
        for mode_name, config in self.mode_configs.items():
            if mode_name == "full":
                continue

            for pattern in config["context_files"]:
                if "*" in pattern:
                    # Handle glob patterns
                    if list(cwd.glob(pattern)):
                        return mode_name
                else:
                    # Handle direct file/directory checks
                    if (cwd / pattern).exists():
                        return mode_name

        return "full"

    def get_effective_mode(self) -> str:
        """Get the effective mode (considering auto-detection)."""
        if self.auto_detect_enabled:
            detected_mode = self.detect_project_context()
            if detected_mode != "full":
                return detected_mode
        return self.current_mode

    def set_mode(self, mode: str) -> bool:
        """Set the current mode."""
        if mode not in self.mode_configs:
            return False
        self._save_current_mode(mode)
        return True

    def enable_auto_detect(self):
        """Enable auto-detection."""
        self._save_auto_detect_setting(True)

    def disable_auto_detect(self):
        """Disable auto-detection."""
        self._save_auto_detect_setting(False)

    def should_suppress_command(self, command: str) -> bool:
        """Check if command should be suppressed based on category."""
        effective_mode = self.get_effective_mode()

        if effective_mode == "full":
            return False

        # Get command category from metadata
        if command not in self.commands_metadata:
            return False

        cmd_category = self.commands_metadata[command].get("category", "general")
        config = self.mode_configs.get(effective_mode, {})

        # Check suppress_categories (takes precedence)
        suppress_categories = config.get("suppress_categories", [])
        for suppress_cat in suppress_categories:
            if self._category_matches(cmd_category, suppress_cat):
                return True

        # Check allowed_categories
        allowed_categories = config.get("allowed_categories", ["*"])
        if "*" in allowed_categories:
            return False

        for allowed_cat in allowed_categories:
            if self._category_matches(cmd_category, allowed_cat):
                return False

        return True  # Not in allowed list, suppress it

    def _category_matches(self, cmd_category: str, pattern: str) -> bool:
        """Check if command category matches pattern (supports wildcards)."""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            # Wildcard: "aws-*" matches "aws-s3", "aws-ec2", etc.
            return cmd_category.startswith(pattern[:-1])
        return cmd_category == pattern

    def get_risk_multiplier(self) -> float:
        """Get risk multiplier for current mode."""
        effective_mode = self.get_effective_mode()
        config = self.mode_configs.get(effective_mode, {})
        return config.get("risk_multiplier", 1.0)

    def list_modes(self) -> Dict:
        """List all available modes with descriptions."""
        return {mode: config["description"] for mode, config in self.mode_configs.items()}


class CommandTutor:
    """Main class for command description lookup."""

    def __init__(self):
        self.commands, self.commands_metadata = self._load_commands()
        self.command_buckets = self._build_command_buckets()

        self.mode_manager = ModeManager(self.commands_metadata)
        self.history_manager = HistoryManager()
        self.config_manager = ConfigurationManager()
        self._openai_manager_instance = None  # Lazy loaded

    def _build_command_buckets(self) -> Dict[str, list]:
        """Index commands by their first word for O(1) matching."""
        buckets = {}
        for cmd in self.commands:
             first_word = cmd.split()[0]
             if first_word not in buckets:
                 buckets[first_word] = []
             buckets[first_word].append(cmd)
        return buckets

    @property
    def openai_manager(self):
        """Lazy load OpenAI manager only when needed (natural language search)."""
        if self._openai_manager_instance is None:
            OpenAIKeyManager = _get_openai_manager()
            self._openai_manager_instance = OpenAIKeyManager()
        return self._openai_manager_instance

    def _load_commands(self) -> tuple[Dict[str, str], Dict[str, dict]]:
        """Load command database from JSON file with metadata.

        Loads from two sources (user custom commands override defaults):
        1. Default commands: terminal_tutor/data/commands.json
        2. User custom commands: ~/.tlnr_custom_commands.json
        """
        commands = {}
        metadata = {}

        # Load default commands first
        commands_file = Path(__file__).parent / "data" / "commands.json"
        if commands_file.exists() and commands_file.stat().st_size > 0:
            try:
                with open(commands_file, 'r') as f:
                    data = json.load(f)

                # New JSON structure with metadata
                if "commands" in data and isinstance(data["commands"], dict):
                    for cmd, cmd_data in data["commands"].items():
                        if isinstance(cmd_data, dict):
                            commands[cmd] = cmd_data.get("description", "")
                            metadata[cmd] = cmd_data
                        else:
                            # Old format: just description string
                            commands[cmd] = cmd_data
                            metadata[cmd] = {"description": cmd_data, "risk_level": "SAFE", "category": "general"}

            except (json.JSONDecodeError, KeyError):
                # Use hardcoded defaults if JSON fails
                commands = self._get_default_commands()
                metadata = {cmd: {"description": desc, "risk_level": "SAFE", "category": "general"}
                           for cmd, desc in commands.items()}
        else:
            # Fallback to hardcoded defaults if file doesn't exist
            commands = self._get_default_commands()
            metadata = {cmd: {"description": desc, "risk_level": "SAFE", "category": "general"}
                       for cmd, desc in commands.items()}

        # Load user custom commands (overrides defaults)
        user_commands_file = Path.home() / ".tlnr_custom_commands.json"
        if user_commands_file.exists() and user_commands_file.stat().st_size > 0:
            try:
                with open(user_commands_file, 'r') as f:
                    user_data = json.load(f)

                if "commands" in user_data and isinstance(user_data["commands"], dict):
                    for cmd, cmd_data in user_data["commands"].items():
                        if isinstance(cmd_data, dict):
                            commands[cmd] = cmd_data.get("description", "")
                            metadata[cmd] = cmd_data
                        else:
                            # Old format: just description string
                            commands[cmd] = cmd_data
                            metadata[cmd] = {"description": cmd_data, "risk_level": "SAFE", "category": "custom"}

            except (json.JSONDecodeError, KeyError):
                # Silently ignore invalid user custom commands file
                pass

        return commands, metadata

    def _get_default_commands(self) -> Dict[str, str]:
        """Default command database."""
        return {
            # Git commands
            "git": "Distributed version control system - tracks changes in files",
            "git status": "Show the working tree status",
            "git add": "Add file contents to the index",
            "git commit": "Record changes to the repository",
            "git push": "Update remote refs along with associated objects",
            "git pull": "Fetch from and integrate with another repository",
            "git clone": "Clone a repository into a new directory",
            "git branch": "List, create, or delete branches",
            "git checkout": "Switch branches or restore working tree files",
            "git merge": "Join two or more development histories together",
            "git log": "Show commit logs",
            "git diff": "Show changes between commits, commit and working tree, etc",
            "git reset": "Reset current HEAD to the specified state",

            # Docker commands
            "docker": "Container platform for building, sharing, and running applications",
            "docker run": "Run a command in a new container",
            "docker build": "Build an image from a Dockerfile",
            "docker ps": "List containers",
            "docker images": "List images",
            "docker pull": "Pull an image or a repository from a registry",
            "docker push": "Push an image or a repository to a registry",
            "docker stop": "Stop one or more running containers",
            "docker start": "Start one or more stopped containers",
            "docker restart": "Restart one or more containers",
            "docker rm": "Remove one or more containers",
            "docker rmi": "Remove one or more images",
            "docker exec": "Run a command in a running container",
            "docker logs": "Fetch the logs of a container",
            "docker inspect": "Return low-level information on Docker objects",

            # Kubernetes commands
            "kubectl": "Kubernetes command-line tool for cluster management",
            "kubectl get": "Display one or many resources",
            "kubectl get pods": "List all pods in the current namespace",
            "kubectl get services": "List all services in the current namespace",
            "kubectl get deployments": "List all deployments in the current namespace",
            "kubectl get nodes": "List all nodes in the cluster",
            "kubectl describe": "Show details of a specific resource",
            "kubectl apply": "Apply a configuration to a resource by filename or stdin",
            "kubectl delete": "Delete resources by filenames, stdin, resources and names",
            "kubectl logs": "Print the logs for a container in a pod",
            "kubectl exec": "Execute a command in a container",
            "kubectl port-forward": "Forward one or more local ports to a pod",
            "kubectl scale": "Set a new size for a Deployment, ReplicaSet or Replication Controller",

            # System commands
            "ps aux": "Display information about running processes",
            "ps -ef": "Display full format listing of processes",
            "top": "Display Linux processes in real time",
            "htop": "Interactive process viewer",
            "kill": "Terminate processes by process ID",
            "killall": "Kill processes by name",
            "systemctl start": "Start a systemd service",
            "systemctl stop": "Stop a systemd service",
            "systemctl restart": "Restart a systemd service",
            "systemctl status": "Show status of a systemd service",
            "systemctl enable": "Enable a systemd service to start at boot",
            "systemctl disable": "Disable a systemd service from starting at boot",

            # File operations
            "ls -la": "List all files in long format including hidden files",
            "ls -l": "List files in long format",
            "find": "Search for files and directories",
            "grep": "Search text using patterns",
            "grep -r": "Search recursively through directories",
            "chmod": "Change file permissions",
            "chown": "Change file ownership",
            "cp -r": "Copy directories recursively",
            "mv": "Move/rename files and directories",
            "rm -rf": "Remove files and directories forcefully and recursively",
            "tar -xzf": "Extract gzipped tar archive",
            "tar -czf": "Create gzipped tar archive",

            # Network commands
            "netstat -tulpn": "Display network connections, routing tables, interface statistics",
            "ss -tulpn": "Display socket statistics (modern netstat replacement)",
            "iptables -L": "List all iptables rules",
            "ufw enable": "Enable uncomplicated firewall",
            "ufw disable": "Disable uncomplicated firewall",
            "ufw allow": "Allow traffic through firewall",
            "ufw deny": "Deny traffic through firewall",
            "ping": "Send ICMP echo requests to network hosts",
            "curl": "Transfer data from or to a server",
            "wget": "Download files from the web",
            "ssh": "Secure Shell remote login",
            "scp": "Secure copy files over SSH",

            # Basic shell commands
            "cd": "Change current directory",
            "pwd": "Print working directory path",
            "ls": "List directory contents",
            "ls -l": "List files in long format with details",
            "ls -la": "List all files in long format including hidden files",
            "ls -a": "List all files including hidden ones",
            "mkdir": "Create directories",
            "mkdir -p": "Create directories and parent directories as needed",
            "rmdir": "Remove empty directories",
            "touch": "Create empty files or update timestamps",
            "cp": "Copy files and directories",
            "mv": "Move/rename files and directories",
            "rm": "Remove files and directories",
            "cat": "Display file contents",
            "less": "View file contents page by page",
            "more": "View file contents page by page",
            "head": "Display first lines of a file",
            "tail": "Display last lines of a file",
            "wc": "Count lines, words, and characters in files",
            "sort": "Sort lines in text files",
            "uniq": "Report or omit repeated lines",
            "cut": "Extract columns from text",
            "awk": "Pattern scanning and text processing",
            "sed": "Stream editor for filtering and transforming text",
            "which": "Locate a command",
            "whereis": "Locate binary, source, manual for a command",
            "file": "Determine file type",
            "stat": "Display file or filesystem status",
            "du": "Display directory space usage",
            "df": "Display filesystem disk space usage",
            "free": "Display amount of free and used memory",
            "uptime": "Show how long system has been running",
            "whoami": "Display current username",
            "id": "Display user and group IDs",
            "date": "Display or set system date",
            "history": "Display command history",
            "alias": "Create command aliases",
            "unalias": "Remove command aliases",
            "export": "Set environment variables",
            "env": "Display environment variables",
            "echo": "Display text",
            "printf": "Format and print text",
            "clear": "Clear the terminal screen",
            "reset": "Reset terminal to default state",

            # AWS CLI commands
            "aws": "Amazon Web Services command line interface",

            # S3 commands
            "aws s3 ls": "List S3 buckets or objects",
            "aws s3 cp": "Copy files to/from S3",
            "aws s3 mv": "Move files to/from S3",
            "aws s3 sync": "Sync directories with S3",
            "aws s3 rm": "Remove S3 objects",
            "aws s3 mb": "Create S3 bucket",
            "aws s3 rb": "Remove S3 bucket",
            "aws s3api create-bucket": "Create S3 bucket with advanced options",
            "aws s3api delete-bucket": "Delete S3 bucket",
            "aws s3api put-object": "Upload object to S3",
            "aws s3api get-object": "Download object from S3",
            "aws s3api list-objects": "List objects in S3 bucket",
            "aws s3api put-bucket-policy": "Set bucket policy",
            "aws s3api get-bucket-policy": "Get bucket policy",

            # EC2 commands
            "aws ec2 describe-instances": "Describe EC2 instances",
            "aws ec2 start-instances": "Start EC2 instances",
            "aws ec2 stop-instances": "Stop EC2 instances",
            "aws ec2 terminate-instances": "Terminate EC2 instances",
            "aws ec2 reboot-instances": "Reboot EC2 instances",
            "aws ec2 run-instances": "Launch new EC2 instances",
            "aws ec2 describe-images": "Describe AMI images",
            "aws ec2 create-image": "Create AMI from instance",
            "aws ec2 describe-key-pairs": "List EC2 key pairs",
            "aws ec2 create-key-pair": "Create EC2 key pair",
            "aws ec2 delete-key-pair": "Delete EC2 key pair",
            "aws ec2 describe-security-groups": "List security groups",
            "aws ec2 create-security-group": "Create security group",
            "aws ec2 delete-security-group": "Delete security group",
            "aws ec2 authorize-security-group-ingress": "Add inbound rule to security group",
            "aws ec2 revoke-security-group-ingress": "Remove inbound rule from security group",
            "aws ec2 describe-volumes": "List EBS volumes",
            "aws ec2 create-volume": "Create EBS volume",
            "aws ec2 delete-volume": "Delete EBS volume",
            "aws ec2 attach-volume": "Attach EBS volume to instance",
            "aws ec2 detach-volume": "Detach EBS volume from instance",

            # IAM commands
            "aws iam list-users": "List IAM users",
            "aws iam create-user": "Create IAM user",
            "aws iam delete-user": "Delete IAM user",
            "aws iam list-groups": "List IAM groups",
            "aws iam create-group": "Create IAM group",
            "aws iam delete-group": "Delete IAM group",
            "aws iam list-roles": "List IAM roles",
            "aws iam create-role": "Create IAM role",
            "aws iam delete-role": "Delete IAM role",
            "aws iam list-policies": "List IAM policies",
            "aws iam create-policy": "Create IAM policy",
            "aws iam delete-policy": "Delete IAM policy",
            "aws iam attach-user-policy": "Attach policy to user",
            "aws iam detach-user-policy": "Detach policy from user",
            "aws iam list-access-keys": "List access keys for user",
            "aws iam create-access-key": "Create access key for user",
            "aws iam delete-access-key": "Delete access key",

            # Lambda commands
            "aws lambda list-functions": "List Lambda functions",
            "aws lambda create-function": "Create Lambda function",
            "aws lambda delete-function": "Delete Lambda function",
            "aws lambda invoke": "Invoke Lambda function",
            "aws lambda update-function-code": "Update Lambda function code",
            "aws lambda get-function": "Get Lambda function details",

            # CloudWatch commands
            "aws logs describe-log-groups": "List CloudWatch log groups",
            "aws logs describe-log-streams": "List log streams in log group",
            "aws logs get-log-events": "Get log events from log stream",
            "aws logs tail": "Tail CloudWatch logs",
            "aws logs create-log-group": "Create log group",
            "aws logs delete-log-group": "Delete log group",
            "aws cloudwatch list-metrics": "List CloudWatch metrics",
            "aws cloudwatch get-metric-statistics": "Get metric statistics",
            "aws cloudwatch put-metric-data": "Put custom metric data",

            # RDS commands
            "aws rds describe-db-instances": "List RDS database instances",
            "aws rds create-db-instance": "Create RDS database instance",
            "aws rds delete-db-instance": "Delete RDS database instance",
            "aws rds start-db-instance": "Start RDS database instance",
            "aws rds stop-db-instance": "Stop RDS database instance",
            "aws rds reboot-db-instance": "Reboot RDS database instance",

            # ECS commands
            "aws ecs list-clusters": "List ECS clusters",
            "aws ecs describe-clusters": "Describe ECS clusters",
            "aws ecs list-services": "List ECS services",
            "aws ecs describe-services": "Describe ECS services",
            "aws ecs list-tasks": "List ECS tasks",
            "aws ecs describe-tasks": "Describe ECS tasks",
            "aws ecs run-task": "Run ECS task",
            "aws ecs stop-task": "Stop ECS task",

            # EKS commands
            "aws eks list-clusters": "List EKS clusters",
            "aws eks describe-cluster": "Describe EKS cluster",
            "aws eks create-cluster": "Create EKS cluster",
            "aws eks delete-cluster": "Delete EKS cluster",
            "aws eks update-kubeconfig": "Update kubeconfig for EKS cluster",

            # CloudFormation commands
            "aws cloudformation list-stacks": "List CloudFormation stacks",
            "aws cloudformation describe-stacks": "Describe CloudFormation stacks",
            "aws cloudformation create-stack": "Create CloudFormation stack",
            "aws cloudformation update-stack": "Update CloudFormation stack",
            "aws cloudformation delete-stack": "Delete CloudFormation stack",
            "aws cloudformation validate-template": "Validate CloudFormation template",

            # Route53 commands
            "aws route53 list-hosted-zones": "List Route53 hosted zones",
            "aws route53 list-resource-record-sets": "List DNS records in hosted zone",
            "aws route53 change-resource-record-sets": "Modify DNS records",

            # Package managers
            "apt update": "Update package index",
            "apt upgrade": "Upgrade installed packages",
            "apt install": "Install packages",
            "apt remove": "Remove packages",
            "apt autoremove": "Remove automatically installed packages no longer needed",
            "snap install": "Install snap packages",
            "snap list": "List installed snap packages",
            "pip install": "Install Python packages",
            "pip list": "List installed Python packages",
            "npm install": "Install Node.js packages",
            "npm list": "List installed Node.js packages",
        }

    def get_description(self, command_line: str) -> Optional[str]:
        """Get description for a command line with progressive matching."""
        command_line = command_line.strip()
        if not command_line:
            return None

        # Check mode-based suppression first
        if self.mode_manager.should_suppress_command(command_line):
            return None

        # Progressive matching for real-time prediction
        # Find the best match for current input
        best_match = None
        best_score = 0

        for cmd_pattern, description in self.commands.items():
            # Exact match gets highest priority
            if command_line == cmd_pattern:
                return description

            # Partial match from beginning
            if cmd_pattern.startswith(command_line):
                score = len(command_line) / len(cmd_pattern)
                if score > best_score:
                    best_score = score
                    best_match = description

        # If we found a good partial match, return it
        if best_match and best_score > 0.3:  # At least 30% match
            return best_match

        # Fallback with Smart Flag Parsing using shared logic
        flag_info = self.parse_command_flags(command_line)
        if flag_info:
            base_cmd = flag_info['base_command']
            base_desc = self.commands.get(base_cmd, "")
            
            # Format flag descriptions
            flag_descs = []
            if flag_info['flag_explanations']:
                for flag_dict in flag_info['flag_explanations']:
                    for desc in flag_dict.values():
                        # Polish description
                        clean = desc
                        for prefix in ["Show ", "Enable ", "Display ", "Give output in "]:
                            if clean.startswith(prefix):
                                clean = clean[len(prefix):]
                                if clean: clean = clean[0].upper() + clean[1:]
                                break
                        flag_descs.append(clean)
            
            if flag_descs:
                # Limit to 3 flags
                if len(flag_descs) > 3:
                     flag_descs = flag_descs[:3] + [f"+{len(flag_descs)-3}"]
                return f"{base_desc} • {' • '.join(flag_descs)}"
            
            return base_desc

        parts = command_line.split()
        if parts and parts[0] in self.commands:
            return self.commands[parts[0]]

        return None



    def get_description_realtime(self, command_line: str) -> Optional[str]:
        """Ultra-fast O(1) lookup for real-time predictions with fuzzy suggestions."""
        command_line = command_line.strip()
        if not command_line:
            return None

        # Check mode-based suppression first
        if self.mode_manager.should_suppress_command(command_line):
            return None

        # --- BUCKET MATCHING STRATEGY (O(1)) ---
        # 1. Identify potential candidates from the bucket of the first word
        first_word = command_line.split()[0]
        candidates = self.command_buckets.get(first_word, [])
        
        best_match_cmd = None
        best_match_len = -1
        
        # 2. Iterate ONLY the candidates (small subset)
        for cmd_template in candidates:
            # Prepare template for matching: remove <> placeholders generally?
            # Actually, we want to see if 'command_line' matches the fixed parts of 'cmd_template'
            # Simple heuristic: Split both by space and match word-by-word until a placeholder
            
            # Quicker approach: Check if cmd_template prefix matches command_line?
            # cmd_template: "systemctl restart <unit>"
            # command_line: "systemctl restart nginx"
            
            # Clean template to purely fixed prefix: "systemctl restart"
            # (Remove <...>)
            clean_template = re.sub(r'<[^>]+>.*', '', cmd_template).strip()
            # Also remove optional brackets logic if present [ ... ] -> handled in ingestion usually?
            # Ingestion kept them in KEYS? No, ingestion cleaned keys: `clean_cmd = cmd_str.replace('{{', '<').replace('}}', '>')`
            # So key is `systemctl restart <unit>`.
            
            # If the command line starts with this cleaned template
            if command_line.startswith(clean_template):
                # We want the LONGEST match (specificity)
                if len(clean_template) > best_match_len:
                    best_match_len = len(clean_template)
                    best_match_cmd = cmd_template
            
            # Also check exact match of the key itself
            if command_line == cmd_template:
                 best_match_len = len(cmd_template) + 1 # Priority +1
                 best_match_cmd = cmd_template

        # 3. Return the best match found
        if best_match_cmd:
            description = self.commands[best_match_cmd]
            risk_level = self.get_risk_level(best_match_cmd)
            
            # Append risk styling
            output = f"{risk_level} - {description}"
            
            # Optional: Add flag info if we matched a base command but user typed more flags
            # (Only needed if the best match didn't consume all flags)
            
            return output

        # --- Fallback: Fuzzy Suggestions ---
        # For partial matches, show top 3 suggestions
        suggestions = self.get_fuzzy_suggestions(command_line, max_results=3)

        if suggestions:
            if len(suggestions) == 1:
                # Single match
                suggestion = suggestions[0]
                return f"{suggestion['risk_level']} - {suggestion['description']}"
            else:
                # Multiple matches
                lines = []
                for i, suggestion in enumerate(suggestions, 1):
                    lines.append(f"{suggestion['risk_level']} {suggestion['command']} - {suggestion['description']}")
                return "\n".join(lines)

        return None

    def get_risk_level(self, command_line: str) -> str:
        """Get risk level - reads from metadata (JSON) or calculates for unknown commands."""
        # Check if command exists in metadata (from JSON)
        if command_line in self.commands_metadata:
            risk_level = self.commands_metadata[command_line].get("risk_level", "SAFE")
            # Add emoji prefix
            if risk_level == "DANGEROUS":
                return "✗ DANGEROUS"
            elif risk_level == "CAUTION":
                return "▲ CAUTION"
            else:
                return "● SAFE"

        # Fallback: calculate for unknown commands (not in database)
        return self._calculate_risk_level(command_line)

    def _calculate_risk_level(self, command_line: str) -> str:
        """Calculate risk level for unknown commands - fallback only."""
        dangerous_patterns = [
            r'rm\s+.*-rf',
            r'rm\s+.*-fr',
            r'dd\s+.*of=',
            r'mkfs\.',
            r'fdisk',
            r'parted',
            r':(){ :|:& };:',  # Fork bomb
            r'chmod\s+777',
            r'chown\s+.*-R.*/',
            r'iptables\s+.*-F',
            r'ufw\s+--force-reset'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command_line, re.IGNORECASE):
                return "✗ DANGEROUS"

        caution_patterns = [
            r'sudo',
            r'rm\s+',
            r'mv\s+.*/',
            r'chmod',
            r'chown',
            r'systemctl\s+(stop|disable|mask)',
            r'docker\s+rm',
            r'kubectl\s+delete'
        ]

        for pattern in caution_patterns:
            if re.search(pattern, command_line, re.IGNORECASE):
                return "▲ CAUTION"

        return "● SAFE"



    def get_fuzzy_suggestions(self, partial_command: str, max_results: int = 3) -> list:
        """Get top fuzzy matches using FZF-inspired smart scoring algorithm."""
        partial_command = partial_command.strip().lower()
        if not partial_command:
            return []

        # Special handling for multi-word input - only exact prefix matches
        if ' ' in partial_command:
            exact_matches = []
            for cmd, description in self.commands.items():
                # Check mode-based suppression
                if self.mode_manager.should_suppress_command(cmd):
                    continue

                if cmd.lower().startswith(partial_command):
                    score = self._calculate_smart_score(partial_command, cmd.lower(), description)
                    exact_matches.append({
                        'command': cmd,
                        'description': description,
                        'risk_level': self.get_risk_level(cmd),
                        'score': score
                    })
            if exact_matches:
                exact_matches.sort(key=lambda x: x['score'], reverse=True)
                return exact_matches[:max_results]
            else:
                return []

        matches = []

        for cmd, description in self.commands.items():
            # Check mode-based suppression
            if self.mode_manager.should_suppress_command(cmd):
                continue

            cmd_lower = cmd.lower()
            score = self._calculate_smart_score(partial_command, cmd_lower, description)

            if score > 0:
                matches.append({
                    'command': cmd,
                    'description': description,
                    'risk_level': self.get_risk_level(cmd),
                    'score': score
                })

        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)

        # Apply dynamic relevance threshold - only show results that are reasonably relevant
        if not matches:
            return []

        top_score = matches[0]['score']

        # Dynamic threshold based on top score and minimum absolute threshold
        dynamic_threshold = max(
            top_score * 0.3,  # At least 30% of the top score
            200  # Absolute minimum threshold for relevance
        )

        # Filter matches that meet the relevance threshold
        relevant_matches = [m for m in matches if m['score'] >= dynamic_threshold]

        return relevant_matches[:max_results]

    def _calculate_smart_score(self, partial: str, full_command: str, description: str) -> float:
        """FZF-inspired smart scoring algorithm with word boundary detection and relevance filtering."""
        if not partial or not full_command:
            return 0

        # Command frequency/priority weights
        command_priority = self._get_command_priority(full_command)

        # 1. Exact prefix match - highest priority
        if full_command.startswith(partial):
            base_score = (len(partial) / len(full_command)) * 1000
            return base_score + command_priority + 500

        # 2. Word boundary prefix match - prioritize matches at word starts
        words = full_command.split()
        for i, word in enumerate(words):
            if word.startswith(partial):
                base_score = (len(partial) / len(word)) * 500
                word_position_bonus = max(0, 100 - (i * 20))  # Earlier words get higher bonus

                # CRITICAL: Apply exponential position decay to word boundary matches too
                # Calculate the starting position of this word in the full command
                word_start_position = full_command.find(word)
                position_decay = self._calculate_position_decay(word_start_position)

                final_score = (base_score + word_position_bonus + 200) * position_decay + command_priority
                return final_score

        # 3. CRITICAL FIX: Word boundary fuzzy matching - heavily prefer matches at word starts
        for i, word in enumerate(words):
            if len(partial) >= 2:  # Only for meaningful partial inputs
                word_fuzzy_score = self._calculate_fuzzy_score(partial, word)
                if word_fuzzy_score > 0:
                    # Word start matches get massive bonus, later words get penalties
                    word_position_multiplier = 1.0 if i == 0 else 0.3 if i == 1 else 0.1
                    adjusted_score = word_fuzzy_score * word_position_multiplier

                    # Only return if it meets minimum relevance threshold
                    if adjusted_score > 30:  # Minimum relevance threshold
                        return adjusted_score + command_priority

        # 4. Full command fuzzy matching (with exponential position decay)
        if len(partial) >= 2:
            fuzzy_score = self._calculate_fuzzy_score(partial, full_command)
            if fuzzy_score > 0:
                # Apply exponential position decay and match quality assessment
                match_quality = self._assess_match_quality(partial, full_command)

                # CRITICAL: Apply exponential position decay
                # "cl" in "clear" (avg_pos=0.5) gets minimal penalty
                # "cl" in "cloudwatch" (avg_pos=4.5) gets heavy penalty
                position_penalty = match_quality['position_decay_multiplier']
                fuzzy_score *= position_penalty

                # Apply additional penalties for scattered matches
                if match_quality['is_scattered'] and len(full_command) > 10:
                    fuzzy_score *= 0.5  # Additional penalty for scattered matches

                # Calculate final score with command priority
                final_score = fuzzy_score + command_priority

                # Soft threshold - allow very low scores to be filtered naturally
                return final_score if final_score > 10 else 0

        return 0

    def _assess_match_quality(self, partial: str, full_command: str) -> dict:
        """Assess the quality of a fuzzy match to detect scattered vs coherent matches."""
        partial_idx = 0
        match_positions = []
        gaps = []

        # Find all character match positions
        for i, char in enumerate(full_command):
            if partial_idx < len(partial) and char == partial[partial_idx]:
                match_positions.append(i)
                partial_idx += 1

        if len(match_positions) < 2:
            return {'is_scattered': False, 'avg_gap': 0, 'max_gap': 0}

        # Calculate gaps between consecutive matches
        for i in range(1, len(match_positions)):
            gap = match_positions[i] - match_positions[i-1] - 1
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        max_gap = max(gaps) if gaps else 0

        # CRITICAL: Calculate average character position for exponential position decay
        avg_position = sum(match_positions) / len(match_positions) if match_positions else 0
        first_match_position = match_positions[0] if match_positions else 0

        # FZF-inspired exponential position decay function
        # Characters matching deeper in strings get exponentially lower relevance
        position_decay_multiplier = self._calculate_position_decay(avg_position)

        # Define scattered match criteria
        is_scattered = (
            avg_gap > 3 or  # Average gap > 3 characters
            max_gap > 8 or  # Any gap > 8 characters
            len(gaps) > 0 and sum(g > 2 for g in gaps) > len(gaps) * 0.5  # More than 50% of gaps > 2
        )

        return {
            'is_scattered': is_scattered,
            'avg_gap': avg_gap,
            'max_gap': max_gap,
            'avg_position': avg_position,
            'first_match_position': first_match_position,
            'position_decay_multiplier': position_decay_multiplier,
            'match_positions': match_positions,
            'gaps': gaps
        }

    def _calculate_position_decay(self, avg_position: float, decay_rate: float = 0.5) -> float:
        """
        FZF-inspired exponential position decay function.

        Characters matching deeper in strings get exponentially lower relevance.

        Examples:
        - "cl" in "clear" (avg_pos=0.5) -> multiplier = 0.86 (minimal penalty)
        - "cl" in "cloudwatch" (avg_pos=4.5) -> multiplier = 0.27 (heavy penalty)

        Args:
            avg_position: Average position of matched characters in the string
            decay_rate: Controls how aggressively scores decay (0.1=gentle, 0.5=aggressive)

        Returns:
            Multiplier between 0.0-1.0 to apply to the base score
        """
        return math.exp(-decay_rate * avg_position)

    def _get_command_priority(self, command: str) -> float:
        """Assign priority scores based on command category and frequency."""
        # Basic shell commands (highest priority)
        basic_commands = {
            'cd', 'ls', 'pwd', 'clear', 'cat', 'echo', 'mv', 'cp', 'rm', 'mkdir',
            'touch', 'grep', 'find', 'head', 'tail', 'sort', 'uniq', 'wc'
        }

        # Development tools (medium-high priority)
        dev_commands = {
            'git', 'docker', 'npm', 'pip', 'vim', 'nano', 'code'
        }

        # Get first word of command
        first_word = command.split()[0]

        if first_word in basic_commands:
            return 100  # Highest priority
        elif first_word in dev_commands or command.startswith('git '):
            return 50   # Medium-high priority
        elif command.startswith('aws '):
            return 10   # Lower priority for specialized tools
        else:
            return 25   # Default priority

    def _calculate_fuzzy_score(self, partial: str, full_command: str, debug: bool = False) -> float:
        """Calculate fuzzy match score with position bonuses and gap penalties."""
        partial_idx = 0
        score = 0
        last_match_pos = -1
        consecutive_matches = 0
        match_positions = []
        gaps = []

        for i, char in enumerate(full_command):
            if partial_idx < len(partial) and char == partial[partial_idx]:
                # Track match positions for debugging
                match_positions.append((partial[partial_idx], i))

                # Position bonuses (FZF-inspired)
                position_bonus = 0

                # Start of command bonus
                if i == 0:
                    position_bonus += 50
                # Start of word bonus
                elif i > 0 and full_command[i-1] in ' -_':
                    position_bonus += 30
                # CamelCase bonus
                elif char.isupper() and i > 0 and full_command[i-1].islower():
                    position_bonus += 20

                # Consecutive match bonus
                if last_match_pos == i - 1:
                    consecutive_matches += 1
                    position_bonus += consecutive_matches * 5
                else:
                    consecutive_matches = 0

                # Gap penalty
                gap = 0
                if last_match_pos >= 0:
                    gap = i - last_match_pos - 1
                    gaps.append(gap)
                    gap_penalty = min(gap * 2, 20)  # Cap penalty at 20
                    position_bonus = max(0, position_bonus - gap_penalty)

                score += 10 + position_bonus
                last_match_pos = i
                partial_idx += 1

        # Only return score if we matched all characters
        if partial_idx == len(partial):
            # Length penalty for very long commands
            length_penalty = max(0, len(full_command) - 20) * 0.5
            final_score = max(0, score - length_penalty)

            # Debug output
            if debug:
                total_gaps = sum(gaps)
                avg_gap = total_gaps / len(gaps) if gaps else 0
                print(f"DEBUG: '{partial}' in '{full_command}':")
                print(f"  Matches: {match_positions}")
                print(f"  Gaps: {gaps} (total: {total_gaps}, avg: {avg_gap:.1f})")
                print(f"  Score: {final_score:.1f}")
                print()

            return final_score

        return 0

    def _find_base_command(self, parts: list) -> str:
        """
        Find the longest matching command from parts.

        Args:
            parts: Command line split into words

        Returns:
            The longest matching base command or None
        """
        # Try progressively longer combinations (up to 5 words for multi-word commands)
        for length in range(min(len(parts), 5), 0, -1):
            candidate = ' '.join(parts[:length])
            if candidate in self.commands:
                return candidate
        return None

    def parse_command_flags(self, command_line: str) -> dict:
        """
        Extract flags from command line and match against database.

        Args:
            command_line: Full command line string

        Returns:
            Dictionary with:
                'base_command': The base command (e.g., 'docker run')
                'flags': List of flags found (e.g., ['-i', '-t'])
                'flag_explanations': List of dicts mapping flags to descriptions
                'unknown_flags': Flags not in database
        """
        parts = command_line.strip().split()
        if not parts:
            return None

        # Find base command (handle multi-word commands like "git commit")
        base_command = self._find_base_command(parts)
        if not base_command or base_command not in self.commands_metadata:
            return None

        # Extract and expand flags (handle combined short flags like -it, -lah)
        raw_flags = [p for p in parts if p.startswith('-') and not p.startswith('---')]
        flags = []

        for raw_flag in raw_flags:
            if raw_flag.startswith('--'):
                # Long flag - use as-is
                flags.append(raw_flag)
            elif len(raw_flag) > 2:
                # Combined short flags like -it → [-i, -t]
                for char in raw_flag[1:]:  # Skip the leading '-'
                    flags.append(f'-{char}')
            else:
                # Single short flag like -i
                flags.append(raw_flag)

        # Get flag metadata from JSON
        cmd_metadata = self.commands_metadata[base_command]
        flag_db = cmd_metadata.get('flags', [])

        if not flag_db:
            return None  # No flags defined for this command

        # Match flags against database
        flag_explanations = []
        unknown_flags = []

        for flag in flags:
            matched = False
            for flag_entry in flag_db:
                if flag in flag_entry:
                    flag_explanations.append({flag: flag_entry[flag]})
                    matched = True
                    break
            if not matched:
                unknown_flags.append(flag)

        # Only return if we found at least one known flag
        if not flag_explanations:
            return None

        return {
            'base_command': base_command,
            'flags': flags,
            'flag_explanations': flag_explanations,
            'unknown_flags': unknown_flags
        }



    def natural_language_search(self, query: str) -> Optional[dict]:
        """
        Use AI (Local or OpenAI) to translate natural language queries into terminal commands.
        Defaults to Local LLM if available, falls back to OpenAI if key exists.
        """
        try:
            # Check configured provider
            provider = self.config_manager.get_provider()
            command_name = None
            used_provider = None

            # 1. Explicit Configuration
            if provider == 'local':
                manager = _get_local_llm()
                if manager:
                    used_provider = 'local'
                    command_name = manager.query(query)
            
            elif provider == 'openai':
                used_provider = 'openai'
                command_name = self._query_openai(query)

            # 2. Auto-Detection (Default)
            else:
                # Priority 1: Check if Local LLM libs are installed
                local_manager = _get_local_llm()
                if local_manager:
                    # Use Local LLM by default if dependencies exist
                    # (It handles model downloading prompt internally)
                    used_provider = 'local'
                    command_name = local_manager.query(query)
                
                # Priority 2: Check if OpenAI Key exists (silent check)
                elif self.openai_manager.has_api_key():
                    used_provider = 'openai'
                    command_name = self._query_openai(query)
                
                # Priority 3: No provider available
                else:
                    print("No AI provider configured.")
                    return None
            
            if not command_name:
                return None

            # Handle structured JSON response from Local LLM or OpenAI
            # Handle structured JSON response from Local LLM or OpenAI
            if isinstance(command_name, dict):
                ai_command = command_name.get('command', '')
                ai_desc = command_name.get('description', 'AI Generated Command')
                ai_risk = command_name.get('risk_level', 'SAFE').upper()
                
                # SAFETY OVERRIDE: Run regex checks on the generated command
                # We trust the database/regex logic more than the AI for safety
                calc_risk = self._calculate_risk_level(ai_command)
                
                # Normalize calculated risk (remove icons for comparison if needed, though _calculate adds them)
                # _calculate_risk_level returns strings like "✗ DANGEROUS" or "● SAFE"
                # E.g., "git push" is SAFE, "rm -rf" is DANGEROUS
                final_risk = "● SAFE"
                
                # If regex says DANGER, we force DANGER
                if "DANGEROUS" in calc_risk:
                    final_risk = "✗ DANGEROUS"
                # If regex says CAUTION, we force CAUTION unless AI says DANGER
                elif "CAUTION" in calc_risk:
                    if "DANGER" in ai_risk:
                         final_risk = "✗ DANGER" # AI warning took precedence
                    else:
                         final_risk = "▲ CAUTION"
                # If Regex says SAFE, we mostly trust AI, but map its string to icons
                else: 
                    if "DANGER" in ai_risk:
                        final_risk = "✗ DANGER"
                    elif "CAUTION" in ai_risk:
                        final_risk = "▲ CAUTION"
                    else:
                        final_risk = "● SAFE"

                return {
                    'command': ai_command,
                    'description': ai_desc,
                    'risk_level': final_risk
                }

            # If we somehow got a string (shouldn't happen with current logic, but safety net)
            # OR if command_name was None (already handled above)
            return None

        except Exception as e:
            # Graceful degradation
            print(f"DEBUG: Error in natural_language_search: {e}")
            return None

    def is_setup_in_progress(self) -> bool:
        """Check if background setup is currently running."""
        # Check lock file directly or via manager logic
        # Since manager might be None if dependencies missing, check lock file manualy
        lock_file = Path.home() / ".terminal-tutor.download.lock"
        if lock_file.exists():
            return True
            
        # Also check local manager if available
        local_manager = _get_local_llm()
        if local_manager and local_manager.is_downloading():
            return True
            
        return False

    def explain_command(self, command: str) -> Optional[str]:
        """Explain a command using the Local LLM."""
        try:
             # Priority 1: Check if Local LLM libs are installed
            local_manager = _get_local_llm()
            if local_manager:
                return local_manager.explain(command)
            
            # Priority 2: Check if OpenAI Key exists (silent check)
            # TODO: Implement OpenAI fallback for explanation if desired
            
            print("No AI provider configured for explanation.")
            print("Run: pip install terminal-tutor[local-llm]")
            return None
        except Exception as e:
            print(f"Error explaining command: {e}")
            return None

    def _query_openai(self, query: str) -> Optional[dict]:
        """
        Query OpenAI API for natural language to command translation.

        Args:
            query: Natural language query

        Returns:
            Dict with command, description, risk_level or None
        """
        # Get API key from manager (prompts user if needed)
        api_key = self.openai_manager.get_api_key()
        if not api_key:
            return None

        try:
            import openai
            import json
        except ImportError:
            # OpenAI package not installed
            return None

        try:
            client = openai.OpenAI(api_key=api_key)

            # Optimized prompt for command translation
            system_prompt = """You are a strict zsh command expert.
INSTRUCTIONS:
1. FIRST, check if the request is a valid terminal command or coding task.
2. If NO (e.g. cooking, life advice, general knowledge), return command="" and description="I can only help with terminal commands".
3. If YES, provide the best zsh command.
4. Respond in JSON keys: 'command', 'description', 'risk_level' ('SAFE', 'CAUTION', or 'DANGER')."""

            # Make request to OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106", # Support JSON mode
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=100
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None


class HistoryManager:
    """Manage local command history and statistics."""
    
    def __init__(self):
        self.history_file = Path.home() / ".terminal_tutor_local_history"
        
    def get_history(self, limit: int = 50) -> list:
        """Get recent command history."""
        if not self.history_file.exists():
            return []
            
        history = []
        try:
            # Read last N lines efficiently for large files? 
            # For now, read all and slice last N since typical history is manageable text size
            lines = self.history_file.read_text(errors='ignore').splitlines()
            for line in reversed(lines):
                if '|' in line:
                    ts, cmd = line.split('|', 1)
                    try:
                        timestamp = datetime.fromtimestamp(int(ts))
                        history.append({
                            'timestamp': timestamp,
                            'command': cmd,
                            'time_str': timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    except ValueError:
                        continue
                        
                if len(history) >= limit:
                    break
        except Exception:
            return []
            
        return history

    def get_stats(self) -> dict:
        """Calculate usage statistics."""
        if not self.history_file.exists():
            return {"total_commands": 0, "top_commands": [], "busy_hours": []}
            
        cmd_counts = Counter()
        hour_counts = Counter()
        total = 0
        
        try:
            lines = self.history_file.read_text(errors='ignore').splitlines()
            for line in lines:
                if '|' in line:
                    ts, cmd = line.split('|', 1)
                    base_cmd = cmd.strip().split()[0]
                    cmd_counts[base_cmd] += 1
                    
                    try:
                        hour = datetime.fromtimestamp(int(ts)).hour
                        hour_counts[hour] += 1
                        total += 1
                    except ValueError:
                        continue
                        
            return {
                "total_commands": total,
                "top_commands": cmd_counts.most_common(10),
                "busy_hours": hour_counts.most_common(3)
            }
        except Exception:
            return {"total_commands": 0, "top_commands": [], "busy_hours": []}


