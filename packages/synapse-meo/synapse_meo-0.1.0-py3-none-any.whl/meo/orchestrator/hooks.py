from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import time


class Hook(ABC):
    @abstractmethod
    def before(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def after(self, context: Dict[str, Any], result: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        pass


class ToolCallHook(Hook):
    def __init__(
        self,
        before_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        after_callback: Optional[Callable[[Dict[str, Any], Any], Dict[str, Any]]] = None,
        error_callback: Optional[Callable[[Dict[str, Any], Exception], Dict[str, Any]]] = None,
    ):
        self.before_callback = before_callback
        self.after_callback = after_callback
        self.error_callback = error_callback
    
    def before(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["start_time"] = time.time()
        context["hook_type"] = "tool_call"
        
        if self.before_callback:
            context = self.before_callback(context)
        
        return context
    
    def after(self, context: Dict[str, Any], result: Any) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": True,
        }
        
        context["metrics"] = metrics
        context["result"] = result
        
        if self.after_callback:
            context = self.after_callback(context, result)
        
        return context
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
        }
        
        context["metrics"] = metrics
        context["error"] = error
        
        if self.error_callback:
            context = self.error_callback(context, error)
        
        return context


class AgentCallHook(Hook):
    def __init__(
        self,
        before_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        after_callback: Optional[Callable[[Dict[str, Any], Any], Dict[str, Any]]] = None,
        error_callback: Optional[Callable[[Dict[str, Any], Exception], Dict[str, Any]]] = None,
    ):
        self.before_callback = before_callback
        self.after_callback = after_callback
        self.error_callback = error_callback
    
    def before(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["start_time"] = time.time()
        context["hook_type"] = "agent_call"
        
        if self.before_callback:
            context = self.before_callback(context)
        
        return context
    
    def after(self, context: Dict[str, Any], result: Any) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": True,
        }
        
        context["metrics"] = metrics
        context["result"] = result
        
        if self.after_callback:
            context = self.after_callback(context, result)
        
        return context
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
        }
        
        context["metrics"] = metrics
        context["error"] = error
        
        if self.error_callback:
            context = self.error_callback(context, error)
        
        return context


class PlanningHook(Hook):
    def __init__(
        self,
        before_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        after_callback: Optional[Callable[[Dict[str, Any], Any], Dict[str, Any]]] = None,
        error_callback: Optional[Callable[[Dict[str, Any], Exception], Dict[str, Any]]] = None,
    ):
        self.before_callback = before_callback
        self.after_callback = after_callback
        self.error_callback = error_callback
    
    def before(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["start_time"] = time.time()
        context["hook_type"] = "planning"
        
        if self.before_callback:
            context = self.before_callback(context)
        
        return context
    
    def after(self, context: Dict[str, Any], result: Any) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": True,
        }
        
        context["metrics"] = metrics
        context["result"] = result
        
        if self.after_callback:
            context = self.after_callback(context, result)
        
        return context
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        
        metrics = {
            "duration": end_time - start_time,
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
        }
        
        context["metrics"] = metrics
        context["error"] = error
        
        if self.error_callback:
            context = self.error_callback(context, error)
        
        return context


class CompositeHook(Hook):
    def __init__(self, hooks: list[Hook]):
        self.hooks = hooks
    
    def before(self, context: Dict[str, Any]) -> Dict[str, Any]:
        for hook in self.hooks:
            context = hook.before(context)
        return context
    
    def after(self, context: Dict[str, Any], result: Any) -> Dict[str, Any]:
        for hook in self.hooks:
            context = hook.after(context, result)
        return context
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        for hook in self.hooks:
            context = hook.on_error(context, error)
        return context
