"""
Vector Router - Routes MCP server behavior based on epistemic vectors

Key routing decisions:
- Low context (< 0.5) → load_context mode
- High uncertainty (> 0.6) → investigate mode  
- High know + low uncertainty → confident_implementation mode
- Moderate uncertainty → cautious_implementation mode
- Low clarity → clarify mode
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RoutingDecision:
    """Result of vector-based routing"""
    mode: str
    confidence: float
    reasoning: str
    context_depth: str  # "minimal", "standard", "deep"
    
    def to_dict(self) -> Dict:
        return {
            "mode": self.mode,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "context_depth": self.context_depth
        }


class VectorRouter:
    """
    Routes MCP server behavior based on epistemic vectors.
    
    Modes:
    - load_context: Low context → load project data
    - investigate: High uncertainty → systematic research
    - confident_implementation: High know, low uncertainty
    - cautious_implementation: Moderate uncertainty
    - clarify: Low clarity → ask questions
    """
    
    def __init__(self, personality: Optional[Dict] = None):
        """
        personality: Optional dict with thresholds like:
          {"uncertainty_tolerance": 0.6, "context_threshold": 0.5}
        """
        self.personality = personality or {
            "uncertainty_tolerance": 0.6,
            "context_threshold": 0.5,
            "know_threshold": 0.7,
            "clarity_threshold": 0.6
        }
    
    def route(self, vectors: Dict[str, float], request: str) -> RoutingDecision:
        """
        Main routing logic - returns mode based on vector assessment
        
        Priority (highest to lowest):
        1. Low clarity → clarify
        2. Low context → load_context
        3. High uncertainty → investigate
        4. High know + low uncertainty → confident_implementation
        5. Default → cautious_implementation
        """
        
        # Extract key vectors
        clarity = vectors.get("clarity", 0.5)
        context = vectors.get("context", 0.5)
        uncertainty = vectors.get("uncertainty", 0.5)
        know = vectors.get("know", 0.5)
        
        # Route 1: Low clarity → clarify
        if clarity < self.personality["clarity_threshold"]:
            return RoutingDecision(
                mode="clarify",
                confidence=0.9,
                reasoning=f"Clarity={clarity:.2f} < {self.personality['clarity_threshold']}, need clarification",
                context_depth="minimal"
            )
        
        # Route 2: Low context → load_context
        if context < self.personality["context_threshold"]:
            return RoutingDecision(
                mode="load_context",
                confidence=0.85,
                reasoning=f"Context={context:.2f} < {self.personality['context_threshold']}, loading project data",
                context_depth="deep"
            )
        
        # Route 3: High uncertainty → investigate
        if uncertainty > self.personality["uncertainty_tolerance"]:
            return RoutingDecision(
                mode="investigate",
                confidence=0.8,
                reasoning=f"Uncertainty={uncertainty:.2f} > {self.personality['uncertainty_tolerance']}, systematic investigation needed",
                context_depth="standard"
            )
        
        # Route 4: High know + low uncertainty → confident_implementation
        if know >= self.personality["know_threshold"] and uncertainty < 0.4:
            return RoutingDecision(
                mode="confident_implementation",
                confidence=0.95,
                reasoning=f"Know={know:.2f} ≥ {self.personality['know_threshold']}, Uncertainty={uncertainty:.2f} < 0.4, confident execution",
                context_depth="minimal"
            )
        
        # Route 5: Default → cautious_implementation
        return RoutingDecision(
            mode="cautious_implementation",
            confidence=0.7,
            reasoning=f"Moderate vectors (know={know:.2f}, uncertainty={uncertainty:.2f}), proceeding cautiously",
            context_depth="standard"
        )
    
    def get_context_depth(self, vectors: Dict[str, float]) -> str:
        """
        Determine how much context to load based on vectors
        
        Returns: "minimal" | "standard" | "deep"
        """
        context = vectors.get("context", 0.5)
        uncertainty = vectors.get("uncertainty", 0.5)
        
        # Low context OR high uncertainty → deep
        if context < 0.4 or uncertainty > 0.7:
            return "deep"
        
        # Moderate context/uncertainty → standard
        elif context < 0.7 or uncertainty > 0.4:
            return "standard"
        
        # High context, low uncertainty → minimal
        else:
            return "minimal"
    
    def explain_routing(self, decision: RoutingDecision) -> str:
        """
        Generate human-readable explanation of routing decision
        """
        return (
            f"🧠 Epistemic Routing:\n"
            f"  Mode: {decision.mode}\n"
            f"  Confidence: {decision.confidence:.2f}\n"
            f"  Context Depth: {decision.context_depth}\n"
            f"  Reasoning: {decision.reasoning}"
        )
