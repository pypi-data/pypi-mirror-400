"""
Context Graph Skill - Memory and Knowledge Graph Tools

Provides agents with persistent memory capabilities using async job polling.
All operations are automatically scoped to environment-specific datasets.
"""

from typing import Optional, Dict, Any
import httpx
import logging
import asyncio
import time
from agno.tools import Toolkit

logger = logging.getLogger(__name__)

# Configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 10.0
POLL_INTERVAL = 2.0  # seconds between job status checks
MAX_POLL_TIME = 300.0  # 5 minutes max wait


def _is_retryable_error(response: httpx.Response | None, exception: Exception | None) -> bool:
    """Determine if error is retryable (network/5xx) or permanent (4xx)."""
    if exception and isinstance(exception, (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)):
        return True
    if response and response.status_code >= 500:
        return True
    return False


async def _retry_with_backoff(func, max_retries: int = MAX_RETRIES):
    """Retry with exponential backoff for transient failures only."""
    last_exception = None
    delay = INITIAL_RETRY_DELAY

    for attempt in range(max_retries):
        try:
            result = await func()
            if isinstance(result, httpx.Response) and not _is_retryable_error(result, None):
                return result
            return result
        except Exception as e:
            last_exception = e
            if not _is_retryable_error(None, e):
                logger.error(f"Non-retryable error", extra={"error": str(e)})
                raise
            if attempt < max_retries - 1:
                logger.warning(f"Retry {attempt + 1}/{max_retries} in {delay}s", extra={"error": str(e)})
                await asyncio.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)
            else:
                logger.error(f"All retries failed", extra={"error": str(e)})

    if last_exception:
        raise last_exception


class ContextGraphSkill(Toolkit):
    """
    Context graph skill with async job polling and progress indicators.

    Tools:
    - store_memory: Store information (can wait for completion or return immediately)
    - poll_job_status: Poll job status until complete
    - recall_memory: Search stored memories
    - semantic_search: Search knowledge graph
    """

    def __init__(
        self,
        graph_api_url: str,
        api_key: str,
        organization_id: str,
        dataset_name: str,
        auto_create_dataset: bool = True,
    ):
        super().__init__(name="context-graph-memory")

        self.graph_api_url = graph_api_url.rstrip('/')
        self.api_key = api_key
        self.organization_id = organization_id
        self.dataset_name = dataset_name
        self.auto_create_dataset = auto_create_dataset
        self._dataset_id = None

        self.register(self.store_memory)
        self.register(self.poll_job_status)
        self.register(self.recall_memory)
        self.register(self.semantic_search)

        logger.info("Initialized ContextGraphSkill", extra={"dataset_name": dataset_name})

    async def _get_or_create_dataset(self) -> str:
        """Get or create dataset ID (cached)."""
        if self._dataset_id:
            return self._dataset_id

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Organization-ID": self.organization_id,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.graph_api_url}/api/v1/graph/datasets",
                headers=headers,
            )

            if response.status_code == 200:
                response_data = response.json()
                # Handle both list response (old API) and dict response (new API)
                if isinstance(response_data, dict):
                    datasets = response_data.get("datasets", [])
                else:
                    datasets = response_data

                for ds in datasets:
                    if ds.get("name") == self.dataset_name:
                        self._dataset_id = ds["id"]
                        return self._dataset_id

            if self.auto_create_dataset:
                create_response = await client.post(
                    f"{self.graph_api_url}/api/v1/graph/datasets",
                    headers=headers,
                    json={
                        "name": self.dataset_name,
                        "description": f"Auto-created for: {self.dataset_name}",
                        "scope": "org",
                    },
                )

                if create_response.status_code in [200, 201]:
                    self._dataset_id = create_response.json()["id"]
                    return self._dataset_id
                else:
                    raise Exception(f"Failed to create dataset: {create_response.status_code}")
            else:
                raise Exception(f"Dataset '{self.dataset_name}' not found")

    async def _poll_job_status(
        self,
        job_id: str,
        dataset_id: str,
        headers: Dict[str, str],
    ) -> tuple[Dict[str, Any], str]:
        """
        Poll job status until complete, building progress log.

        Returns (final_job_status, progress_log) or raises exception on timeout/failure.
        """
        start_time = time.time()
        last_progress = -1
        progress_log = []
        poll_count = 0

        progress_log.append(f"⏳ Submitting memory job...")
        logger.info("Starting job polling", extra={"job_id": job_id})

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                elapsed = time.time() - start_time
                poll_count += 1

                if elapsed > MAX_POLL_TIME:
                    progress_log.append(f"✗ Timeout after {MAX_POLL_TIME}s ({poll_count} polls)")
                    raise Exception(f"Job timed out after {MAX_POLL_TIME}s")

                # Poll job status
                try:
                    response = await client.get(
                        f"{self.graph_api_url}/api/v1/graph/jobs/{job_id}",
                        headers=headers,
                    )

                    if response.status_code != 200:
                        # Fallback to memory/status endpoint
                        response = await client.get(
                            f"{self.graph_api_url}/api/v1/graph/memory/status/{job_id}",
                            headers=headers,
                            params={"dataset_id": dataset_id},
                        )

                    if response.status_code == 200:
                        job_status = response.json()
                        status = job_status.get("status", "unknown")
                        progress = job_status.get("progress", 0)

                        # Log progress changes
                        if progress != last_progress and progress > 0:
                            progress_log.append(f"  ⚙️ Progress: {progress}%")
                            last_progress = progress
                        elif poll_count == 1:
                            progress_log.append(f"  🔄 Job submitted, polling for completion...")

                        # Check completion
                        if status == "completed":
                            progress_log.append(f"✅ Complete in {elapsed:.1f}s ({poll_count} polls)")
                            logger.info("Job completed", extra={"job_id": job_id, "elapsed": elapsed})
                            return job_status, "\n".join(progress_log)
                        elif status == "failed":
                            error = job_status.get("error", "Unknown error")
                            progress_log.append(f"✗ Job failed: {error}")
                            raise Exception(f"Job failed: {error}")

                        # Log occasional status updates
                        if poll_count % 5 == 0:
                            progress_log.append(f"  ⏱️ Still processing... ({elapsed:.0f}s elapsed)")

                except httpx.HTTPError as e:
                    logger.warning("Poll error", extra={"error": str(e), "poll_count": poll_count})
                    if poll_count == 1:
                        progress_log.append(f"  ⚠️ Connection issue, retrying...")

                # Wait before next poll
                await asyncio.sleep(POLL_INTERVAL)

    async def store_memory(
        self,
        context: str,
        wait: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store context in persistent memory.

        Args:
            context: Information to remember
            wait: If True, wait for job to complete. If False, return immediately with job_id
            metadata: Optional metadata

        Returns:
            If wait=True: Success message with memory ID (only after job completes)
            If wait=False: Job ID for manual polling with poll_job_status tool
        """
        try:
            dataset_id = await self._get_or_create_dataset()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.organization_id,
            }

            context_dict = {"content": context}
            if metadata:
                context_dict["metadata"] = metadata

            # Submit job (async mode - returns immediately)
            async def _do_store():
                async with httpx.AsyncClient(timeout=30.0) as client:
                    return await client.post(
                        f"{self.graph_api_url}/api/v1/graph/memory/store",
                        headers=headers,
                        json={
                            "context": context_dict,
                            "dataset_id": dataset_id,
                            "metadata": metadata,
                            "sync": False,  # Async mode
                        },
                    )

            response = await _retry_with_backoff(_do_store)

            if response.status_code != 200:
                error_msg = f"Failed to submit memory job: HTTP {response.status_code}"
                logger.error(error_msg, extra={"response": response.text[:500]})
                return f"✗ Error: {error_msg}"

            result = response.json()
            job_id = result.get("job_id")
            memory_id = result.get("memory_id", "unknown")

            if not job_id:
                # Sync response (shouldn't happen with sync=False, but handle it)
                return f"✓ Memory stored. Memory ID: {memory_id}"

            # If wait=False, return job_id immediately for manual polling
            if not wait:
                return f"⏳ Memory storage job submitted.\n\nJob ID: {job_id}\nMemory ID: {memory_id}\n\n" \
                       f"Use poll_job_status(job_id=\"{job_id}\") to check progress."

            # If wait=True, poll until complete (backend waits for Cognee pipeline)
            try:
                final_status, progress_log = await self._poll_job_status(job_id, dataset_id, headers)

                logger.info("Memory stored and indexed", extra={"memory_id": memory_id, "job_id": job_id})

                # Return detailed progress log with final status
                return f"{progress_log}\n\n✅ Memory stored and indexed successfully!\nMemory ID: {memory_id}\n\n" \
                       f"The memory is now searchable and can be recalled."
            except Exception as poll_error:
                logger.error("Polling failed", extra={"error": str(poll_error), "job_id": job_id})
                return f"✗ Job submitted (ID: {job_id[:8]}...) but polling failed: {str(poll_error)}\n" \
                       f"Use poll_job_status(job_id=\"{job_id}\") to check manually."

        except Exception as e:
            error_msg = f"Failed to store memory: {str(e)}"
            logger.error(error_msg, extra={"error_type": type(e).__name__})
            return f"✗ Error: {error_msg}"

    async def poll_job_status(
        self,
        job_id: str,
    ) -> str:
        """
        Poll a memory storage job until complete.

        Use this after calling store_memory with wait=False to monitor job progress.

        Args:
            job_id: Job ID returned from store_memory

        Returns:
            Progress log and final status
        """
        try:
            dataset_id = await self._get_or_create_dataset()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.organization_id,
            }

            final_status, progress_log = await self._poll_job_status(job_id, dataset_id, headers)
            memory_id = final_status.get("job_metadata", {}).get("memory_id", "unknown")

            logger.info("Job polling complete", extra={"memory_id": memory_id, "job_id": job_id})

            return f"{progress_log}\n\n✅ Job completed successfully!\nMemory ID: {memory_id}"

        except Exception as e:
            error_msg = f"Failed to poll job status: {str(e)}"
            logger.error(error_msg, extra={"error_type": type(e).__name__, "job_id": job_id})
            return f"✗ Error: {error_msg}"

    async def recall_memory(
        self,
        query: str,
        limit: int = 5,
    ) -> str:
        """Recall memories using semantic search."""
        try:
            dataset_id = await self._get_or_create_dataset()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.organization_id,
            }

            async def _do_recall():
                # Increased timeout to 300s for large datasets/slow Cognee queries
                async with httpx.AsyncClient(timeout=300.0) as client:
                    return await client.post(
                        f"{self.graph_api_url}/api/v1/graph/memory/recall",
                        headers=headers,
                        json={"query": query, "dataset_id": dataset_id, "limit": limit},
                    )

            response = await _retry_with_backoff(_do_recall)

            if response.status_code == 200:
                response_data = response.json()

                # Handle both response formats
                if isinstance(response_data, dict) and 'memories' in response_data:
                    results = response_data['memories']
                elif isinstance(response_data, list):
                    results = response_data
                else:
                    results = []

                if not results:
                    return f"No memories found for: '{query}'"

                formatted = f"Found {len(results)} memories:\n\n"
                for i, item in enumerate(results, 1):
                    content = item.get('content', item.get('text', 'N/A'))
                    formatted += f"{i}. {content}\n"
                    if item.get('metadata'):
                        formatted += f"   Metadata: {item['metadata']}\n"
                    if item.get('similarity_score'):
                        formatted += f"   Relevance: {item['similarity_score']:.2f}\n"
                    formatted += "\n"

                return formatted
            else:
                return f"✗ Error: HTTP {response.status_code}"

        except Exception as e:
            return f"✗ Error: {str(e)}"

    async def semantic_search(self, query: str, limit: int = 10) -> str:
        """Perform semantic search across knowledge graph."""
        try:
            dataset_id = await self._get_or_create_dataset()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.organization_id,
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.graph_api_url}/api/v1/graph/nodes/search/semantic",
                    headers=headers,
                    json={"query": query, "filters": {"dataset_ids": [dataset_id]}, "limit": limit},
                )

                if response.status_code == 200:
                    results = response.json()
                    if not results:
                        return f"No results for: '{query}'"

                    formatted = f"Search results for '{query}':\n\n"
                    for i, item in enumerate(results, 1):
                        content = item.get('content', item.get('text', 'N/A'))
                        formatted += f"{i}. {content}\n"
                        if item.get('similarity_score'):
                            formatted += f"   Relevance: {item['similarity_score']:.2f}\n"
                        if item.get('metadata'):
                            formatted += f"   Metadata: {item['metadata']}\n"
                        formatted += "\n"

                    return formatted
                else:
                    return f"✗ Error: HTTP {response.status_code}"

        except Exception as e:
            return f"✗ Error: {str(e)}"
