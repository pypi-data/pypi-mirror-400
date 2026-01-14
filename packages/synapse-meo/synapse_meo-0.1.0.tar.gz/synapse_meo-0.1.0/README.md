# MEO (Memory Embedded Orchestration)

**MEO** is a foundational layer for agentic AI systems that adds persistent memory, evaluation, semantic compression, and meta-policy adaptation to any existing agent/orchestrator framework.

## 🎯 Overview

MEO doesn't implement agents itself. Instead, it **wraps and enhances** existing agent frameworks like LangChain, LangGraph, Autogen, CrewAI, or custom agents to make any orchestrator **self-improving across multiple runs**.

## 🧠 Why Memory-Enhanced Orchestration Matters

Adding a persistent memory + meta-policy layer transforms your AI orchestration from static planning to adaptive intelligence:

| Benefit | Impact |
|---------|--------|
| **Learn from past workflows** | Avoid repeating failed decisions across runs |
| **Adaptive agent/tool selection** | Reduce cost, latency, and errors dynamically |
| **Pattern recognition** | Automatically prefer strategies that worked before |
| **Proactive quality assurance** | Flag likely failures before they happen |
| **Continuous improvement** | Orchestrator becomes smarter with every execution |
| **Vendor/agent-agnostic** | Works with LangChain, Autogen, custom agents |

**In short:** MEO turns orchestration into a **self-improving layer**, not just a static planner.

## 💎 Strategic Value

### Foundational Technology
Anyone building multi-agent AI workflows needs adaptive orchestration. MEO provides the missing memory and learning layer that makes agents truly intelligent over time.

### Competitive Advantage
Major frameworks like LangChain could adopt this approach in the future — early implementation gives you **first-mover advantage** in the rapidly evolving agentic AI space.

### Enterprise Appeal
Organizations demand **reliability, efficiency, and cost control**. Memory-enhanced orchestration directly addresses these needs by:
- Reducing redundant API calls through learned patterns
- Minimizing failures by avoiding known problematic paths
- Optimizing resource allocation based on historical performance

### Research Relevance
MEO overlaps with cutting-edge areas including **meta-reinforcement learning**, **multi-agent learning**, and **AI self-optimization** — making it both practically useful and academically significant.

## ⚙️ Technical Viability

- **Python-first ecosystem** → Easy integration with existing tools
- **Minimal dependencies** → Simple adoption and enterprise trust
- **Scalable architecture** → Episodic memory, semantic summarization, meta-policy adapter
- **Flexible implementation** → Start lightweight (file-based, LLM stubs) and scale to vector DB + embeddings + advanced evaluators

## ⚠️ Considerations

| Challenge | Mitigation |
|-----------|-----------|
| Not a replacement for agents | Users wrap existing workflows carefully with clear interfaces |
| Semantic memory quality depends on evaluator | Configurable reward functions and custom evaluators supported |
| Scaling to many agents/workflows | Thoughtful vector memory architecture (roadmap item) |

None of these are showstoppers — they're solvable with careful engineering and the extensible architecture MEO provides.

## ✨ Key Features

- **Episodic Memory**: Records every step taken by an agent workflow
- **Semantic Memory**: Converts episodic logs into compressed semantic insights (patterns, rules, statistics)
- **Evaluation System**: Assigns reward scores based on success, cost, latency, and error rates
- **Meta-Policy Adaptation**: Modifies orchestration decisions using learned rules from semantic memory
- **Framework Agnostic**: Works with LangChain, Autogen, and custom agent implementations
- **Persistent Storage**: File-based storage (JSONL or SQLite) for long-term memory

## 📦 Installation

```bash
pip install synapse-meo
```

### Optional Dependencies

For LangChain integration:
```bash
pip install synapse-meo[langchain]
```

For Autogen integration:
```bash
pip install synapse-meo[autogen]
```

## 🚀 Quick Start

### Basic Usage

```python
from meo import WisdomOrchestrator

# Create the orchestrator
orchestrator = WisdomOrchestrator()

# Define your agent as a callable
def my_agent(input_data):
    # Your agent logic here
    return {"result": "processed", "success": True}

# Run with MEO orchestration
result = orchestrator.run(agent=my_agent, input_data="Hello, world!")

print(result)
# {
#     "workflow_id": "...",
#     "result": {"result": "processed", "success": True},
#     "success": True,
#     "metadata": {}
# }
```

### LangChain Integration

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from meo.integrations.langchain_wrapper import LangChainWrapper

# Create your LangChain components
llm = OpenAI(temperature=0.7)
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short poem about {topic}"
)
chain = LLMChain(llm=llm, prompt=prompt)

# Wrap with MEO
wrapper = LangChainWrapper()
enhanced_chain = wrapper.wrap_chain(chain)

# Use as normal - MEO tracks everything
result = enhanced_chain.invoke({"topic": "artificial intelligence"})

# Get insights from past runs
insights = wrapper.get_insights()
print(f"Learned {len(insights)} insights from previous executions")
```

### Autogen Integration

```python
from autogen import AssistantAgent, UserProxyAgent
from meo.integrations.autogen_wrapper import AutogenWrapper

# Create Autogen agents
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER"
)

# Wrap with MEO
wrapper = AutogenWrapper()
enhanced_assistant = wrapper.wrap_agent(assistant)

# Agents now learn from past interactions
user_proxy.initiate_chat(
    enhanced_assistant,
    message="Solve this problem: ..."
)

# View workflow history
history = wrapper.get_workflow_history(limit=10)
```

## 🏗️ Architecture

MEO consists of several key modules:

### Memory Module

- **EpisodicMemory**: Records individual steps (state, action, input, output, metrics)
- **SemanticMemory**: Compresses episodes into patterns, rules, and insights
- **StorageBackend**: Persists memory (JSONL or SQLite)

```python
from meo.memory import InMemoryEpisodicMemory, LLMSemanticMemory, JSONLStorage

episodic = InMemoryEpisodicMemory()
semantic = LLMSemanticMemory()
storage = JSONLStorage("./my_memory.jsonl")
```

### Evaluators Module

- **Evaluator**: Assigns reward scores to workflow executions
- **Metrics**: Computes quality/performance metrics

```python
from meo.evaluators import DefaultRewardEvaluator

evaluator = DefaultRewardEvaluator(
    weights={
        "success": 1.0,
        "cost": -0.1,
        "latency": -0.05,
        "error_rate": -0.5,
    }
)
```

### Meta Module

- **PolicyAdapter**: Modifies decisions using semantic memory insights

```python
from meo.meta import RuleBasedPolicyAdapter

policy = RuleBasedPolicyAdapter()

# Get recommendations based on learned patterns
recommendation = policy.adapt_decision(
    context={"current_task": "summarization"},
    available_actions=["tool_a", "tool_b", "tool_c"],
    insights=semantic.get_insights()
)
```

### Orchestrator Module

- **WisdomOrchestrator**: Main class that coordinates all components
- **Hooks**: Intercept tool calls, agent calls, and planning steps

```python
from meo import WisdomOrchestrator
from meo.config import DefaultConfig

config = DefaultConfig()
config.STORAGE_DIR = "./my_meo_data"
config.ENABLE_POLICY_ADAPTATION = True

orchestrator = WisdomOrchestrator(
    episodic_memory=episodic,
    semantic_memory=semantic,
    storage_backend=storage,
    evaluator=evaluator,
    policy_adapter=policy,
    config=config
)
```

## 🔧 Advanced Usage

### Custom Evaluator

```python
from meo.evaluators import Evaluator, EvaluationResult

class CustomEvaluator(Evaluator):
    def evaluate(self, episodes, workflow_result=None):
        # Custom evaluation logic
        success = len(episodes) > 0 and all(
            ep.metadata.get("success", False) for ep in episodes
        )
        reward = 1.0 if success else 0.0
        
        return EvaluationResult(
            workflow_id=episodes[0].workflow_id,
            reward=reward,
            success=success,
            metrics={"episode_count": len(episodes)}
        )

orchestrator = WisdomOrchestrator(evaluator=CustomEvaluator())
```

### Custom Semantic Compression

```python
from meo.memory import SemanticMemory, SemanticInsight

class CustomSemanticMemory(SemanticMemory):
    def compress_episodes(self, episodes):
        # Analyze episodes and extract insights
        insights = []
        
        # Example: Find frequently failing actions
        action_failures = {}
        for ep in episodes:
            if not ep.metadata.get("success", True):
                action = ep.action
                action_failures[action] = action_failures.get(action, 0) + 1
        
        for action, count in action_failures.items():
            if count > 3:
                insight = SemanticInsight(
                    insight_type="rule",
                    content=f"Avoid using {action} - high failure rate",
                    confidence=0.8,
                    source_episodes=[ep.episode_id for ep in episodes]
                )
                insights.append(insight)
                self.add_insight(insight)
        
        return insights
```

### Tool Call Interception

```python
# Intercept and track individual tool calls
def my_expensive_tool(input_data):
    # Some expensive operation
    return process(input_data)

result = orchestrator.intercept_tool_call(
    tool_name="expensive_tool",
    tool_input={"query": "data"},
    tool_function=my_expensive_tool
)

# MEO automatically tracks cost, latency, success/failure
```

### Policy-Guided Decision Making

```python
# Get recommendations based on learned patterns
context = {
    "task_type": "data_analysis",
    "data_size": "large",
    "priority": "speed"
}

available_actions = ["pandas_tool", "spark_tool", "dask_tool"]

recommendation = orchestrator.get_policy_recommendation(
    context=context,
    available_actions=available_actions
)

print(f"Recommended action: {recommendation['recommended_action']}")
print(f"Action scores: {recommendation['action_scores']}")
```

## 📊 Monitoring and Analysis

```python
# Get workflow history
history = orchestrator.get_workflow_history(limit=20)
for eval_result in history:
    print(f"Workflow {eval_result['workflow_id']}: "
          f"reward={eval_result['reward']:.2f}, "
          f"success={eval_result['success']}")

# Get learned insights
insights = orchestrator.get_insights(insight_type="statistics")
for insight in insights:
    print(f"{insight['insight_type']}: {insight['content']}")
```

## 🎛️ Configuration

```python
from meo.config import DefaultConfig

config = DefaultConfig()

# Storage settings
config.STORAGE_DIR = "./meo_data"
config.STORAGE_BACKEND = "jsonl"  # or "sqlite"

# Evaluation weights
config.REWARD_WEIGHTS = {
    "success": 1.0,
    "cost": -0.1,
    "latency": -0.05,
    "error_rate": -0.5,
}

# Semantic compression
config.SEMANTIC_COMPRESSION_THRESHOLD = 10  # Compress after N episodes

# Policy adaptation
config.ENABLE_POLICY_ADAPTATION = True

# Logging
config.LOG_LEVEL = "INFO"
```

## 🧪 Examples

See the `examples/` directory for complete working examples:

- `examples/basic_usage.py` - Simple agent wrapping
- `examples/langchain_example.py` - LangChain integration
- `examples/autogen_example.py` - Autogen integration
- `examples/custom_components.py` - Custom evaluators and memory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Apache License 2.0 - see LICENSE file for details.

This project is licensed under the Apache License 2.0, which includes an explicit patent grant, ensuring contributors retain patent rights while providing users with patent protection.

## 🔗 Links

- Documentation: [GitHub Wiki](https://github.com/yourusername/meo/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/meo/issues)
- PyPI: [https://pypi.org/project/meo/](https://pypi.org/project/meo/)

## 💡 How It Works

1. **Intercept**: MEO wraps your agent/framework and intercepts every decision
2. **Record**: Each step is recorded into episodic memory (state, action, I/O, metrics)
3. **Evaluate**: After workflow completion, the evaluator assigns rewards and labels
4. **Compress**: Episodic logs are compressed into semantic insights (patterns, rules, stats)
5. **Store**: Insights are persisted to storage for future runs
6. **Adapt**: Insights are injected back into decision-making via the policy adapter

This creates a **self-improving loop** where your agent learns from past executions and continuously optimizes its behavior.

---

**Made with ❤️ for the agentic AI community**

© 2026 Synapse Data / Ivan Lluch
