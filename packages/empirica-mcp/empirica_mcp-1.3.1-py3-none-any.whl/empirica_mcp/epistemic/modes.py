"""
Epistemic Modes - Behavioral implementations for different epistemic states

Each mode is a distinct way the MCP server behaves based on its vector state.
"""

from typing import Dict, Any, Optional
import subprocess
import json


class EpistemicModes:
    """
    Collection of epistemic modes the MCP server can operate in
    """
    
    def __init__(self, empirica_cli: str = "empirica"):
        self.empirica_cli = empirica_cli
    
    async def load_context(self, session_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load context mode: Low context → load project data
        
        Calls: empirica project-bootstrap
        Result: context↑, know↑, density↑, uncertainty↓
        """
        try:
            cmd = [self.empirica_cli, "project-bootstrap", "--output", "json"]
            if project_id:
                cmd.extend(["--project-id", project_id])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "mode": "load_context",
                    "data": data,
                    "message": "Context loaded successfully"
                }
            else:
                return {
                    "success": False,
                    "mode": "load_context",
                    "error": result.stderr,
                    "message": "Failed to load context"
                }
        except Exception as e:
            return {
                "success": False,
                "mode": "load_context",
                "error": str(e),
                "message": "Exception loading context"
            }
    
    async def investigate(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Investigate mode: High uncertainty → systematic research
        
        This would integrate with investigation tools, for now returns guidance
        Result: know↑, uncertainty↓, signal↑
        """
        return {
            "success": True,
            "mode": "investigate",
            "guidance": (
                "🔍 INVESTIGATION MODE ACTIVATED\n\n"
                f"Query: {query}\n\n"
                "Systematic investigation steps:\n"
                "1. Search codebase for relevant patterns\n"
                "2. Check documentation and architecture docs\n"
                "3. Review recent commits and changes\n"
                "4. Test hypotheses incrementally\n"
                "5. Document findings as you learn\n\n"
                "Update vectors as understanding grows."
            ),
            "message": "Investigation mode guidance provided"
        }
    
    async def confident_implementation(self, session_id: str, task: str) -> Dict[str, Any]:
        """
        Confident implementation mode: High know + low uncertainty
        
        Direct action, minimal checking, high confidence
        Result: change↑, completion↑, impact↑
        """
        return {
            "success": True,
            "mode": "confident_implementation",
            "guidance": (
                "✅ CONFIDENT IMPLEMENTATION MODE\n\n"
                f"Task: {task}\n\n"
                "Epistemic assessment: Know ≥ 0.7, Uncertainty < 0.4\n"
                "Action: Proceed with direct implementation\n"
                "- Make surgical changes\n"
                "- Trust your knowledge\n"
                "- Validate after implementation\n"
                "- Update completion vectors"
            ),
            "message": "Confident implementation mode activated"
        }
    
    async def cautious_implementation(self, session_id: str, task: str) -> Dict[str, Any]:
        """
        Cautious implementation mode: Moderate uncertainty
        
        Incremental changes, frequent validation, CHECK gates
        Result: change↑ (slower), completion↑ (careful)
        """
        return {
            "success": True,
            "mode": "cautious_implementation",
            "guidance": (
                "⚠️ CAUTIOUS IMPLEMENTATION MODE\n\n"
                f"Task: {task}\n\n"
                "Epistemic assessment: Moderate uncertainty or knowledge\n"
                "Action: Proceed incrementally with validation\n"
                "- Make small, testable changes\n"
                "- Use CHECK gates (empirica check)\n"
                "- Validate frequently\n"
                "- Log learnings as you go\n"
                "- Update vectors after each step"
            ),
            "message": "Cautious implementation mode activated"
        }
    
    async def clarify(self, session_id: str, unclear_request: str) -> Dict[str, Any]:
        """
        Clarify mode: Low clarity → ask questions
        
        Ask specific questions to improve clarity
        Result: clarity↑, uncertainty↓
        """
        return {
            "success": True,
            "mode": "clarify",
            "guidance": (
                "❓ CLARIFICATION MODE\n\n"
                f"Unclear request: {unclear_request}\n\n"
                "Epistemic assessment: Clarity < 0.6\n"
                "Action: Ask specific questions before proceeding:\n\n"
                "Questions to ask:\n"
                "- What is the specific goal?\n"
                "- What does success look like?\n"
                "- Are there constraints or requirements?\n"
                "- What should be preserved/unchanged?\n"
                "- What's the priority/timeline?\n\n"
                "Once clarity improves, reassess vectors and route again."
            ),
            "message": "Clarification questions generated"
        }
    
    def get_mode_description(self, mode_name: str) -> str:
        """Get human-readable description of a mode"""
        descriptions = {
            "load_context": "Load project context (low context → gather information)",
            "investigate": "Systematic investigation (high uncertainty → research)",
            "confident_implementation": "Direct implementation (high know, low uncertainty)",
            "cautious_implementation": "Incremental implementation (moderate uncertainty)",
            "clarify": "Ask clarifying questions (low clarity → improve understanding)"
        }
        return descriptions.get(mode_name, "Unknown mode")
