from typing import Any, Dict, Optional, Callable, List
import uuid
from datetime import datetime

from meo.memory.episodic import EpisodicMemory, InMemoryEpisodicMemory
from meo.memory.semantic import SemanticMemory, LLMSemanticMemory
from meo.memory.storage import StorageBackend, JSONLStorage
from meo.evaluators.reward import Evaluator, DefaultRewardEvaluator
from meo.meta.policy_adapter import PolicyAdapter, RuleBasedPolicyAdapter
from meo.orchestrator.hooks import Hook, ToolCallHook, AgentCallHook
from meo.config.default_settings import DefaultConfig
from meo.utils.logging import get_logger


class WisdomOrchestrator:
    def __init__(
        self,
        episodic_memory: Optional[EpisodicMemory] = None,
        semantic_memory: Optional[SemanticMemory] = None,
        storage_backend: Optional[StorageBackend] = None,
        evaluator: Optional[Evaluator] = None,
        policy_adapter: Optional[PolicyAdapter] = None,
        config: Optional[DefaultConfig] = None,
        enable_hooks: bool = True,
    ):
        self.config = config or DefaultConfig()
        self.logger = get_logger(__name__, self.config.LOG_LEVEL)
        
        self.episodic_memory = episodic_memory or InMemoryEpisodicMemory()
        self.semantic_memory = semantic_memory or LLMSemanticMemory()
        self.storage_backend = storage_backend or JSONLStorage(
            self.config.EPISODIC_MEMORY_FILE
        )
        self.evaluator = evaluator or DefaultRewardEvaluator(
            weights=self.config.REWARD_WEIGHTS
        )
        self.policy_adapter = policy_adapter or RuleBasedPolicyAdapter()
        
        self.enable_hooks = enable_hooks
        self._tool_hook = ToolCallHook()
        self._agent_hook = AgentCallHook()
        
        self._current_workflow_id: Optional[str] = None
        self._workflow_state: Dict[str, Any] = {}
    
    def run(
        self,
        agent: Callable[[Any], Any],
        input_data: Any,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._current_workflow_id = workflow_id or str(uuid.uuid4())
        self._workflow_state = {
            "workflow_id": self._current_workflow_id,
            "start_time": datetime.utcnow(),
            "input": input_data,
            "metadata": metadata or {},
        }
        
        self.logger.info(f"Starting workflow: {self._current_workflow_id}")
        
        try:
            insights = self.semantic_memory.get_insights()
            if insights and self.config.ENABLE_POLICY_ADAPTATION:
                self.logger.info(f"Loaded {len(insights)} insights from semantic memory")
            
            result = self._execute_agent(agent, input_data)
            
            self._workflow_state["result"] = result
            self._workflow_state["success"] = True
            
        except Exception as e:
            self.logger.error(f"Workflow {self._current_workflow_id} failed: {e}")
            self._workflow_state["error"] = str(e)
            self._workflow_state["success"] = False
            result = {"error": str(e), "success": False}
        
        self._workflow_state["end_time"] = datetime.utcnow()
        
        self._post_workflow_processing(result)
        
        return {
            "workflow_id": self._current_workflow_id,
            "result": result,
            "success": self._workflow_state.get("success", False),
            "metadata": self._workflow_state.get("metadata", {}),
        }
    
    def _execute_agent(self, agent: Callable[[Any], Any], input_data: Any) -> Any:
        wrapped_agent = self._wrap_agent(agent)
        
        result = wrapped_agent(input_data)
        
        return result
    
    def _wrap_agent(self, agent: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapped_agent_call(input_data: Any) -> Any:
            context = {
                "workflow_id": self._current_workflow_id,
                "action": "agent_call",
                "action_input": input_data,
                "state": self._workflow_state.copy(),
            }
            
            if self.enable_hooks:
                context = self._agent_hook.before(context)
            
            try:
                result = agent(input_data)
                
                if self.enable_hooks:
                    context = self._agent_hook.after(context, result)
                
                self._record_step(
                    action="agent_call",
                    action_input=input_data,
                    action_output=result,
                    metrics=context.get("metrics", {}),
                    metadata={"success": True},
                )
                
                return result
                
            except Exception as e:
                if self.enable_hooks:
                    context = self._agent_hook.on_error(context, e)
                
                self._record_step(
                    action="agent_call",
                    action_input=input_data,
                    action_output=None,
                    metrics=context.get("metrics", {}),
                    metadata={"success": False, "error": str(e)},
                )
                
                raise
        
        return wrapped_agent_call
    
    def _record_step(
        self,
        action: str,
        action_input: Any,
        action_output: Any,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        episode = self.episodic_memory.record_step(
            workflow_id=self._current_workflow_id,
            state=self._workflow_state.copy(),
            action=action,
            action_input=action_input,
            action_output=action_output,
            metrics=metrics,
            metadata=metadata,
        )
        
        self.storage_backend.save(
            key=f"episode_{episode.episode_id}",
            data=episode.to_dict(),
        )
        
        self.logger.debug(f"Recorded episode: {episode.episode_id}")
    
    def _post_workflow_processing(self, result: Any) -> None:
        episodes = self.episodic_memory.get_workflow_episodes(self._current_workflow_id)
        
        if not episodes:
            self.logger.warning(f"No episodes found for workflow {self._current_workflow_id}")
            return
        
        evaluation = self.evaluator.evaluate(episodes, result)
        
        self.logger.info(
            f"Workflow {self._current_workflow_id} evaluation: "
            f"reward={evaluation.reward:.3f}, success={evaluation.success}"
        )
        
        self.storage_backend.save(
            key=f"evaluation_{self._current_workflow_id}",
            data=evaluation.to_dict(),
        )
        
        if len(episodes) >= self.config.SEMANTIC_COMPRESSION_THRESHOLD:
            insights = self.semantic_memory.compress_episodes(episodes)
            
            self.logger.info(f"Generated {len(insights)} insights from {len(episodes)} episodes")
            
            for insight in insights:
                self.storage_backend.save(
                    key=f"insight_{insight.insight_id}",
                    data=insight.to_dict(),
                )
            
            if self.config.ENABLE_POLICY_ADAPTATION:
                all_insights = self.semantic_memory.get_insights()
                self.logger.info(f"Updating policy adapter with {len(all_insights)} insights")
    
    def intercept_tool_call(
        self,
        tool_name: str,
        tool_input: Any,
        tool_function: Callable[[Any], Any],
    ) -> Any:
        context = {
            "workflow_id": self._current_workflow_id,
            "action": f"tool_call:{tool_name}",
            "action_input": tool_input,
            "state": self._workflow_state.copy(),
        }
        
        if self.enable_hooks:
            context = self._tool_hook.before(context)
        
        try:
            result = tool_function(tool_input)
            
            if self.enable_hooks:
                context = self._tool_hook.after(context, result)
            
            self._record_step(
                action=f"tool_call:{tool_name}",
                action_input=tool_input,
                action_output=result,
                metrics=context.get("metrics", {}),
                metadata={"success": True, "tool_name": tool_name},
            )
            
            return result
            
        except Exception as e:
            if self.enable_hooks:
                context = self._tool_hook.on_error(context, e)
            
            self._record_step(
                action=f"tool_call:{tool_name}",
                action_input=tool_input,
                action_output=None,
                metrics=context.get("metrics", {}),
                metadata={"success": False, "error": str(e), "tool_name": tool_name},
            )
            
            raise
    
    def get_policy_recommendation(
        self,
        context: Dict[str, Any],
        available_actions: List[str],
    ) -> Dict[str, Any]:
        insights = self.semantic_memory.get_insights()
        
        recommendation = self.policy_adapter.adapt_decision(
            context=context,
            available_actions=available_actions,
            insights=insights,
        )
        
        return recommendation
    
    def get_workflow_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        evaluations = self.storage_backend.load_all(prefix="evaluation_")
        
        if limit:
            evaluations = evaluations[-limit:]
        
        return evaluations
    
    def get_insights(
        self, insight_type: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        insights = self.semantic_memory.get_insights(insight_type=insight_type, limit=limit)
        return [insight.to_dict() for insight in insights]
