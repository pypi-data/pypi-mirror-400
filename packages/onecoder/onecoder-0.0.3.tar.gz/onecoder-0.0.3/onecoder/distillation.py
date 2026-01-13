import os
import json
import re
import datetime
from typing import Any, List, Dict
from pathlib import Path

class SessionCapture:
    """
    Captures session events (text, tool calls) for later distillation.
    """
    def __init__(self, directory: str = "."):
        self.directory = directory
        self.logs_dir = os.path.join(directory, ".sprint", "logs")
        
        self.current_session_id = None
        self.events: List[Dict[str, Any]] = []

    def start_session(self, session_id: str):
        os.makedirs(self.logs_dir, exist_ok=True)
        self.current_session_id = session_id
        self.events = []

    def log_event(self, event_data: Dict[str, Any]):
        """Logs an event within the current session."""
        event_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": event_data
        }
        self.events.append(event_entry)

    def save_session(self):
        """Saves the current session logs to the .sprint/logs directory."""
        if not self.current_session_id:
            return
            
        filename = f"session_{self.current_session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.logs_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump({
                "session_id": self.current_session_id,
                "events": self.events
            }, f, indent=2)
        
        print(f"Session logs saved to {filepath}")
        
    def distill_patterns(self) -> str:
        """
        [v0.1.0 Mechanical] Implementation for pattern capture.
        In the future, this will use an LLM to extract reusable skills.
        """
        patterns = []
        for event in self.events:
            data = event.get("data", {})
            if "tool_call" in data:
                patterns.append(data["tool_call"])
        
        return f"Captured {len(patterns)} tool call patterns."

# Singleton instance for the API to use
capture_engine = SessionCapture()

class SprintDistiller:
    """
    Distills learnings from a sprint and updates project awareness.
    """
    def __init__(self, project_root: str = "."):
        self.project_root = self._find_repo_root(Path(project_root).absolute())
        self.antigravity_md = self.project_root / "ANTIGRAVITY.md"

    def _find_repo_root(self, start_path: Path) -> Path:
        """Traverses upwards to find the repository root."""
        curr = start_path
        while curr != curr.parent:
            if (curr / ".sprint").exists() or (curr / ".git").exists():
                return curr
            curr = curr.parent
        return start_path # Fallback to start_path

    def distill_sprint(self, sprint_id: str) -> Dict[str, Any]:
        """
        Analyzes a finished sprint and extracts learnings.
        """
        sprint_dir = self.project_root / ".sprint" / sprint_id
        retro_path = sprint_dir / "RETRO.md"
        
        if not retro_path.exists():
            return {"error": f"RETRO.md not found in {sprint_id}"}

        content = retro_path.read_text()
        
        # Use LLM with mechanical fallback
        try:
            learnings = self._extract_learnings_llm(content)
        except Exception as e:
            print(f"Warning: LLM distillation failed ({e}). Falling back to mechanical extraction.")
            learnings = self._extract_learnings_mechanical(content)
        
        if learnings:
            self._update_awareness(sprint_id, learnings)
            
        return {
            "sprint_id": sprint_id,
            "learnings_extracted": len(learnings),
            "updated": self.antigravity_md.name if learnings else None,
            "method": "llm" if hasattr(self, "_llm_used") and self._llm_used else "mechanical"
        }

    def _extract_learnings_llm(self, content: str) -> List[str]:
        """Uses LLM to semantically extract learnings from retro content."""
        import litellm
        import os
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found")

        model = "openrouter/xiaomi/mimo-v2-flash:free"
        
        prompt = f"""
        Analyze the following Sprint Retro (RETRO.md) content and extract key engineering/architectural learnings.
        Focus on reusable patterns, failure modes to avoid, and optimized workflows.
        
        Format your response EXACTLY as a JSON list of strings. Each string should be a concise, action-oriented learning.
        DO NOT include any other text in your response.
        
        RETRO CONTENT:
        {content}
        
        Example Output: ["Always use relative paths in sprint-cli", "Verify JWT presence before syncing secrets"]
        """
        
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            response_format={ "type": "json_object" } # Try to enforce JSON
        )
        
        text = response.choices[0].message.content
        try:
            # Handle if LLM returned a JSON object with a 'learnings' key instead of a list
            data = json.loads(text)
            if isinstance(data, list):
                learnings = data
            elif isinstance(data, dict):
                # Look for common keys
                learnings = data.get("learnings", data.get("items", list(data.values())[0]))
            else:
                learnings = []
        except:
             # Fallback: extract anything that looks like a list
             match = re.search(r'\[.*\]', text, re.DOTALL)
             if match:
                 learnings = json.loads(match.group(0))
             else:
                 raise ValueError("Could not parse LLM response as JSON list")

        self._llm_used = True
        return learnings

    def _extract_learnings_mechanical(self, content: str) -> List[str]:
        """
        Extracts bullet points and numbered items from 'Learnings', 'To Improve', or 'Went Well' sections.
        This is a simple mechanical extraction fallback.
        """
        learnings = []
        capture = False
        for line in content.split("\n"):
            line_stripped = line.strip()
            # Start capturing after these headers
            if line_stripped.startswith("## ") and any(x in line_stripped for x in ["Learnings", "Learning", "Went Well", "To Improve", "Could Be Improved"]):
                capture = True
                continue
            # Stop if we hit another header or end of section
            elif line_stripped.startswith("## "):
                capture = False
            
            if capture:
                # Match bullet points: - text
                if line_stripped.startswith("- "):
                    learning = line_stripped[2:].strip()
                    if learning:
                        learnings.append(learning)
                # Match numbered lists: 1. text, 2. text, etc.
                elif re.match(r'^\d+\.\s+', line_stripped):
                    learning = re.sub(r'^\d+\.\s+', '', line_stripped).strip()
                    if learning:
                        learnings.append(learning)
        
        self._llm_used = False
        return learnings

    def _update_awareness(self, sprint_id: str, learnings: List[str]):
        """
        Injects learnings into ANTIGRAVITY.md.
        """
        if not self.antigravity_md.exists():
            return

        lines = self.antigravity_md.read_text().split("\n")
        new_lines = []
        in_learned_section = False
        injected = False
        
        marker = "### 🛡️ Distilled from Sprints"
        
        # Check if the marker already exists
        content = self.antigravity_md.read_text()
        if marker not in content:
            # Inject it after ## 🛠️ Environmental Awareness (Learned)
            for line in lines:
                new_lines.append(line)
                if "## 🛠️ Environmental Awareness (Learned)" in line:
                    new_lines.append("")
                    new_lines.append(marker)
                    for l in learnings:
                        new_lines.append(f"- {l} (distilled from {sprint_id})")
                    new_lines.append("")
                    injected = True
        else:
            # Append to the existing section, but avoid duplicates
            content = self.antigravity_md.read_text()
            for line in lines:
                new_lines.append(line)
                if marker in line:
                    for l in learnings:
                        entry = f"- {l} (distilled from {sprint_id})"
                        if entry not in content:
                            new_lines.append(entry)
                    injected = True

        if injected:
            self.antigravity_md.write_text("\n".join(new_lines))
