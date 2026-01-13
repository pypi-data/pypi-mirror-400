import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .state import SprintStateManager


class SprintPreflight:
    def __init__(self, sprint_dir: Path, repo_root: Path):
        self.sprint_dir = sprint_dir
        self.repo_root = repo_root
        self.state_manager = SprintStateManager(sprint_dir)
        self.results = []

    def run_all(self) -> Tuple[int, List[Dict[str, Any]]]:
        self.results = []

        # 1. Task Breakdown Check
        self.results.append(self.check_task_breakdown())

        # 2. Documentation Check
        self.results.append(self.check_documentation())

        # 3. Spec Tracing Check
        self.results.append(self.check_spec_tracing())

        # 4. Component Scope Check
        self.results.append(self.check_component_scope())

        # 5. Governance Check
        self.results.append(self.check_governance())

        # 6. Retro Sync Check
        self.results.append(self.check_retro_sync())

        # 7. LOC Limit Check (New Zero Debt Policy)
        self.results.append(self.check_loc_limit())

        # 8. Secret Scanning (New Zero Debt Policy)
        self.results.append(self.check_secrets())

        # Calculate score
        passed_count = sum(1 for r in self.results if r["status"] == "passed")
        total_count = len(self.results)
        score = int((passed_count / total_count) * 100) if total_count > 0 else 0

        return score, self.results

    def check_task_breakdown(self) -> Dict[str, Any]:
        # Ensure latest sync
        self.state_manager.sync_from_files()
        state = self.state_manager.load()
        tasks = state.get("tasks", [])
        if len(tasks) < 5:
            return {
                "name": "Task Breakdown",
                "status": "failed",
                "message": f"Sprint has only {len(tasks)} tasks (minimum 5 required).",
                "critical": True,
            }
        return {
            "name": "Task Breakdown",
            "status": "passed",
            "message": f"Sprint has {len(tasks)} tasks.",
        }

    def check_documentation(self) -> Dict[str, Any]:
        readme_file = self.sprint_dir / "README.md"
        todo_file = self.sprint_dir / "TODO.md"

        errors = []
        if not readme_file.exists() or readme_file.stat().st_size < 20:
            errors.append("README.md is missing or empty.")
        if not todo_file.exists() or todo_file.stat().st_size < 20:
            errors.append("TODO.md is missing or empty.")

        if errors:
            return {
                "name": "Documentation",
                "status": "failed",
                "message": " ".join(errors),
                "critical": True,
            }
        return {
            "name": "Documentation",
            "status": "passed",
            "message": "README.md and TODO.md are present.",
        }

    def check_spec_tracing(self) -> Dict[str, Any]:
        # Check if Spec-Id is present in README or TODO
        readme_content = ""
        todo_content = ""

        if (self.sprint_dir / "README.md").exists():
            readme_content = (self.sprint_dir / "README.md").read_text()
        if (self.sprint_dir / "TODO.md").exists():
            todo_content = (self.sprint_dir / "TODO.md").read_text()

        combined = readme_content + todo_content
        if "Spec-Id" not in combined and not re.search(r"SPEC-[A-Z]+-\d+", combined):
            return {
                "name": "Spec Tracing",
                "status": "failed",
                "message": "No Spec-Id found in sprint documentation.",
                "critical": True,
            }
        return {
            "name": "Spec Tracing",
            "status": "passed",
            "message": "Spec tracking markers found.",
        }

    def check_component_scope(self) -> Dict[str, Any]:
        component = self.state_manager.get_component()
        if not component:
            return {
                "name": "Component Scope",
                "status": "failed",
                "message": "No component scope defined in sprint.json.",
                "critical": True,
            }
        return {
            "name": "Component Scope",
            "status": "passed",
            "message": f"Component scope: {component}",
        }

    def check_governance(self) -> Dict[str, Any]:
        # Clean git state check (no staged changes outside sprint artifacts)
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

            sprint_rel_path = str(self.sprint_dir.relative_to(self.repo_root))

            illegal_staged = [
                f
                for f in staged_files
                if not (
                    f.startswith(sprint_rel_path)
                    or f in ["TODO.md", "RETRO.md", "README.md", "sprint.json"]
                )
            ]

            if illegal_staged:
                return {
                    "name": "Governance (Git State)",
                    "status": "failed",
                    "message": f"Illegal staged changes found: {', '.join(illegal_staged[:3])}...",
                    "critical": True,
                }
        except Exception as e:
            return {
                "name": "Governance (Git State)",
                "status": "warning",
                "message": f"Could not check git state: {e}",
            }

        return {
            "name": "Governance (Git State)",
            "status": "passed",
            "message": "Git state is clean.",
        }

    def check_retro_sync(self) -> Dict[str, Any]:
        """Check if RETRO.md content matches sprint.json data."""
        # Only required if sprint is closed or in review
        # For now, we perform a sync to check if values match what's in file vs what's in existing json
        # But sine preflight might be run BEFORE sync, we should rely on state_manager.sync_from_files() being called in run_all?
        # Actually preflight.run_all calls check_task_breakdown which calls sync_from_files.
        # So state should be fresh.

        state = self.state_manager.load()
        if not state:
            return {
                "name": "Retro Sync",
                "status": "warning",
                "message": "Could not load sprint state.",
            }

        # If RETRO.md exists, ensure it's parsed
        if (self.sprint_dir / "RETRO.md").exists():
            retro = state.get("retro", {})
            if not retro.get("summary") and not retro.get("actionItems"):
                return {
                    "name": "Retro Sync",
                    "status": "warning",
                    "message": "RETRO.md exists but no summary/actions parsed in sprint.json. Check RETRO.md format.",
                }
            return {
                "name": "Retro Sync",
                "status": "passed",
                "message": "RETRO.md content synced to sprint.json.",
            }
    def check_loc_limit(self) -> Dict[str, Any]:
        """Check if any files exceed the 400 LOC limit."""
        violations = []
        # Focus on implementation areas, excluding standard ignore paths
        ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".sprint"}
        
        for p in self.repo_root.rglob("*"):
            if p.is_file() and not any(part in p.parts for part in ignore_dirs):
                if p.suffix in {".py", ".ts", ".js", ".tsx", ".jsx"}:
                    try:
                        with open(p, "r", errors="ignore") as f:
                            lines = sum(1 for _ in f)
                        if lines > 400:
                            violations.append(f"{p.relative_to(self.repo_root)} ({lines} lines)")
                    except Exception: pass

        if violations:
            return {
                "name": "LOC Limit Enforcement",
                "status": "failed",
                "message": f"Found {len(violations)} files exceeding 400 LOC: {', '.join(violations[:2])}...",
                "critical": False,
            }
        return {
            "name": "LOC Limit Enforcement",
            "status": "passed",
            "message": "All files are under 400 LOC.",
        }

    def check_secrets(self) -> Dict[str, Any]:
        """Basic secret scanning for common patterns."""
        patterns = [
            r"sk-ant-api03-[a-zA-Z0-9\-_]{20,}", # Anthropic
            r"AIza[0-9A-Za-z\-_]{35}",           # Google Cloud/Gemini
            r"ghp_[a-zA-Z0-9]{36}",              # GitHub Personal Access Token
            r"xox[bpgr]-[0-9]{12}-[a-zA-Z0-9]{24}", # Slack
        ]
        violations = []
        ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", ".sprint"}
        
        for p in self.repo_root.rglob("*"):
            if p.is_file() and not any(part in p.parts for part in ignore_dirs):
                if p.suffix in {".py", ".ts", ".js", ".env", ".json", ".yaml", ".yml"}:
                    try:
                         content = p.read_text(errors="ignore")
                         for pattern in patterns:
                             if re.search(pattern, content):
                                 violations.append(str(p.relative_to(self.repo_root)))
                                 break
                    except Exception: pass

        if violations:
            return {
                "name": "Secret Scanning",
                "status": "failed",
                "message": f"Found potential secrets in: {', '.join(violations[:3])}",
                "critical": True,
            }
        return {
            "name": "Secret Scanning",
            "status": "passed",
            "message": "No secrets detected.",
        }

        return {
            "name": "Retro Sync",
            "status": "passed",
            "message": "No RETRO.md to sync.",
        }
