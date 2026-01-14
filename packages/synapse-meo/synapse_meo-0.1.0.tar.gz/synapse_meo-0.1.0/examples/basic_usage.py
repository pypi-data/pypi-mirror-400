from meo import WisdomOrchestrator


def simple_agent(input_data):
    print(f"Processing: {input_data}")
    
    if "error" in str(input_data).lower():
        raise ValueError("Simulated error")
    
    result = {
        "processed": input_data,
        "length": len(str(input_data)),
        "success": True
    }
    
    return result


def main():
    orchestrator = WisdomOrchestrator()
    
    print("=== Running workflows ===\n")
    
    for i in range(5):
        input_text = f"Task {i+1}: Process this data"
        
        print(f"\nWorkflow {i+1}:")
        result = orchestrator.run(
            agent=simple_agent,
            input_data=input_text,
            metadata={"iteration": i+1}
        )
        
        print(f"  Workflow ID: {result['workflow_id']}")
        print(f"  Success: {result['success']}")
        print(f"  Result: {result['result']}")
    
    print("\n=== Workflow History ===\n")
    history = orchestrator.get_workflow_history()
    for eval_result in history:
        print(f"Workflow {eval_result['workflow_id'][:8]}...: "
              f"reward={eval_result['reward']:.3f}, "
              f"success={eval_result['success']}")
    
    print("\n=== Learned Insights ===\n")
    insights = orchestrator.get_insights()
    for insight in insights:
        print(f"[{insight['insight_type']}] {insight['content']}")
    
    print("\n=== Policy Recommendations ===\n")
    recommendation = orchestrator.get_policy_recommendation(
        context={"task": "processing"},
        available_actions=["agent_call", "tool_call", "planning"]
    )
    print(f"Recommended action: {recommendation['recommended_action']}")
    print(f"Action scores: {recommendation['action_scores']}")


if __name__ == "__main__":
    main()
