# SLI/SLO/Error Budget Management

Complete guide to Site Reliability Engineering best practices, SLO definition, and error budget tracking.

## SRE Fundamentals

### Service Level Indicators (SLIs)
- **Definition**: Quantitative measures of service reliability
- **Common SLIs**: Availability, latency, throughput, error rate, data durability
- **Measurement**: Based on actual user experience, not system metrics
- **Granularity**: Measured over time windows (1min, 5min, 1hour)

### Service Level Objectives (SLOs)
- **Definition**: Target values for SLIs that define acceptable reliability
- **Format**: "X% of requests should complete in < Y ms"
- **Example**: 99.9% availability = 43.2 minutes downtime per month
- **Balance**: Trade-off between reliability and development velocity

### Service Level Agreements (SLAs)
- **Definition**: Contractual obligations with customers
- **Relationship**: SLA < SLO (buffer for internal incidents)
- **Consequences**: Financial penalties, credits, or service commitments
- **Example**: SLO 99.9%, SLA 99.5% (buffer for internal improvements)

## Error Budget Tracking

```python
"""Error budget calculation and tracking"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List

@dataclass
class SLO:
    name: str
    target: float  # e.g., 0.999 for 99.9%
    window: str  # 'daily', 'weekly', 'monthly'

class ErrorBudgetTracker:
    """Track error budgets and burn rates"""

    def __init__(self, slos: List[SLO]):
        self.slos = {slo.name: slo for slo in slos}

    def calculate_error_budget(self, slo_name: str, window_days: int = 30) -> Dict:
        """Calculate error budget for SLO"""
        slo = self.slos[slo_name]

        # Total time in window
        total_time = window_days * 24 * 60  # minutes

        # Allowed downtime based on SLO
        allowed_downtime = total_time * (1 - slo.target)

        # Get actual downtime (from metrics)
        actual_downtime = self.get_actual_downtime(slo_name, window_days)

        # Calculate remaining budget
        remaining_budget = allowed_downtime - actual_downtime
        budget_percentage = (remaining_budget / allowed_downtime) * 100

        return {
            'slo_name': slo_name,
            'slo_target': slo.target,
            'window_days': window_days,
            'total_time_minutes': total_time,
            'allowed_downtime_minutes': allowed_downtime,
            'actual_downtime_minutes': actual_downtime,
            'remaining_budget_minutes': remaining_budget,
            'budget_percentage': budget_percentage,
            'status': self.budget_status(budget_percentage)
        }

    def calculate_burn_rate(self, slo_name: str, hours: int = 1) -> float:
        """Calculate error budget burn rate"""
        # How fast are we consuming the error budget?
        # > 1.0 means burning faster than sustainable

        recent_downtime = self.get_actual_downtime(slo_name, hours / 24)
        allowed_downtime_per_hour = self.get_hourly_budget(slo_name)

        burn_rate = recent_downtime / (allowed_downtime_per_hour * hours)
        return burn_rate

    def get_actual_downtime(self, slo_name: str, days: float) -> float:
        """Get actual downtime from metrics (minutes)"""
        # Query Prometheus or other monitoring system
        # Example: count time when error rate exceeded threshold
        return 0.0

    def get_hourly_budget(self, slo_name: str) -> float:
        """Get allowed downtime per hour"""
        slo = self.slos[slo_name]
        monthly_budget = 30 * 24 * 60 * (1 - slo.target)  # minutes per month
        return monthly_budget / (30 * 24)  # minutes per hour

    def budget_status(self, percentage: float) -> str:
        """Determine error budget status"""
        if percentage > 75:
            return "healthy"
        elif percentage > 50:
            return "warning"
        elif percentage > 25:
            return "critical"
        else:
            return "exhausted"

    def should_halt_releases(self, slo_name: str) -> bool:
        """Determine if releases should be halted"""
        budget = self.calculate_error_budget(slo_name)
        burn_rate = self.calculate_burn_rate(slo_name, hours=6)

        # Halt if budget < 25% OR burn rate > 10x
        return budget['budget_percentage'] < 25 or burn_rate > 10

# Example SLO definitions
availability_slo = SLO(
    name="api_availability",
    target=0.999,  # 99.9% uptime
    window="monthly"
)

latency_slo = SLO(
    name="api_latency_p95",
    target=0.95,  # 95% of requests < 500ms
    window="monthly"
)

error_rate_slo = SLO(
    name="api_error_rate",
    target=0.99,  # < 1% error rate
    window="monthly"
)

tracker = ErrorBudgetTracker([availability_slo, latency_slo, error_rate_slo])
```

## Error Budget Policy

### When Budget is Healthy (> 75%)
- **Development velocity**: Normal feature development
- **Risk tolerance**: Can take calculated risks
- **Deployment frequency**: Regular deployments
- **Focus**: Innovation and feature delivery

### When Budget is Warning (50-75%)
- **Increased caution**: Review deployment processes
- **Focus shift**: Start prioritizing reliability work
- **Monitoring**: Enhanced observability and alerting
- **Planning**: Prepare reliability improvements

### When Budget is Critical (25-50%)
- **Deployment freeze**: Halt non-critical deployments
- **Focus**: Reliability improvements only
- **Investigation**: Identify root causes of budget consumption
- **Communication**: Update stakeholders on status

### When Budget is Exhausted (< 25%)
- **Full freeze**: All feature development halted
- **Incident mode**: Treat as ongoing incident
- **Recovery plan**: Detailed plan to restore reliability
- **Leadership escalation**: Executive awareness and support

## Best Practices

### Defining SLOs
- **User-centric**: Based on actual user experience
- **Measurable**: Objective, quantifiable metrics
- **Achievable**: Realistic given current architecture
- **Meaningful**: Align with business objectives
- **Reviewed**: Regular evaluation and adjustment

### Monitoring Error Budgets
- **Real-time tracking**: Continuous budget consumption visibility
- **Burn rate alerts**: Alert on fast burn rates
- **Trend analysis**: Identify patterns and improvements
- **Team visibility**: Dashboard accessible to all stakeholders

### Using Error Budgets for Decision-Making
- **Deployment decisions**: Gate deployments based on budget
- **Priority setting**: Balance features vs. reliability work
- **Resource allocation**: Justify reliability investments
- **Performance reviews**: Measure team effectiveness
