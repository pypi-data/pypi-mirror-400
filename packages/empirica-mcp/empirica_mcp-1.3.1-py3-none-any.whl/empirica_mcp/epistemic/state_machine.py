"""
Epistemic State Machine - Core 13-vector state tracking

The MCP server maintains epistemic self-awareness through 13 vectors
that track what it knows, can do, and how certain it is.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class VectorState:
    """13 epistemic vectors (all 0.0-1.0)"""
    # Tier 0 - Foundation
    engagement: float = 0.5
    know: float = 0.5
    do: float = 0.5
    context: float = 0.5
    
    # Tier 1 - Comprehension
    clarity: float = 0.5
    coherence: float = 0.5
    signal: float = 0.5
    density: float = 0.5
    
    # Tier 2 - Execution
    state: float = 0.5
    change: float = 0.5
    completion: float = 0.0
    impact: float = 0.5
    
    # Meta
    uncertainty: float = 0.5
    
    def to_dict(self) -> Dict[str, float]:
        """Export as flat dict"""
        return {
            "engagement": self.engagement,
            "know": self.know,
            "do": self.do,
            "context": self.context,
            "clarity": self.clarity,
            "coherence": self.coherence,
            "signal": self.signal,
            "density": self.density,
            "state": self.state,
            "change": self.change,
            "completion": self.completion,
            "impact": self.impact,
            "uncertainty": self.uncertainty
        }


class EpistemicStateMachine:
    """
    Maintains epistemic state and updates it based on:
    - Incoming requests (assess complexity/clarity)
    - Action outcomes (learn from results)
    - Context changes (load data → context up, know up)
    """
    
    def __init__(self, initial_vectors: Optional[Dict[str, float]] = None):
        if initial_vectors:
            self.vectors = VectorState(**initial_vectors)
        else:
            # Default: moderate engagement, low knowledge
            self.vectors = VectorState(
                engagement=0.7,
                know=0.3,
                do=0.6,
                context=0.3,
                clarity=0.5,
                coherence=0.5,
                signal=0.5,
                density=0.3,
                state=0.3,
                change=0.2,
                completion=0.0,
                impact=0.4,
                uncertainty=0.6
            )
    
    def assess_request(self, user_request: str) -> Dict[str, float]:
        """
        Self-assess epistemic state given new request.
        Updates vectors based on request analysis.
        
        Returns: Updated vector dict
        """
        request_lower = user_request.lower()
        
        # Assess clarity from request characteristics
        if any(word in request_lower for word in ["specifically", "exactly", "step by step", "details"]):
            self.vectors.clarity = min(0.9, self.vectors.clarity + 0.2)
        elif any(word in request_lower for word in ["maybe", "somehow", "figure out"]):
            self.vectors.clarity = max(0.3, self.vectors.clarity - 0.2)
        
        # Assess complexity → uncertainty
        complexity_markers = ["integrate", "design", "architecture", "system", "complex"]
        if any(marker in request_lower for marker in complexity_markers):
            self.vectors.uncertainty = min(0.8, self.vectors.uncertainty + 0.15)
        
        # Simple queries reduce uncertainty
        if any(word in request_lower for word in ["list", "show", "get", "what is"]):
            self.vectors.uncertainty = max(0.2, self.vectors.uncertainty - 0.1)
        
        # Context indicators
        if "context" in request_lower or "understand" in request_lower:
            # Acknowledging context need means current context is low
            self.vectors.context = max(0.3, self.vectors.context - 0.1)
        
        return self.vectors.to_dict()
    
    def update_from_action(self, action_type: str, result: Dict[str, Any]) -> Dict[str, float]:
        """
        Learn from action outcomes.
        
        action_type: "load_context", "investigate", "implement", "clarify"
        result: {"success": bool, "data": {...}}
        """
        success = result.get("success", False)
        
        if action_type == "load_context" and success:
            # Loaded context → context/know/density increase
            self.vectors.context = min(0.9, self.vectors.context + 0.3)
            self.vectors.know = min(0.85, self.vectors.know + 0.2)
            self.vectors.density = min(0.8, self.vectors.density + 0.25)
            self.vectors.uncertainty = max(0.2, self.vectors.uncertainty - 0.2)
        
        elif action_type == "investigate" and success:
            # Investigation → know up, uncertainty down
            self.vectors.know = min(0.8, self.vectors.know + 0.15)
            self.vectors.uncertainty = max(0.25, self.vectors.uncertainty - 0.15)
            self.vectors.signal = min(0.85, self.vectors.signal + 0.1)
        
        elif action_type == "implement" and success:
            # Implementation → change/completion/impact increase
            self.vectors.change = min(0.9, self.vectors.change + 0.2)
            self.vectors.completion = min(1.0, self.vectors.completion + 0.25)
            self.vectors.impact = min(0.9, self.vectors.impact + 0.15)
        
        elif action_type == "clarify" and success:
            # Clarification → clarity up, uncertainty down
            self.vectors.clarity = min(0.9, self.vectors.clarity + 0.2)
            self.vectors.uncertainty = max(0.3, self.vectors.uncertainty - 0.1)
        
        elif not success:
            # Failure → uncertainty up slightly
            self.vectors.uncertainty = min(0.9, self.vectors.uncertainty + 0.1)
        
        return self.vectors.to_dict()
    
    def get_state(self) -> Dict[str, float]:
        """Return current epistemic state"""
        return self.vectors.to_dict()
    
    def persist_state(self, session_id: str) -> bool:
        """
        Save state to Empirica (future integration).
        For now, just return True.
        """
        # TODO: Call empirica CLI to log state
        # empirica epistemics-update --session-id {session_id} --vectors '{json}'
        return True
    
    def __repr__(self) -> str:
        v = self.vectors
        return (
            f"EpistemicState(know={v.know:.2f}, uncertainty={v.uncertainty:.2f}, "
            f"context={v.context:.2f}, clarity={v.clarity:.2f})"
        )
