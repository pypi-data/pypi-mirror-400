from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class Episode:
    def __init__(
        self,
        episode_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        state: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        action_input: Optional[Any] = None,
        action_output: Optional[Any] = None,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.episode_id = episode_id or str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.timestamp = timestamp or datetime.utcnow()
        self.state = state or {}
        self.action = action
        self.action_input = action_input
        self.action_output = action_output
        self.metrics = metrics or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "workflow_id": self.workflow_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "state": self.state,
            "action": self.action,
            "action_input": self.action_input,
            "action_output": self.action_output,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        timestamp = data.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        return cls(
            episode_id=data.get("episode_id"),
            workflow_id=data.get("workflow_id"),
            timestamp=timestamp,
            state=data.get("state"),
            action=data.get("action"),
            action_input=data.get("action_input"),
            action_output=data.get("action_output"),
            metrics=data.get("metrics"),
            metadata=data.get("metadata"),
        )


class EpisodicMemory(ABC):
    @abstractmethod
    def record_step(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        action: str,
        action_input: Any,
        action_output: Any,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        pass
    
    @abstractmethod
    def get_workflow_episodes(self, workflow_id: str) -> List[Episode]:
        pass
    
    @abstractmethod
    def get_all_episodes(self, limit: Optional[int] = None) -> List[Episode]:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class InMemoryEpisodicMemory(EpisodicMemory):
    def __init__(self):
        self._episodes: List[Episode] = []
    
    def record_step(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        action: str,
        action_input: Any,
        action_output: Any,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        episode = Episode(
            workflow_id=workflow_id,
            state=state,
            action=action,
            action_input=action_input,
            action_output=action_output,
            metrics=metrics,
            metadata=metadata,
        )
        self._episodes.append(episode)
        return episode
    
    def get_workflow_episodes(self, workflow_id: str) -> List[Episode]:
        return [ep for ep in self._episodes if ep.workflow_id == workflow_id]
    
    def get_all_episodes(self, limit: Optional[int] = None) -> List[Episode]:
        if limit:
            return self._episodes[-limit:]
        return self._episodes.copy()
    
    def clear(self) -> None:
        self._episodes.clear()
