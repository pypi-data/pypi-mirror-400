from typing import Any, Dict, Optional, List
from meo.orchestrator.wrappers import WisdomOrchestrator


class LangChainWrapper:
    def __init__(self, orchestrator: Optional[WisdomOrchestrator] = None):
        self.orchestrator = orchestrator or WisdomOrchestrator()
    
    def wrap_chain(self, chain: Any) -> Any:
        original_invoke = chain.invoke if hasattr(chain, "invoke") else None
        original_run = chain.run if hasattr(chain, "run") else None
        
        def wisdom_invoke(input_data: Any, **kwargs) -> Any:
            def agent_callable(data: Any) -> Any:
                if original_invoke:
                    return original_invoke(data, **kwargs)
                elif original_run:
                    return original_run(data, **kwargs)
                else:
                    raise AttributeError("Chain has no invoke or run method")
            
            result = self.orchestrator.run(
                agent=agent_callable,
                input_data=input_data,
                metadata={"framework": "langchain", "chain_type": type(chain).__name__},
            )
            
            return result["result"]
        
        def wisdom_run(input_data: Any, **kwargs) -> Any:
            return wisdom_invoke(input_data, **kwargs)
        
        if original_invoke:
            chain.invoke = wisdom_invoke
        if original_run:
            chain.run = wisdom_run
        
        chain._meo_orchestrator = self.orchestrator
        
        return chain
    
    def wrap_agent(self, agent: Any) -> Any:
        original_run = agent.run if hasattr(agent, "run") else None
        original_invoke = agent.invoke if hasattr(agent, "invoke") else None
        
        def wisdom_run(input_data: Any, **kwargs) -> Any:
            def agent_callable(data: Any) -> Any:
                if original_run:
                    return original_run(data, **kwargs)
                elif original_invoke:
                    return original_invoke(data, **kwargs)
                else:
                    raise AttributeError("Agent has no run or invoke method")
            
            result = self.orchestrator.run(
                agent=agent_callable,
                input_data=input_data,
                metadata={"framework": "langchain", "agent_type": type(agent).__name__},
            )
            
            return result["result"]
        
        if original_run:
            agent.run = wisdom_run
        if original_invoke:
            agent.invoke = wisdom_run
        
        agent._meo_orchestrator = self.orchestrator
        
        return agent
    
    def wrap_tool(self, tool: Any, tool_name: Optional[str] = None) -> Any:
        name = tool_name or (tool.name if hasattr(tool, "name") else "unknown_tool")
        
        original_run = tool.run if hasattr(tool, "run") else None
        original_func = tool.func if hasattr(tool, "func") else None
        
        def wisdom_tool_run(input_data: Any, **kwargs) -> Any:
            def tool_callable(data: Any) -> Any:
                if original_run:
                    return original_run(data, **kwargs)
                elif original_func:
                    return original_func(data, **kwargs)
                else:
                    raise AttributeError("Tool has no run or func method")
            
            return self.orchestrator.intercept_tool_call(
                tool_name=name,
                tool_input=input_data,
                tool_function=tool_callable,
            )
        
        if original_run:
            tool.run = wisdom_tool_run
        if original_func:
            tool.func = wisdom_tool_run
        
        tool._meo_orchestrator = self.orchestrator
        
        return tool
    
    def get_insights(self) -> List[Dict[str, Any]]:
        return self.orchestrator.get_insights()
    
    def get_workflow_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.orchestrator.get_workflow_history(limit=limit)
