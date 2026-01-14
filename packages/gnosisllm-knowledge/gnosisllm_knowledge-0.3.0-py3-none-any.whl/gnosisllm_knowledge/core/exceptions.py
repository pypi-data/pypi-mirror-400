"""Exception hierarchy for gnosisllm-knowledge."""

from __future__ import annotations

from typing import Any


class KnowledgeError(Exception):
    """Base exception for gnosisllm-knowledge.

    All library exceptions inherit from this class.

    Attributes:
        message: Human-readable error message.
        code: Machine-readable error code.
        details: Additional error details.
        cause: Original exception that caused this error.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            details: Additional error details.
            cause: Original exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.cause = cause

    def __str__(self) -> str:
        """Return string representation."""
        parts = [self.message]
        if self.code:
            parts.append(f"[{self.code}]")
        if self.cause:
            parts.append(f"(caused by: {self.cause})")
        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class ConfigurationError(KnowledgeError):
    """Invalid or missing configuration.

    Raised when required configuration is missing or invalid.
    """

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class ConnectionError(KnowledgeError):
    """Failed to connect to backend.

    Raised when unable to establish connection to a service.
    """

    def __init__(
        self,
        message: str,
        *,
        host: str | None = None,
        port: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port
        if host:
            self.details["host"] = host
        if port:
            self.details["port"] = port


class AuthenticationError(KnowledgeError):
    """Authentication failed.

    Raised when authentication to a service fails.
    """

    pass


class AuthorizationError(KnowledgeError):
    """Authorization denied.

    Raised when a user doesn't have permission to perform an operation.
    """

    def __init__(
        self,
        message: str,
        *,
        required_permission: str | None = None,
        resource: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.required_permission = required_permission
        self.resource = resource
        if required_permission:
            self.details["required_permission"] = required_permission
        if resource:
            self.details["resource"] = resource


class LoadError(KnowledgeError):
    """Failed to load content.

    Raised when content loading fails (fetch error, parse error, etc.).
    """

    def __init__(
        self,
        message: str,
        *,
        source: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(f"Failed to load '{source}': {message}", **kwargs)
        self.source = source
        self.details["source"] = source


class FetchError(LoadError):
    """Failed to fetch content from URL.

    More specific than LoadError, for HTTP/network failures.
    """

    def __init__(
        self,
        message: str,
        *,
        source: str,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, source=source, **kwargs)
        self.status_code = status_code
        if status_code:
            self.details["status_code"] = status_code


class ValidationError(KnowledgeError):
    """Content validation failed.

    Raised when document content fails validation rules.
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
        errors: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.errors = errors or []
        if field:
            self.details["field"] = field
        if errors:
            self.details["errors"] = errors


class IndexError(KnowledgeError):
    """Failed to index documents.

    Raised when document indexing fails.
    """

    def __init__(
        self,
        message: str,
        *,
        index_name: str | None = None,
        doc_count: int = 0,
        failed_count: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.index_name = index_name
        self.doc_count = doc_count
        self.failed_count = failed_count
        if index_name:
            self.details["index_name"] = index_name
        self.details["doc_count"] = doc_count
        self.details["failed_count"] = failed_count


class SearchError(KnowledgeError):
    """Failed to execute search.

    Raised when search operations fail.
    """

    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        index_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.query = query
        self.index_name = index_name
        if query:
            self.details["query"] = query
        if index_name:
            self.details["index_name"] = index_name


class AgenticSearchError(SearchError):
    """Failed to execute agentic search.

    Raised when AI agent-powered search operations fail.
    This includes agent execution failures, LLM errors, and timeouts.
    """

    def __init__(
        self,
        message: str,
        *,
        agent_id: str | None = None,
        agent_type: str | None = None,
        conversation_id: str | None = None,
        iteration: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.conversation_id = conversation_id
        self.iteration = iteration
        if agent_id:
            self.details["agent_id"] = agent_id
        if agent_type:
            self.details["agent_type"] = agent_type
        if conversation_id:
            self.details["conversation_id"] = conversation_id
        if iteration is not None:
            self.details["iteration"] = iteration


class EmbeddingError(KnowledgeError):
    """Failed to generate embeddings.

    Raised when embedding generation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        model: str | None = None,
        text_length: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.model = model
        self.text_length = text_length
        if model:
            self.details["model"] = model
        self.details["text_length"] = text_length


class SetupError(KnowledgeError):
    """Failed during setup.

    Raised when backend setup fails.
    """

    def __init__(
        self,
        message: str,
        *,
        step: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(f"Setup failed at '{step}': {message}", **kwargs)
        self.step = step
        self.details["step"] = step


class TimeoutError(KnowledgeError):
    """Operation timed out.

    Raised when an operation exceeds its timeout.
    """

    def __init__(
        self,
        message: str = "Operation timed out",
        *,
        timeout: float | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout = timeout
        self.operation = operation
        if timeout:
            self.details["timeout"] = timeout
        if operation:
            self.details["operation"] = operation


class CircuitBreakerOpenError(KnowledgeError):
    """Circuit breaker is open.

    Raised when a circuit breaker is open and rejecting requests.
    """

    def __init__(
        self,
        message: str = "Circuit breaker is open",
        *,
        recovery_time: float | None = None,
        component: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.recovery_time = recovery_time
        self.component = component
        if recovery_time:
            self.details["recovery_time"] = recovery_time
        if component:
            self.details["component"] = component


class RateLimitError(KnowledgeError):
    """Rate limit exceeded.

    Raised when API rate limits are exceeded.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: float | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.limit = limit
        if retry_after:
            self.details["retry_after"] = retry_after
        if limit:
            self.details["limit"] = limit


class DocumentNotFoundError(KnowledgeError):
    """Document not found.

    Raised when a document cannot be found.
    """

    def __init__(
        self,
        message: str = "Document not found",
        *,
        doc_id: str | None = None,
        index_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.doc_id = doc_id
        self.index_name = index_name
        if doc_id:
            self.details["doc_id"] = doc_id
        if index_name:
            self.details["index_name"] = index_name


# === Memory Exceptions ===


class MemoryError(KnowledgeError):
    """Base exception for memory operations.

    Raised when memory operations fail.
    """

    pass


class ContainerNotFoundError(MemoryError):
    """Container does not exist.

    Raised when a memory container cannot be found.
    """

    def __init__(
        self,
        message: str = "Container not found",
        *,
        container_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.container_id = container_id
        if container_id:
            self.details["container_id"] = container_id


class ContainerExistsError(MemoryError):
    """Container already exists.

    Raised when attempting to create a container that already exists.
    """

    def __init__(
        self,
        message: str = "Container already exists",
        *,
        container_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.container_name = container_name
        if container_name:
            self.details["container_name"] = container_name


class SessionNotFoundError(MemoryError):
    """Session does not exist.

    Raised when a session cannot be found.
    """

    def __init__(
        self,
        message: str = "Session not found",
        *,
        session_id: str | None = None,
        container_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.session_id = session_id
        self.container_id = container_id
        if session_id:
            self.details["session_id"] = session_id
        if container_id:
            self.details["container_id"] = container_id


class InferenceError(MemoryError):
    """LLM inference failed.

    Raised when LLM inference for memory extraction fails.
    """

    def __init__(
        self,
        message: str = "LLM inference failed",
        *,
        model_id: str | None = None,
        strategy: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.model_id = model_id
        self.strategy = strategy
        if model_id:
            self.details["model_id"] = model_id
        if strategy:
            self.details["strategy"] = strategy


class InferenceTimeoutError(InferenceError):
    """LLM inference timed out.

    Raised when LLM inference exceeds the configured timeout.
    """

    def __init__(
        self,
        message: str = "LLM inference timed out",
        *,
        timeout_seconds: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds


class MemoryConfigurationError(MemoryError):
    """Memory is not properly configured.

    Raised when memory configuration is missing or invalid.
    """

    def __init__(
        self,
        message: str = "Memory configuration error",
        *,
        missing_config: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.missing_config = missing_config
        if missing_config:
            self.details["missing_config"] = missing_config
