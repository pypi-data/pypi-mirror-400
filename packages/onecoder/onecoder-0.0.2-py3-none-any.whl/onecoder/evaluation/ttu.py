from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import os

@dataclass
class TTUResult:
    """Result of a Time-To-Understand (TTU) evaluation."""
    score: float  # 0.0 to 1.0
    passed: bool
    context_found: List[str] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

class TTUEvaluator:
    """Evaluates whether the current context is sufficient to start a task."""

    def __init__(self, threshold: float = 0.8): # Increased threshold due to strict governance
        self.threshold = threshold

    def evaluate(self, sprint_path: Optional[Path] = None) -> TTUResult:
        """
        Evaluates the context of the given sprint path.
        If no path is provided, attempts to find the current active sprint.
        """
        repo_root = self._find_repo_root()

        if sprint_path is None:
            sprint_path = self._find_active_sprint(repo_root)

        if sprint_path is None:
            return TTUResult(
                score=0.0,
                passed=False,
                missing_context=["Active Sprint Directory"],
                failure_modes=["Uninitialized Environment"],
                recommendations=["Initialize a sprint using 'sprint init' or 'onecoder init'"]
            )

        score = 0.0
        missing = []
        found = []
        failure_modes = []
        recommendations = []
        details = {}

        # 0. Check for AGENTS.md (Governance) - Weight: 0.2
        agents_md = repo_root / "AGENTS.md"
        if agents_md.exists():
            score += 0.2
            found.append("AGENTS.md")
        else:
            missing.append("AGENTS.md (Root)")
            failure_modes.append("Governance Blindness")
            recommendations.append("Create AGENTS.md in repo root to define agent policies.")

        # 1. Check for sprint.json (Metadata) - Weight: 0.2
        sprint_json = sprint_path / "sprint.json"
        if sprint_json.exists():
            found.append("sprint.json")
            try:
                with open(sprint_json, "r") as f:
                    data = json.load(f)

                # Check for goals
                if data.get("goals", {}).get("primary"):
                    score += 0.15
                    details["goals"] = "Present"
                else:
                    missing.append("Primary Goal in sprint.json")
                    failure_modes.append("Goal Ambiguity")
                    recommendations.append("Define a primary goal in sprint.json")

                # Check for tasks
                if data.get("tasks"):
                    score += 0.05
                    details["tasks"] = f"{len(data['tasks'])} tasks found"
                else:
                    # Not strictly missing if just starting, but good to have
                    details["tasks"] = "None"

            except Exception as e:
                missing.append(f"Valid sprint.json ({str(e)})")
                failure_modes.append("Corrupt Metadata")
        else:
            missing.append("sprint.json")
            failure_modes.append("Missing Metadata")
            recommendations.append("Run 'sprint init' to generate sprint structure.")

        # 2. Check for Context/Walkthrough - Weight: 0.3
        # Look for README.md or WALKTHROUGH.md or context folder
        context_files = ["README.md", "WALKTHROUGH.md", "context/context.md"]
        context_found_count = 0
        for cf in context_files:
            if (sprint_path / cf).exists():
                context_found_count += 1
                found.append(cf)

        if context_found_count > 0:
            score += 0.3
        else:
            missing.append("Context Documentation (README.md or WALKTHROUGH.md)")
            failure_modes.append("Context Blindness")
            recommendations.append("Add a README.md or WALKTHROUGH.md describing the sprint.")

        # 3. Check for Media/Reference (Optional but good) - Weight: 0.1
        media_dir = sprint_path / "media"
        if media_dir.exists() and any(media_dir.iterdir()):
            score += 0.1
            found.append("media/")

        # 4. Check for Planning - Weight: 0.2
        planning_dir = sprint_path / "planning"
        if planning_dir.exists():
            score += 0.2
            found.append("planning/")
        else:
            # Maybe TODO.md?
            if (sprint_path / "TODO.md").exists():
                score += 0.2
                found.append("TODO.md")
            else:
                missing.append("Planning Documents")
                failure_modes.append("Unplanned Execution")
                recommendations.append("Create a plan in planning/ or TODO.md")

        # Normalize score if needed, but here simple sum max is 1.0

        passed = score >= self.threshold

        return TTUResult(
            score=min(score, 1.0),
            passed=passed,
            context_found=found,
            missing_context=missing,
            failure_modes=failure_modes,
            recommendations=recommendations,
            details=details
        )

    def _find_repo_root(self) -> Path:
        """Finds the repository root."""
        curr = Path.cwd()
        root = curr
        # Traverse up
        while root != root.parent:
            if (root / ".git").exists() or (root / ".sprint").exists():
                return root
            root = root.parent
        return curr # Default to cwd if not found

    def _find_active_sprint(self, root: Optional[Path] = None) -> Optional[Path]:
        # Simple heuristic: Look for .sprint folder in root
        if root:
             sprint_dir = root / ".sprint"
             if sprint_dir.exists():
                # Get latest subdir
                subdirs = sorted([d for d in sprint_dir.iterdir() if d.is_dir()])
                if subdirs:
                    return subdirs[-1]
             return None

        # Fallback if root not provided (legacy)
        cwd = Path.cwd()
        curr_root = cwd
        while curr_root != curr_root.parent:
            sprint_dir = curr_root / ".sprint"
            if sprint_dir.exists():
                subdirs = sorted([d for d in sprint_dir.iterdir() if d.is_dir()])
                if subdirs:
                    return subdirs[-1]
            curr_root = curr_root.parent
        return None
