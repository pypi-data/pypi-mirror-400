from meo.integrations.langchain_wrapper import LangChainWrapper


def mock_langchain_chain():
    class MockChain:
        def __init__(self):
            self.name = "MockChain"
        
        def invoke(self, input_data, **kwargs):
            topic = input_data.get("topic", "unknown")
            return {
                "result": f"Generated content about {topic}",
                "success": True,
                "tokens": 150
            }
        
        def run(self, input_data, **kwargs):
            return self.invoke(input_data, **kwargs)
    
    return MockChain()


def main():
    print("=== LangChain + MEO Integration Example ===\n")
    
    wrapper = LangChainWrapper()
    
    chain = mock_langchain_chain()
    
    enhanced_chain = wrapper.wrap_chain(chain)
    
    print("Running enhanced chain multiple times...\n")
    
    topics = ["AI", "quantum computing", "blockchain", "robotics", "neuroscience"]
    
    for topic in topics:
        print(f"Processing topic: {topic}")
        result = enhanced_chain.invoke({"topic": topic})
        print(f"  Result: {result}\n")
    
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
        if insight.get('metadata', {}).get('statistics'):
            print(f"  Statistics: {insight['metadata']['statistics']}")


if __name__ == "__main__":
    main()
