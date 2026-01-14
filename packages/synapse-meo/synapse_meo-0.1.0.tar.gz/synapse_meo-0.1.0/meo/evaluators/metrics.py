from typing import List, Any, Dict


def compute_success_rate(episodes: List[Any]) -> float:
    if not episodes:
        return 0.0
    
    success_count = 0
    for episode in episodes:
        if hasattr(episode, "metadata") and episode.metadata:
            if episode.metadata.get("success", False):
                success_count += 1
        elif hasattr(episode, "metrics") and episode.metrics:
            if episode.metrics.get("success", False):
                success_count += 1
    
    return success_count / len(episodes)


def compute_average_latency(episodes: List[Any]) -> float:
    if not episodes:
        return 0.0
    
    total_latency = 0.0
    count = 0
    
    for episode in episodes:
        latency = None
        
        if hasattr(episode, "metrics") and episode.metrics:
            latency = episode.metrics.get("latency") or episode.metrics.get("duration")
        
        if latency is not None:
            total_latency += float(latency)
            count += 1
    
    return total_latency / count if count > 0 else 0.0


def compute_cost(episodes: List[Any]) -> float:
    if not episodes:
        return 0.0
    
    total_cost = 0.0
    
    for episode in episodes:
        cost = None
        
        if hasattr(episode, "metrics") and episode.metrics:
            cost = episode.metrics.get("cost")
        
        if cost is not None:
            total_cost += float(cost)
    
    return total_cost


def compute_error_rate(episodes: List[Any]) -> float:
    if not episodes:
        return 0.0
    
    error_count = 0
    for episode in episodes:
        if hasattr(episode, "metadata") and episode.metadata:
            if episode.metadata.get("error", False) or episode.metadata.get("failed", False):
                error_count += 1
        elif hasattr(episode, "metrics") and episode.metrics:
            if episode.metrics.get("error", False) or episode.metrics.get("failed", False):
                error_count += 1
    
    return error_count / len(episodes)


def compute_action_distribution(episodes: List[Any]) -> Dict[str, int]:
    distribution = {}
    
    for episode in episodes:
        if hasattr(episode, "action") and episode.action:
            action = episode.action
            distribution[action] = distribution.get(action, 0) + 1
    
    return distribution


def compute_average_metric(episodes: List[Any], metric_name: str) -> float:
    if not episodes:
        return 0.0
    
    total = 0.0
    count = 0
    
    for episode in episodes:
        value = None
        
        if hasattr(episode, "metrics") and episode.metrics:
            value = episode.metrics.get(metric_name)
        
        if value is not None:
            total += float(value)
            count += 1
    
    return total / count if count > 0 else 0.0


def compute_workflow_duration(episodes: List[Any]) -> float:
    if not episodes:
        return 0.0
    
    timestamps = []
    for episode in episodes:
        if hasattr(episode, "timestamp") and episode.timestamp:
            timestamps.append(episode.timestamp)
    
    if len(timestamps) < 2:
        return 0.0
    
    timestamps.sort()
    duration = (timestamps[-1] - timestamps[0]).total_seconds()
    return duration
