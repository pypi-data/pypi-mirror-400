import sys
import contextlib
from typing import Any

from _reusable import Elapsed, Welford


class LoopScope:

    def __init__(self, precision: int = 3):
        self.precision = precision
        self.welford = Welford()
        self.elapsed: float = 0
        self.min: Reading | None = None
        self.max: Reading | None = None
        self.error_count: int = 0

    @property
    def throughput(self) -> float:
        return self.welford.n / self.elapsed if self.welford.n else 0

    @contextlib.contextmanager
    def iteration(self, item_id: str | None = None):
        elapsed = Elapsed(self.precision)
        try:
            yield
        except:
            self.error_count += 1
            raise
        finally:
            current = float(elapsed)
            self.welford.update(current)
            self.elapsed += current
            if not self.min or current < self.min.elapsed:
                self.min = Reading(item_id or str(self.welford.n), current)
            if not self.max or current > self.max.elapsed:
                self.max = Reading(item_id or str(self.welford.n), current)

    def dump(self) -> dict[str, Any]:
        return {
            "iteration_count": self.welford.n,
            "error_count": self.error_count,
            "elapsed": {
                "sum": round(self.elapsed, self.precision),
                "mean": round(self.welford.mean, self.precision),
                "var": round(self.welford.var, self.precision) if self.welford.var is float("nan") else None,
                "std_dev": round(self.welford.std_dev, self.precision) if self.welford.std_dev is float("nan") else None,
                "min": self.min.dump() if self.min else None,
                "max": self.max.dump() if self.max else None,
            },
            "throughput": {
                "per_second": round(self.throughput, self.precision),
                "per_minute": round(self.throughput * 60, self.precision),
            },
        }


class Reading:
    def __init__(self, item_id: str | None = None, elapsed: float = 0):
        self.item_id = item_id
        self.elapsed = elapsed

    def dump(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "elapsed": round(self.elapsed, 3),
        }
