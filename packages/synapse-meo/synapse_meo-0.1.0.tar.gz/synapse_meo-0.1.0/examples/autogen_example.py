from meo.integrations.autogen_wrapper import AutogenWrapper


def mock_autogen_agent():
    class MockAgent:
        def __init__(self, name):
            self.name = name
        
        def generate_reply(self, messages, **kwargs):
            if isinstance(messages, list) and messages:
                last_message = messages[-1]
                content = last_message.get("content", "")
            else:
                content = str(messages)
            
            return {
                "role": "assistant",
                "content": f"Processed by {self.name}: {content}",
                "success": True
            }
    
    return MockAgent("assistant")


def main():
    print("=== Autogen + MEO Integration Example ===\n")
    
    wrapper = AutogenWrapper()
    
    agent = mock_autogen_agent()
    
    enhanced_agent = wrapper.wrap_agent(agent)
    
    print("Running enhanced agent multiple times...\n")
    
    messages_list = [
        [{"role": "user", "content": "Analyze this dataset"}],
        [{"role": "user", "content": "Generate a report"}],
        [{"role": "user", "content": "Summarize findings"}],
        [{"role": "user", "content": "Create visualizations"}],
    ]
    
    for i, messages in enumerate(messages_list, 1):
        print(f"Interaction {i}:")
        result = enhanced_agent.generate_reply(messages)
        print(f"  Response: {result['content']}\n")
    
    print("\n=== Workflow History ===\n")
    history = wrapper.get_workflow_history()
    for i, eval_result in enumerate(history, 1):
        print(f"{i}. Workflow {eval_result['workflow_id'][:8]}...: "
              f"reward={eval_result['reward']:.3f}, "
              f"success={eval_result['success']}")
    
    print("\n=== Learned Insights ===\n")
    insights = wrapper.get_insights()
    for insight in insights:
        print(f"[{insight['insight_type']}] {insight['content']}")


if __name__ == "__main__":
    main()
