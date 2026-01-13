from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from onecoder.metrics import find_repo_root

ENV_FILENAMES = [".env", ".env.local", ".dev.vars"]
SHARED_SECRETS = ["GITHUB_CLIENT_ID", "JWT_SECRET", "GEMINI_API_KEY"]
COMPONENT_PATHS: Dict[str, List[Path]] = {
    "onecoder-api": [Path("onecoder-api")],
    "oneadmin": [Path("oneadmin/worker"), Path("oneadmin/client")],
    "oneui": [Path("oneui"), Path("components/devcenter")],
    "onewebsite": [Path("components/onewebsite")],
    "sprint-cli": [Path("sprint-cli")],
    "onecoder-cli": [Path("onecoder-cli")],
}


@dataclass
class EnvFinding:
    component: str
    check: str
    status: str
    message: str
    file: Optional[Path] = None
    tt_id: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        return {
            "component": self.component,
            "check": self.check,
            "status": self.status,
            "message": self.message,
            "file": str(self.file) if self.file else None,
            "tt_id": self.tt_id,
        }


class EnvDoctor:
    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = repo_root or find_repo_root()

    def run(self) -> List[EnvFinding]:
        findings: List[EnvFinding] = []
        component_envs: Dict[str, Dict[str, str]] = {}

        for name, rel_paths in COMPONENT_PATHS.items():
            env_files: List[Path] = []
            for rel_path in rel_paths:
                env_files.extend(self._discover_env_files(self.repo_root / rel_path))

            if not env_files:
                findings.append(
                    EnvFinding(
                        component=name,
                        check="env_files",
                        status="warn",
                        message=f"No env files found (searched: {', '.join(str(self.repo_root / p) for p in rel_paths)})",
                    )
                )
                continue

            merged_env: Dict[str, str] = {}
            for env_file in env_files:
                try:
                    merged_env.update(self._load_env_file(env_file))
                    findings.append(
                        EnvFinding(
                            component=name,
                            check="env_files",
                            status="pass",
                            message=f"Found {env_file.name}",
                            file=env_file,
                        )
                    )
                except ValueError as exc:
                    findings.append(
                        EnvFinding(
                            component=name,
                            check="env_parse",
                            status="fail",
                            message=f"{env_file}: {exc}",
                            file=env_file,
                        )
                    )
            component_envs[name] = merged_env

            for key in SHARED_SECRETS:
                if key not in merged_env:
                    findings.append(
                        EnvFinding(
                            component=name,
                            check=key,
                            status="warn",
                            message=f"{key} missing in {', '.join(f.name for f in env_files)}",
                        )
                    )

        findings.extend(self._compare_shared_secrets(component_envs))
        return findings

    def write_artifact(self, findings: List[EnvFinding]) -> Path:
        debug_dir = self.repo_root / ".onecoder" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = debug_dir / "doctor-env.json"
        artifact_path.write_text(json.dumps([f.to_dict() for f in findings], indent=2))
        return artifact_path

    @staticmethod
    def to_json(findings: List[EnvFinding]) -> str:
        return json.dumps([f.to_dict() for f in findings], indent=2)

    @staticmethod
    def has_failures(findings: List[EnvFinding]) -> bool:
        return any(f.status == "fail" for f in findings)

    @staticmethod
    def _discover_env_files(component_root: Path) -> List[Path]:
        files: List[Path] = []
        if not component_root.exists():
            return files
        for filename in ENV_FILENAMES:
            for candidate in component_root.rglob(filename):
                if "node_modules" in candidate.parts or ".git" in candidate.parts:
                    continue
                files.append(candidate)
        return list(dict.fromkeys(files))

    @staticmethod
    def _load_env_file(path: Path) -> Dict[str, str]:
        values: Dict[str, str] = {}
        current_key: Optional[str] = None
        multiline_buffer: List[str] = []
        with path.open() as handle:
            for line in handle:
                raw_line = line.rstrip("\n")
                stripped = raw_line.strip()

                if current_key:
                    closing = stripped.endswith('"')
                    content = raw_line.rstrip()[:-1] if closing else raw_line
                    multiline_buffer.append(content)
                    if closing:
                        values[current_key] = "\n".join(multiline_buffer)
                        current_key = None
                        multiline_buffer = []
                    continue

                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    raise ValueError("Invalid line (missing '=')")
                key, value = stripped.split("=", 1)
                clean_value = value.strip()
                values[key.strip()] = clean_value.strip('"').strip("'")

                if clean_value.startswith('"') and not clean_value.endswith('"'):
                    current_key = key.strip()
                    multiline_buffer.append(clean_value.lstrip('"'))
        if current_key:
            raise ValueError(f"Unterminated multiline value for {current_key}")
        return values

    def _compare_shared_secrets(
        self, component_envs: Dict[str, Dict[str, str]]
    ) -> List[EnvFinding]:
        findings: List[EnvFinding] = []
        for secret in SHARED_SECRETS:
            values: Dict[str, str] = {
                component: envs[secret]
                for component, envs in component_envs.items()
                if secret in envs
            }
            if len(values) <= 1:
                continue
            unique_values = set(values.values())
            if len(unique_values) == 1:
                continue

            tt_id = "TT-032" if self._is_font_trap(unique_values) and secret == "GITHUB_CLIENT_ID" else None
            message = "; ".join(
                f"{component}={display_value}"
                for component, display_value in values.items()
            )
            findings.append(
                EnvFinding(
                    component="shared",
                    check=secret,
                    status="fail",
                    message=f"Mismatched {secret}: {message}",
                    tt_id=tt_id,
                )
            )
        return findings

    @staticmethod
    def _is_font_trap(values: Iterable[str]) -> bool:
        normalized = {_font_normalize(value) for value in values}
        return len(normalized) < len(set(values))


def _font_normalize(value: str) -> str:
    """Normalize ambiguous glyphs so I/l mix-ups collapse to the same value."""
    return value.replace("I", "1").replace("l", "1")
