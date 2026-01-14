"""
CI/CD Pipeline Skill - Autonomous Development Pipeline
=======================================================

This skill enables the cognitive system to manage its own development
lifecycle, including testing, building, deploying, and improving skills.

Multi-Model Strategy:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTELLIGENT MODEL ROUTING                          │
│                                                                         │
│  CodeGemma (133 tok/s)  →  Quick checks, linting, syntax validation    │
│  Qwen3 (87 tok/s)       →  Code generation, skill creation, fixes      │
│  DeepSeek-R1 (74 tok/s) →  Analysis, debugging, architecture decisions │
│                                                                         │
│  Task Type → Model Selection:                                           │
│  - lint/format/quick    → CodeGemma (fast reflexes)                    │
│  - generate/create/fix  → Qwen3 (creative synthesis)                   │
│  - analyze/debug/decide → DeepSeek (deep reasoning)                    │
└─────────────────────────────────────────────────────────────────────────┘
```

Pipeline Stages:
1. VALIDATE  - Lint, type check, syntax validation (CodeGemma)
2. ANALYZE   - Understand changes, find issues (DeepSeek)
3. TEST      - Run tests, check coverage
4. BUILD     - Build containers, artifacts
5. IMPROVE   - Generate improvements, fix issues (Qwen3)
6. DEPLOY    - Push to registry, deploy to environment
7. LEARN     - Store outcomes in memory for future reference
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
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


class PipelineStage(Enum):
    VALIDATE = "validate"
    ANALYZE = "analyze"
    TEST = "test"
    BUILD = "build"
    IMPROVE = "improve"
    DEPLOY = "deploy"
    LEARN = "learn"


class ModelRole(Enum):
    QUICK = "codegemma"      # Fast checks, formatting
    CREATIVE = "qwen3"       # Code generation, creation
    REASONING = "deepseek"   # Analysis, debugging


@dataclass
class PipelineRun:
    """Represents a single pipeline execution."""
    id: str
    started_at: datetime
    stages: Dict[str, Dict] = field(default_factory=dict)
    status: str = "running"
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    improvements: List[Dict] = field(default_factory=list)


# Model routing based on task type
MODEL_ROUTING = {
    # Quick tasks → CodeGemma
    "lint": ModelRole.QUICK,
    "format": ModelRole.QUICK,
    "syntax": ModelRole.QUICK,
    "validate": ModelRole.QUICK,
    "check": ModelRole.QUICK,

    # Creative tasks → Qwen3
    "generate": ModelRole.CREATIVE,
    "create": ModelRole.CREATIVE,
    "fix": ModelRole.CREATIVE,
    "implement": ModelRole.CREATIVE,
    "refactor": ModelRole.CREATIVE,
    "improve": ModelRole.CREATIVE,

    # Reasoning tasks → DeepSeek
    "analyze": ModelRole.REASONING,
    "debug": ModelRole.REASONING,
    "review": ModelRole.REASONING,
    "decide": ModelRole.REASONING,
    "architect": ModelRole.REASONING,
    "explain": ModelRole.REASONING,
}


class CICDPipelineSkill(Skill):
    """
    CI/CD Pipeline for autonomous skill development and deployment.

    This skill orchestrates the entire development lifecycle:
    - Validates code quality
    - Analyzes changes with deep reasoning
    - Runs tests and checks coverage
    - Builds containers and artifacts
    - Generates improvements using AI
    - Deploys to environments
    - Learns from outcomes
    """

    def __init__(self):
        self._mindset = None
        self._memory = None
        self._docker = None
        self._growth = None
        self._safety = None
        self._current_run: Optional[PipelineRun] = None
        self._runs_dir = Path("data/pipeline_runs")
        self._runs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def mindset(self):
        """Access MindsetSkill for LLM reasoning."""
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    @property
    def docker(self):
        if self._docker is None:
            try:
                from skills.automation.docker_control.skill import DockerControlSkill
                self._docker = DockerControlSkill()
            except Exception as e:
                logger.warning(f"DockerControlSkill not available: {e}")
        return self._docker

    @property
    def growth(self):
        if self._growth is None:
            try:
                from skills.conscience.growth.skill import GrowthSkill
                self._growth = GrowthSkill()
            except Exception as e:
                logger.warning(f"GrowthSkill not available: {e}")
        return self._growth

    @property
    def safety(self):
        if self._safety is None:
            try:
                from skills.conscience.safety.skill import SafetySkill
                self._safety = SafetySkill()
            except Exception as e:
                logger.warning(f"SafetySkill not available: {e}")
        return self._safety

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="automation/cicd-pipeline",
            name="CI/CD Pipeline",
            description="Autonomous development pipeline with multi-model intelligence",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.EXPERT,
            tags=["cicd", "pipeline", "automation", "testing", "deployment", "multi-model"],
            dependencies=[
                {"skill_id": "conscience/mindset", "required": True},
                {"skill_id": "conscience/memory", "required": True},
                {"skill_id": "automation/docker-control", "required": False},
                {"skill_id": "conscience/growth", "required": False},
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": [
                        "run",           # Run full pipeline
                        "validate",      # Lint/type check
                        "analyze",       # Deep analysis
                        "test",          # Run tests
                        "build",         # Build artifacts
                        "improve",       # AI improvements
                        "deploy",        # Deploy to environment
                        "improve_skill", # Improve a specific skill
                        "create_skill",  # Create new skill from spec
                        "status",        # Get pipeline status
                        "history",       # Get run history
                    ],
                },
                "target": {"type": "string", "description": "Target path or skill ID"},
                "skill_spec": {"type": "object", "description": "Skill specification for creation"},
                "environment": {"type": "string", "enum": ["dev", "staging", "production"], "default": "dev"},
                "stages": {"type": "array", "items": {"type": "string"}, "description": "Stages to run"},
                "options": {"type": "object", "description": "Additional options"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "status": {"type": "string"},
                "stages": {"type": "object"},
                "artifacts": {"type": "array"},
                "improvements": {"type": "array"},
                "errors": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "run": self._run_pipeline,
            "validate": self._validate,
            "analyze": self._analyze,
            "test": self._test,
            "build": self._build,
            "improve": self._improve,
            "deploy": self._deploy,
            "improve_skill": self._improve_skill,
            "create_skill": self._create_skill,
            "status": self._status,
            "history": self._history,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"Pipeline {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _get_model_for_task(self, task_type: str) -> str:
        """Route task to appropriate model."""
        role = MODEL_ROUTING.get(task_type, ModelRole.CREATIVE)

        model_map = {
            ModelRole.QUICK: "codegemma:latest",
            ModelRole.CREATIVE: "qwen3:latest",
            ModelRole.REASONING: "deepseek-r1:latest",
        }

        return model_map[role]

    def _call_model(
        self,
        task_type: str,
        prompt: str,
        context: SkillContext,
        pattern: str = "balanced"
    ) -> Optional[Dict]:
        """Call appropriate model based on task type."""
        if not self.mindset:
            return None

        # Map task type to mindset pattern
        pattern_map = {
            "quick": "rapid_iteration",
            "creative": "creative_synthesis",
            "reasoning": "deep_analysis",
        }

        role = MODEL_ROUTING.get(task_type, ModelRole.CREATIVE)
        if role == ModelRole.QUICK:
            pattern = "rapid_iteration"
        elif role == ModelRole.CREATIVE:
            pattern = "creative_synthesis"
        else:
            pattern = "deep_analysis"

        result = self.mindset.execute({
            "capability": "analyze",
            "problem": prompt,
            "pattern": pattern,
            "store_reasoning": True,
        }, context)

        if result.success:
            return result.output
        return None

    def _run_cmd(self, cmd: List[str], cwd: str = None, timeout: int = 300) -> tuple[bool, str]:
        """Run shell command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def _run_pipeline(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Run full CI/CD pipeline."""
        target = input_data.get("target", ".")
        stages = input_data.get("stages", ["validate", "analyze", "test", "build"])
        environment = input_data.get("environment", "dev")

        # Create pipeline run
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_run = PipelineRun(
            id=run_id,
            started_at=datetime.now(),
        )

        results = {}

        for stage in stages:
            logger.info(f"Pipeline stage: {stage}")

            stage_input = {**input_data, "capability": stage}

            if stage == "validate":
                result = self._validate(stage_input, context)
            elif stage == "analyze":
                result = self._analyze(stage_input, context)
            elif stage == "test":
                result = self._test(stage_input, context)
            elif stage == "build":
                result = self._build(stage_input, context)
            elif stage == "improve":
                result = self._improve(stage_input, context)
            elif stage == "deploy":
                result = self._deploy(stage_input, context)
            else:
                continue

            results[stage] = {
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }

            self._current_run.stages[stage] = results[stage]

            # Stop pipeline on critical failure
            if not result.success and stage in ["validate", "test"]:
                self._current_run.status = "failed"
                self._current_run.errors.append(f"Stage {stage} failed: {result.error}")
                break

        # Finalize run
        if self._current_run.status != "failed":
            self._current_run.status = "completed"

        # Learn from run
        self._learn_from_run(context)

        # Save run
        self._save_run()

        return SkillResult(
            success=self._current_run.status == "completed",
            output={
                "run_id": run_id,
                "status": self._current_run.status,
                "stages": results,
                "artifacts": self._current_run.artifacts,
                "improvements": self._current_run.improvements,
                "errors": self._current_run.errors,
            },
            error="; ".join(self._current_run.errors) if self._current_run.errors else None,
            skill_id=self.metadata().id,
        )

    def _validate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Validate code using quick model (CodeGemma)."""
        target = input_data.get("target", ".")

        results = {
            "lint": None,
            "type_check": None,
            "syntax": None,
        }

        # Run ruff for linting
        success, output = self._run_cmd(["ruff", "check", target, "--output-format", "json"])
        results["lint"] = {"success": success, "output": output[:2000]}

        # Run mypy for type checking (if available)
        success, output = self._run_cmd(["mypy", target, "--ignore-missing-imports"])
        results["type_check"] = {"success": success, "output": output[:2000]}

        # Use quick model for additional validation
        if self.mindset:
            quick_check = self._call_model(
                "validate",
                f"Quick validation check for code in {target}. Check for obvious issues.",
                context,
            )
            if quick_check:
                results["ai_check"] = quick_check.get("conclusion", "")

        all_passed = all(r.get("success", True) for r in results.values() if isinstance(r, dict))

        return SkillResult(
            success=all_passed,
            output=results,
            error=None if all_passed else "Validation failed",
            skill_id=self.metadata().id,
        )

    def _analyze(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Deep analysis using reasoning model (DeepSeek)."""
        target = input_data.get("target", ".")

        # Get git diff for analysis
        success, diff = self._run_cmd(["git", "diff", "--cached", target])
        if not success:
            success, diff = self._run_cmd(["git", "diff", target])

        analysis = {}

        if self.mindset:
            # Deep analysis with DeepSeek
            result = self._call_model(
                "analyze",
                f"""
                Analyze the following code changes:

                ```diff
                {diff[:4000]}
                ```

                Provide:
                1. Summary of changes
                2. Potential issues or bugs
                3. Security concerns
                4. Performance implications
                5. Suggested improvements
                """,
                context,
            )

            if result:
                analysis = {
                    "summary": result.get("conclusion", ""),
                    "reasoning_trace": result.get("reasoning_trace", []),
                    "diff_size": len(diff),
                }

        return SkillResult(
            success=True,
            output=analysis,
            skill_id=self.metadata().id,
        )

    def _test(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Run tests."""
        target = input_data.get("target", ".")
        options = input_data.get("options", {})

        results = {
            "pytest": None,
            "coverage": None,
        }

        # Run pytest
        pytest_args = ["pytest", target, "-v", "--tb=short"]
        if options.get("coverage", True):
            pytest_args.extend(["--cov", "--cov-report=json"])

        success, output = self._run_cmd(pytest_args, timeout=600)
        results["pytest"] = {
            "success": success,
            "output": output[:3000],
        }

        # Parse coverage if available
        if Path("coverage.json").exists():
            try:
                with open("coverage.json") as f:
                    cov_data = json.load(f)
                results["coverage"] = {
                    "total": cov_data.get("totals", {}).get("percent_covered", 0),
                }
            except Exception:
                pass

        return SkillResult(
            success=success,
            output=results,
            error=None if success else "Tests failed",
            skill_id=self.metadata().id,
        )

    def _build(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Build Docker images and artifacts."""
        target = input_data.get("target", ".")
        environment = input_data.get("environment", "dev")

        results = {}

        # Build using Docker skill if available
        if self.docker:
            build_result = self.docker.execute({
                "capability": "build",
                "target": target,
            }, context)
            results["docker_build"] = {
                "success": build_result.success,
                "output": build_result.output,
            }

            if build_result.success and self._current_run:
                self._current_run.artifacts.append(f"cli-ai:{environment}")
        else:
            # Fallback to direct docker command
            success, output = self._run_cmd(
                ["docker", "build", "-t", f"cli-ai:{environment}", target],
                timeout=600,
            )
            results["docker_build"] = {"success": success, "output": output[:2000]}

        return SkillResult(
            success=results.get("docker_build", {}).get("success", False),
            output=results,
            error=None if results.get("docker_build", {}).get("success") else "Build failed",
            skill_id=self.metadata().id,
        )

    def _improve(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Generate improvements using creative model (Qwen3)."""
        target = input_data.get("target", ".")

        improvements = []

        if self.mindset:
            # Use creative model for improvements
            result = self._call_model(
                "improve",
                f"""
                Review the code in {target} and suggest concrete improvements:

                1. Code quality improvements
                2. Performance optimizations
                3. Better error handling
                4. Cleaner abstractions
                5. Missing test cases

                For each improvement, provide:
                - What to change
                - Why it's better
                - Code snippet if applicable
                """,
                context,
            )

            if result:
                improvements.append({
                    "type": "ai_suggestions",
                    "content": result.get("conclusion", ""),
                    "model": "qwen3",
                    "timestamp": datetime.now().isoformat(),
                })

        if self._current_run:
            self._current_run.improvements.extend(improvements)

        return SkillResult(
            success=True,
            output={"improvements": improvements},
            skill_id=self.metadata().id,
        )

    def _deploy(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Deploy to environment."""
        environment = input_data.get("environment", "dev")

        # Safety check for production
        if environment == "production" and self.safety:
            safety_result = self.safety.execute({
                "action_type": "deploy",
                "target_path": "production",
                "details": "Production deployment requested",
            }, context)

            if not safety_result.output.get("allowed", False):
                return SkillResult(
                    success=False,
                    output=None,
                    error="Production deployment requires approval",
                    skill_id=self.metadata().id,
                )

        results = {}

        # Deploy using docker-compose
        if self.docker:
            deploy_result = self.docker.execute({
                "capability": "compose",
                "compose_action": "up",
                "compose_file": f"docker-compose.{environment}.yml" if environment != "dev" else "docker-compose.yml",
            }, context)
            results["compose"] = {
                "success": deploy_result.success,
                "output": deploy_result.output,
            }

        return SkillResult(
            success=results.get("compose", {}).get("success", False),
            output=results,
            error=None if results.get("compose", {}).get("success") else "Deployment failed",
            skill_id=self.metadata().id,
        )

    def _improve_skill(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Improve an existing skill using multi-model reasoning."""
        skill_id = input_data.get("target", "")

        if not skill_id:
            return SkillResult(
                success=False,
                output=None,
                error="No skill ID specified",
                skill_id=self.metadata().id,
            )

        # Find skill file
        skill_path = Path(f"skills/{skill_id.replace('/', os.sep)}/skill.py")
        if not skill_path.exists():
            # Try alternate paths
            for pattern in ["skills/**/*.py"]:
                for p in Path("skills").rglob("skill.py"):
                    if skill_id in str(p):
                        skill_path = p
                        break

        if not skill_path.exists():
            return SkillResult(
                success=False,
                output=None,
                error=f"Skill not found: {skill_id}",
                skill_id=self.metadata().id,
            )

        # Read current skill
        skill_code = skill_path.read_text()

        improvements = []

        # Step 1: Analyze with DeepSeek
        if self.mindset:
            analysis = self._call_model(
                "analyze",
                f"""
                Analyze this skill implementation and identify improvements:

                ```python
                {skill_code[:6000]}
                ```

                Focus on:
                1. Error handling gaps
                2. Missing capabilities
                3. Performance issues
                4. Better abstractions
                """,
                context,
            )

            if analysis:
                improvements.append({
                    "phase": "analysis",
                    "model": "deepseek",
                    "findings": analysis.get("conclusion", ""),
                })

            # Step 2: Generate improvements with Qwen3
            generation = self._call_model(
                "improve",
                f"""
                Based on this skill:

                ```python
                {skill_code[:4000]}
                ```

                And these findings:
                {analysis.get("conclusion", "") if analysis else "No analysis available"}

                Generate improved code for the skill. Focus on the most impactful improvements.
                Return only the improved code sections, not the entire file.
                """,
                context,
            )

            if generation:
                improvements.append({
                    "phase": "generation",
                    "model": "qwen3",
                    "suggestions": generation.get("conclusion", ""),
                })

        # Store in memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Skill improvement analysis for {skill_id}",
                "memory_type": "procedural",
                "importance": 0.8,
                "context": {
                    "skill_id": skill_id,
                    "improvements": len(improvements),
                },
            }, context)

        return SkillResult(
            success=True,
            output={
                "skill_id": skill_id,
                "skill_path": str(skill_path),
                "improvements": improvements,
            },
            skill_id=self.metadata().id,
        )

    def _create_skill(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Create a new skill from specification."""
        skill_spec = input_data.get("skill_spec", {})

        if not skill_spec:
            return SkillResult(
                success=False,
                output=None,
                error="No skill specification provided",
                skill_id=self.metadata().id,
            )

        skill_id = skill_spec.get("id", "")
        skill_name = skill_spec.get("name", "")
        skill_description = skill_spec.get("description", "")
        capabilities = skill_spec.get("capabilities", [])

        if not skill_id:
            return SkillResult(
                success=False,
                output=None,
                error="Skill ID required",
                skill_id=self.metadata().id,
            )

        # Generate skill code using Qwen3
        if self.mindset:
            generation = self._call_model(
                "generate",
                f"""
                Generate a complete Python skill implementation:

                Skill ID: {skill_id}
                Name: {skill_name}
                Description: {skill_description}
                Capabilities: {", ".join(capabilities)}

                Follow this structure:
                1. Import from skills.base (Skill, SkillCategory, etc.)
                2. Create a class that extends Skill
                3. Implement metadata(), input_schema(), output_schema(), execute()
                4. Add handlers for each capability
                5. Include proper error handling
                6. Add docstrings and type hints

                Return the complete Python code.
                """,
                context,
            )

            if generation:
                # Extract code from response
                code = generation.get("conclusion", "")

                # Create skill directory
                skill_dir = Path(f"skills/{skill_id.replace('/', os.sep)}")
                skill_dir.mkdir(parents=True, exist_ok=True)

                # Write skill file
                skill_file = skill_dir / "skill.py"
                skill_file.write_text(code)

                # Create manifest
                manifest = {
                    "id": skill_id,
                    "name": skill_name,
                    "description": skill_description,
                    "version": "1.0.0",
                    "category": skill_spec.get("category", "automation"),
                    "capabilities": capabilities,
                    "author": "CI/CD Pipeline (auto-generated)",
                    "created_at": datetime.now().isoformat(),
                }

                manifest_file = skill_dir / "manifest.yaml"
                import yaml
                manifest_file.write_text(yaml.dump(manifest, default_flow_style=False))

                # Validate with quick model
                validation = self._call_model(
                    "validate",
                    f"Quick syntax check for this Python code:\n{code[:2000]}",
                    context,
                )

                # Use growth skill to integrate
                if self.growth:
                    self.growth.execute({
                        "capability": "integrate",
                        "skill_spec": {
                            "id": skill_id,
                            "name": skill_name,
                            "description": skill_description,
                            "acquisition_type": "generated",
                        },
                    }, context)

                return SkillResult(
                    success=True,
                    output={
                        "skill_id": skill_id,
                        "skill_path": str(skill_file),
                        "manifest_path": str(manifest_file),
                        "validation": validation.get("conclusion", "") if validation else "Not validated",
                    },
                    skill_id=self.metadata().id,
                )

        return SkillResult(
            success=False,
            output=None,
            error="Failed to generate skill",
            skill_id=self.metadata().id,
        )

    def _status(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Get current pipeline status."""
        if not self._current_run:
            return SkillResult(
                success=True,
                output={"status": "idle", "message": "No pipeline running"},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=True,
            output={
                "run_id": self._current_run.id,
                "status": self._current_run.status,
                "started_at": self._current_run.started_at.isoformat(),
                "stages": self._current_run.stages,
                "artifacts": self._current_run.artifacts,
                "errors": self._current_run.errors,
            },
            skill_id=self.metadata().id,
        )

    def _history(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Get pipeline run history."""
        runs = []

        for run_file in sorted(self._runs_dir.glob("*.json"), reverse=True)[:20]:
            try:
                with open(run_file) as f:
                    runs.append(json.load(f))
            except Exception:
                pass

        return SkillResult(
            success=True,
            output={"runs": runs, "count": len(runs)},
            skill_id=self.metadata().id,
        )

    def _learn_from_run(self, context: SkillContext) -> None:
        """Store pipeline outcomes in memory."""
        if not self._current_run or not self.memory:
            return

        summary = f"Pipeline run {self._current_run.id}: {self._current_run.status}"
        if self._current_run.errors:
            summary += f" with {len(self._current_run.errors)} errors"
        if self._current_run.improvements:
            summary += f", {len(self._current_run.improvements)} improvements suggested"

        self.memory.execute({
            "capability": "experience",
            "content": summary,
            "memory_type": "procedural",
            "importance": 0.7 if self._current_run.status == "completed" else 0.9,
            "context": {
                "type": "pipeline_run",
                "run_id": self._current_run.id,
                "status": self._current_run.status,
                "stages": list(self._current_run.stages.keys()),
            },
        }, context)

    def _save_run(self) -> None:
        """Save pipeline run to disk."""
        if not self._current_run:
            return

        run_data = {
            "id": self._current_run.id,
            "started_at": self._current_run.started_at.isoformat(),
            "status": self._current_run.status,
            "stages": self._current_run.stages,
            "artifacts": self._current_run.artifacts,
            "improvements": self._current_run.improvements,
            "errors": self._current_run.errors,
        }

        run_file = self._runs_dir / f"{self._current_run.id}.json"
        with open(run_file, "w") as f:
            json.dump(run_data, f, indent=2)


__all__ = ["CICDPipelineSkill"]
