# Cognitive Load Monitor

**Operational visibility for AI agent architectures**

Cirquit Breakers for Agentic Workflows. When you deploy AI agents into production, they become intelligent workers managing resources and making decisions under varying conditions. Yet unlike traditional distributed systems—where we monitor CPU, memory, and latency—AI agents operate as black boxes. You send requests, get responses, and everything in between remains opaque.

**Until something breaks.**

The Cognitive Load Monitor brings the operational discipline of distributed systems to AI agents. It treats cognitive load as an engineering metric—measurable, actionable, and essential for production reliability.

## The Problem

Your agent fleet handles requests with wildly different complexity:
- Simple queries: 500 tokens, 2 reasoning steps, done in 200ms
- Complex queries: 3,500 tokens, 12 reasoning steps, multiple uncertain assumptions, 2 seconds

**Without visibility, your orchestration layer treats both identically.** You can't route simple queries to cheaper models. You can't detect when agents are pushed beyond capacity. You can't flag outputs needing human review. You're flying blind.

Traditional monitoring doesn't help. System metrics don't reveal that an agent is at 90% of its context budget. API latency doesn't show repeated backtracking. You only learn about problems through user complaints.

## The Solution

The Cognitive Load Monitor captures what agents already expose during normal execution:

- **Token consumption** → Context pressure
- **Reasoning steps & backtracking** → Problem-solving complexity  
- **Latency vs expectations** → Temporal stress
- **Unresolved assumptions** → Output uncertainty
- **Self-corrections** → Execution stability

These observable signals combine into a normalized **Cognitive Load Index (0–1)** that drives intelligent orchestration decisions.

## Installation

```bash
pip install cognitive-load-monitor
```

**Zero dependencies.** Python 3.10+. That's it.

## Quick Start

```python
from cognitive_load_monitor import CognitiveLoadMonitor

monitor = CognitiveLoadMonitor()

# During agent execution, track observable metrics
report = monitor.record(
    tokens_used=1500,
    tokens_budget=2000,
    reasoning_steps=8,
    latency_ms=450,
    unresolved_assumptions=2,
    total_assumptions=5,
)

# Make orchestration decisions
if report.is_overloaded():
    route_to_different_agent()
elif report.load_index < 0.3:
    use_cheaper_model()  # Task is simple
```

## What You Can Build

### Intelligent Load Balancing
Route tasks to the least-loaded agent instead of round-robin. Prevent individual agents from becoming overwhelmed while others sit idle.

```python
agents = [agent1, agent2, agent3]
loads = [a.monitor.get_current_load() for a in agents]
selected = agents[loads.index(min(loads))]
```

### Dynamic Model Selection
Use expensive frontier models only when necessary. Route simple tasks to cheaper alternatives automatically.

```python
if report.load_index < 0.3:
    model = "gpt-4o-mini"  # 10-20x cheaper
elif report.load_index > 0.7:
    model = "o1"  # Maximum capability
```

### Proactive Quality Gates
Flag outputs for human review before they ship, based on execution characteristics.

```python
if report.is_rising_fast(threshold=0.65):
    escalate_to_human_review(result, report)
```

### Cost Optimization
Automatically match model capability to actual task requirements, not static rules.

### Circuit Breakers
Detect overload conditions and shed load gracefully before cascading failures occur.

## Metrics

The monitor computes a normalized **Cognitive Load Index (0–1)** using five proxy metrics:

### 1. Context Pressure (0–1)
Ratio of tokens used to budget. Measures memory/context constraints.

### 2. Reasoning Complexity (0–1)
Normalized combination of reasoning steps and backtracking. High values indicate difficult problem-solving.

### 3. Temporal Stress (0–1)
Ratio of actual latency to expected latency. Measures time pressure and processing delays.

### 4. Uncertainty (0–1)
Ratio of unresolved to total assumptions. High values indicate ambiguity or missing information.

### 5. Error Recovery (0–1)
Ratio of self-corrections to total operations. Measures instability and rework overhead.

## Configuration

### Custom Weights

```python
from cognitive_load_monitor import CognitiveLoadMonitor, MetricWeights

# Define custom weights (must sum to 1.0)
weights = MetricWeights(
    context_pressure=0.30,
    reasoning_complexity=0.30,
    temporal_stress=0.20,
    uncertainty=0.10,
    error_recovery=0.10,
)

monitor = CognitiveLoadMonitor(weights=weights)
```

### Trend Detection

```python
monitor = CognitiveLoadMonitor(
    history_window=15,        # Track last 15 samples
    trend_threshold=0.08,     # Sensitivity for rising/falling detection
)
```

## Why This Matters

### The Five Dimensions

Each metric captures a different aspect of agent operational stress:

**Context Pressure** - An agent at 20% of its context budget has room to explore. At 90%, it's forced into aggressive summarization and risks losing critical information. Context exhaustion is often a silent failure mode.

**Reasoning Complexity** - Some tasks have clear solution paths. Others require extensive search and backtracking. Tracking reasoning steps and backtracks quantifies problem-solving difficulty and correlates with both cost and solution uncertainty.

**Temporal Stress** - When actual latency significantly exceeds expected latency, something interesting is happening. The agent might be tackling an unusually difficult problem or working inefficiently.

**Uncertainty** - Agents make assumptions during execution. The ratio of unresolved to total assumptions provides insight into output confidence. High uncertainty doesn't mean the output is wrong, but signals that human review may be warranted.

**Error Recovery** - Occasional self-corrections are healthy—they show an agent is checking its work. Frequent corrections suggest the agent is operating at the edge of its capability or mismatched to the task.

### Production Patterns

Real-world deployments have converged on several patterns:

**Progressive Model Escalation** - Start tasks with cheaper models and escalate only when load metrics indicate necessity. Most simple tasks never touch expensive models, while complex tasks get the capability they need.

**Load-Based Throttling** - Monitor aggregate load across your agent fleet and adjust acceptance rates. When approaching saturation, return 503s or queue requests rather than degrading quality across the board.

**Confidence-Gated Autonomy** - When load is low and trends stable, agents operate fully autonomously. When load spikes or uncertainty rises, require human approval before taking action. Adaptive guardrails that tighten automatically when conditions suggest elevated risk.

## API Reference

### `CognitiveLoadMonitor`

#### `__init__(weights=None, history_window=10, trend_threshold=0.05)`
Initialize monitor with optional custom configuration.

#### `record(**kwargs) -> CognitiveLoadReport`
Record current agent state and compute load report.

**Parameters:**
- `tokens_used` (int): Current token count consumed
- `tokens_budget` (int): Maximum tokens available
- `reasoning_steps` (int): Number of reasoning steps taken
- `max_reasoning_steps` (int): Expected maximum steps
- `backtrack_count` (int): Number of backtracks/revisions
- `latency_ms` (float): Actual processing time in milliseconds
- `expected_latency_ms` (float): Baseline expected latency
- `unresolved_assumptions` (int): Count of uncertain assumptions
- `total_assumptions` (int): Total assumptions made
- `self_corrections` (int): Number of self-corrections
- `total_operations` (int): Total operations attempted

#### `reset_history()`
Clear historical data. Useful when agent context resets.

#### `get_current_load() -> Optional[float]`
Get most recent load index, or None if no data.

### `CognitiveLoadReport`

#### `to_dict() -> dict`
Convert report to dictionary for serialization.

#### `is_overloaded(threshold=0.75) -> bool`
Check if cognitive load exceeds threshold.

#### `is_rising_fast(threshold=0.60) -> bool`
Check if load is rising and already above threshold.

**Attributes:**
- `timestamp`: Unix timestamp when report was generated
- `load_index`: Normalized cognitive load score (0.0–1.0)
- `trend`: Direction of load change (`LoadTrend` enum)
- `metrics`: Raw metric values used to compute load_index
- `weights`: Weight configuration used for this report
- `history_size`: Number of historical samples

## Design Philosophy

**Zero Dependencies** - No external requirements create operational fragility. Standard library Python only.

**Transparent Metrics** - No black-box scoring algorithms. Context pressure is tokens used divided by tokens available. Reasoning complexity is a straightforward combination of step count and backtrack rate. You can understand, debug, and trust what you're measuring.

**Configurable but Constrained** - Adjust metric weights to match your priorities, but weights must sum to 1.0. Tune trend detection sensitivity, but the underlying algorithm remains consistent. This prevents the system from becoming either too rigid or too flexible to reason about.

**Architecture Agnostic** - Works with LangChain agents, custom reasoning loops, or hand-coded state machines. Works with GPT-4, Claude, open-source models, or fine-tuned variants. Works in synchronous request-response systems, asynchronous message queues, or long-running autonomous agents.

**Primitive, Not Framework** - This is a building block that enables better decisions about routing, scaling, quality assurance, and cost management. It doesn't dictate architecture—it adapts to yours.

## Performance

- **15-25 microseconds** per `record()` call on typical hardware
- **~200 bytes** memory allocation per measurement
- **<0.01%** overhead for agent tasks taking hundreds of milliseconds
- **~2KB** memory footprint per monitor instance (default 10-measurement history)

Suitable for high-throughput production systems where every microsecond matters.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) file for details.

Copyright 2026 Synapse Data / Ivan Lluch

## Integration Examples

### Embedded Monitoring
```python
class MonitoredAgent:
    def __init__(self):
        self.monitor = CognitiveLoadMonitor()
        
    def execute(self, task):
        start = time.time()
        result = self.process_task(task)
        
        report = self.monitor.record(
            tokens_used=result.tokens,
            tokens_budget=self.context_limit,
            reasoning_steps=result.steps,
            latency_ms=(time.time() - start) * 1000
        )
        
        return result, report
```

### External Orchestration
```python
class AgentOrchestrator:
    def __init__(self, agents):
        self.agents = agents
        self.monitors = {a.id: CognitiveLoadMonitor() for a in agents}
    
    def route_request(self, request):
        # Select least-loaded agent
        loads = {a.id: self.monitors[a.id].get_current_load() 
                 for a in self.agents}
        selected = min(loads.items(), key=lambda x: x[1] or 0)
        return self.agents[selected[0]]
```

### Quality Gates
```python
def process_with_quality_gate(task):
    result = agent.execute(task)
    report = monitor.record(...)
    
    if report.is_rising_fast(threshold=0.65):
        return {
            'result': result,
            'status': 'NEEDS_REVIEW',
            'reason': f'Load at {report.load_index:.2f} and rising'
        }
    
    return {'result': result, 'status': 'APPROVED'}
```

## Why Not Model Introspection?

Some teams attempt to solve this through examining chain-of-thought outputs or prompting models to self-assess confidence. These approaches work to some extent, but they're:

- **Model-dependent** - Break when you switch from GPT-4 to Claude
- **Computationally expensive** - Add latency and cost
- **Tightly coupled** - Require specific implementation patterns

The Cognitive Load Monitor uses observable runtime metrics that work across any agent architecture, any model, and any deployment pattern.

## Requirements

- Python 3.10+
- No external dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: Synapse Data

## Authors

- **Ivan Lluch** - Synapse Data

---

**Built by Synapse Data** • Production-quality infrastructure for AI agents
