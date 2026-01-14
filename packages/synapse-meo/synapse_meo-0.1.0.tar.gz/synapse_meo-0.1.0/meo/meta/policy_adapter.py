from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class PolicyRule:
    rule_id: str
    rule_type: str
    condition: str
    action: str
    priority: int = 0
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority,
            "confidence": self.confidence,
            "metadata": self.metadata or {},
        }


class PolicyAdapter(ABC):
    @abstractmethod
    def adapt_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[str],
        insights: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def add_rule(self, rule: PolicyRule) -> None:
        pass
    
    @abstractmethod
    def get_rules(self) -> List[PolicyRule]:
        pass
    
    @abstractmethod
    def clear_rules(self) -> None:
        pass


class RuleBasedPolicyAdapter(PolicyAdapter):
    def __init__(self):
        self._rules: List[PolicyRule] = []
        self._action_preferences: Dict[str, float] = {}
    
    def adapt_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[str],
        insights: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        if insights:
            self._update_from_insights(insights)
        
        applicable_rules = self._find_applicable_rules(context)
        
        action_scores = {action: 0.0 for action in available_actions}
        
        for action in available_actions:
            if action in self._action_preferences:
                action_scores[action] += self._action_preferences[action]
        
        for rule in applicable_rules:
            if rule.action in action_scores:
                action_scores[rule.action] += rule.confidence * (1 + rule.priority * 0.1)
        
        recommended_action = None
        if action_scores:
            recommended_action = max(action_scores.items(), key=lambda x: x[1])[0]
        
        return {
            "recommended_action": recommended_action,
            "action_scores": action_scores,
            "applicable_rules": [r.to_dict() for r in applicable_rules],
            "context": context,
        }
    
    def _find_applicable_rules(self, context: Dict[str, Any]) -> List[PolicyRule]:
        applicable = []
        
        for rule in self._rules:
            if self._evaluate_condition(rule.condition, context):
                applicable.append(rule)
        
        applicable.sort(key=lambda r: r.priority, reverse=True)
        return applicable
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        if not condition:
            return True
        
        if ":" in condition:
            key, value = condition.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            context_value = context.get(key)
            if context_value is not None:
                return str(context_value) == value
        
        return False
    
    def _update_from_insights(self, insights: List[Any]) -> None:
        for insight in insights:
            if not hasattr(insight, "insight_type"):
                continue
            
            if insight.insight_type == "statistics":
                if hasattr(insight, "metadata") and "statistics" in insight.metadata:
                    stats = insight.metadata["statistics"]
                    for action, action_stats in stats.items():
                        success_rate = 0.0
                        if action_stats.get("count", 0) > 0:
                            success_rate = action_stats.get("success", 0) / action_stats["count"]
                        
                        self._action_preferences[action] = success_rate
            
            elif insight.insight_type == "rule":
                if hasattr(insight, "content"):
                    self._extract_rule_from_content(insight.content, insight)
    
    def _extract_rule_from_content(self, content: str, insight: Any) -> None:
        if "prefer" in content.lower() or "prioritize" in content.lower():
            rule = PolicyRule(
                rule_id=getattr(insight, "insight_id", "auto_rule"),
                rule_type="preference",
                condition="",
                action=content,
                priority=1,
                confidence=getattr(insight, "confidence", 0.8),
            )
            self._rules.append(rule)
    
    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)
    
    def get_rules(self) -> List[PolicyRule]:
        return self._rules.copy()
    
    def clear_rules(self) -> None:
        self._rules.clear()
        self._action_preferences.clear()


class LearningPolicyAdapter(PolicyAdapter):
    def __init__(self, learning_rate: float = 0.1):
        self._rules: List[PolicyRule] = []
        self._action_values: Dict[str, float] = {}
        self._action_counts: Dict[str, int] = {}
        self.learning_rate = learning_rate
    
    def adapt_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[str],
        insights: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        if insights:
            self._learn_from_insights(insights)
        
        action_scores = {}
        for action in available_actions:
            action_scores[action] = self._action_values.get(action, 0.0)
        
        recommended_action = None
        if action_scores:
            recommended_action = max(action_scores.items(), key=lambda x: x[1])[0]
        
        return {
            "recommended_action": recommended_action,
            "action_scores": action_scores,
            "action_counts": self._action_counts.copy(),
            "context": context,
        }
    
    def _learn_from_insights(self, insights: List[Any]) -> None:
        for insight in insights:
            if not hasattr(insight, "metadata"):
                continue
            
            if "statistics" in insight.metadata:
                stats = insight.metadata["statistics"]
                for action, action_stats in stats.items():
                    count = action_stats.get("count", 0)
                    success = action_stats.get("success", 0)
                    
                    if count > 0:
                        success_rate = success / count
                        
                        current_value = self._action_values.get(action, 0.5)
                        new_value = current_value + self.learning_rate * (success_rate - current_value)
                        self._action_values[action] = new_value
                        self._action_counts[action] = count
    
    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)
    
    def get_rules(self) -> List[PolicyRule]:
        return self._rules.copy()
    
    def clear_rules(self) -> None:
        self._rules.clear()
        self._action_values.clear()
        self._action_counts.clear()
