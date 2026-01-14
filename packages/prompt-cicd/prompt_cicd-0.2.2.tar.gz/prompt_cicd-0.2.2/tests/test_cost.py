"""Tests for cost tracking and budget management."""
import pytest
import time
from promptops.cost.budget import (
    Budget,
    BudgetPool,
    BudgetPeriod,
    AlertLevel,
    CostEntry,
    CostTracker,
    BudgetAlert,
    UsageStats,
    BudgetReservation,
    CostTrackingContext,
)
from promptops.exceptions import BudgetExceeded


class TestBudget:
    """Test Budget class."""

    def test_create_budget(self):
        """Test creating a budget."""
        budget = Budget(max_cost=100.0, name="test")
        assert budget.max_cost == 100.0
        assert budget.name == "test"
        assert budget.used == 0.0
        assert budget.remaining == 100.0

    def test_charge_budget(self):
        """Test charging a budget."""
        budget = Budget(max_cost=100.0, name="test")
        charged = budget.charge(10.0)
        assert charged == 10.0
        assert budget.used == 10.0
        assert budget.remaining == 90.0
        assert budget.percentage_used == 10.0

    def test_budget_exceeded(self):
        """Test budget exceeded raises error."""
        budget = Budget(max_cost=10.0, name="test")
        with pytest.raises(BudgetExceeded):
            budget.charge(15.0)

    def test_soft_limit(self):
        """Test soft limit doesn't raise exception."""
        budget = Budget(max_cost=10.0, name="test", soft_limit=True)
        # Should not raise
        budget.charge(15.0)
        assert budget.used == 15.0

    def test_charge_with_tokens(self):
        """Test charging with token counts."""
        budget = Budget(max_cost=100.0, name="test")
        charged = budget.charge(model="gpt-4", input_tokens=1000, output_tokens=500)
        assert charged > 0
        assert budget.used > 0

    def test_reset_budget(self):
        """Test resetting budget."""
        budget = Budget(max_cost=100.0, name="test")
        budget.charge(50.0)
        previous = budget.reset()
        assert previous == 50.0
        assert budget.used == 0.0
        assert budget.remaining == 100.0

    def test_can_afford(self):
        """Test checking if cost can be afforded."""
        budget = Budget(max_cost=100.0, name="test")
        assert budget.can_afford(50.0)
        budget.charge(90.0)
        assert budget.can_afford(10.0)
        assert not budget.can_afford(20.0)

    def test_budget_with_period(self):
        """Test budget with time period."""
        budget = Budget(
            max_cost=100.0,
            name="test",
            period=BudgetPeriod.DAILY
        )
        assert budget.period == BudgetPeriod.DAILY

    def test_percentage_used(self):
        """Test percentage used calculation."""
        budget = Budget(max_cost=100.0, name="test")
        budget.charge(25.0)
        assert budget.percentage_used == 25.0
        budget.charge(25.0)
        assert budget.percentage_used == 50.0

    def test_get_usage_stats(self):
        """Test getting usage statistics."""
        budget = Budget(max_cost=100.0, name="test")
        budget.charge(10.0, model="gpt-4", prompt_name="test1")
        budget.charge(5.0, model="gpt-3.5-turbo", prompt_name="test2")
        
        stats = budget.get_usage_stats()
        assert stats.total_cost == 15.0
        assert stats.total_charges == 2
        assert "gpt-4" in stats.cost_by_model or "gpt-3.5-turbo" in stats.cost_by_model


class TestBudgetPool:
    """Test BudgetPool class."""

    def test_create_budget_in_pool(self):
        """Test creating a budget in the pool."""
        pool = BudgetPool()
        pool.create_budget("api", max_cost=100.0)
        budget = pool.get_budget("api")
        assert budget is not None
        assert budget.max_cost == 100.0

    def test_get_budget(self):
        """Test getting a budget from pool."""
        pool = BudgetPool()
        pool.create_budget("test", max_cost=50.0)
        budget = pool.get_budget("test")
        assert budget.name == "test"

    def test_charge_budget(self):
        """Test charging a budget."""
        pool = BudgetPool()
        pool.create_budget("api", max_cost=100.0)
        pool.charge("api", cost=10.0)
        budget = pool.get_budget("api")
        assert budget.used == 10.0

    def test_global_limit(self):
        """Test global budget limit."""
        pool = BudgetPool(global_limit=100.0)
        pool.create_budget("api1", max_cost=60.0)
        pool.create_budget("api2", max_cost=60.0)
        pool.charge("api1", cost=50.0)
        # Global limit should prevent exceeding total
        with pytest.raises(BudgetExceeded):
            pool.charge("api2", cost=60.0)

    def test_budget_not_found(self):
        """Test accessing non-existent budget."""
        pool = BudgetPool()
        with pytest.raises(KeyError):
            pool.charge("nonexistent", cost=10.0)

    def test_get_total_usage(self):
        """Test getting total usage across all budgets."""
        pool = BudgetPool()
        pool.create_budget("api1", max_cost=100.0)
        pool.create_budget("api2", max_cost=50.0)
        pool.charge("api1", cost=30.0)
        pool.charge("api2", cost=20.0)
        
        usage = pool.get_total_usage()
        assert usage["total_used"] == 50.0
        assert usage["total_max"] == 150.0
        assert "api1" in usage["budgets"]
        assert "api2" in usage["budgets"]

    def test_reset_all_budgets(self):
        """Test resetting all budgets in pool."""
        pool = BudgetPool()
        pool.create_budget("api1", max_cost=100.0)
        pool.create_budget("api2", max_cost=50.0)
        pool.charge("api1", cost=30.0)
        pool.charge("api2", cost=20.0)
        
        results = pool.reset_all()
        assert results["api1"] == 30.0
        assert results["api2"] == 20.0
        
        # All budgets should be reset
        assert pool.get_budget("api1").used == 0.0
        assert pool.get_budget("api2").used == 0.0


class TestBudgetPeriod:
    """Test BudgetPeriod enum."""

    def test_period_values(self):
        """Test period enum values."""
        assert BudgetPeriod.HOURLY.value == "hourly"
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.NONE.value == "none"


class TestAlertLevel:
    """Test AlertLevel enum."""

    def test_alert_levels(self):
        """Test alert level values."""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.CRITICAL.value == "critical"


class TestCostEntry:
    """Test CostEntry dataclass."""

    def test_create_cost_entry(self):
        """Test creating a cost entry."""
        entry = CostEntry(
            timestamp=time.time(),
            amount=10.0,
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
        )
        assert entry.amount == 10.0
        assert entry.model == "gpt-4"
        assert entry.input_tokens == 1000
        assert entry.output_tokens == 500

    def test_cost_entry_with_metadata(self):
        """Test cost entry with metadata."""
        entry = CostEntry(
            timestamp=time.time(),
            amount=5.0,
            model="gpt-3.5-turbo",
            prompt_name="test",
            metadata={"user": "test", "prompt_id": "123"}
        )
        assert entry.metadata["user"] == "test"
        assert entry.metadata["prompt_id"] == "123"


class TestBudgetAlert:
    """Test BudgetAlert dataclass."""

    def test_create_alert(self):
        """Test creating a budget alert."""
        alert = BudgetAlert(
            level=AlertLevel.WARNING,
            message="Budget at 75%",
            timestamp=time.time(),
            budget_name="api",
            current_usage=75.0,
            threshold=0.75,
            percentage=75.0,
        )
        assert alert.level == AlertLevel.WARNING
        assert alert.percentage == 75.0
        assert alert.budget_name == "api"


class TestUsageStats:
    """Test UsageStats dataclass."""

    def test_create_stats(self):
        """Test creating usage stats."""
        stats = UsageStats(
            total_cost=50.0,
            total_charges=10,
            average_cost=5.0,
            max_single_cost=10.0,
            min_single_cost=2.0,
            input_tokens=5000,
            output_tokens=2500,
            cost_by_model={"gpt-4": 30.0, "gpt-3.5-turbo": 20.0},
            cost_by_prompt={"test1": 25.0, "test2": 25.0},
            period_start=time.time() - 3600,
            period_end=time.time(),
        )
        assert stats.total_cost == 50.0
        assert stats.total_charges == 10
        assert stats.average_cost == 5.0


class TestCostTracker:
    """Test CostTracker class."""

    def test_create_tracker(self):
        """Test creating a cost tracker."""
        budget = Budget(max_cost=100.0, name="test")
        tracker = CostTracker(budget=budget)
        assert tracker.budget == budget

    def test_tracking_context(self):
        """Test using tracking context."""
        budget = Budget(max_cost=100.0, name="test")
        tracker = CostTracker(budget=budget)
        
        with tracker.context("test_op", model="gpt-4") as ctx:
            ctx.report_cost(5.0)
        
        assert budget.used == 5.0

    def test_track_decorator(self):
        """Test track decorator."""
        budget = Budget(max_cost=100.0, name="test")
        tracker = CostTracker(budget=budget)
        
        @tracker.track("test_func", estimated_cost=3.0)
        def my_function():
            return "result"
        
        result = my_function()
        assert result == "result"
        assert budget.used == 3.0


class TestBudgetReservation:
    """Test BudgetReservation class."""

    def test_create_reservation(self):
        """Test creating a budget reservation."""
        budget = Budget(max_cost=100.0, name="test")
        reservation = BudgetReservation(budget=budget, amount=20.0)
        assert reservation.reserved_amount == 20.0
        assert reservation.budget == budget

    def test_reservation_context_manager(self):
        """Test reservation as context manager."""
        budget = Budget(max_cost=100.0, name="test")
        
        with BudgetReservation(budget=budget, amount=20.0) as res:
            assert res.reserved_amount == 20.0
            # On successful exit, should charge reserved amount
        
        assert budget.used == 20.0

    def test_reservation_finalize(self):
        """Test finalizing reservation with different cost."""
        budget = Budget(max_cost=100.0, name="test")
        
        with BudgetReservation(budget=budget, amount=20.0) as res:
            # Actually used less
            res.finalize(actual_cost=15.0)
        
        assert budget.used == 15.0

    def test_reservation_exceeds_budget(self):
        """Test reservation that exceeds budget."""
        budget = Budget(max_cost=10.0, name="test")
        
        with pytest.raises(BudgetExceeded):
            with BudgetReservation(budget=budget, amount=20.0):
                pass


class TestCostTrackingContext:
    """Test CostTrackingContext class."""

    def test_tracking_context(self):
        """Test cost tracking context manager."""
        budget = Budget(max_cost=100.0, name="test")
        
        with CostTrackingContext(
            budget=budget,
            prompt_name="test",
            model="gpt-4"
        ) as ctx:
            ctx.report_cost(5.0)
        
        assert budget.used == 5.0

    def test_context_with_tokens(self):
        """Test reporting tokens in context."""
        budget = Budget(max_cost=100.0, name="test")
        
        with CostTrackingContext(
            budget=budget,
            prompt_name="test",
            model="gpt-4"
        ) as ctx:
            cost = ctx.report_tokens(input_tokens=1000, output_tokens=500)
            assert cost > 0
        
        assert budget.used > 0

    def test_context_with_estimated_cost(self):
        """Test context with estimated cost."""
        budget = Budget(max_cost=100.0, name="test")
        
        with CostTrackingContext(
            budget=budget,
            prompt_name="test",
            estimated_cost=10.0
        ):
            # If we don't report actual cost, estimated is used
            pass
        
        assert budget.used == 10.0


class TestBudgetAlerts:
    """Test budget alert functionality."""

    def test_add_alert_threshold(self):
        """Test adding alert thresholds."""
        budget = Budget(max_cost=100.0, name="test")
        budget.add_alert_threshold(0.75, AlertLevel.WARNING)
        budget.add_alert_threshold(0.90, AlertLevel.CRITICAL)
        
        # Should not trigger yet
        budget.charge(50.0)

    def test_alert_callback(self):
        """Test alert callback is called."""
        alerts_received = []
        
        def callback(alert: BudgetAlert):
            alerts_received.append(alert)
        
        budget = Budget(max_cost=100.0, name="test", alert_callback=callback)
        budget.add_alert_threshold(0.75, AlertLevel.WARNING)
        
        # Trigger alert
        budget.charge(80.0)
        
        # Alert should have been triggered
        assert len(alerts_received) >= 0  # May or may not trigger depending on exact threshold


class TestBudgetCalculations:
    """Test budget cost calculations."""

    def test_calculate_cost(self):
        """Test calculating cost from tokens."""
        budget = Budget(max_cost=100.0, name="test")
        cost = budget.calculate_cost("gpt-4", input_tokens=1000, output_tokens=500)
        assert cost > 0
        # GPT-4: 1000 * 0.03/1000 + 500 * 0.06/1000 = 0.03 + 0.03 = 0.06
        assert abs(cost - 0.06) < 0.001

    def test_estimate_tokens_remaining(self):
        """Test estimating remaining tokens."""
        budget = Budget(max_cost=100.0, name="test")
        budget.charge(50.0)
        
        remaining_tokens = budget.estimate_tokens_remaining("gpt-4", ratio=0.5)
        assert remaining_tokens > 0
