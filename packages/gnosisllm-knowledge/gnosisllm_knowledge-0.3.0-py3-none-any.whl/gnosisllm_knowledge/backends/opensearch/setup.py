"""OpenSearch setup adapter implementation.

Handles the complete neural search setup:
1. OpenAI embedding connector creation
2. Model group creation
3. Model deployment
4. Ingest pipeline for automatic embedding
5. Search pipeline for hybrid search
6. Vector index creation
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.mappings import (
    get_index_template,
    get_knowledge_index_mappings,
    get_knowledge_index_settings,
    get_memory_index_mappings,
    get_memory_index_settings,
)
from gnosisllm_knowledge.core.exceptions import SetupError
from gnosisllm_knowledge.core.interfaces.setup import (
    DiagnosticReport,
    HealthReport,
    HealthStatus,
    SetupResult,
)

if TYPE_CHECKING:
    from opensearchpy import AsyncOpenSearch

logger = logging.getLogger(__name__)


class OpenSearchSetupAdapter:
    """OpenSearch setup adapter for neural search configuration.

    Configures OpenSearch with:
    - OpenAI embedding model connector
    - Model group and deployment
    - Ingest pipeline for automatic text embedding
    - Search pipeline for hybrid search
    - Vector index for semantic search

    Example:
        ```python
        from opensearchpy import AsyncOpenSearch

        config = OpenSearchConfig.from_env()
        client = AsyncOpenSearch(hosts=[{"host": config.host, "port": config.port}])
        setup = OpenSearchSetupAdapter(client, config)

        # Run complete setup
        result = await setup.setup()
        print(f"Model ID: {setup.model_id}")
        ```
    """

    def __init__(
        self,
        client: AsyncOpenSearch,
        config: OpenSearchConfig,
    ) -> None:
        """Initialize the setup adapter.

        Args:
            client: OpenSearch async client.
            config: OpenSearch configuration.
        """
        self._client = client
        self._config = config

        # IDs populated during setup
        self._connector_id: str | None = None
        self._model_group_id: str | None = None
        self._model_id: str | None = None

    @property
    def name(self) -> str:
        """Human-readable backend name."""
        return "OpenSearch"

    @property
    def model_id(self) -> str | None:
        """Get the deployed model ID."""
        return self._model_id

    @property
    def connector_id(self) -> str | None:
        """Get the connector ID."""
        return self._connector_id

    async def health_check(self) -> bool:
        """Quick health check.

        Returns:
            True if cluster is responsive.
        """
        try:
            response = await self._client.cluster.health()
            return response.get("status") in ("green", "yellow")
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def deep_health_check(self) -> HealthReport:
        """Comprehensive health check with component status.

        Returns:
            Detailed health report.
        """
        components: dict[str, Any] = {}
        start_time = datetime.now(timezone.utc)

        # Check cluster health
        try:
            cluster_health = await self._client.cluster.health()
            cluster_status = cluster_health.get("status", "unknown")

            if cluster_status == "green":
                status = HealthStatus.HEALTHY
            elif cluster_status == "yellow":
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            components["cluster"] = {
                "status": status.value,
                "cluster_status": cluster_status,
                "node_count": cluster_health.get("number_of_nodes", 0),
                "data_node_count": cluster_health.get("number_of_data_nodes", 0),
                "active_shards": cluster_health.get("active_shards", 0),
                "unassigned_shards": cluster_health.get("unassigned_shards", 0),
            }
        except Exception as e:
            components["cluster"] = {
                "status": HealthStatus.UNHEALTHY.value,
                "error": str(e),
            }
            status = HealthStatus.UNHEALTHY

        # Check knowledge index
        try:
            index_name = self._config.knowledge_index_name
            index_exists = await self._client.indices.exists(index=index_name)
            if index_exists:
                stats = await self._client.indices.stats(index=index_name)
                indices_stats = stats.get("indices", {}).get(index_name, {})
                primaries = indices_stats.get("primaries", {})
                docs = primaries.get("docs", {})

                components["knowledge_index"] = {
                    "status": HealthStatus.HEALTHY.value,
                    "exists": True,
                    "doc_count": docs.get("count", 0),
                    "size_bytes": primaries.get("store", {}).get("size_in_bytes", 0),
                }
            else:
                components["knowledge_index"] = {
                    "status": HealthStatus.DEGRADED.value,
                    "exists": False,
                    "message": "Index not created yet",
                }
        except Exception as e:
            components["knowledge_index"] = {
                "status": HealthStatus.UNKNOWN.value,
                "error": str(e),
            }

        # Determine overall status
        statuses = [c.get("status", HealthStatus.UNKNOWN.value) for c in components.values()]
        if all(s == HealthStatus.HEALTHY.value for s in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY.value for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED.value for s in statuses):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNKNOWN

        return HealthReport(
            healthy=overall_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED),
            status=overall_status,
            components=components,
            checked_at=start_time,
        )

    async def setup(self, **options: Any) -> SetupResult:
        """Run complete setup including ML model deployment.

        Creates connector, deploys model, creates pipelines and indices.

        Args:
            **options: Setup options:
                - force_recreate: Delete existing resources first
                - skip_ml: Skip ML model setup (use existing model_id from config)
                - skip_sample_data: Don't ingest sample documents

        Returns:
            Setup result with model_id and details.
        """
        steps_completed: list[str] = []
        errors: list[str] = []
        force_recreate = options.get("force_recreate", False)
        skip_ml = options.get("skip_ml", False)

        # Force cleanup if requested
        if force_recreate:
            cleanup_result = await self.cleanup()
            if cleanup_result.steps_completed:
                steps_completed.extend(cleanup_result.steps_completed)

        # Step 1: Create connector (OpenAI)
        if not skip_ml:
            try:
                await self._create_connector()
                steps_completed.append(f"Created connector: {self._connector_id}")
            except Exception as e:
                errors.append(f"Failed to create connector: {e}")
                logger.error(f"Failed to create connector: {e}")

        # Step 2: Create model group
        if not skip_ml and self._connector_id:
            try:
                await self._create_model_group()
                steps_completed.append(f"Created model group: {self._model_group_id}")
            except Exception as e:
                errors.append(f"Failed to create model group: {e}")
                logger.error(f"Failed to create model group: {e}")

        # Step 3: Deploy model
        if not skip_ml and self._connector_id and self._model_group_id:
            try:
                await self._deploy_model()
                steps_completed.append(f"Deployed model: {self._model_id}")
            except Exception as e:
                errors.append(f"Failed to deploy model: {e}")
                logger.error(f"Failed to deploy model: {e}")

        # Use config model_id if skipping ML or if deployment failed
        if not self._model_id:
            self._model_id = self._config.model_id

        # Step 4: Create ingest pipeline
        # Only create ingest pipeline for global setup (not per-account)
        # Account indices should use the global pipeline to ensure consistent model
        is_global_setup = self._config.index_prefix == "gnosisllm"
        if self._model_id and is_global_setup:
            try:
                await self._create_ingest_pipeline()
                pipeline_name = self._config.ingest_pipeline_name or f"{self._config.index_prefix}-ingest-pipeline"
                steps_completed.append(f"Created ingest pipeline: {pipeline_name}")
            except Exception as e:
                errors.append(f"Failed to create ingest pipeline: {e}")
                logger.error(f"Failed to create ingest pipeline: {e}")

        # Step 5: Create search pipeline (only for global setup)
        if is_global_setup:
            try:
                await self._create_search_pipeline()
                pipeline_name = self._config.search_pipeline_name or f"{self._config.index_prefix}-search-pipeline"
                steps_completed.append(f"Created search pipeline: {pipeline_name}")
            except Exception as e:
                errors.append(f"Failed to create search pipeline: {e}")
                logger.error(f"Failed to create search pipeline: {e}")

        # Step 6: Create index template (only for global setup)
        # Template covers all gnosisllm-* indices including per-account indices
        if is_global_setup:
            try:
                template_name = f"{self._config.index_prefix}-template"
                template_body = get_index_template(self._config)

                # Ensure template has global pipeline for auto-index creation
                global_pipeline = self._config.ingest_pipeline_name or "gnosisllm-ingest-pipeline"
                template_body["template"]["settings"]["index"]["default_pipeline"] = global_pipeline

                await self._client.indices.put_index_template(
                    name=template_name,
                    body=template_body,
                )
                steps_completed.append(f"Created index template: {template_name}")
            except Exception as e:
                errors.append(f"Failed to create index template: {e}")
                logger.error(f"Failed to create index template: {e}")

        # Step 7: Create knowledge index
        try:
            index_name = self._config.knowledge_index_name
            exists = await self._client.indices.exists(index=index_name)

            if not exists:
                settings = get_knowledge_index_settings(self._config)
                # Add default pipeline - always use global pipeline for consistency
                # This ensures all accounts use the same embedding model
                pipeline_name = self._config.ingest_pipeline_name or "gnosisllm-ingest-pipeline"
                settings["index"]["default_pipeline"] = pipeline_name

                await self._client.indices.create(
                    index=index_name,
                    body={
                        "settings": settings,
                        "mappings": get_knowledge_index_mappings(self._config),
                    },
                )
                steps_completed.append(f"Created knowledge index: {index_name}")
            else:
                steps_completed.append(f"Knowledge index already exists: {index_name}")
        except Exception as e:
            errors.append(f"Failed to create knowledge index: {e}")
            logger.error(f"Failed to create knowledge index: {e}")

        # Step 8: Create memory index
        try:
            memory_index = self._config.agentic_memory_index_name
            exists = await self._client.indices.exists(index=memory_index)

            if not exists:
                await self._client.indices.create(
                    index=memory_index,
                    body={
                        "settings": get_memory_index_settings(self._config),
                        "mappings": get_memory_index_mappings(),
                    },
                )
                steps_completed.append(f"Created memory index: {memory_index}")
            else:
                steps_completed.append(f"Memory index already exists: {memory_index}")
        except Exception as e:
            errors.append(f"Failed to create memory index: {e}")
            logger.error(f"Failed to create memory index: {e}")

        return SetupResult(
            success=len(errors) == 0,
            steps_completed=steps_completed,
            errors=errors if errors else None,
            data={"model_id": self._model_id} if self._model_id else None,
        )

    async def _create_connector(self) -> None:
        """Create OpenAI embedding connector."""
        # Check if connector already exists
        connector_name = f"{self._config.index_prefix}-openai-connector"
        existing = await self._find_connector_by_name(connector_name)
        if existing:
            self._connector_id = existing
            logger.info(f"Using existing connector: {existing}")
            return

        if not self._config.openai_api_key:
            raise SetupError(
                message="OPENAI_API_KEY required to create connector",
                step="connector",
                details={"hint": "Set OPENAI_API_KEY environment variable"},
            )

        # Create new connector
        connector_body = {
            "name": connector_name,
            "description": "OpenAI embedding connector for GnosisLLM Knowledge",
            "version": 1,
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
                    "request_body": '{ "input": ${parameters.input}, "model": "${parameters.model}" }',
                    "pre_process_function": "connector.pre_process.openai.embedding",
                    "post_process_function": "connector.post_process.openai.embedding",
                }
            ],
        }

        response = await self._client.transport.perform_request(
            "POST",
            "/_plugins/_ml/connectors/_create",
            body=connector_body,
        )

        self._connector_id = response.get("connector_id")
        logger.info(f"Created connector: {self._connector_id}")

    async def _create_model_group(self) -> None:
        """Create model group."""
        model_group_name = f"{self._config.index_prefix}-model-group"

        # Check if model group already exists
        existing = await self._find_model_group_by_name(model_group_name)
        if existing:
            self._model_group_id = existing
            logger.info(f"Using existing model group: {existing}")
            return

        response = await self._client.transport.perform_request(
            "POST",
            "/_plugins/_ml/model_groups/_register",
            body={
                "name": model_group_name,
                "description": "Model group for GnosisLLM Knowledge embeddings",
            },
        )

        self._model_group_id = response.get("model_group_id")
        logger.info(f"Created model group: {self._model_group_id}")

    async def _deploy_model(self) -> None:
        """Deploy embedding model."""
        model_name = f"{self._config.index_prefix}-embedding-model"

        # Check if model already exists
        existing = await self._find_model_by_name(model_name)
        if existing:
            self._model_id = existing
            # Check if deployed
            status = await self._get_model_status(existing)
            if status == "DEPLOYED":
                logger.info(f"Using existing deployed model: {existing}")
                return
            # Deploy if not deployed
            await self._deploy_model_by_id(existing)
            logger.info(f"Deployed existing model: {existing}")
            return

        # Register new model
        response = await self._client.transport.perform_request(
            "POST",
            "/_plugins/_ml/models/_register",
            body={
                "name": model_name,
                "function_name": "remote",
                "model_group_id": self._model_group_id,
                "description": "OpenAI embedding model for GnosisLLM Knowledge",
                "connector_id": self._connector_id,
            },
        )

        task_id = response.get("task_id")
        if not task_id:
            raise SetupError(
                message="No task_id returned from model registration",
                step="model_deployment",
            )

        # Wait for registration
        model_id = await self._wait_for_task(task_id, "model registration")
        if not model_id:
            raise SetupError(
                message="Model registration timed out",
                step="model_deployment",
            )

        self._model_id = model_id

        # Deploy the model
        await self._deploy_model_by_id(model_id)
        logger.info(f"Deployed model: {model_id}")

    async def _create_ingest_pipeline(self) -> None:
        """Create ingest pipeline for automatic embedding."""
        pipeline_name = self._config.ingest_pipeline_name or f"{self._config.index_prefix}-ingest-pipeline"

        pipeline_body = {
            "description": "GnosisLLM ingest pipeline for text embedding",
            "processors": [
                {
                    "text_embedding": {
                        "model_id": self._model_id,
                        "field_map": {
                            "content": self._config.embedding_field,
                        },
                    }
                },
                {
                    "set": {
                        "field": "indexed_at",
                        "value": "{{_ingest.timestamp}}",
                    }
                },
            ],
        }

        await self._client.ingest.put_pipeline(
            id=pipeline_name,
            body=pipeline_body,
        )

    async def _create_search_pipeline(self) -> None:
        """Create search pipeline for hybrid search."""
        pipeline_name = self._config.search_pipeline_name or f"{self._config.index_prefix}-search-pipeline"

        pipeline_body = {
            "description": "GnosisLLM search pipeline for hybrid search",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {"weights": [0.7, 0.3]},
                        },
                    }
                }
            ],
        }

        await self._client.transport.perform_request(
            "PUT",
            f"/_search/pipeline/{pipeline_name}",
            body=pipeline_body,
        )

    async def cleanup(self) -> SetupResult:
        """Clean up all resources in correct order.

        Deletes all indices and templates matching the index prefix pattern.

        Returns:
            Cleanup result.
        """
        steps_completed: list[str] = []
        errors: list[str] = []
        prefix = self._config.index_prefix

        # Delete all indices matching prefix-*
        try:
            index_pattern = f"{prefix}-*"
            # Check if any indices match the pattern
            indices_response = await self._client.indices.get(index=index_pattern)
            if indices_response:
                for index_name in indices_response.keys():
                    try:
                        await self._client.indices.delete(index=index_name)
                        steps_completed.append(f"Deleted index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete index {index_name}: {e}")
        except Exception:
            pass  # No matching indices

        # Delete all index templates matching prefix-*
        try:
            templates_response = await self._client.indices.get_index_template(name=f"{prefix}-*")
            if templates_response and "index_templates" in templates_response:
                for template_info in templates_response["index_templates"]:
                    template_name = template_info.get("name")
                    if template_name:
                        try:
                            await self._client.indices.delete_index_template(name=template_name)
                            steps_completed.append(f"Deleted template: {template_name}")
                        except Exception as e:
                            logger.warning(f"Failed to delete template {template_name}: {e}")
        except Exception:
            pass  # No matching templates

        # Delete search pipeline
        try:
            pipeline_name = self._config.search_pipeline_name or f"{self._config.index_prefix}-search-pipeline"
            await self._client.transport.perform_request(
                "DELETE",
                f"/_search/pipeline/{pipeline_name}",
            )
            steps_completed.append(f"Deleted search pipeline: {pipeline_name}")
        except Exception:
            pass  # May not exist

        # Delete ingest pipeline
        try:
            pipeline_name = self._config.ingest_pipeline_name or f"{self._config.index_prefix}-ingest-pipeline"
            await self._client.ingest.delete_pipeline(id=pipeline_name)
            steps_completed.append(f"Deleted ingest pipeline: {pipeline_name}")
        except Exception:
            pass  # May not exist

        # Undeploy and delete model
        model_name = f"{self._config.index_prefix}-embedding-model"
        model_id = self._model_id or await self._find_model_by_name(model_name)
        if model_id:
            try:
                await self._client.transport.perform_request(
                    "POST",
                    f"/_plugins/_ml/models/{model_id}/_undeploy",
                )
                await asyncio.sleep(2)
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/models/{model_id}",
                )
                steps_completed.append(f"Deleted model: {model_id}")
            except Exception as e:
                logger.warning(f"Failed to delete model: {e}")

        # Delete model group
        model_group_name = f"{self._config.index_prefix}-model-group"
        model_group_id = self._model_group_id or await self._find_model_group_by_name(model_group_name)
        if model_group_id:
            try:
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/model_groups/{model_group_id}",
                )
                steps_completed.append(f"Deleted model group: {model_group_id}")
            except Exception as e:
                logger.warning(f"Failed to delete model group: {e}")

        # Delete connector
        connector_name = f"{self._config.index_prefix}-openai-connector"
        connector_id = self._connector_id or await self._find_connector_by_name(connector_name)
        if connector_id:
            try:
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/connectors/{connector_id}",
                )
                steps_completed.append(f"Deleted connector: {connector_id}")
            except Exception as e:
                logger.warning(f"Failed to delete connector: {e}")

        return SetupResult(
            success=len(errors) == 0,
            steps_completed=steps_completed,
            errors=errors if errors else None,
        )

    async def diagnose(self) -> DiagnosticReport:
        """Run diagnostics and return recommendations.

        Returns:
            Diagnostic report with issues and recommendations.
        """
        health = await self.deep_health_check()
        issues: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Check cluster status
        cluster_info = health.components.get("cluster", {})
        if cluster_info.get("status") == HealthStatus.UNHEALTHY.value:
            issues.append("OpenSearch cluster is unhealthy")
            recommendations.append("Check OpenSearch logs and cluster state")
        elif cluster_info.get("cluster_status") == "yellow":
            warnings.append("Cluster is yellow - some replicas may be unassigned")
            recommendations.append("Consider adding more nodes or reducing replica count")

        # Check unassigned shards
        unassigned = cluster_info.get("unassigned_shards", 0)
        if unassigned > 0:
            warnings.append(f"{unassigned} unassigned shards detected")
            recommendations.append("Review shard allocation and disk space")

        # Check index existence
        index_info = health.components.get("knowledge_index", {})
        if not index_info.get("exists", True):
            issues.append("Knowledge index does not exist")
            recommendations.append("Run setup() to create the index")

        # Check document count
        doc_count = index_info.get("doc_count", 0)
        if doc_count == 0 and index_info.get("exists"):
            warnings.append("Knowledge index is empty")
            recommendations.append("Load documents using the loader")

        return DiagnosticReport(
            health=health,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
        )

    def get_setup_steps(self) -> list[tuple[str, str]]:
        """Get list of setup steps.

        Returns:
            List of (step_name, description) tuples.
        """
        return [
            ("connector", "Create OpenAI embedding connector"),
            ("model_group", "Create model group"),
            ("model", "Deploy embedding model"),
            ("ingest_pipeline", "Create ingest pipeline for text embedding"),
            ("search_pipeline", "Create search pipeline for hybrid search"),
            ("index_template", "Create index template"),
            ("knowledge_index", "Create knowledge document index"),
            ("memory_index", "Create conversation memory index"),
        ]

    # === Helper Methods ===

    async def _find_connector_by_name(self, name: str) -> str | None:
        """Find connector by exact name."""
        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/connectors/_search",
                body={"query": {"term": {"name.keyword": name}}},
            )
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_id"]
        except Exception:
            pass
        return None

    async def _find_model_group_by_name(self, name: str) -> str | None:
        """Find model group by exact name."""
        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/model_groups/_search",
                body={"query": {"term": {"name.keyword": name}}},
            )
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_id"]
        except Exception:
            pass
        return None

    async def _find_model_by_name(self, name: str) -> str | None:
        """Find model by exact name."""
        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/models/_search",
                body={"query": {"term": {"name.keyword": name}}},
            )
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_id"]
        except Exception:
            pass
        return None

    async def _get_model_status(self, model_id: str) -> str | None:
        """Get model deployment status."""
        try:
            response = await self._client.transport.perform_request(
                "GET",
                f"/_plugins/_ml/models/{model_id}",
            )
            return response.get("model_state")
        except Exception:
            return None

    async def _deploy_model_by_id(self, model_id: str) -> None:
        """Deploy a model by ID."""
        response = await self._client.transport.perform_request(
            "POST",
            f"/_plugins/_ml/models/{model_id}/_deploy",
        )

        task_id = response.get("task_id")
        if task_id:
            await self._wait_for_task(task_id, "model deployment")

        # Wait for model to actually be in DEPLOYED state
        await self._wait_for_model_deployed(model_id)

    async def _wait_for_model_deployed(
        self,
        model_id: str,
        timeout: int = 120,
    ) -> bool:
        """Wait for model to reach DEPLOYED state.

        Args:
            model_id: Model ID to check.
            timeout: Maximum time to wait in seconds.

        Returns:
            True if deployed, False if timeout.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = await self._get_model_status(model_id)
            if status == "DEPLOYED":
                logger.info(f"Model {model_id} is now DEPLOYED")
                return True
            elif status in ("DEPLOY_FAILED", "UNDEPLOYED"):
                logger.error(f"Model deployment failed, status: {status}")
                return False

            logger.debug(f"Waiting for model deployment, current status: {status}")
            await asyncio.sleep(2)

        logger.error(f"Model deployment timed out after {timeout}s")
        return False

    async def _wait_for_task(
        self,
        task_id: str,
        task_name: str,
        timeout: int = 120,
    ) -> str | None:
        """Wait for an ML task to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = await self._client.transport.perform_request(
                    "GET",
                    f"/_plugins/_ml/tasks/{task_id}",
                )

                state = response.get("state")
                if state == "COMPLETED":
                    return response.get("model_id")
                elif state in ("FAILED", "CANCELLED"):
                    logger.error(f"Task {task_name} failed: {response}")
                    return None

            except Exception as e:
                logger.warning(f"Error checking task status: {e}")

            await asyncio.sleep(2)

        logger.error(f"Task {task_name} timed out after {timeout}s")
        return None

    async def get_cluster_stats(self) -> dict[str, Any]:
        """Get cluster statistics.

        Returns:
            Cluster statistics dictionary.
        """
        try:
            health = await self._client.cluster.health()
            stats = await self._client.cluster.stats()

            return {
                "cluster_name": health.get("cluster_name"),
                "cluster_status": health.get("status"),
                "node_count": health.get("number_of_nodes"),
                "data_node_count": health.get("number_of_data_nodes"),
                "active_shards": health.get("active_shards"),
                "active_primary_shards": health.get("active_primary_shards"),
                "relocating_shards": health.get("relocating_shards"),
                "initializing_shards": health.get("initializing_shards"),
                "unassigned_shards": health.get("unassigned_shards"),
                "total_indices": stats.get("indices", {}).get("count", 0),
                "total_docs": stats.get("indices", {}).get("docs", {}).get("count", 0),
            }
        except Exception as e:
            raise SetupError(
                message=f"Failed to get cluster stats: {e}",
                step="cluster_stats",
                cause=e,
            ) from e

    async def get_index_stats(self, index_name: str) -> dict[str, Any]:
        """Get index-specific statistics.

        Args:
            index_name: Index to get stats for.

        Returns:
            Index statistics dictionary.
        """
        try:
            stats = await self._client.indices.stats(index=index_name)
            index_stats = stats.get("indices", {}).get(index_name, {})
            primaries = index_stats.get("primaries", {})

            return {
                "index_name": index_name,
                "doc_count": primaries.get("docs", {}).get("count", 0),
                "deleted_doc_count": primaries.get("docs", {}).get("deleted", 0),
                "primary_store_size_bytes": primaries.get("store", {}).get("size_in_bytes", 0),
                "query_total": primaries.get("search", {}).get("query_total", 0),
                "query_time_ms": primaries.get("search", {}).get("query_time_in_millis", 0),
                "index_total": primaries.get("indexing", {}).get("index_total", 0),
                "index_time_ms": primaries.get("indexing", {}).get("index_time_in_millis", 0),
            }
        except Exception as e:
            raise SetupError(
                message=f"Failed to get index stats: {e}",
                step="index_stats",
                details={"index_name": index_name},
                cause=e,
            ) from e

    # === Agentic Search Setup Methods ===

    async def enable_agentic_search(self) -> None:
        """Enable agentic search cluster settings.

        The agent framework is enabled by default in OpenSearch 3.x.
        This method verifies that required settings are enabled.

        Note: The settings plugins.ml_commons.agentic_search_enabled and
        plugins.neural_search.agentic_search_enabled do not exist in
        OpenSearch 3.4+. The agent_framework_enabled and rag_pipeline_feature_enabled
        settings are used instead and are enabled by default.

        Raises:
            SetupError: If required settings are not enabled.
        """
        try:
            # Check if agent framework is enabled (required for agents)
            settings = await self._client.cluster.get_settings(
                include_defaults=True,
                flat_settings=True,
            )
            defaults = settings.get("defaults", {})

            agent_enabled = defaults.get(
                "plugins.ml_commons.agent_framework_enabled", "false"
            )
            rag_enabled = defaults.get(
                "plugins.ml_commons.rag_pipeline_feature_enabled", "false"
            )

            if agent_enabled != "true":
                raise SetupError(
                    message="Agent framework is not enabled. Set plugins.ml_commons.agent_framework_enabled=true",
                    step="enable_agentic_search",
                )

            if rag_enabled != "true":
                logger.warning("RAG pipeline feature is not enabled, some features may be limited")

            logger.info("Agent framework is enabled (agentic search ready)")
        except SetupError:
            raise
        except Exception as e:
            raise SetupError(
                message=f"Failed to verify agentic search settings: {e}",
                step="enable_agentic_search",
                cause=e,
            ) from e

    async def setup_flow_agent(self) -> str:
        """Create flow agent with RAGTool for agentic search.

        Flow agents use RAGTool to perform retrieval-augmented generation:
        1. Search the knowledge base using neural/semantic search
        2. Pass results to LLM for answer generation
        3. Return AI-generated answer with source citations

        This provides a conversational experience where users get natural
        language answers instead of raw search results.

        Returns:
            Agent ID of the created/existing flow agent.

        Raises:
            SetupError: If agent creation fails.
        """
        agent_name = f"{self._config.index_prefix}-flow-agent"

        # Check if agent already exists
        existing = await self._find_agent_by_name(agent_name)
        if existing:
            logger.info(f"Using existing flow agent: {existing}")
            return existing

        # Enable agentic search if not already enabled
        await self.enable_agentic_search()

        # Create LLM model for answer generation
        llm_model_id = await self._setup_llm_model()

        # Get embedding model ID for neural search
        embedding_model_id = self._model_id or self._config.model_id
        if not embedding_model_id:
            raise SetupError(
                message="Embedding model ID is required for RAGTool. Run 'gnosisllm-knowledge setup' first.",
                step="flow_agent",
            )

        # Index pattern for multi-tenant knowledge bases
        # Matches: gnosisllm-<account_id>-knowledge
        index_pattern = f"{self._config.index_prefix}-*-knowledge"

        # Create RAGTool configuration
        rag_tool = self._create_rag_tool_config(
            embedding_model_id=embedding_model_id,
            llm_model_id=llm_model_id,
            index_pattern=index_pattern,
        )

        # Register flow agent with RAGTool
        # Flow agents execute tools sequentially and return the last tool's output
        agent_body = {
            "name": agent_name,
            "type": "flow",
            "description": "Agentic search agent for GnosisLLM Knowledge - uses RAGTool for conversational AI answers",
            "tools": [rag_tool],
        }

        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/agents/_register",
                body=agent_body,
            )
            agent_id = response.get("agent_id")
            logger.info(f"Created flow agent with RAGTool: {agent_id}")
            return agent_id
        except Exception as e:
            raise SetupError(
                message=f"Failed to create flow agent: {e}",
                step="flow_agent",
                cause=e,
            ) from e

    async def setup_conversational_agent(self) -> str:
        """Create conversational agent with RAGTool and memory.

        Conversational agents support multi-turn dialogue with memory
        persistence. They use RAGTool to search and generate AI answers,
        providing a chat-like experience with context from previous turns.

        Returns:
            Agent ID of the created/existing conversational agent.

        Raises:
            SetupError: If agent creation fails.
        """
        agent_name = f"{self._config.index_prefix}-conversational-agent"

        # Check if agent already exists
        existing = await self._find_agent_by_name(agent_name)
        if existing:
            logger.info(f"Using existing conversational agent: {existing}")
            return existing

        # Enable agentic search if not already enabled
        await self.enable_agentic_search()

        # Create LLM model for answer generation
        llm_model_id = await self._setup_llm_model()

        # Get embedding model ID for neural search
        embedding_model_id = self._model_id or self._config.model_id
        if not embedding_model_id:
            raise SetupError(
                message="Embedding model ID is required for RAGTool. Run 'gnosisllm-knowledge setup' first.",
                step="conversational_agent",
            )

        # Index pattern for multi-tenant knowledge bases
        index_pattern = f"{self._config.index_prefix}-*-knowledge"

        # Create RAGTool configuration
        rag_tool = self._create_rag_tool_config(
            embedding_model_id=embedding_model_id,
            llm_model_id=llm_model_id,
            index_pattern=index_pattern,
        )

        # Register conversational agent with memory support
        # Use conversational_flow type for simpler tool execution without ReAct prompting
        agent_body = {
            "name": agent_name,
            "type": "conversational_flow",
            "description": "Conversational agentic search for GnosisLLM Knowledge - multi-turn dialogue with memory and AI answers",
            "llm": {
                "model_id": llm_model_id,
                "parameters": {
                    "max_iteration": str(self._config.agentic_max_iterations),
                },
            },
            "tools": [rag_tool],
            "memory": {
                "type": "conversation_index",
            },
        }

        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/agents/_register",
                body=agent_body,
            )
            agent_id = response.get("agent_id")
            logger.info(f"Created conversational agent with RAGTool: {agent_id}")
            return agent_id
        except Exception as e:
            raise SetupError(
                message=f"Failed to create conversational agent: {e}",
                step="conversational_agent",
                cause=e,
            ) from e

    async def setup_agents(self, agent_types: list[str] | None = None) -> dict[str, str]:
        """Setup agentic search agents with RAGTool.

        Creates agents using RAGTool for retrieval-augmented generation.
        Agents search the knowledge base and generate AI-powered answers.
        Also creates an agentic search pipeline for the flow agent.

        Args:
            agent_types: List of agent types to setup ('flow', 'conversational').
                        If None, sets up all agent types.

        Returns:
            Dictionary mapping agent type to agent ID, plus agentic_pipeline_name.

        Raises:
            SetupError: If any agent creation fails.
        """
        if agent_types is None:
            agent_types = ["flow", "conversational"]

        results: dict[str, str] = {}

        if "flow" in agent_types:
            flow_agent_id = await self.setup_flow_agent()
            results["flow_agent_id"] = flow_agent_id

            # Create agentic search pipeline for the flow agent
            # This allows using agentic search via standard _search API
            pipeline_name = await self.setup_agentic_search_pipeline(flow_agent_id)
            results["agentic_pipeline_name"] = pipeline_name

        if "conversational" in agent_types:
            results["conversational_agent_id"] = await self.setup_conversational_agent()

        return results

    async def cleanup_agents(self) -> SetupResult:
        """Clean up agentic search agents and pipelines.

        Returns:
            Cleanup result with steps completed.
        """
        steps_completed: list[str] = []
        errors: list[str] = []

        # Delete agentic search pipeline first
        pipeline_name = f"{self._config.index_prefix}-agentic-pipeline"
        try:
            await self._client.transport.perform_request(
                "DELETE",
                f"/_search/pipeline/{pipeline_name}",
            )
            steps_completed.append(f"Deleted agentic pipeline: {pipeline_name}")
        except Exception:
            pass  # Pipeline may not exist

        # Delete flow agent
        flow_agent_name = f"{self._config.index_prefix}-flow-agent"
        flow_agent_id = await self._find_agent_by_name(flow_agent_name)
        if flow_agent_id:
            try:
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/agents/{flow_agent_id}",
                )
                steps_completed.append(f"Deleted flow agent: {flow_agent_id}")
            except Exception as e:
                errors.append(f"Failed to delete flow agent: {e}")

        # Delete conversational agent
        conv_agent_name = f"{self._config.index_prefix}-conversational-agent"
        conv_agent_id = await self._find_agent_by_name(conv_agent_name)
        if conv_agent_id:
            try:
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/agents/{conv_agent_id}",
                )
                steps_completed.append(f"Deleted conversational agent: {conv_agent_id}")
            except Exception as e:
                errors.append(f"Failed to delete conversational agent: {e}")

        # Delete LLM model
        llm_model_name = f"{self._config.index_prefix}-llm-model"
        llm_model_id = await self._find_model_by_name(llm_model_name)
        if llm_model_id:
            try:
                await self._client.transport.perform_request(
                    "POST",
                    f"/_plugins/_ml/models/{llm_model_id}/_undeploy",
                )
                await asyncio.sleep(2)
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/models/{llm_model_id}",
                )
                steps_completed.append(f"Deleted LLM model: {llm_model_id}")
            except Exception as e:
                logger.warning(f"Failed to delete LLM model: {e}")

        # Delete LLM connector
        llm_connector_name = f"{self._config.index_prefix}-llm-connector"
        llm_connector_id = await self._find_connector_by_name(llm_connector_name)
        if llm_connector_id:
            try:
                await self._client.transport.perform_request(
                    "DELETE",
                    f"/_plugins/_ml/connectors/{llm_connector_id}",
                )
                steps_completed.append(f"Deleted LLM connector: {llm_connector_id}")
            except Exception as e:
                logger.warning(f"Failed to delete LLM connector: {e}")

        return SetupResult(
            success=len(errors) == 0,
            steps_completed=steps_completed,
            errors=errors if errors else None,
        )

    def _create_rag_tool_config(
        self,
        embedding_model_id: str,
        llm_model_id: str,
        index_pattern: str,
    ) -> dict[str, Any]:
        """Create RAGTool configuration for agentic search.

        RAGTool (OpenSearch 2.13+) performs retrieval-augmented generation:
        1. Searches the index using neural/semantic search
        2. Passes results to LLM for answer generation
        3. Returns AI-generated answer with source citations

        This provides a conversational experience where users get natural
        language answers instead of raw search results.

        Args:
            embedding_model_id: Embedding model ID for neural search.
            llm_model_id: LLM model ID for answer generation.
            index_pattern: Index pattern to search (supports wildcards).

        Returns:
            Tool configuration dictionary.
        """
        # Prompt template for RAGTool - instructs LLM how to use retrieved context
        # RAGTool fills ${parameters.output:-} with search results
        prompt_template = (
            "You are a helpful assistant. Use the following context to answer the question. "
            "If the context doesn't contain enough information, say so.\n\n"
            "Context:\n${parameters.output:-}\n\n"
            "Question: ${parameters.question}\n\n"
            "Answer:"
        )

        return {
            "type": "RAGTool",
            "name": "knowledge_search",
            "description": "Search knowledge base and generate AI answer. "
                          "Retrieves relevant documents and synthesizes a natural language response.",
            "parameters": {
                "embedding_model_id": embedding_model_id,
                "inference_model_id": llm_model_id,
                "index": index_pattern,
                "embedding_field": self._config.embedding_field,
                "source_field": '["content", "title", "url"]',
                "doc_size": "5",
                "query_type": "neural",
                "input": "${parameters.question}",
                "prompt": prompt_template,
            },
        }

    def _create_query_planning_tool_config(
        self, llm_model_id: str
    ) -> dict[str, Any]:
        """Create QueryPlanningTool configuration for agentic search.

        QueryPlanningTool (OpenSearch 3.2+) translates natural language queries
        into OpenSearch DSL. The LLM decides the optimal query type based on
        user intent - keyword, neural, hybrid, or complex aggregations.

        NOTE: QueryPlanningTool only generates DSL - it does NOT generate answers.
        Use RAGTool for conversational experience with AI-generated answers.

        Args:
            llm_model_id: LLM model ID for query generation.

        Returns:
            Tool configuration dictionary.
        """
        # Response filter extracts generated DSL from OpenAI chat completions format
        # Format: {"choices": [{"message": {"content": "<DSL JSON>"}}]}
        response_filter = "$.choices[0].message.content"

        return {
            "type": "QueryPlanningTool",
            "name": "query_planner",
            "description": "Generate OpenSearch DSL queries from natural language. "
                          "Supports keyword search, neural/semantic search, hybrid search, "
                          "and complex aggregations based on user intent.",
            "parameters": {
                "model_id": llm_model_id,
                "response_filter": response_filter,
            },
        }

    async def setup_agentic_search_pipeline(self, agent_id: str) -> str:
        """Create search pipeline with agentic query translator.

        This pipeline allows using agentic search via the standard
        _search API by translating natural language to DSL.

        Args:
            agent_id: Agent ID to use for query translation.

        Returns:
            Pipeline name.

        Raises:
            SetupError: If pipeline creation fails.
        """
        pipeline_name = f"{self._config.index_prefix}-agentic-pipeline"

        pipeline_body = {
            "description": "GnosisLLM agentic search pipeline - translates natural language to DSL",
            "request_processors": [
                {
                    "agentic_query_translator": {
                        "agent_id": agent_id,
                    }
                }
            ],
        }

        try:
            await self._client.transport.perform_request(
                "PUT",
                f"/_search/pipeline/{pipeline_name}",
                body=pipeline_body,
            )
            logger.info(f"Created agentic search pipeline: {pipeline_name}")
            return pipeline_name
        except Exception as e:
            raise SetupError(
                message=f"Failed to create agentic search pipeline: {e}",
                step="agentic_pipeline",
                cause=e,
            ) from e

    async def _setup_llm_model(self) -> str:
        """Setup LLM model for agent reasoning.

        Creates an LLM connector and deploys the model if not exists.

        Returns:
            LLM model ID.

        Raises:
            SetupError: If LLM setup fails.
        """
        # Create LLM connector
        llm_connector_id = await self._create_llm_connector()

        # Create LLM model
        llm_model_name = f"{self._config.index_prefix}-llm-model"
        existing_model = await self._find_model_by_name(llm_model_name)
        if existing_model:
            # Check if deployed
            status = await self._get_model_status(existing_model)
            if status == "DEPLOYED":
                logger.info(f"Using existing deployed LLM model: {existing_model}")
                return existing_model
            # Deploy if not deployed
            await self._deploy_model_by_id(existing_model)
            return existing_model

        # Register new LLM model
        response = await self._client.transport.perform_request(
            "POST",
            "/_plugins/_ml/models/_register",
            body={
                "name": llm_model_name,
                "function_name": "remote",
                "model_group_id": self._model_group_id or await self._find_or_create_model_group(),
                "description": f"OpenAI {self._config.agentic_llm_model} for GnosisLLM agent reasoning",
                "connector_id": llm_connector_id,
            },
        )

        task_id = response.get("task_id")
        if not task_id:
            raise SetupError(
                message="No task_id returned from LLM model registration",
                step="llm_model",
            )

        # Wait for registration
        model_id = await self._wait_for_task(task_id, "LLM model registration")
        if not model_id:
            raise SetupError(
                message="LLM model registration timed out",
                step="llm_model",
            )

        # Deploy the model
        await self._deploy_model_by_id(model_id)
        logger.info(f"Deployed LLM model: {model_id}")
        return model_id

    async def _create_llm_connector(self) -> str:
        """Create LLM connector for agent reasoning.

        Returns:
            Connector ID.

        Raises:
            SetupError: If connector creation fails.
        """
        connector_name = f"{self._config.index_prefix}-llm-connector"

        # Check if connector already exists
        existing = await self._find_connector_by_name(connector_name)
        if existing:
            logger.info(f"Using existing LLM connector: {existing}")
            return existing

        if not self._config.openai_api_key:
            raise SetupError(
                message="OPENAI_API_KEY required for LLM connector",
                step="llm_connector",
                details={"hint": "Set OPENAI_API_KEY environment variable"},
            )

        # Connector for RAGTool uses 'prompt' parameter
        # See: https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/rag-tool/
        connector_body = {
            "name": connector_name,
            "description": f"OpenAI {self._config.agentic_llm_model} connector for agent reasoning",
            "version": 1,
            "protocol": "http",
            "parameters": {
                "model": self._config.agentic_llm_model,
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
                    # RAGTool sends 'prompt' containing question + retrieved context
                    "request_body": '{ "model": "${parameters.model}", "messages": [{"role": "user", "content": "${parameters.prompt}"}] }',
                },
            ],
        }

        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/connectors/_create",
                body=connector_body,
            )
            connector_id = response.get("connector_id")
            logger.info(f"Created LLM connector: {connector_id}")
            return connector_id
        except Exception as e:
            raise SetupError(
                message=f"Failed to create LLM connector: {e}",
                step="llm_connector",
                cause=e,
            ) from e

    async def _find_or_create_model_group(self) -> str:
        """Find existing model group or create one.

        Returns:
            Model group ID.
        """
        if self._model_group_id:
            return self._model_group_id

        model_group_name = f"{self._config.index_prefix}-model-group"
        existing = await self._find_model_group_by_name(model_group_name)
        if existing:
            return existing

        # Create model group
        response = await self._client.transport.perform_request(
            "POST",
            "/_plugins/_ml/model_groups/_register",
            body={
                "name": model_group_name,
                "description": "Model group for GnosisLLM Knowledge",
            },
        )
        return response.get("model_group_id")

    async def _find_agent_by_name(self, name: str) -> str | None:
        """Find agent by exact name.

        Args:
            name: Agent name to search for (exact match).

        Returns:
            Agent ID if found, None otherwise.
        """
        try:
            response = await self._client.transport.perform_request(
                "POST",
                "/_plugins/_ml/agents/_search",
                body={"query": {"term": {"name.keyword": name}}},
            )
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_id"]
        except Exception:
            pass
        return None

    async def get_agent_status(self, agent_id: str) -> dict[str, Any] | None:
        """Get status of an agent.

        Args:
            agent_id: Agent identifier.

        Returns:
            Agent status info or None if not found.
        """
        try:
            response = await self._client.transport.perform_request(
                "GET",
                f"/_plugins/_ml/agents/{agent_id}",
            )
            return {
                "agent_id": agent_id,
                "name": response.get("name"),
                "type": response.get("type"),
                "description": response.get("description"),
                "tools": [t.get("name") for t in response.get("tools", [])],
                "created_at": response.get("created_time"),
            }
        except Exception as e:
            logger.warning(f"Failed to get agent status: {e}")
            return None
