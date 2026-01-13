import os
import json
import subprocess
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from .agent import get_model

class AlignmentTracker:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or self._find_repo_root()
        self.alignment_dir = self.repo_root / ".onecoder" / "alignment"
        self.logs_dir = self.alignment_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _find_repo_root(self) -> Path:
        current = Path.cwd().resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd().resolve()

    def get_time_window(self, hour: int) -> str:
        if 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 24:
            return "Evening"
        else:
            return "Night"

    def fetch_recent_prs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches recent merged PRs using gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--state", "merged", "--limit", str(limit), "--json", "number,title,mergedAt,author,url"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def log_current_state(self) -> str:
        """Logs the current commit and PR status to the filesystem."""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        window = self.get_time_window(now.hour)
        
        # Get latest commit
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], text=True).strip()
        except subprocess.CalledProcessError:
            commit_hash = "unknown"
            commit_msg = "unknown"

        recent_prs = self.fetch_recent_prs()
        
        log_file = self.logs_dir / f"{date_str}.json"
        
        if log_file.exists():
            with open(log_file, "r") as f:
                try:
                    daily_logs = json.load(f)
                except json.JSONDecodeError:
                    daily_logs = {}
        else:
            daily_logs = {}

        if window not in daily_logs:
            daily_logs[window] = []

        entry = {
            "timestamp": now.isoformat(),
            "commit_hash": commit_hash,
            "commit_message": commit_msg,
            "recent_prs": recent_prs
        }
        
        daily_logs[window].append(entry)
        
        with open(log_file, "w") as f:
            json.dump(daily_logs, f, indent=4)
            
        return f"Logged state for {window} in {log_file.name}"

    def check_roadmap_alignment(self) -> Dict[str, Any]:
        """Checks current activity against MVP_ROADMAP.md."""
        roadmap_path = self.repo_root / "MVP_ROADMAP.md"
        if not roadmap_path.exists():
            return {"status": "unknown", "message": "MVP_ROADMAP.md not found"}
        
        roadmap_content = roadmap_path.read_text()
        
        # Simple heuristic check: find active sections mentioned in recent commits
        try:
            recent_commits = subprocess.check_output(["git", "log", "-n", "10", "--pretty=%s"], text=True).split("\n")
        except subprocess.CalledProcessError:
            recent_commits = []

        aligned_items = []
        for line in roadmap_content.split("\n"):
            if "###" in line or "- **" in line:
                item = line.strip("#-* ").split(" (")[0]
                for commit in recent_commits:
                    if item.lower() in commit.lower():
                        aligned_items.append(item)
                        break
        
        return {
            "status": "aligned" if aligned_items else "diverged",
            "aligned_items": list(set(aligned_items)),
            "message": f"Found {len(aligned_items)} items aligned with roadmap."
        }

    def capture_suggestions(self) -> List[str]:
        """Scans ANTIGRAVITY.md and recent RETRO.md files for suggestions."""
        suggestions = []
        
        # Scan ANTIGRAVITY.md
        antigravity_path = self.repo_root / "ANTIGRAVITY.md"
        if antigravity_path.exists():
            content = antigravity_path.read_text()
            # Simple heuristic: lines in 'Future' or 'To Watch' sections
            capture = False
            for line in content.split("\n"):
                if "##" in line and any(x in line for x in ["Future", "Watch", "Improvement"]):
                    capture = True
                elif "##" in line:
                    capture = False
                
                if capture and line.strip().startswith("-"):
                    suggestions.append(line.strip("- ").strip())

        # Scan recent RETRO.md
        sprint_dir = self.repo_root / ".sprint"
        if sprint_dir.exists():
            retro_files = sorted(list(sprint_dir.glob("*/RETRO.md")), key=os.path.getmtime, reverse=True)[:3]
            for retro_path in retro_files:
                content = retro_path.read_text()
                # Simple heuristic: bullet points under 'To Improve' or 'Learnings'
                capture = False
                for line in content.split("\n"):
                    if "##" in line and any(x in line for x in ["Improve", "Learning", "Next"]):
                        capture = True
                    elif "##" in line:
                        capture = False
                    
                    if capture and line.strip().startswith("-"):
                        suggestions.append(line.strip("- ").strip())
        
        return list(set(suggestions))

    def summarize_alignment_agentic(self, alignment_data: Dict[str, Any], recent_prs: List[Dict[str, Any]], suggestions: List[str]) -> str:
        """Uses LLM to summarize the alignment status."""
        try:
            from google.adk.agents import LlmAgent
            model = get_model()
            agent = LlmAgent(
                name="alignment_summarizer",
                model=model,
                instruction="You are a project manager analyst. Provide a 2-3 sentence summary of project health."
            )
            
            prompt = f"""
            Analyze current alignment:
            Roadmap Status: {alignment_data['status']}
            Aligned Items: {alignment_data['aligned_items']}
            Recent PRs: {json.dumps(recent_prs)}
            Suggestions: {json.dumps(suggestions[:5])}
            """
            
            response = agent.run(prompt)
            return response
                
        except Exception as e:
            return f"Agentic summary unavailable: {e}"

                
        except Exception as e:
            return {"status": "DRIFTING", "message": f"Semantic check fallback: {e}", "aligned_items": [], "drift_items": []}

    def check_roadmap_alignment_agentic(self) -> Dict[str, Any]:
        """Uses LLM to semantically compare activity against MVP_ROADMAP.md."""
        roadmap_path = self.repo_root / "MVP_ROADMAP.md"
        if not roadmap_path.exists():
            return {"status": "unknown", "message": "MVP_ROADMAP.md not found"}
        
        roadmap_content = roadmap_path.read_text()
        
        try:
            recent_commits = subprocess.check_output(["git", "log", "-n", "20", "--pretty=%s"], text=True)
            recent_prs = self.fetch_recent_prs(limit=10)
            
            model = get_model()
            
            prompt = f"""
            Analyze the following Roadmap and recent development activity (commits and PRs). 
            Perform a semantic mapping of the activity to the Roadmap items.
            
            ROADMAP:
            {roadmap_content}
            
            RECENT COMMITS:
            {recent_commits}
            
            RECENT PRS:
            {json.dumps(recent_prs)}
            
            Categorize the project status as:
            - **ALIGNED**: Work is directly advancing items in the Roadmap.
            - **DRIFTING**: Work is valuable but not explicitly in the Roadmap.
            - **DIVERGED**: Work is unrelated to the Roadmap goals.
            
            Format your response as a JSON object:
            {{
                "status": "ALIGNED" | "DRIFTING" | "DIVERGED",
                "aligned_items": ["List of items from the roadmap that the work aligns with"],
                "drift_items": ["List of work items that are not in the roadmap"],
                "message": "A brief explanation of the alignment status (1-2 sentences)"
            }}
            """
            
            if hasattr(model, "completion"):
                response = model.completion(messages=[{"role": "user", "content": prompt}], response_format={ "type": "json_object" })
                data = json.loads(response.choices[0].message.content)
                return data
            else:
                return {"status": "DRIFTING", "aligned_items": [], "drift_items": [], "message": "LiteLLM fallback. Run with GEMINI_API_KEY for semantic analysis."}
                
        except Exception as e:
            return {"status": "error", "message": f"Semantic check failed: {e}", "aligned_items": [], "drift_items": []}
