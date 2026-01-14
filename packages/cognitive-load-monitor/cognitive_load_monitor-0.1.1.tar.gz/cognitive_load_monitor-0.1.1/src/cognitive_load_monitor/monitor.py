"""
Cognitive Load Monitor for AI Agents

A lightweight, drop-in module for AI agents to self-report cognitive load
using observable runtime metrics. Designed for operational reliability and
external orchestration (throttling, cloning, load balancing).

Copyright 2026 Synapse Data / Ivan Lluch

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Python: 3.10+
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from collections import deque
from time import time


class LoadTrend(Enum):
    """Trend direction for cognitive load over recent history."""
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class MetricWeights:
    """
    Configurable weights for each cognitive load dimension.
    All weights should sum to 1.0 for proper normalization.
    """
    context_pressure: float = 0.25
    reasoning_complexity: float = 0.25
    temporal_stress: float = 0.20
    uncertainty: float = 0.15
    error_recovery: float = 0.15

    def __post_init__(self):
        total = (
            self.context_pressure +
            self.reasoning_complexity +
            self.temporal_stress +
            self.uncertainty +
            self.error_recovery
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")


@dataclass
class CognitiveLoadReport:
    """
    Structured report of cognitive load at a point in time.
    
    Attributes:
        timestamp: Unix timestamp when report was generated
        load_index: Normalized cognitive load score (0.0 = minimal, 1.0 = maximum)
        trend: Direction of load change over recent history
        metrics: Raw metric values used to compute load_index
        weights: Weight configuration used for this report
        history_size: Number of historical samples used for trend detection
    """
    timestamp: float
    load_index: float
    trend: LoadTrend
    metrics: dict[str, float]
    weights: MetricWeights
    history_size: int

    def __post_init__(self):
        if not (0.0 <= self.load_index <= 1.0):
            raise ValueError(f"load_index must be in [0, 1], got {self.load_index:.3f}")

    def to_dict(self) -> dict:
        """Convert report to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "load_index": round(self.load_index, 4),
            "trend": self.trend.value,
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "weights": {
                "context_pressure": self.weights.context_pressure,
                "reasoning_complexity": self.weights.reasoning_complexity,
                "temporal_stress": self.weights.temporal_stress,
                "uncertainty": self.weights.uncertainty,
                "error_recovery": self.weights.error_recovery,
            },
            "history_size": self.history_size,
        }

    def is_overloaded(self, threshold: float = 0.75) -> bool:
        """Check if cognitive load exceeds threshold."""
        return self.load_index >= threshold

    def is_rising_fast(self, threshold: float = 0.60) -> bool:
        """Check if load is rising and already above threshold."""
        return self.trend == LoadTrend.RISING and self.load_index >= threshold


class CognitiveLoadMonitor:
    """
    Monitor for tracking and reporting cognitive load of an AI agent.
    
    Usage:
        monitor = CognitiveLoadMonitor()
        report = monitor.record(
            tokens_used=1500,
            tokens_budget=2000,
            reasoning_steps=8,
            latency_ms=450,
            ...
        )
        
        if report.is_overloaded():
            # Signal orchestrator to take action
            pass
    """

    def __init__(
        self,
        weights: Optional[MetricWeights] = None,
        history_window: int = 10,
        trend_threshold: float = 0.05,
    ):
        """
        Initialize cognitive load monitor.
        
        Args:
            weights: Custom metric weights (uses defaults if None)
            history_window: Number of recent samples to keep for trend detection
            trend_threshold: Minimum change to classify as rising/falling (0-1 scale)
        """
        self.weights = weights or MetricWeights()
        self.history_window = max(2, history_window)
        self.trend_threshold = trend_threshold
        self._history: deque[float] = deque(maxlen=self.history_window)

    def record(
        self,
        tokens_used: int = 0,
        tokens_budget: int = 1,
        reasoning_steps: int = 0,
        max_reasoning_steps: int = 10,
        backtrack_count: int = 0,
        latency_ms: float = 0.0,
        expected_latency_ms: float = 1000.0,
        unresolved_assumptions: int = 0,
        total_assumptions: int = 1,
        self_corrections: int = 0,
        total_operations: int = 1,
    ) -> CognitiveLoadReport:
        """
        Record current state and compute cognitive load report.
        
        Context Pressure (0-1):
            Ratio of tokens used to budget. Measures memory/context constraints.
            
        Reasoning Complexity (0-1):
            Normalized combination of reasoning steps and backtracking.
            High values indicate difficult problem-solving.
            
        Temporal Stress (0-1):
            Ratio of actual latency to expected latency.
            Measures time pressure and processing delays.
            
        Uncertainty (0-1):
            Ratio of unresolved to total assumptions.
            High values indicate ambiguity or missing information.
            
        Error Recovery (0-1):
            Ratio of self-corrections to total operations.
            Measures instability and rework overhead.
        
        Args:
            tokens_used: Current token count consumed
            tokens_budget: Maximum tokens available
            reasoning_steps: Number of reasoning steps taken
            max_reasoning_steps: Expected maximum steps for normal operation
            backtrack_count: Number of times agent backtracked/revised
            latency_ms: Actual processing time in milliseconds
            expected_latency_ms: Baseline expected latency
            unresolved_assumptions: Count of uncertain/unvalidated assumptions
            total_assumptions: Total assumptions made
            self_corrections: Number of self-corrections or retries
            total_operations: Total operations attempted
            
        Returns:
            CognitiveLoadReport with computed load index and trend
        """
        # Compute normalized metrics (all in [0, 1] range)
        context_pressure = self._normalize_ratio(tokens_used, tokens_budget)
        
        # Reasoning complexity: weighted average of steps and backtracking
        step_ratio = self._normalize_ratio(reasoning_steps, max_reasoning_steps)
        backtrack_penalty = min(backtrack_count / max(reasoning_steps, 1), 1.0)
        reasoning_complexity = 0.7 * step_ratio + 0.3 * backtrack_penalty
        
        temporal_stress = self._normalize_ratio(latency_ms, expected_latency_ms)
        uncertainty = self._normalize_ratio(unresolved_assumptions, total_assumptions)
        error_recovery = self._normalize_ratio(self_corrections, total_operations)

        # Compute weighted cognitive load index
        load_index = (
            self.weights.context_pressure * context_pressure +
            self.weights.reasoning_complexity * reasoning_complexity +
            self.weights.temporal_stress * temporal_stress +
            self.weights.uncertainty * uncertainty +
            self.weights.error_recovery * error_recovery
        )
        
        # Clamp to [0, 1] to handle any floating point edge cases
        load_index = max(0.0, min(1.0, load_index))
        
        # Update history and detect trend
        self._history.append(load_index)
        trend = self._detect_trend()
        
        # Build report
        report = CognitiveLoadReport(
            timestamp=time(),
            load_index=load_index,
            trend=trend,
            metrics={
                "context_pressure": context_pressure,
                "reasoning_complexity": reasoning_complexity,
                "temporal_stress": temporal_stress,
                "uncertainty": uncertainty,
                "error_recovery": error_recovery,
            },
            weights=self.weights,
            history_size=len(self._history),
        )
        
        return report

    def _normalize_ratio(self, value: float, maximum: float) -> float:
        """
        Normalize a ratio to [0, 1] range with saturation.
        Handles division by zero and values exceeding maximum.
        """
        if maximum <= 0:
            return 0.0
        ratio = value / maximum
        return max(0.0, min(1.0, ratio))

    def _detect_trend(self) -> LoadTrend:
        """
        Detect trend from recent history using simple linear regression.
        
        Returns:
            LoadTrend indicating direction of cognitive load change
        """
        if len(self._history) < 3:
            return LoadTrend.INSUFFICIENT_DATA
        
        # Simple linear regression: compute slope
        n = len(self._history)
        x_mean = (n - 1) / 2.0
        y_mean = sum(self._history) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(self._history))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return LoadTrend.STABLE
        
        slope = numerator / denominator
        
        # Classify based on slope magnitude
        if slope > self.trend_threshold:
            return LoadTrend.RISING
        elif slope < -self.trend_threshold:
            return LoadTrend.FALLING
        else:
            return LoadTrend.STABLE

    def reset_history(self) -> None:
        """Clear historical data. Useful when agent context resets."""
        self._history.clear()

    def get_current_load(self) -> Optional[float]:
        """Get most recent load index, or None if no data."""
        return self._history[-1] if self._history else None


# Example usage demonstrating integration pattern
if __name__ == "__main__":
    # Initialize monitor with default weights
    monitor = CognitiveLoadMonitor(history_window=10)
    
    print("Cognitive Load Monitor - Example Usage\n")
    print("=" * 60)
    
    # Simulate agent processing a series of tasks with increasing complexity
    scenarios = [
        {
            "name": "Simple query",
            "tokens_used": 500,
            "tokens_budget": 4000,
            "reasoning_steps": 2,
            "latency_ms": 150,
            "unresolved_assumptions": 0,
            "total_assumptions": 2,
        },
        {
            "name": "Moderate complexity",
            "tokens_used": 1800,
            "tokens_budget": 4000,
            "reasoning_steps": 5,
            "backtrack_count": 1,
            "latency_ms": 450,
            "unresolved_assumptions": 1,
            "total_assumptions": 4,
        },
        {
            "name": "High complexity with errors",
            "tokens_used": 3200,
            "tokens_budget": 4000,
            "reasoning_steps": 9,
            "backtrack_count": 3,
            "latency_ms": 1200,
            "expected_latency_ms": 800,
            "unresolved_assumptions": 3,
            "total_assumptions": 6,
            "self_corrections": 2,
            "total_operations": 10,
        },
        {
            "name": "Near capacity",
            "tokens_used": 3800,
            "tokens_budget": 4000,
            "reasoning_steps": 12,
            "max_reasoning_steps": 10,
            "backtrack_count": 5,
            "latency_ms": 1800,
            "expected_latency_ms": 800,
            "unresolved_assumptions": 4,
            "total_assumptions": 5,
            "self_corrections": 4,
            "total_operations": 12,
        },
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        name = scenario.pop("name")
        report = monitor.record(**scenario)
        
        print(f"\nScenario {i}: {name}")
        print(f"  Load Index: {report.load_index:.3f}")
        print(f"  Trend: {report.trend.value}")
        print(f"  Overloaded: {report.is_overloaded()}")
        print(f"  Rising Fast: {report.is_rising_fast()}")
        print(f"  Metrics:")
        for metric, value in report.metrics.items():
            print(f"    - {metric}: {value:.3f}")
    
    print("\n" + "=" * 60)
    print("\nOrchestrator Integration Pattern:")
    print("""
    # In agent runtime:
    report = monitor.record(
        tokens_used=current_tokens,
        tokens_budget=max_tokens,
        reasoning_steps=step_count,
        latency_ms=elapsed_time,
        ...
    )
    
    # Emit to orchestrator (stdout, API, message queue, etc.)
    if report.is_overloaded():
        emit_signal("THROTTLE", report.to_dict())
    elif report.is_rising_fast():
        emit_signal("WARN", report.to_dict())
    """)
