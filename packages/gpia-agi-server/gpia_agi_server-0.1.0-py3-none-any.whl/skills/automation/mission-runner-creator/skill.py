"""
Mission Runner Creator Skill
============================
Generate multi-agent mission runners for complex orchestrated tasks.

This skill enables GPIA to create new mission runners dynamically,
teaching the system how to automate any complex workflow using
multiple LLM agents working in concert.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from enum import Enum

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from skills.base import BaseSkill, SkillCategory, SkillContext, SkillLevel, SkillResult
except ImportError:
    # Fallback definitions
    @dataclass
    class SkillResult:
        success: bool
        output: Dict[str, Any]
        error: Optional[str] = None

    @dataclass
    class SkillContext:
        agent_role: str = "system"

    class SkillCategory:
        AUTOMATION = "automation"

    class SkillLevel:
        ADVANCED = "advanced"

    class BaseSkill:
        def execute(self, params: Dict, context: SkillContext) -> SkillResult:
            raise NotImplementedError


class AgentRole(str, Enum):
    """Available LLM agents for mission phases."""
    ARCHITECT = "deepseek-r1"      # System design, planning
    CREATOR = "qwen3"              # Code generation, creative
    FAST = "codegemma"             # Quick tasks, validation
    SYNTHESIZER = "gpt-oss:20b"    # Integration, synthesis
    REASONING = "deepseek-r1"      # Deep analysis


@dataclass
class PhaseSpec:
    """Specification for a mission phase."""
    name: str
    description: str
    agent: AgentRole
    parallel: bool = False
    timeout_seconds: int = 180
    depends_on: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class MissionSpec:
    """Complete mission specification."""
    name: str
    goal: str
    phases: List[PhaseSpec]
    deliverables: List[str]
    estimated_minutes: int = 10
    include_pass: bool = True
    include_parallel: bool = True
    include_memory: bool = True


class MissionRunnerCreator(BaseSkill):
    """
    Skill for creating multi-agent mission runners.

    Capabilities:
    - design_mission: Design mission structure with phases
    - generate_runner: Generate Python mission runner script
    - execute_mission: Run a mission and monitor progress
    - list_missions: List all created missions
    """

    SKILL_ID = "automation/mission-runner-creator"
    SKILL_NAME = "Mission Runner Creator"
    SKILL_DESCRIPTION = "Generates multi-agent mission runners for complex workflows."
    SKILL_CATEGORY = SkillCategory.AUTOMATION
    SKILL_LEVEL = SkillLevel.ADVANCED
    SKILL_TAGS = ["automation", "orchestration", "multi-agent", "mission-runner", "code-generation"]

    def __init__(self):
        self.missions_dir = PROJECT_ROOT / "runs" / "missions"
        self.missions_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path(__file__).parent / "templates"

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute a capability of this skill."""
        capability = params.get("capability", "design_mission")

        handlers = {
            "design_mission": self._design_mission,
            "generate_runner": self._generate_runner,
            "execute_mission": self._execute_mission,
            "list_missions": self._list_missions,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output={},
                error=f"Unknown capability: {capability}"
            )

        try:
            return handler(params, context)
        except Exception as e:
            return SkillResult(
                success=False,
                output={},
                error=str(e)
            )

    def _design_mission(self, params: Dict, context: SkillContext) -> SkillResult:
        """Design a mission structure with phases and agent assignments."""
        goal = params.get("goal", "")
        constraints = params.get("constraints", "")
        deliverables = params.get("deliverables", [])

        if not goal:
            return SkillResult(False, {}, "Goal is required")

        # Analyze goal to determine phases
        phases = self._analyze_goal_for_phases(goal, constraints)

        # Calculate timing
        total_sequential = sum(p.timeout_seconds for p in phases if not p.parallel)
        parallel_groups = {}
        for p in phases:
            if p.parallel:
                key = tuple(p.depends_on) if p.depends_on else ("root",)
                if key not in parallel_groups:
                    parallel_groups[key] = []
                parallel_groups[key].append(p.timeout_seconds)

        parallel_time = sum(max(times) for times in parallel_groups.values()) if parallel_groups else 0
        estimated_minutes = (total_sequential + parallel_time) // 60 + 1

        mission_spec = MissionSpec(
            name=self._goal_to_name(goal),
            goal=goal,
            phases=phases,
            deliverables=deliverables or self._infer_deliverables(goal),
            estimated_minutes=estimated_minutes,
        )

        return SkillResult(
            success=True,
            output={
                "mission_spec": asdict(mission_spec),
                "phases": [asdict(p) for p in phases],
                "estimated_time": f"{estimated_minutes} minutes"
            }
        )

    def _analyze_goal_for_phases(self, goal: str, constraints: str) -> List[PhaseSpec]:
        """Analyze goal to determine optimal phase structure."""
        goal_lower = goal.lower()
        phases = []

        # Always start with planning/architecture
        phases.append(PhaseSpec(
            name="architecture",
            description=f"Design the architecture for: {goal}",
            agent=AgentRole.ARCHITECT,
            outputs=["architecture_spec"]
        ))

        # Determine if we need research phase
        if any(kw in goal_lower for kw in ["learn", "understand", "research", "explore"]):
            phases.append(PhaseSpec(
                name="research",
                description="Deep research on requirements and best practices",
                agent=AgentRole.REASONING,
                parallel=True,
                depends_on=["architecture"],
                outputs=["research_findings"]
            ))

        # Implementation phases (often parallel)
        if any(kw in goal_lower for kw in ["build", "create", "implement", "generate", "develop"]):
            # Backend
            if any(kw in goal_lower for kw in ["api", "backend", "server", "endpoint"]):
                phases.append(PhaseSpec(
                    name="backend",
                    description="Implement backend components",
                    agent=AgentRole.CREATOR,
                    parallel=True,
                    depends_on=["architecture"],
                    outputs=["backend_code"]
                ))

            # Frontend
            if any(kw in goal_lower for kw in ["ui", "frontend", "interface", "vue", "react", "component"]):
                phases.append(PhaseSpec(
                    name="frontend",
                    description="Implement frontend components",
                    agent=AgentRole.CREATOR,
                    parallel=True,
                    depends_on=["architecture"],
                    outputs=["frontend_code"]
                ))

            # Generic implementation if no specific type detected
            if not any(kw in goal_lower for kw in ["api", "backend", "ui", "frontend"]):
                phases.append(PhaseSpec(
                    name="implementation",
                    description="Implement core functionality",
                    agent=AgentRole.CREATOR,
                    depends_on=["architecture"],
                    outputs=["implementation_code"]
                ))

        # Integration phase
        phases.append(PhaseSpec(
            name="integration",
            description="Integrate all components and generate documentation",
            agent=AgentRole.SYNTHESIZER,
            depends_on=[p.name for p in phases[1:]],  # Depends on all previous
            outputs=["integration_guide"]
        ))

        # Validation phase
        phases.append(PhaseSpec(
            name="validation",
            description="Validate outputs and check for errors",
            agent=AgentRole.FAST,
            depends_on=["integration"],
            outputs=["validation_report"]
        ))

        return phases

    def _goal_to_name(self, goal: str) -> str:
        """Convert goal to a valid mission name."""
        import re
        # Extract key words
        words = re.findall(r'\b\w+\b', goal.lower())
        # Filter common words
        stopwords = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'with', 'using', 'that', 'this'}
        keywords = [w for w in words if w not in stopwords][:4]
        return "_".join(keywords) + "_mission"

    def _infer_deliverables(self, goal: str) -> List[str]:
        """Infer expected deliverables from goal."""
        deliverables = []
        goal_lower = goal.lower()

        if "ui" in goal_lower or "interface" in goal_lower or "frontend" in goal_lower:
            deliverables.append("Vue components")
        if "api" in goal_lower or "backend" in goal_lower:
            deliverables.append("API endpoints")
        if "learn" in goal_lower:
            deliverables.append("Knowledge base entries")

        deliverables.append("Integration documentation")
        deliverables.append("Validation report")

        return deliverables

    def _generate_runner(self, params: Dict, context: SkillContext) -> SkillResult:
        """Generate a complete Python mission runner script."""
        mission_spec_dict = params.get("mission_spec")
        output_path = params.get("output_path")
        include_pass = params.get("include_pass", True)
        include_parallel = params.get("include_parallel", True)
        include_memory = params.get("include_memory", True)

        if not mission_spec_dict:
            return SkillResult(False, {}, "mission_spec is required")

        # Reconstruct MissionSpec
        phases = [PhaseSpec(**p) for p in mission_spec_dict.get("phases", [])]
        mission_spec = MissionSpec(
            name=mission_spec_dict["name"],
            goal=mission_spec_dict["goal"],
            phases=phases,
            deliverables=mission_spec_dict.get("deliverables", []),
            estimated_minutes=mission_spec_dict.get("estimated_minutes", 10),
            include_pass=include_pass,
            include_parallel=include_parallel,
            include_memory=include_memory,
        )

        # Generate the script
        script = self._render_mission_script(mission_spec)

        # Determine output path
        if not output_path:
            output_path = PROJECT_ROOT / f"{mission_spec.name}.py"
        else:
            output_path = Path(output_path)

        # Write script
        output_path.write_text(script, encoding='utf-8')

        return SkillResult(
            success=True,
            output={
                "script_path": str(output_path),
                "components": [
                    f"{p.name.title()}Phase" for p in phases
                ],
                "mission_name": mission_spec.name
            }
        )

    def _render_mission_script(self, spec: MissionSpec) -> str:
        """Render the complete mission runner script."""

        # Generate phase classes
        phase_classes = []
        for phase in spec.phases:
            phase_classes.append(self._render_phase_class(phase))

        # Generate imports
        imports = self._render_imports(spec)

        # Generate orchestrator
        orchestrator = self._render_orchestrator(spec)

        # Generate main
        main_block = self._render_main(spec)

        script = f'''#!/usr/bin/env python3
"""
{spec.name.replace("_", " ").title()}
{"=" * len(spec.name)}
Auto-generated mission runner by GPIA Mission Runner Creator skill.

Goal: {spec.goal}
Phases: {len(spec.phases)}
Estimated Time: {spec.estimated_minutes} minutes

Generated: {datetime.now().isoformat()}
"""

{imports}

# =============================================================================
# CONFIGURATION
# =============================================================================

OLLAMA_BASE = "http://localhost:11434"
PROJECT_ROOT = Path(__file__).parent


class AgentRole(str, Enum):
    ARCHITECT = "deepseek-r1"
    CREATOR = "qwen3"
    FAST = "codegemma"
    SYNTHESIZER = "gpt-oss:20b"
    REASONING = "deepseek-r1"


# =============================================================================
# PHASE IMPLEMENTATIONS
# =============================================================================

{chr(10).join(phase_classes)}


# =============================================================================
# ORCHESTRATOR
# =============================================================================

{orchestrator}


# =============================================================================
# MAIN
# =============================================================================

{main_block}
'''
        return script

    def _render_imports(self, spec: MissionSpec) -> str:
        """Render import statements."""
        imports = [
            "import os",
            "import sys",
            "import json",
            "import time",
            "from pathlib import Path",
            "from datetime import datetime",
            "from dataclasses import dataclass, field, asdict",
            "from typing import Dict, List, Any, Optional, Tuple",
            "from enum import Enum",
        ]

        if spec.include_parallel:
            imports.append("from concurrent.futures import ThreadPoolExecutor, as_completed")

        return "\n".join(imports)

    def _render_phase_class(self, phase: PhaseSpec) -> str:
        """Render a single phase class."""
        class_name = f"{phase.name.title().replace('_', '')}Phase"

        return f'''
@dataclass
class {class_name}:
    """
    {phase.description}
    Agent: {phase.agent.value}
    Parallel: {phase.parallel}
    """
    name: str = "{phase.name}"
    agent: str = "{phase.agent.value}"
    timeout: int = {phase.timeout_seconds}
    parallel: bool = {phase.parallel}
    depends_on: List[str] = field(default_factory=lambda: {phase.depends_on})

    def execute(self, context: Dict[str, Any], client) -> Dict[str, Any]:
        """Execute this phase."""
        start = time.time()

        system = "You are an expert assistant helping with: {phase.description}"
        prompt = f"""
Phase: {phase.name}
Goal: {{context.get('goal', '')}}
Previous Results: {{json.dumps(context.get('previous', {{}}), indent=2)}}

Execute this phase and provide structured output.
"""

        try:
            response = self._call_llm(client, prompt, system)
            return {{
                "status": "completed",
                "phase": self.name,
                "output": response,
                "duration": time.time() - start
            }}
        except Exception as e:
            return {{
                "status": "failed",
                "phase": self.name,
                "error": str(e),
                "duration": time.time() - start
            }}

    def _call_llm(self, client, prompt: str, system: str) -> str:
        """Call the LLM for this phase."""
        import urllib.request
        payload = {{
            "model": self.agent,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {{"temperature": 0.3}}
        }}
        req = urllib.request.Request(
            f"{{client}}/api/generate",
            data=json.dumps(payload).encode('utf-8'),
            headers={{"Content-Type": "application/json"}},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get("response", "")
'''

    def _render_orchestrator(self, spec: MissionSpec) -> str:
        """Render the orchestrator class."""
        phase_inits = []
        for phase in spec.phases:
            class_name = f"{phase.name.title().replace('_', '')}Phase"
            phase_inits.append(f"            {class_name}(),")

        return f'''
class {spec.name.title().replace("_", "")}Orchestrator:
    """Orchestrates the {spec.name.replace("_", " ")}."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = OLLAMA_BASE
        self.phases = [
{chr(10).join(phase_inits)}
        ]
        self.results = {{}}
        self.context = {{"goal": """{spec.goal}"""}}

    def run(self) -> Dict[str, Any]:
        """Execute all phases."""
        print("=" * 70)
        print("    {spec.name.replace("_", " ").upper()}")
        print("=" * 70)
        print(f"Goal: {spec.goal}")
        print(f"Phases: {{len(self.phases)}}")
        print("=" * 70 + "\\n")

        start = time.time()

        for phase in self.phases:
            print(f"[{{phase.name.upper()}}] Starting... ({{phase.agent}})")
            result = phase.execute(self.context, self.client)
            self.results[phase.name] = result

            if result["status"] == "completed":
                print(f"[{{phase.name.upper()}}] Completed in {{result['duration']:.1f}}s")
                self.context["previous"] = self.context.get("previous", {{}})
                self.context["previous"][phase.name] = result.get("output", "")
            else:
                print(f"[{{phase.name.upper()}}] FAILED: {{result.get('error', 'Unknown')}}")

        total = time.time() - start
        print("\\n" + "=" * 70)
        print("MISSION COMPLETE")
        print(f"Duration: {{total:.1f}}s")
        print("=" * 70)

        return {{
            "status": "completed",
            "duration": total,
            "phases": self.results
        }}
'''

    def _render_main(self, spec: MissionSpec) -> str:
        """Render the main block."""
        class_name = f"{spec.name.title().replace('_', '')}Orchestrator"

        return f'''
def main():
    import argparse
    parser = argparse.ArgumentParser(description="{spec.goal}")
    parser.add_argument("--dry-run", action="store_true", help="Don't execute LLM calls")
    args = parser.parse_args()

    orchestrator = {class_name}(dry_run=args.dry_run)
    result = orchestrator.run()

    # Save report
    report_path = PROJECT_ROOT / "runs" / f"{spec.name}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"Report saved: {{report_path}}")


if __name__ == "__main__":
    main()
'''

    def _execute_mission(self, params: Dict, context: SkillContext) -> SkillResult:
        """Execute a mission runner script."""
        script_path = params.get("script_path")
        dry_run = params.get("dry_run", False)
        verbose = params.get("verbose", True)

        if not script_path:
            return SkillResult(False, {}, "script_path is required")

        script_path = Path(script_path)
        if not script_path.exists():
            return SkillResult(False, {}, f"Script not found: {script_path}")

        # Build command
        cmd = [sys.executable, str(script_path)]
        if dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(PROJECT_ROOT)
            )

            return SkillResult(
                success=result.returncode == 0,
                output={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "script": str(script_path)
                }
            )
        except subprocess.TimeoutExpired:
            return SkillResult(False, {}, "Mission timed out after 10 minutes")
        except Exception as e:
            return SkillResult(False, {}, str(e))

    def _list_missions(self, params: Dict, context: SkillContext) -> SkillResult:
        """List all created mission runners."""
        missions = []

        # Find mission runner scripts
        for py_file in PROJECT_ROOT.glob("*_mission.py"):
            missions.append({
                "name": py_file.stem,
                "path": str(py_file),
                "modified": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
            })

        # Also check runs directory
        runs_dir = PROJECT_ROOT / "runs"
        if runs_dir.exists():
            for json_file in runs_dir.glob("*_mission_*.json"):
                missions.append({
                    "name": json_file.stem,
                    "path": str(json_file),
                    "type": "report"
                })

        return SkillResult(
            success=True,
            output={"missions": missions, "count": len(missions)}
        )


# Skill instance for registry
skill = MissionRunnerCreator()


def execute(params: Dict[str, Any], context: SkillContext) -> SkillResult:
    """Entry point for skill execution."""
    return skill.execute(params, context)


if __name__ == "__main__":
    # Test the skill
    ctx = SkillContext()

    # Test design_mission
    print("Testing design_mission...")
    result = skill.execute({
        "capability": "design_mission",
        "goal": "Build the GPAI Live-Link interface with adapter management and neural HUD",
        "deliverables": ["Vue components", "API endpoints", "Integration guide"]
    }, ctx)

    print(f"Success: {result.success}")
    print(f"Phases: {len(result.output.get('phases', []))}")
    print(f"Estimated: {result.output.get('estimated_time')}")

    if result.success:
        # Test generate_runner
        print("\nTesting generate_runner...")
        gen_result = skill.execute({
            "capability": "generate_runner",
            "mission_spec": result.output["mission_spec"],
            "output_path": str(PROJECT_ROOT / "test_generated_mission.py")
        }, ctx)

        print(f"Generated: {gen_result.output.get('script_path')}")
