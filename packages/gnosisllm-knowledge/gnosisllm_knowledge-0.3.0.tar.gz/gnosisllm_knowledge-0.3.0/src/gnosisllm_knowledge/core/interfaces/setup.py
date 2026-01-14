"""Setup adapter protocol - Interface for backend setup operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class SetupResult:
    """Result of a setup operation.

    Attributes:
        success: Whether setup completed successfully.
        steps_completed: List of completed step descriptions.
        errors: List of errors encountered.
        warnings: List of warnings.
        duration_ms: Duration in milliseconds.
        data: Additional result data (e.g., model_id).
    """

    success: bool
    steps_completed: list[str] | None = None
    errors: list[str] | None = None
    warnings: list[str] | None = None
    duration_ms: float = 0.0
    data: dict[str, Any] | None = None


@dataclass
class HealthReport:
    """Comprehensive health report.

    Attributes:
        healthy: Overall health status.
        status: HealthStatus enum value.
        components: Component health details.
        checked_at: When the check was performed.
    """

    healthy: bool
    status: HealthStatus = HealthStatus.UNKNOWN
    components: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiagnosticReport:
    """Diagnostic report with recommendations.

    Attributes:
        health: Health report.
        issues: List of issues found.
        warnings: List of warnings.
        recommendations: List of recommendations.
        cluster_info: Cluster-specific information.
    """

    health: HealthReport
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    cluster_info: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ISetupAdapter(Protocol):
    """Protocol for backend setup operations.

    Setup adapters are responsible for:
    - Setting up the search backend (indices, pipelines, etc.)
    - Health checking the backend
    - Running diagnostics and providing recommendations
    - Cleaning up resources

    Implementations should handle all backend-specific setup
    requirements transparently.
    """

    @property
    def name(self) -> str:
        """Human-readable backend name.

        Returns:
            Backend name (e.g., "OpenSearch", "Elasticsearch").
        """
        ...

    async def health_check(self) -> bool:
        """Quick health check.

        Returns:
            True if backend is healthy and responding.
        """
        ...

    async def deep_health_check(self) -> HealthReport:
        """Comprehensive health check with component status.

        Checks all components (cluster, indices, pipelines, etc.)
        and returns detailed health information.

        Returns:
            HealthReport with component-level health status.
        """
        ...

    async def setup(self, **options: Any) -> SetupResult:
        """Run complete setup.

        Creates indices, pipelines, templates, and any other
        required backend resources.

        Args:
            **options: Setup options like:
                - force: Recreate existing resources
                - skip_pipelines: Skip pipeline creation
                - index_prefix: Custom index prefix

        Returns:
            SetupResult with completion status.
        """
        ...

    async def cleanup(self) -> SetupResult:
        """Clean up all resources.

        Removes all resources created by setup. Use with caution
        as this will delete all data.

        Returns:
            SetupResult with cleanup status.
        """
        ...

    async def diagnose(self) -> DiagnosticReport:
        """Run diagnostics and return recommendations.

        Analyzes the backend configuration and state,
        identifies issues, and provides recommendations.

        Returns:
            DiagnosticReport with issues and recommendations.
        """
        ...

    def get_setup_steps(self) -> list[tuple[str, str]]:
        """Get list of setup steps.

        Returns:
            List of (step_name, step_description) tuples.
        """
        ...
