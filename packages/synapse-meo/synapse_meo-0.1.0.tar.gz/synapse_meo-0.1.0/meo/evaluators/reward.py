from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from meo.evaluators.metrics import (
    compute_success_rate,
    compute_average_latency,
    compute_cost,
    compute_error_rate,
)


@dataclass
class EvaluationResult:
    workflow_id: str
    reward: float
    success: bool
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "reward": self.reward,
            "success": self.success,
            "metrics": self.metrics,
            "metadata": self.metadata or {},
        }


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, episodes: List[Any], workflow_result: Optional[Any] = None) -> EvaluationResult:
        pass


class DefaultRewardEvaluator(Evaluator):
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.weights = weights or {
            "success": 1.0,
            "cost": -0.1,
            "latency": -0.05,
            "error_rate": -0.5,
        }
    
    def evaluate(self, episodes: List[Any], workflow_result: Optional[Any] = None) -> EvaluationResult:
        if not episodes:
            return EvaluationResult(
                workflow_id="unknown",
                reward=0.0,
                success=False,
                metrics={},
            )
        
        workflow_id = episodes[0].workflow_id if hasattr(episodes[0], "workflow_id") else "unknown"
        
        success_rate = compute_success_rate(episodes)
        avg_latency = compute_average_latency(episodes)
        total_cost = compute_cost(episodes)
        error_rate = compute_error_rate(episodes)
        
        metrics = {
            "success_rate": success_rate,
            "average_latency": avg_latency,
            "total_cost": total_cost,
            "error_rate": error_rate,
            "episode_count": len(episodes),
        }
        
        reward = 0.0
        reward += self.weights.get("success", 0.0) * success_rate
        reward += self.weights.get("cost", 0.0) * total_cost
        reward += self.weights.get("latency", 0.0) * avg_latency
        reward += self.weights.get("error_rate", 0.0) * error_rate
        
        success = success_rate > 0.5 and error_rate < 0.3
        
        if workflow_result is not None:
            if hasattr(workflow_result, "get"):
                success = workflow_result.get("success", success)
            elif isinstance(workflow_result, bool):
                success = workflow_result
        
        return EvaluationResult(
            workflow_id=workflow_id,
            reward=reward,
            success=success,
            metrics=metrics,
            metadata={"weights": self.weights},
        )


class ThresholdEvaluator(Evaluator):
    def __init__(
        self,
        success_threshold: float = 0.7,
        error_threshold: float = 0.2,
        latency_threshold: float = 10.0,
    ):
        self.success_threshold = success_threshold
        self.error_threshold = error_threshold
        self.latency_threshold = latency_threshold
    
    def evaluate(self, episodes: List[Any], workflow_result: Optional[Any] = None) -> EvaluationResult:
        if not episodes:
            return EvaluationResult(
                workflow_id="unknown",
                reward=0.0,
                success=False,
                metrics={},
            )
        
        workflow_id = episodes[0].workflow_id if hasattr(episodes[0], "workflow_id") else "unknown"
        
        success_rate = compute_success_rate(episodes)
        avg_latency = compute_average_latency(episodes)
        error_rate = compute_error_rate(episodes)
        
        metrics = {
            "success_rate": success_rate,
            "average_latency": avg_latency,
            "error_rate": error_rate,
            "episode_count": len(episodes),
        }
        
        success = (
            success_rate >= self.success_threshold
            and error_rate <= self.error_threshold
            and avg_latency <= self.latency_threshold
        )
        
        reward = 1.0 if success else 0.0
        
        return EvaluationResult(
            workflow_id=workflow_id,
            reward=reward,
            success=success,
            metrics=metrics,
            metadata={
                "thresholds": {
                    "success": self.success_threshold,
                    "error": self.error_threshold,
                    "latency": self.latency_threshold,
                }
            },
        )
