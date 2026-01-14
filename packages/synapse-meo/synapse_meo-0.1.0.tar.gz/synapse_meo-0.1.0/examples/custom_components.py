from meo import WisdomOrchestrator
from meo.evaluators import Evaluator, EvaluationResult
from meo.memory import SemanticMemory, SemanticInsight
from meo.meta import PolicyAdapter, PolicyRule


class CustomEvaluator(Evaluator):
    def evaluate(self, episodes, workflow_result=None):
        if not episodes:
            return EvaluationResult(
                workflow_id="unknown",
                reward=0.0,
                success=False,
                metrics={}
            )
        
        workflow_id = episodes[0].workflow_id
        
        success_count = sum(
            1 for ep in episodes 
            if ep.metadata.get("success", False)
        )
        success_rate = success_count / len(episodes)
        
        reward = success_rate * 10.0
        
        return EvaluationResult(
            workflow_id=workflow_id,
            reward=reward,
            success=success_rate > 0.8,
            metrics={
                "success_rate": success_rate,
                "episode_count": len(episodes),
                "custom_metric": "evaluated"
            }
        )


class CustomSemanticMemory(SemanticMemory):
    def __init__(self):
        self._insights = []
    
    def compress_episodes(self, episodes):
        insights = []
        
        action_stats = {}
        for ep in episodes:
            action = ep.action
            if action not in action_stats:
                action_stats[action] = {"total": 0, "success": 0}
            
            action_stats[action]["total"] += 1
            if ep.metadata.get("success", False):
                action_stats[action]["success"] += 1
        
        for action, stats in action_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            
            insight = SemanticInsight(
                insight_type="action_performance",
                content=f"Action '{action}' has {success_rate:.1%} success rate",
                confidence=min(stats["total"] / 10.0, 1.0),
                metadata={"action": action, "stats": stats}
            )
            insights.append(insight)
            self._insights.append(insight)
        
        return insights
    
    def get_insights(self, insight_type=None, limit=None):
        insights = self._insights
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        if limit:
            insights = insights[-limit:]
        return insights
    
    def add_insight(self, insight):
        self._insights.append(insight)
    
    def clear(self):
        self._insights.clear()


class CustomPolicyAdapter(PolicyAdapter):
    def __init__(self):
        self._rules = []
        self._learned_preferences = {}
    
    def adapt_decision(self, context, available_actions, insights=None):
        if insights:
            for insight in insights:
                if insight.insight_type == "action_performance":
                    action = insight.metadata.get("action")
                    stats = insight.metadata.get("stats", {})
                    if stats.get("total", 0) > 0:
                        success_rate = stats["success"] / stats["total"]
                        self._learned_preferences[action] = success_rate
        
        action_scores = {}
        for action in available_actions:
            score = self._learned_preferences.get(action, 0.5)
            action_scores[action] = score
        
        recommended = max(action_scores.items(), key=lambda x: x[1])[0] if action_scores else None
        
        return {
            "recommended_action": recommended,
            "action_scores": action_scores,
            "learned_preferences": self._learned_preferences.copy()
        }
    
    def add_rule(self, rule):
        self._rules.append(rule)
    
    def get_rules(self):
        return self._rules.copy()
    
    def clear_rules(self):
        self._rules.clear()
        self._learned_preferences.clear()


def custom_agent(input_data):
    import random
    
    success = random.random() > 0.3
    
    if not success:
        return {
            "result": "failed",
            "success": False,
            "error": "Random failure"
        }
    
    return {
        "result": f"Processed: {input_data}",
        "success": True,
        "quality_score": random.uniform(0.7, 1.0)
    }


def main():
    print("=== Custom Components Example ===\n")
    
    orchestrator = WisdomOrchestrator(
        evaluator=CustomEvaluator(),
        semantic_memory=CustomSemanticMemory(),
        policy_adapter=CustomPolicyAdapter()
    )
    
    print("Running workflows with custom components...\n")
    
    for i in range(10):
        result = orchestrator.run(
            agent=custom_agent,
            input_data=f"Task {i+1}",
            metadata={"iteration": i+1}
        )
        
        print(f"Workflow {i+1}: success={result['success']}, "
              f"result={result['result']}")
    
    print("\n=== Custom Evaluation Results ===\n")
    history = orchestrator.get_workflow_history()
    for eval_result in history:
        print(f"Workflow {eval_result['workflow_id'][:8]}...: "
              f"reward={eval_result['reward']:.2f}, "
              f"metrics={eval_result['metrics']}")
    
    print("\n=== Custom Semantic Insights ===\n")
    insights = orchestrator.get_insights()
    for insight in insights:
        print(f"[{insight['insight_type']}] {insight['content']}")
        print(f"  Confidence: {insight['confidence']:.2f}")
    
    print("\n=== Custom Policy Recommendations ===\n")
    recommendation = orchestrator.get_policy_recommendation(
        context={"task": "processing"},
        available_actions=["agent_call", "tool_call:search", "tool_call:analyze"]
    )
    print(f"Recommended: {recommendation['recommended_action']}")
    print(f"Learned preferences: {recommendation.get('learned_preferences', {})}")


if __name__ == "__main__":
    main()
