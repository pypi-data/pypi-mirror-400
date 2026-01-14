"""Benchmark resources."""

from typing import Any

from planvantage.resources.base import BaseResource


class BenchmarksResource(BaseResource):
    """Resource for accessing benchmark data."""

    def get_hierarchy(self) -> Any:
        """Get the benchmark hierarchy.

        Returns:
            Benchmark hierarchy data.

        Example:
            >>> hierarchy = client.benchmarks.get_hierarchy()
        """
        return self._http.get("/benchmarks/hierarchy")

    def get(self, guid: str) -> Any:
        """Get a specific benchmark by GUID.

        Args:
            guid: The benchmark's unique identifier.

        Returns:
            Benchmark data.

        Example:
            >>> benchmark = client.benchmarks.get("bm_abc123")
        """
        return self._http.get(f"/benchmark/{guid}")
