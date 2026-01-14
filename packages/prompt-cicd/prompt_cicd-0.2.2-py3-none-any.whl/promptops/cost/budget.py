"""
Budget management for tracking and controlling LLM costs.

Provides comprehensive cost tracking with support for:
- Multiple budget periods (daily, monthly, per-request)
- Cost alerts and thresholds
- Detailed usage history and analytics
- Per-model and per-prompt cost tracking
"""

import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..exceptions import BudgetExceeded

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Budget reset periods."""
    NONE = "none"  # Never resets
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertLevel(Enum):
    """Budget alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CostEntry:
    """Record of a single cost charge."""
    amount: float
    timestamp: float
    prompt_name: Optional[str] = None
    model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetAlert:
    """Alert triggered when a budget threshold is reached."""
    level: AlertLevel
    message: str
    timestamp: float
    budget_name: str
    current_usage: float
    threshold: float
    percentage: float


@dataclass
class UsageStats:
    """Usage statistics for a budget."""
    total_cost: float
    total_charges: int
    average_cost: float
    max_single_cost: float
    min_single_cost: float
    input_tokens: int
    output_tokens: int
    cost_by_model: Dict[str, float]
    cost_by_prompt: Dict[str, float]
    period_start: Optional[float]
    period_end: Optional[float]


# Default pricing per 1K tokens (can be customized)
DEFAULT_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
}


class Budget:
    """
    Budget manager for tracking and controlling LLM costs.
    
    Features:
    - Set maximum cost limits with automatic enforcement
    - Track usage by model, prompt, and time period
    - Configure alerts at various thresholds
    - Automatic period-based budget resets
    - Detailed usage history and analytics
    
    Example:
        >>> budget = Budget(max_cost=100.0, period=BudgetPeriod.DAILY)
        >>> budget.add_alert_threshold(0.8, AlertLevel.WARNING)
        >>> budget.charge(5.0, prompt_name="summarize", model="gpt-4")
    """
    
    def __init__(
        self,
        max_cost: float,
        name: str = "default",
        period: BudgetPeriod = BudgetPeriod.NONE,
        soft_limit: bool = False,
        alert_callback: Optional[Callable[[BudgetAlert], None]] = None,
    ):
        """
        Initialize a budget.
        
        Args:
            max_cost: Maximum allowed cost.
            name: Name for this budget (for identification).
            period: Reset period for the budget.
            soft_limit: If True, log warning instead of raising on exceed.
            alert_callback: Callback function for budget alerts.
        """
        self.name = name
        self.max_cost = max_cost
        self.period = period
        self.soft_limit = soft_limit
        self.alert_callback = alert_callback
        
        self._lock = threading.Lock()
        self._used: float = 0.0
        self._history: List[CostEntry] = []
        self._period_start: float = time.time()
        self._alert_thresholds: List[Tuple[float, AlertLevel]] = []
        self._triggered_alerts: set = set()
        self._model_pricing: Dict[str, Dict[str, float]] = dict(DEFAULT_MODEL_PRICING)
        
        # Persistence
        self._persistence_path: Optional[Path] = None
        
        logger.info(f"Budget '{name}' initialized: max=${max_cost:.2f}, period={period.value}")
    
    @property
    def used(self) -> float:
        """Get the current used amount."""
        with self._lock:
            self._check_period_reset()
            return self._used
    
    @property
    def remaining(self) -> float:
        """Get the remaining budget."""
        return max(0, self.max_cost - self.used)
    
    @property
    def percentage_used(self) -> float:
        """Get the percentage of budget used."""
        if self.max_cost <= 0:
            return 100.0
        return (self.used / self.max_cost) * 100
    
    def _check_period_reset(self) -> None:
        """Check if budget should reset based on period."""
        if self.period == BudgetPeriod.NONE:
            return
        
        now = time.time()
        should_reset = False
        
        period_seconds = {
            BudgetPeriod.HOURLY: 3600,
            BudgetPeriod.DAILY: 86400,
            BudgetPeriod.WEEKLY: 604800,
            BudgetPeriod.MONTHLY: 2592000,  # 30 days
        }
        
        if self.period in period_seconds:
            elapsed = now - self._period_start
            if elapsed >= period_seconds[self.period]:
                should_reset = True
        
        if should_reset:
            logger.info(f"Budget '{self.name}' period reset. Previous usage: ${self._used:.4f}")
            self._used = 0.0
            self._period_start = now
            self._triggered_alerts.clear()
    
    def configure_persistence(self, path: str) -> None:
        """
        Configure file-based persistence for budget data.
        
        Args:
            path: File path for storing budget data.
        """
        self._persistence_path = Path(path)
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """Load budget data from disk."""
        if self._persistence_path and self._persistence_path.exists():
            try:
                with open(self._persistence_path, "r") as f:
                    data = json.load(f)
                    self._used = data.get("used", 0.0)
                    self._period_start = data.get("period_start", time.time())
                    # Restore history
                    for entry_data in data.get("history", []):
                        self._history.append(CostEntry(**entry_data))
                logger.debug(f"Loaded budget data from {self._persistence_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load budget data: {e}")
    
    def _save_to_disk(self) -> None:
        """Save budget data to disk."""
        if self._persistence_path:
            try:
                self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
                data = {
                    "used": self._used,
                    "period_start": self._period_start,
                    "history": [
                        {
                            "amount": e.amount,
                            "timestamp": e.timestamp,
                            "prompt_name": e.prompt_name,
                            "model": e.model,
                            "input_tokens": e.input_tokens,
                            "output_tokens": e.output_tokens,
                            "metadata": e.metadata,
                        }
                        for e in self._history[-1000:]  # Keep last 1000 entries
                    ],
                }
                with open(self._persistence_path, "w") as f:
                    json.dump(data, f, indent=2)
            except IOError as e:
                logger.warning(f"Failed to save budget data: {e}")
    
    def set_model_pricing(self, model: str, input_price: float, output_price: float) -> None:
        """
        Set custom pricing for a model (per 1K tokens).
        
        Args:
            model: Model name.
            input_price: Price per 1K input tokens.
            output_price: Price per 1K output tokens.
        """
        self._model_pricing[model] = {"input": input_price, "output": output_price}
        logger.debug(f"Set pricing for {model}: input=${input_price}/1K, output=${output_price}/1K")
    
    def add_alert_threshold(self, percentage: float, level: AlertLevel = AlertLevel.WARNING) -> None:
        """
        Add an alert threshold.
        
        Args:
            percentage: Percentage of budget (0.0-1.0) to trigger alert.
            level: Severity level of the alert.
        """
        self._alert_thresholds.append((percentage, level))
        self._alert_thresholds.sort(key=lambda x: x[0])
        logger.debug(f"Added alert threshold at {percentage*100:.0f}% ({level.value})")
    
    def _check_alerts(self) -> None:
        """Check and trigger any pending alerts."""
        current_pct = self._used / self.max_cost if self.max_cost > 0 else 1.0
        
        for threshold, level in self._alert_thresholds:
            if current_pct >= threshold and threshold not in self._triggered_alerts:
                self._triggered_alerts.add(threshold)
                alert = BudgetAlert(
                    level=level,
                    message=f"Budget '{self.name}' reached {current_pct*100:.1f}% "
                            f"(threshold: {threshold*100:.0f}%)",
                    timestamp=time.time(),
                    budget_name=self.name,
                    current_usage=self._used,
                    threshold=threshold * self.max_cost,
                    percentage=current_pct * 100,
                )
                logger.log(
                    logging.WARNING if level == AlertLevel.WARNING else
                    logging.ERROR if level == AlertLevel.CRITICAL else logging.INFO,
                    alert.message
                )
                if self.alert_callback:
                    try:
                        self.alert_callback(alert)
                    except Exception as e:
                        logger.error(f"Alert callback error: {e}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate the cost for a given token usage.
        
        Args:
            model: The model name.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
        
        Returns:
            Calculated cost in dollars.
        """
        pricing = self._model_pricing.get(model, {"input": 0.01, "output": 0.03})
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
    
    def charge(
        self,
        cost: Optional[float] = None,
        *,
        model: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        prompt_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Charge an amount to the budget.
        
        You can either provide a direct cost, or provide model and token counts
        to have the cost calculated automatically.
        
        Args:
            cost: Direct cost to charge (optional if tokens provided).
            model: Model name for cost calculation.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            prompt_name: Name of the prompt (for tracking).
            metadata: Additional metadata to store.
        
        Returns:
            The charged amount.
        
        Raises:
            BudgetExceeded: If budget is exceeded and soft_limit is False.
        """
        with self._lock:
            self._check_period_reset()
            
            # Calculate cost if not provided
            if cost is None:
                if model and (input_tokens or output_tokens):
                    cost = self.calculate_cost(model, input_tokens, output_tokens)
                else:
                    raise ValueError("Either 'cost' or 'model' with tokens must be provided")
            
            # Record the charge
            entry = CostEntry(
                amount=cost,
                timestamp=time.time(),
                prompt_name=prompt_name,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata=metadata or {},
            )
            self._history.append(entry)
            self._used += cost
            
            logger.debug(
                f"Budget '{self.name}' charged ${cost:.4f} "
                f"(total: ${self._used:.4f}/{self.max_cost:.2f})"
            )
            
            # Check alerts
            self._check_alerts()
            
            # Check if exceeded
            if self._used > self.max_cost:
                msg = (
                    f"Budget '{self.name}' exceeded: "
                    f"${self._used:.4f} > ${self.max_cost:.2f}"
                )
                if self.soft_limit:
                    logger.warning(msg)
                else:
                    self._save_to_disk()
                    raise BudgetExceeded(msg)
            
            self._save_to_disk()
            return cost
    
    def charge_tokens(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        prompt_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Charge based on token usage (convenience method).
        
        Args:
            model: Model name.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            prompt_name: Name of the prompt.
            metadata: Additional metadata.
        
        Returns:
            The calculated and charged cost.
        """
        return self.charge(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            prompt_name=prompt_name,
            metadata=metadata,
        )
    
    def reserve(self, amount: float) -> "BudgetReservation":
        """
        Reserve an amount from the budget.
        
        Use this for pre-allocating budget before an operation.
        
        Args:
            amount: Amount to reserve.
        
        Returns:
            BudgetReservation context manager.
        
        Raises:
            BudgetExceeded: If reservation would exceed budget.
        """
        return BudgetReservation(self, amount)
    
    def can_afford(self, cost: float) -> bool:
        """
        Check if a cost can be afforded.
        
        Args:
            cost: The cost to check.
        
        Returns:
            True if the cost can be afforded.
        """
        return self.remaining >= cost
    
    def estimate_tokens_remaining(self, model: str, ratio: float = 0.5) -> int:
        """
        Estimate how many tokens can still be used.
        
        Args:
            model: Model to estimate for.
            ratio: Assumed input/output token ratio (0.0-1.0, where 0.5 = equal).
        
        Returns:
            Estimated total tokens remaining.
        """
        pricing = self._model_pricing.get(model, {"input": 0.01, "output": 0.03})
        avg_price_per_token = (
            ratio * pricing["input"] / 1000 +
            (1 - ratio) * pricing["output"] / 1000
        )
        if avg_price_per_token <= 0:
            return 0
        return int(self.remaining / avg_price_per_token)
    
    def reset(self) -> float:
        """
        Reset the budget.
        
        Returns:
            The amount that was used before reset.
        """
        with self._lock:
            previous = self._used
            self._used = 0.0
            self._period_start = time.time()
            self._triggered_alerts.clear()
            self._save_to_disk()
            logger.info(f"Budget '{self.name}' reset. Previous usage: ${previous:.4f}")
            return previous
    
    def get_usage_stats(
        self,
        since: Optional[float] = None,
        until: Optional[float] = None,
    ) -> UsageStats:
        """
        Get usage statistics.
        
        Args:
            since: Start timestamp (optional).
            until: End timestamp (optional).
        
        Returns:
            UsageStats with detailed breakdown.
        """
        with self._lock:
            entries = self._history
            
            if since is not None:
                entries = [e for e in entries if e.timestamp >= since]
            if until is not None:
                entries = [e for e in entries if e.timestamp <= until]
            
            if not entries:
                return UsageStats(
                    total_cost=0.0,
                    total_charges=0,
                    average_cost=0.0,
                    max_single_cost=0.0,
                    min_single_cost=0.0,
                    input_tokens=0,
                    output_tokens=0,
                    cost_by_model={},
                    cost_by_prompt={},
                    period_start=since,
                    period_end=until,
                )
            
            costs = [e.amount for e in entries]
            cost_by_model: Dict[str, float] = defaultdict(float)
            cost_by_prompt: Dict[str, float] = defaultdict(float)
            total_input = 0
            total_output = 0
            
            for entry in entries:
                if entry.model:
                    cost_by_model[entry.model] += entry.amount
                if entry.prompt_name:
                    cost_by_prompt[entry.prompt_name] += entry.amount
                total_input += entry.input_tokens
                total_output += entry.output_tokens
            
            return UsageStats(
                total_cost=sum(costs),
                total_charges=len(costs),
                average_cost=sum(costs) / len(costs),
                max_single_cost=max(costs),
                min_single_cost=min(costs),
                input_tokens=total_input,
                output_tokens=total_output,
                cost_by_model=dict(cost_by_model),
                cost_by_prompt=dict(cost_by_prompt),
                period_start=since or (entries[0].timestamp if entries else None),
                period_end=until or (entries[-1].timestamp if entries else None),
            )
    
    def get_history(
        self,
        limit: int = 100,
        prompt_name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[CostEntry]:
        """
        Get charge history.
        
        Args:
            limit: Maximum entries to return.
            prompt_name: Filter by prompt name.
            model: Filter by model.
        
        Returns:
            List of CostEntry objects, most recent first.
        """
        with self._lock:
            entries = list(reversed(self._history))
            
            if prompt_name:
                entries = [e for e in entries if e.prompt_name == prompt_name]
            if model:
                entries = [e for e in entries if e.model == model]
            
            return entries[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export budget state as dictionary.
        
        Returns:
            Dictionary with budget state.
        """
        with self._lock:
            return {
                "name": self.name,
                "max_cost": self.max_cost,
                "used": self._used,
                "remaining": self.remaining,
                "percentage_used": self.percentage_used,
                "period": self.period.value,
                "period_start": self._period_start,
                "total_charges": len(self._history),
                "soft_limit": self.soft_limit,
            }
    
    def __repr__(self) -> str:
        return (
            f"Budget(name='{self.name}', used=${self.used:.4f}, "
            f"max=${self.max_cost:.2f}, remaining=${self.remaining:.4f})"
        )


class BudgetReservation:
    """
    Context manager for reserving budget before an operation.
    
    Example:
        >>> with budget.reserve(10.0) as reservation:
        ...     result = call_llm()
        ...     reservation.finalize(actual_cost=5.0)
    """
    
    def __init__(self, budget: Budget, amount: float):
        self.budget = budget
        self.reserved_amount = amount
        self.finalized = False
        self._actual_cost: Optional[float] = None
    
    def __enter__(self) -> "BudgetReservation":
        # Check if reservation is possible
        if not self.budget.can_afford(self.reserved_amount):
            raise BudgetExceeded(
                f"Cannot reserve ${self.reserved_amount:.4f}, "
                f"only ${self.budget.remaining:.4f} remaining"
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if not self.finalized:
            if exc_type is None:
                # No exception, charge the reserved amount
                self.budget.charge(self.reserved_amount)
            # On exception, don't charge
        return False
    
    def finalize(
        self,
        actual_cost: Optional[float] = None,
        **charge_kwargs,
    ) -> float:
        """
        Finalize the reservation with actual cost.
        
        Args:
            actual_cost: The actual cost (if different from reserved).
            **charge_kwargs: Additional arguments for budget.charge().
        
        Returns:
            The charged amount.
        """
        self.finalized = True
        cost = actual_cost if actual_cost is not None else self.reserved_amount
        self._actual_cost = cost
        return self.budget.charge(cost, **charge_kwargs)


class BudgetPool:
    """
    Manage multiple budgets with hierarchical limits.
    
    Example:
        >>> pool = BudgetPool()
        >>> pool.create_budget("api", max_cost=1000, period=BudgetPeriod.MONTHLY)
        >>> pool.create_budget("testing", max_cost=100, period=BudgetPeriod.DAILY)
        >>> pool.charge("api", 5.0, model="gpt-4")
    """
    
    def __init__(self, global_limit: Optional[float] = None):
        """
        Initialize a budget pool.
        
        Args:
            global_limit: Optional global limit across all budgets.
        """
        self.global_limit = global_limit
        self._budgets: Dict[str, Budget] = {}
        self._global_used: float = 0.0
        self._lock = threading.Lock()
    
    def create_budget(
        self,
        name: str,
        max_cost: float,
        period: BudgetPeriod = BudgetPeriod.NONE,
        **kwargs,
    ) -> Budget:
        """
        Create a new budget in the pool.
        
        Args:
            name: Unique name for the budget.
            max_cost: Maximum cost for this budget.
            period: Reset period.
            **kwargs: Additional Budget constructor arguments.
        
        Returns:
            The created Budget.
        """
        budget = Budget(max_cost=max_cost, name=name, period=period, **kwargs)
        self._budgets[name] = budget
        return budget
    
    def get_budget(self, name: str) -> Optional[Budget]:
        """Get a budget by name."""
        return self._budgets.get(name)
    
    def charge(
        self,
        budget_name: str,
        cost: Optional[float] = None,
        **kwargs,
    ) -> float:
        """
        Charge to a specific budget.
        
        Args:
            budget_name: Name of the budget to charge.
            cost: Cost to charge.
            **kwargs: Additional arguments for Budget.charge().
        
        Returns:
            The charged amount.
        
        Raises:
            KeyError: If budget doesn't exist.
            BudgetExceeded: If budget or global limit exceeded.
        """
        budget = self._budgets.get(budget_name)
        if not budget:
            raise KeyError(f"Budget '{budget_name}' not found")
        
        with self._lock:
            # Check global limit
            if self.global_limit and self._global_used + (cost or 0) > self.global_limit:
                raise BudgetExceeded(
                    f"Global budget exceeded: ${self._global_used:.4f} + ${cost:.4f} "
                    f"> ${self.global_limit:.2f}"
                )
            
            charged = budget.charge(cost, **kwargs)
            self._global_used += charged
            return charged
    
    def get_total_usage(self) -> Dict[str, Any]:
        """
        Get total usage across all budgets.
        
        Returns:
            Dictionary with usage summary.
        """
        budgets_summary = {}
        total_used = 0.0
        total_max = 0.0
        
        for name, budget in self._budgets.items():
            budgets_summary[name] = budget.to_dict()
            total_used += budget.used
            total_max += budget.max_cost
        
        return {
            "global_limit": self.global_limit,
            "global_used": self._global_used,
            "total_used": total_used,
            "total_max": total_max,
            "budgets": budgets_summary,
        }
    
    def reset_all(self) -> Dict[str, float]:
        """
        Reset all budgets.
        
        Returns:
            Dictionary of budget names to their previous usage.
        """
        results = {}
        for name, budget in self._budgets.items():
            results[name] = budget.reset()
        
        with self._lock:
            self._global_used = 0.0
        
        return results


class CostTracker:
    """
    Decorator and context manager for automatic cost tracking.
    
    Example:
        >>> tracker = CostTracker(budget)
        >>> 
        >>> @tracker.track("summarize", model="gpt-4")
        ... def summarize(text):
        ...     return llm.complete(text)
        >>> 
        >>> with tracker.context("translate", model="gpt-4"):
        ...     result = translate(text)
    """
    
    def __init__(self, budget: Budget):
        self.budget = budget
        self._pending_costs: Dict[str, float] = {}
    
    def track(
        self,
        prompt_name: str,
        model: Optional[str] = None,
        estimated_cost: Optional[float] = None,
    ):
        """
        Decorator for tracking function costs.
        
        Args:
            prompt_name: Name to track under.
            model: Model name for cost calculation.
            estimated_cost: Estimated cost if known.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.context(prompt_name, model, estimated_cost):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def context(
        self,
        prompt_name: str,
        model: Optional[str] = None,
        estimated_cost: Optional[float] = None,
    ) -> "CostTrackingContext":
        """
        Context manager for tracking costs.
        
        Args:
            prompt_name: Name to track under.
            model: Model name.
            estimated_cost: Estimated cost.
        
        Returns:
            CostTrackingContext for manual cost reporting.
        """
        return CostTrackingContext(
            budget=self.budget,
            prompt_name=prompt_name,
            model=model,
            estimated_cost=estimated_cost,
        )


class CostTrackingContext:
    """Context manager for tracking costs of an operation."""
    
    def __init__(
        self,
        budget: Budget,
        prompt_name: str,
        model: Optional[str] = None,
        estimated_cost: Optional[float] = None,
    ):
        self.budget = budget
        self.prompt_name = prompt_name
        self.model = model
        self.estimated_cost = estimated_cost
        self._charged = False
        self._cost: float = 0.0
    
    def __enter__(self) -> "CostTrackingContext":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if not self._charged and exc_type is None:
            # Charge estimated cost if actual not reported
            if self.estimated_cost:
                self.report_cost(self.estimated_cost)
        return False
    
    def report_cost(
        self,
        cost: Optional[float] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Report the actual cost of the operation.
        
        Args:
            cost: Direct cost (optional if tokens provided).
            input_tokens: Input token count.
            output_tokens: Output token count.
            metadata: Additional metadata.
        
        Returns:
            The charged amount.
        """
        self._charged = True
        self._cost = self.budget.charge(
            cost=cost,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            prompt_name=self.prompt_name,
            metadata=metadata,
        )
        return self._cost
    
    def report_tokens(
        self,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Report token usage (convenience method).
        
        Args:
            input_tokens: Input token count.
            output_tokens: Output token count.
            metadata: Additional metadata.
        
        Returns:
            The calculated and charged cost.
        """
        return self.report_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata,
        )
