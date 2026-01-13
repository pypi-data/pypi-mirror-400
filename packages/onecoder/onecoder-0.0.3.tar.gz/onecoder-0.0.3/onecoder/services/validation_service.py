import logging
import subprocess
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseValidationRule(ABC):
    """Base class for all validation rules."""
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

class FileExistsRule(BaseValidationRule):
    """Checks if a file exists relative to a base path."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    @property
    def name(self) -> str:
        return f"FileExists({self.filepath})"

    def validate(self, context: Dict[str, Any]) -> bool:
        base_path = context.get("worktree_path")
        if not base_path:
            return False
        return (Path(base_path) / self.filepath).exists()

class CommandSuccessRule(BaseValidationRule):
    """Checks if a command executes successfully (exit code 0)."""
    def __init__(self, command: str):
        self.command = command

    @property
    def name(self) -> str:
        return f"CommandSuccess({self.command})"

    def validate(self, context: Dict[str, Any]) -> bool:
        base_path = context.get("worktree_path")
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                cwd=base_path,
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

class ValidationReport:
    """Structured report for validation results."""
    def __init__(self, session_id: str, all_passed: bool, results: List[Dict[str, Any]]):
        self.session_id = session_id
        self.all_passed = all_passed
        self.results = results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "all_passed": self.all_passed,
            "results": self.results
        }

class ValidationService:
    """
    ValidationService runs a set of rules against a delegation session.
    """

    def validate_session(self, session_context: Dict[str, Any], rules: List[BaseValidationRule]) -> ValidationReport:
        """
        Runs all rules and returns a structured ValidationReport.
        """
        session_id = session_context.get("session_id", "unknown")
        results = []
        all_passed = True
        
        for rule in rules:
            try:
                passed = rule.validate(session_context)
                results.append({
                    "rule": rule.name,
                    "passed": passed,
                    "error": None
                })
                if not passed:
                    all_passed = False
            except Exception as e:
                logger.error(f"Rule {rule.name} failed with error: {e}")
                results.append({
                    "rule": rule.name,
                    "passed": False,
                    "error": str(e)
                })
                all_passed = False
                
        return ValidationReport(session_id, all_passed, results)
