"""
StopWatch operates on a notion of "spans" which represent scopes of code for which we
want to measure timing. Spans can be nested and placed inside loops for aggregation.

StopWatch requires a root scope which upon completion signifies the end of the round
of measurements. On a server, you might use a single request as your root scope.

StopWatch produces two kinds of reports.
1) Aggregated (see _reported_values).
2) Non-aggregated or "tracing" (see _reported_traces).
"""

from importlib.metadata import version

__version__ = version("k3stopwatch")

from .k3stopwatch import (
    TimerData,
    StopWatch,
    default_export_aggregated_timers,
    default_export_tracing,
    format_report,
)

__all__ = [
    "TimerData",
    "StopWatch",
    "default_export_aggregated_timers",
    "default_export_tracing",
    "format_report",
]
