"""
Docker Control Skill - Infrastructure Extension
================================================

This skill allows the cognitive system to manage its own infrastructure.
All actions are validated through SafetySkill before execution.

Capabilities:
- list: Enumerate containers/images/volumes
- start/stop/restart: Container lifecycle
- logs: Retrieve container logs
- exec: Execute commands in containers
- compose: Docker Compose operations
- build: Build images from Dockerfiles

The AI uses this to:
1. Keep itself alive (restart crashed services)
2. Scale resources (spin up workers)
3. Deploy updates (rolling deployments)
4. Debug issues (read logs, exec into containers)
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)


class DockerControlSkill(Skill):
    """
    Docker control for the Act phase of OODA loop.

    This is how the AI extends its physical presence:
    - Containers are "limbs" it can create/destroy
    - Images are "memories" of configurations
    - Networks are "nervous system" connections
    """

    def __init__(self):
        self._safety = None
        self._memory = None

    @property
    def safety(self):
        """Lazy load SafetySkill for action validation."""
        if self._safety is None:
            try:
                from skills.conscience.safety.skill import SafetySkill
                self._safety = SafetySkill()
            except Exception as e:
                logger.warning(f"SafetySkill not available: {e}")
        return self._safety

    @property
    def memory(self):
        """Lazy load MemorySkill to learn from outcomes."""
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="automation/docker-control",
            name="Docker Control",
            description="Manage Docker containers, images, and compose stacks",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.ADVANCED,
            tags=["docker", "containers", "automation", "infrastructure"],
            dependencies=[
                {"skill_id": "conscience/safety", "required": True},
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["list", "start", "stop", "restart", "logs", "exec", "compose", "build", "status"],
                },
                "target": {"type": "string", "description": "Container/image/service name"},
                "command": {"type": "string", "description": "Command for exec capability"},
                "compose_action": {"type": "string", "enum": ["up", "down", "ps", "logs", "build"]},
                "compose_file": {"type": "string", "default": "docker-compose.yml"},
                "tail": {"type": "integer", "default": 100, "description": "Lines to tail for logs"},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "output": {"type": "string"},
                "containers": {"type": "array"},
                "error": {"type": "string"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")
        target = input_data.get("target", "")

        # Route to handler
        handlers = {
            "list": self._list,
            "start": self._start,
            "stop": self._stop,
            "restart": self._restart,
            "logs": self._logs,
            "exec": self._exec,
            "compose": self._compose,
            "build": self._build,
            "status": self._status,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        # Check safety for mutating operations
        mutating = capability in ["start", "stop", "restart", "exec", "compose", "build"]
        if mutating and self.safety:
            safety_result = self.safety.execute({
                "action_type": "docker_command",
                "target_path": target or "docker",
                "details": f"{capability} {target}",
            }, context)

            if not safety_result.output.get("allowed", False):
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Safety check failed: {safety_result.output.get('reason', 'Denied')}",
                    skill_id=self.metadata().id,
                )

        try:
            result = handler(input_data, context)

            # Learn from outcome
            if self.memory and mutating:
                self.memory.execute({
                    "capability": "experience",
                    "content": f"Docker {capability} on {target}: {'success' if result.success else 'failed'}",
                    "memory_type": "procedural",
                    "importance": 0.6 if result.success else 0.8,
                    "context": {"skill": "docker-control", "action": capability},
                }, context)

            return result
        except Exception as e:
            logger.error(f"Docker {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _run_docker(self, args: List[str], timeout: int = 30) -> tuple[bool, str]:
        """Execute docker command and return (success, output)."""
        try:
            result = subprocess.run(
                ["docker"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout or result.stderr
            return result.returncode == 0, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "Docker not found in PATH"
        except Exception as e:
            return False, str(e)

    def _list(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """List containers, images, or volumes."""
        target = input_data.get("target", "containers")

        if target == "images":
            success, output = self._run_docker(["images", "--format", "json"])
        elif target == "volumes":
            success, output = self._run_docker(["volume", "ls", "--format", "json"])
        else:  # containers
            success, output = self._run_docker(["ps", "-a", "--format", "json"])

        if success:
            # Parse JSON lines
            items = []
            for line in output.strip().split("\n"):
                if line:
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        items.append({"raw": line})

            return SkillResult(
                success=True,
                output={"items": items, "count": len(items), "type": target},
                skill_id=self.metadata().id,
            )

        return SkillResult(success=False, output=None, error=output, skill_id=self.metadata().id)

    def _start(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Start a container."""
        target = input_data.get("target")
        if not target:
            return SkillResult(success=False, output=None, error="No target specified", skill_id=self.metadata().id)

        success, output = self._run_docker(["start", target])
        return SkillResult(success=success, output={"message": output}, error=None if success else output, skill_id=self.metadata().id)

    def _stop(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Stop a container."""
        target = input_data.get("target")
        if not target:
            return SkillResult(success=False, output=None, error="No target specified", skill_id=self.metadata().id)

        success, output = self._run_docker(["stop", target])
        return SkillResult(success=success, output={"message": output}, error=None if success else output, skill_id=self.metadata().id)

    def _restart(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Restart a container."""
        target = input_data.get("target")
        if not target:
            return SkillResult(success=False, output=None, error="No target specified", skill_id=self.metadata().id)

        success, output = self._run_docker(["restart", target])
        return SkillResult(success=success, output={"message": output}, error=None if success else output, skill_id=self.metadata().id)

    def _logs(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Get container logs."""
        target = input_data.get("target")
        if not target:
            return SkillResult(success=False, output=None, error="No target specified", skill_id=self.metadata().id)

        tail = input_data.get("tail", 100)
        success, output = self._run_docker(["logs", "--tail", str(tail), target], timeout=60)
        return SkillResult(success=success, output={"logs": output}, error=None if success else output, skill_id=self.metadata().id)

    def _exec(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute command in container."""
        target = input_data.get("target")
        command = input_data.get("command")
        if not target or not command:
            return SkillResult(success=False, output=None, error="Target and command required", skill_id=self.metadata().id)

        # Split command safely
        cmd_parts = command.split() if isinstance(command, str) else command
        success, output = self._run_docker(["exec", target] + cmd_parts, timeout=60)
        return SkillResult(success=success, output={"output": output}, error=None if success else output, skill_id=self.metadata().id)

    def _compose(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Docker Compose operations."""
        action = input_data.get("compose_action", "ps")
        compose_file = input_data.get("compose_file", "docker-compose.yml")

        cmd = ["compose", "-f", compose_file]

        if action == "up":
            cmd.extend(["up", "-d"])
        elif action == "down":
            cmd.append("down")
        elif action == "ps":
            cmd.append("ps")
        elif action == "logs":
            cmd.extend(["logs", "--tail", "50"])
        elif action == "build":
            cmd.append("build")
        else:
            return SkillResult(success=False, output=None, error=f"Unknown compose action: {action}", skill_id=self.metadata().id)

        success, output = self._run_docker(cmd, timeout=300)
        return SkillResult(success=success, output={"output": output, "action": action}, error=None if success else output, skill_id=self.metadata().id)

    def _build(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Build Docker image."""
        target = input_data.get("target", ".")

        success, output = self._run_docker(["build", "-t", "cli-ai:latest", target], timeout=600)
        return SkillResult(success=success, output={"output": output}, error=None if success else output, skill_id=self.metadata().id)

    def _status(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Get Docker system status."""
        success, info = self._run_docker(["info", "--format", "json"])
        if success:
            try:
                data = json.loads(info)
                return SkillResult(
                    success=True,
                    output={
                        "containers": data.get("Containers", 0),
                        "running": data.get("ContainersRunning", 0),
                        "images": data.get("Images", 0),
                        "server_version": data.get("ServerVersion", "unknown"),
                    },
                    skill_id=self.metadata().id,
                )
            except json.JSONDecodeError:
                pass

        return SkillResult(success=False, output=None, error=info, skill_id=self.metadata().id)


__all__ = ["DockerControlSkill"]
