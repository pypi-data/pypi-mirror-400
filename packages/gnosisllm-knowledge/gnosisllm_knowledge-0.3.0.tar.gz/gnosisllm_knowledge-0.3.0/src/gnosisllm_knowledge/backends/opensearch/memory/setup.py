"""Memory setup operations - Connector and Model creation.

CRITICAL: The LLM connector MUST use both system_prompt AND user_prompt.
If only system_prompt is used, zero facts will be extracted.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from gnosisllm_knowledge.core.exceptions import MemoryConfigurationError

if TYPE_CHECKING:
    from gnosisllm_knowledge.backends.opensearch.memory.config import MemoryConfig

logger = logging.getLogger(__name__)


@dataclass
class SetupStatus:
    """Result of setup verification."""

    is_ready: bool
    checks: dict[str, bool]


class MemorySetup:
    """Setup operations for Agentic Memory.

    Creates the required OpenSearch connectors and models for memory to work.

    Example:
        ```python
        setup = MemorySetup(config)

        # Create connectors and models
        llm_model_id = await setup.setup_llm_model()
        embedding_model_id = await setup.setup_embedding_model()

        # Verify setup
        status = await setup.verify_setup()
        if status.is_ready:
            print("Memory is ready!")
        ```
    """

    def __init__(self, config: MemoryConfig) -> None:
        """Initialize setup.

        Args:
            config: Memory configuration.
        """
        self._config = config
        self._base_url = config.url
        self._auth = config.auth

    async def setup_llm_model(self) -> str:
        """Create OpenAI LLM connector and model for fact extraction.

        CRITICAL: The connector uses BOTH system_prompt AND user_prompt.

        Returns:
            The deployed LLM model ID.

        Raises:
            MemoryConfigurationError: If OpenAI API key is not configured.
        """
        if not self._config.openai_api_key:
            raise MemoryConfigurationError(
                "OpenAI API key required for LLM setup",
                missing_config=["openai_api_key"],
            )

        connector_id = await self._create_llm_connector()
        model_id = await self._register_model(
            name="OpenAI LLM for Agentic Memory",
            connector_id=connector_id,
            function_name="remote",
        )
        await self._deploy_model(model_id)

        logger.info(f"LLM model deployed: {model_id}")
        return model_id

    async def _create_llm_connector(self) -> str:
        """Create OpenAI chat connector.

        CRITICAL: Uses BOTH system_prompt AND user_prompt parameters.
        This is required for Agentic Memory fact extraction to work.

        Returns:
            The connector ID.
        """
        # CRITICAL: Both system_prompt AND user_prompt are required
        request_body = (
            '{"model": "${parameters.model}", '
            '"messages": ['
            '{"role": "system", "content": "${parameters.system_prompt}"}, '
            '{"role": "user", "content": "${parameters.user_prompt}"}'
            "]}"
        )

        connector_body: dict[str, Any] = {
            "name": "OpenAI Chat Connector for Agentic Memory",
            "description": "Connector for OpenAI with system_prompt AND user_prompt support",
            "version": "1",
            "protocol": "http",
            "parameters": {
                "model": self._config.llm_model,
            },
            "credential": {
                "openAI_key": self._config.openai_api_key,
            },
            "actions": [
                {
                    "action_type": "predict",
                    "method": "POST",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "headers": {
                        "Authorization": "Bearer ${credential.openAI_key}",
                        "Content-Type": "application/json",
                    },
                    "request_body": request_body,
                }
            ],
        }

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/connectors/_create",
                json=connector_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        connector_id = result.get("connector_id")
        logger.info(f"LLM connector created: {connector_id}")
        return connector_id

    async def setup_embedding_model(self) -> str:
        """Create OpenAI embedding connector and model.

        Returns:
            The deployed embedding model ID.

        Raises:
            MemoryConfigurationError: If OpenAI API key is not configured.
        """
        if not self._config.openai_api_key:
            raise MemoryConfigurationError(
                "OpenAI API key required for embedding setup",
                missing_config=["openai_api_key"],
            )

        connector_id = await self._create_embedding_connector()
        model_id = await self._register_model(
            name="OpenAI Embedding for Agentic Memory",
            connector_id=connector_id,
            function_name="remote",
        )
        await self._deploy_model(model_id)

        logger.info(f"Embedding model deployed: {model_id}")
        return model_id

    async def _create_embedding_connector(self) -> str:
        """Create OpenAI embedding connector.

        Returns:
            The connector ID.
        """
        connector_body: dict[str, Any] = {
            "name": "OpenAI Embedding Connector",
            "description": "Connector for OpenAI text-embedding models",
            "version": "1",
            "protocol": "http",
            "parameters": {
                "model": self._config.embedding_model,
            },
            "credential": {
                "openAI_key": self._config.openai_api_key,
            },
            "actions": [
                {
                    "action_type": "predict",
                    "method": "POST",
                    "url": "https://api.openai.com/v1/embeddings",
                    "headers": {
                        "Authorization": "Bearer ${credential.openAI_key}",
                        "Content-Type": "application/json",
                    },
                    "request_body": '{"model": "${parameters.model}", "input": ${parameters.input}}',
                    "post_process_function": "connector.post_process.openai.embedding",
                }
            ],
        }

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/connectors/_create",
                json=connector_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        connector_id = result.get("connector_id")
        logger.info(f"Embedding connector created: {connector_id}")
        return connector_id

    async def _register_model(
        self,
        name: str,
        connector_id: str,
        function_name: str = "remote",
    ) -> str:
        """Register a model with OpenSearch.

        Args:
            name: Model name.
            connector_id: Connector ID to use.
            function_name: Model function name (default: remote).

        Returns:
            The registered model ID.
        """
        model_body: dict[str, Any] = {
            "name": name,
            "function_name": function_name,
            "connector_id": connector_id,
        }

        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=self._config.connect_timeout,
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/models/_register",
                json=model_body,
                auth=self._auth,
            )
            response.raise_for_status()
            result = response.json()

        return result.get("model_id")

    async def _deploy_model(self, model_id: str) -> None:
        """Deploy a model.

        Args:
            model_id: Model ID to deploy.
        """
        async with httpx.AsyncClient(
            verify=self._config.verify_certs,
            timeout=60.0,  # Deployment can be slow
        ) as client:
            response = await client.post(
                f"{self._base_url}/_plugins/_ml/models/{model_id}/_deploy",
                auth=self._auth,
            )
            response.raise_for_status()

    async def verify_setup(self) -> SetupStatus:
        """Verify that memory is properly configured.

        Returns:
            SetupStatus with verification results.
        """
        checks: dict[str, bool] = {}

        # Check LLM model
        if self._config.llm_model_id:
            llm_ok = await self._check_model(self._config.llm_model_id)
            checks["llm_model"] = llm_ok
        else:
            checks["llm_model"] = False

        # Check embedding model
        if self._config.embedding_model_id:
            embed_ok = await self._check_model(self._config.embedding_model_id)
            checks["embedding_model"] = embed_ok
        else:
            checks["embedding_model"] = False

        is_ready = all(checks.values())
        return SetupStatus(is_ready=is_ready, checks=checks)

    async def _check_model(self, model_id: str) -> bool:
        """Check if a model is deployed and responding.

        Args:
            model_id: Model ID to check.

        Returns:
            True if model is deployed and ready.
        """
        try:
            async with httpx.AsyncClient(
                verify=self._config.verify_certs,
                timeout=self._config.connect_timeout,
            ) as client:
                response = await client.get(
                    f"{self._base_url}/_plugins/_ml/models/{model_id}",
                    auth=self._auth,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("model_state") == "DEPLOYED"
        except Exception:
            pass
        return False
