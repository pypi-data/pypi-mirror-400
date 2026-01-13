"""GitHub Pull Request creation for sprint-cli."""

import subprocess
from pathlib import Path


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def generate_pr_body(sprint_dir: Path, sprint_name: str) -> str:
    """Generate PR body from README goal, RETRO summary, and visual assets."""
    body_parts = []

    # Add sprint goal from README
    readme = sprint_dir / "README.md"
    if readme.exists():
        with open(readme) as f:
            content = f.read()
            # Extract goal section
            if "## Goal" in content:
                goal = content.split("## Goal")[1].split("##")[0].strip()
                body_parts.append(f"## Sprint Goal\n{goal}")

    # Add RETRO summary
    retro = sprint_dir / "RETRO.md"
    if retro.exists():
        with open(retro) as f:
            content = f.read()
            body_parts.append(f"## Retrospective\n{content}")

    # Add visual assets
    media_dir = sprint_dir / "media"
    if media_dir.exists() and list(media_dir.glob("*.png")):
        body_parts.append("## Visual Assets")
        for img in sorted(media_dir.glob("*.png")):
            body_parts.append(f"![{img.stem}](.sprint/{sprint_name}/media/{img.name})")

    return "\n\n".join(body_parts)


def create_pull_request(sprint_dir: Path, sprint_name: str) -> None:
    """Create a pull request using GitHub CLI."""
    if not check_gh_cli():
        raise RuntimeError(
            "GitHub CLI (gh) is not installed or not authenticated. "
            "Install from https://cli.github.com and run 'gh auth login'"
        )

    # Generate PR title and body
    pr_title = f"Sprint {sprint_name}"
    pr_body = generate_pr_body(sprint_dir, sprint_name)

    # Push current branch to ensure remote is up to date
    try:
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        subprocess.run(["git", "push", "origin", current_branch], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to push branch: {e}")
        # Proceed anyway, user might have pushed or we might be on main/detached

    # Create PR
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            "main",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"gh pr create failed: {result.stderr}")

    print(f"Pull request created: {result.stdout.strip()}")
