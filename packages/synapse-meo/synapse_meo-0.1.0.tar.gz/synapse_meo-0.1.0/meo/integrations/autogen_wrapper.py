from typing import Any, Dict, Optional, List, Callable
from meo.orchestrator.wrappers import WisdomOrchestrator


class AutogenWrapper:
    def __init__(self, orchestrator: Optional[WisdomOrchestrator] = None):
        self.orchestrator = orchestrator or WisdomOrchestrator()
    
    def wrap_agent(self, agent: Any) -> Any:
        original_generate_reply = None
        if hasattr(agent, "generate_reply"):
            original_generate_reply = agent.generate_reply
        
        def wisdom_generate_reply(messages: Any, **kwargs) -> Any:
            def agent_callable(data: Any) -> Any:
                if original_generate_reply:
                    return original_generate_reply(data, **kwargs)
                else:
                    raise AttributeError("Agent has no generate_reply method")
            
            result = self.orchestrator.run(
                agent=agent_callable,
                input_data=messages,
                metadata={
                    "framework": "autogen",
                    "agent_name": getattr(agent, "name", "unknown"),
                    "agent_type": type(agent).__name__,
                },
            )
            
            return result["result"]
        
        if original_generate_reply:
            agent.generate_reply = wisdom_generate_reply
        
        agent._meo_orchestrator = self.orchestrator
        
        return agent
    
    def wrap_group_chat(self, group_chat: Any) -> Any:
        original_run = None
        if hasattr(group_chat, "run"):
            original_run = group_chat.run
        
        def wisdom_run(messages: Any, **kwargs) -> Any:
            def group_callable(data: Any) -> Any:
                if original_run:
                    return original_run(data, **kwargs)
                else:
                    raise AttributeError("GroupChat has no run method")
            
            result = self.orchestrator.run(
                agent=group_callable,
                input_data=messages,
                metadata={
                    "framework": "autogen",
                    "type": "group_chat",
                    "agents": getattr(group_chat, "agents", []),
                },
            )
            
            return result["result"]
        
        if original_run:
            group_chat.run = wisdom_run
        
        group_chat._meo_orchestrator = self.orchestrator
        
        return group_chat
    
    def wrap_function(
        self,
        func: Callable,
        function_name: Optional[str] = None,
    ) -> Callable:
        name = function_name or func.__name__
        
        def wisdom_function_wrapper(*args, **kwargs) -> Any:
            def func_callable(data: Any) -> Any:
                return func(*args, **kwargs)
            
            return self.orchestrator.intercept_tool_call(
                tool_name=name,
                tool_input={"args": args, "kwargs": kwargs},
                tool_function=func_callable,
            )
        
        wisdom_function_wrapper._meo_orchestrator = self.orchestrator
        wisdom_function_wrapper.__name__ = name
        
        return wisdom_function_wrapper
    
    def get_insights(self) -> List[Dict[str, Any]]:
        return self.orchestrator.get_insights()
    
    def get_workflow_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.orchestrator.get_workflow_history(limit=limit)
