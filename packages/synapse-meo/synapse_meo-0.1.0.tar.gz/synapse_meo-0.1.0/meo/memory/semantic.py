from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid


class SemanticInsight:
    def __init__(
        self,
        insight_id: Optional[str] = None,
        insight_type: str = "pattern",
        content: str = "",
        confidence: float = 1.0,
        source_episodes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.insight_id = insight_id or str(uuid.uuid4())
        self.insight_type = insight_type
        self.content = content
        self.confidence = confidence
        self.source_episodes = source_episodes or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "insight_type": self.insight_type,
            "content": self.content,
            "confidence": self.confidence,
            "source_episodes": self.source_episodes,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticInsight":
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            insight_id=data.get("insight_id"),
            insight_type=data.get("insight_type", "pattern"),
            content=data.get("content", ""),
            confidence=data.get("confidence", 1.0),
            source_episodes=data.get("source_episodes"),
            metadata=data.get("metadata"),
            created_at=created_at,
        )


class SemanticMemory(ABC):
    @abstractmethod
    def compress_episodes(self, episodes: List[Any]) -> List[SemanticInsight]:
        pass
    
    @abstractmethod
    def get_insights(
        self, insight_type: Optional[str] = None, limit: Optional[int] = None
    ) -> List[SemanticInsight]:
        pass
    
    @abstractmethod
    def add_insight(self, insight: SemanticInsight) -> None:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class LLMSemanticMemory(SemanticMemory):
    def __init__(
        self,
        llm_summarizer: Optional[Callable[[List[Any]], str]] = None,
    ):
        self._insights: List[SemanticInsight] = []
        self._llm_summarizer = llm_summarizer or self._default_summarizer
    
    def _default_summarizer(self, episodes: List[Any]) -> str:
        if not episodes:
            return "No episodes to summarize."
        
        episode_count = len(episodes)
        actions = [ep.action for ep in episodes if hasattr(ep, "action") and ep.action]
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        summary = f"Analyzed {episode_count} episodes. "
        if action_counts:
            most_common = max(action_counts.items(), key=lambda x: x[1])
            summary += f"Most common action: {most_common[0]} ({most_common[1]} times). "
        
        return summary
    
    def compress_episodes(self, episodes: List[Any]) -> List[SemanticInsight]:
        if not episodes:
            return []
        
        summary = self._llm_summarizer(episodes)
        
        insight = SemanticInsight(
            insight_type="summary",
            content=summary,
            confidence=0.8,
            source_episodes=[ep.episode_id for ep in episodes if hasattr(ep, "episode_id")],
            metadata={"episode_count": len(episodes)},
        )
        
        self._insights.append(insight)
        
        action_stats = self._extract_action_statistics(episodes)
        if action_stats:
            stats_insight = SemanticInsight(
                insight_type="statistics",
                content=f"Action statistics: {action_stats}",
                confidence=1.0,
                source_episodes=[ep.episode_id for ep in episodes if hasattr(ep, "episode_id")],
                metadata={"statistics": action_stats},
            )
            self._insights.append(stats_insight)
            return [insight, stats_insight]
        
        return [insight]
    
    def _extract_action_statistics(self, episodes: List[Any]) -> Dict[str, Any]:
        stats = {}
        for ep in episodes:
            if hasattr(ep, "action") and ep.action:
                if ep.action not in stats:
                    stats[ep.action] = {"count": 0, "success": 0, "failure": 0}
                stats[ep.action]["count"] += 1
                
                if hasattr(ep, "metadata") and ep.metadata:
                    if ep.metadata.get("success"):
                        stats[ep.action]["success"] += 1
                    else:
                        stats[ep.action]["failure"] += 1
        
        return stats
    
    def get_insights(
        self, insight_type: Optional[str] = None, limit: Optional[int] = None
    ) -> List[SemanticInsight]:
        insights = self._insights
        
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        
        if limit:
            insights = insights[-limit:]
        
        return insights
    
    def add_insight(self, insight: SemanticInsight) -> None:
        self._insights.append(insight)
    
    def clear(self) -> None:
        self._insights.clear()
