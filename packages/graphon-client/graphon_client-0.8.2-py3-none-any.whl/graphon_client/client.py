"""Async Graphon client using httpx."""

import asyncio
import logging
import os
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = 60.0 * 35

# New BFF API URL
API_BASE_URL = "https://api-frontend-485250924682.us-central1.run.app"
# API_BASE_URL = "http://localhost:8081"


def _create_fake_jwt(user_id: str = "test-user-local") -> str:
    """
    Create a fake JWT token for local testing.

    Uses HS256 algorithm with a test secret. The local validation function
    decodes without verification, so the signature doesn't matter.

    Args:
        user_id: User ID to include in 'sub' claim

    Returns:
        str: JWT token string (signed with test secret)
    """
    try:
        from jose import jwt
    except ImportError:
        raise ImportError(
            "python-jose is required for localhost testing. "
            "Install it with: pip install python-jose"
        )

    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour expiry
    }

    # Sign with HS256 and a test secret (doesn't matter since validation ignores signature)
    token = jwt.encode(payload, key="test-secret-key", algorithm="HS256")
    return token


# ============================================================================
# Response Models
# ============================================================================


@dataclass
class FileObject:
    """Represents a file in the Graphon system."""

    file_id: str
    file_name: str
    file_type: str
    processing_status: str  # UNPROCESSED, PROCESSING, SUCCESS, FAILURE
    error_message: Optional[str] = None


@dataclass
class FileDetail:
    """Detailed file information from the API."""

    file_id: str
    user_id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    file_gcs_location: str
    processing_status: str
    processing_start_time: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class GroupDetail:
    """Detailed group information from the API."""

    group_id: str
    user_id: str
    group_name: str
    file_ids: List[str]
    graph_status: str  # pending, building, ready, failed
    graph_gcs_location: Optional[str] = None
    graph_job_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class GroupListItem:
    """Group item in list response (summary view)."""

    group_id: str
    group_name: str
    file_count: int
    graph_status: str
    created_at: str


@dataclass
class QueryResponseLegacy:
    """Response from querying a group's unified graph (legacy format).

    .. deprecated::
        This response model is deprecated and will be removed in a future version.
        Use :class:`QueryResponse` instead, which provides a cleaner sources structure.
    """

    answer: str
    sources: List[Dict[str, Any]]
    attention_nodes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class QueryResponse:
    """Response from querying a group's unified graph.

    Sources are returned as a dictionary mapping citation keys (e.g., "[1]", "[2]")
    to AttentionNodeV2 objects that include source metadata, relevance scores,
    and citation flags.

    Attributes:
        answer: The generated answer with inline citation markers like [1], [2].
        sources: Dictionary mapping citation keys to source metadata including:
            - source: Object with node_type, file_id, and type-specific fields
            - score: Relevance score (0.0 to 1.0)
            - is_cited: Whether this source was cited in the answer
    """

    answer: str
    sources: Dict[str, Dict[str, Any]]


# ============================================================================
# Graphon Client
# ============================================================================


class GraphonClient:
    """A client library for interacting with the Graphon API."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the client with an API key.

        Args:
            api_key: Your Graphon API key (get from dashboard)
            base_url: Optional custom base URL (defaults to production API)
        """
        self.api_base_url = (base_url or API_BASE_URL).rstrip("/")

        # For localhost testing, use fake JWT instead of API key
        if "localhost" in self.api_base_url:
            fake_token = _create_fake_jwt()
            self._headers = {
                "Authorization": f"Bearer {fake_token}",
                "Content-Type": "application/json",
            }
            logger.info("Using fake JWT for localhost testing")
        else:
            self._headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _determine_file_type(self, filename: str) -> str:
        """
        Determine file type from extension.

        Args:
            filename: Name of the file

        Returns:
            One of: 'video', 'document', 'image'
        """
        ext = filename.split(".")[-1].lower()

        # Video extensions
        if ext in ["mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "m4v", "3gp"]:
            return "video"

        # Document extensions
        if ext in ["pdf", "docx", "pptx", "xlsx", "txt", "md"]:
            return "document"

        # Image extensions
        if ext in ["png", "jpg", "jpeg"]:
            return "image"

        # Default to document
        return "document"

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = (
                    error_data.get("detail")
                    or error_data.get("message")
                    or str(error_data)
                )
            except Exception:
                error_msg = response.text or f"HTTP {response.status_code}"

            raise Exception(f"API error ({response.status_code}): {error_msg}")

        return response.json()

    # ========================================================================
    # File Operations
    # ========================================================================

    async def get_signed_upload_url(
        self, file_name: str, file_type: str, file_size_bytes: int
    ) -> Dict[str, Any]:
        """
        Get a signed URL for uploading a file to GCS.

        Args:
            file_name: Name of the file
            file_type: Type of file ('video', 'document', or 'image')
            file_size_bytes: Size of the file in bytes

        Returns:
            Dict with keys: file_id, upload_url, upload_fields, expires_at
        """
        params = {
            "file_name": file_name,
            "file_type": file_type,
            "file_size_bytes": str(file_size_bytes),
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.api_base_url}/v1/files/get-signed-upload-url",
                params=params,
                headers=self._headers,
            )
            return await self._handle_response(response)

    async def upload_to_gcs(
        self, file_path: str, upload_url: str, upload_fields: Dict[str, str]
    ) -> None:
        """
        Upload a file to GCS using a signed URL.

        Args:
            file_path: Local path to the file
            upload_url: Signed URL from get_signed_upload_url
            upload_fields: Form fields from get_signed_upload_url
        """
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Create multipart form data
        files = {"file": (os.path.basename(file_path), file_content)}

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                upload_url,
                data=upload_fields,
                files=files,
            )

            # GCS returns 204 No Content on success
            if response.status_code not in [200, 204]:
                raise Exception(
                    f"GCS upload failed (status {response.status_code}): {response.text}"
                )

    async def _process_file(self, file_id: str) -> Dict[str, Any]:
        """
        Start processing an uploaded file.

        Args:
            file_id: The file ID returned from get_signed_upload_url

        Returns:
            Dict with status information
        """
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{self.api_base_url}/v1/files/{file_id}/process",
                headers=self._headers,
            )
            return await self._handle_response(response)

    async def _get_file_status(self, file_id: str) -> FileDetail:
        """
        Get the current status of a file.

        Args:
            file_id: The file ID

        Returns:
            FileDetail object with current status
        """
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.api_base_url}/v1/files/{file_id}",
                headers=self._headers,
            )
            data = await self._handle_response(response)
            return FileDetail(**data)

    async def list_files(
        self, status_filter: Optional[str] = None, file_type: Optional[str] = None
    ) -> List[FileDetail]:
        """
        List all files for the authenticated user.

        Args:
            status_filter: Optional filter by processing status
            file_type: Optional filter by file type

        Returns:
            List of FileDetail objects
        """
        params = {}
        if status_filter:
            params["status"] = status_filter
        if file_type:
            params["file_type"] = file_type

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.api_base_url}/v1/files",
                params=params,
                headers=self._headers,
            )
            data = await self._handle_response(response)
            return [FileDetail(**f) for f in data.get("files", [])]

    # ========================================================================
    # Polling Methods
    # ========================================================================

    async def poll_file_until_complete(
        self,
        file_id: str,
        timeout: int = 1800,
        poll_interval: int = 3,
        on_progress: Optional[callable] = None,
    ) -> FileDetail:
        """
        Poll a file until processing completes (SUCCESS or FAILURE).

        Args:
            file_id: The file ID to poll
            timeout: Maximum time to wait in seconds (default: 30 minutes)
            poll_interval: Time between polls in seconds (default: 3)
            on_progress: Optional callback(status: str) called on each poll

        Returns:
            FileDetail object with final status

        Raises:
            Exception: If processing fails or times out
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            file = await self._get_file_status(file_id)

            if on_progress:
                on_progress(file.processing_status)

            if file.processing_status == "SUCCESS":
                return file

            if file.processing_status == "FAILURE":
                raise Exception(
                    f"File {file_id} ({file.file_name}) processing failed: {file.error_message or 'Unknown error'}"
                )

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise Exception(
                    f"File {file_id} ({file.file_name}) processing timed out after {timeout} seconds"
                )

            await asyncio.sleep(poll_interval)

    # ========================================================================
    # High-Level Upload & Process
    # ========================================================================

    async def upload_and_process_files(
        self,
        file_paths: List[str],
        poll_until_complete: bool = True,
        timeout: int = 1800,
        poll_interval: int = 3,
        on_progress: Optional[callable] = None,
    ) -> List[FileObject]:
        """
        Upload and process multiple files.

        This is the main method for getting files into Graphon:
        1. Generates signed URLs for all files
        2. Uploads all files to GCS concurrently
        3. Triggers processing for all files
        4. Optionally waits for processing to complete

        Args:
            file_paths: List of local file paths to upload
            poll_until_complete: If True, waits for all files to finish processing
            timeout: Maximum time to wait per file in seconds (default: 30 minutes)
            poll_interval: Time between status checks in seconds (default: 3)
            on_progress: Optional callback(step: str, current: int, total: int) for progress updates

        Returns:
            List of FileObject with file_id, file_name, processing_status, and error_message.
            processing_status will be "SUCCESS", "FAILURE", or "PROCESSING"
            error_message will contain details if status is "FAILURE"

        Raises:
            Exception: If any file fails to upload (but not if processing fails when poll_until_complete=True)
        """
        if not file_paths:
            return []

        total_files = len(file_paths)
        logger.info(f"Starting upload and process for {total_files} files")

        # Step 1: Generate signed URLs for all files
        if on_progress:
            on_progress("generating_urls", 0, total_files)

        upload_infos = []
        for i, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            file_type = self._determine_file_type(file_name)
            file_size = os.path.getsize(file_path)

            logger.info(
                f"Requesting signed URL for {file_name} (type={file_type}, size={file_size})"
            )
            info = await self.get_signed_upload_url(file_name, file_type, file_size)
            upload_infos.append({"file_path": file_path, "info": info})

            if on_progress:
                on_progress("generating_urls", i + 1, total_files)

        logger.info(f"Generated {len(upload_infos)} signed URLs")

        # Step 2: Upload all files to GCS concurrently
        if on_progress:
            on_progress("uploading_files", 0, total_files)

        semaphore = asyncio.Semaphore(5)  # Limit concurrent uploads

        async def upload_one(idx: int, upload_info: Dict) -> None:
            async with semaphore:
                file_path = upload_info["file_path"]
                info = upload_info["info"]
                logger.info(
                    f"Uploading {os.path.basename(file_path)} (file_id={info['file_id']})"
                )
                await self.upload_to_gcs(
                    file_path, info["upload_url"], info["upload_fields"]
                )
                if on_progress:
                    on_progress("uploading_files", idx + 1, total_files)

        await asyncio.gather(
            *(upload_one(i, info) for i, info in enumerate(upload_infos))
        )

        logger.info("All files uploaded to GCS")

        # Step 3: Trigger processing for all files
        if on_progress:
            on_progress("processing_files", 0, total_files)

        file_ids = [info["info"]["file_id"] for info in upload_infos]

        for i, file_id in enumerate(file_ids):
            logger.info(f"Triggering processing for file_id={file_id}")
            await self._process_file(file_id)
            if on_progress:
                on_progress("processing_files", i + 1, total_files)

        logger.info("All processing jobs triggered")

        # Step 4: Optionally wait for processing to complete
        if poll_until_complete:
            if on_progress:
                on_progress("waiting_for_processing", 0, total_files)

            async def poll_one_safe(
                idx: int, file_id: str, file_name: str
            ) -> FileObject:
                """Poll a single file and return FileObject with success or error status."""
                try:
                    logger.info(f"Polling file_id={file_id} for completion")
                    result = await self.poll_file_until_complete(
                        file_id,
                        timeout=timeout,
                        poll_interval=poll_interval,
                        on_progress=lambda status: logger.debug(
                            f"File {file_id} status: {status}"
                        ),
                    )
                    if on_progress:
                        on_progress("waiting_for_processing", idx + 1, total_files)

                    return FileObject(
                        file_id=result.file_id,
                        file_name=result.file_name,
                        file_type=result.file_type,
                        processing_status="SUCCESS",
                        error_message=None,
                    )
                except Exception as e:
                    # Capture error and continue processing other files
                    logger.error(f"File {file_id} ({file_name}) failed: {str(e)}")
                    if on_progress:
                        on_progress("waiting_for_processing", idx + 1, total_files)

                    return FileObject(
                        file_id=file_id,
                        file_name=file_name,
                        file_type=self._determine_file_type(file_name),
                        processing_status="FAILURE",
                        error_message=str(e),
                    )

            # Poll all files and collect results (with error handling per file)
            file_objects = await asyncio.gather(
                *(
                    poll_one_safe(
                        i, fid, os.path.basename(upload_infos[i]["file_path"])
                    )
                    for i, fid in enumerate(file_ids)
                )
            )

            success_count = sum(
                1 for f in file_objects if f.processing_status == "SUCCESS"
            )
            failure_count = sum(
                1 for f in file_objects if f.processing_status == "FAILURE"
            )
            logger.info(
                f"Processing complete: {success_count} succeeded, {failure_count} failed"
            )

            return list(file_objects)
        else:
            # Return FileObject list with PROCESSING status
            return [
                FileObject(
                    file_id=info["info"]["file_id"],
                    file_name=os.path.basename(info["file_path"]),
                    file_type=self._determine_file_type(
                        os.path.basename(info["file_path"])
                    ),
                    processing_status="PROCESSING",
                    error_message=None,
                )
                for info in upload_infos
            ]

    # ========================================================================
    # Group Operations
    # ========================================================================

    async def create_group(
        self,
        file_ids: List[str],
        group_name: str,
        wait_for_ready: bool = False,
        timeout: int = 3600,
        poll_interval: int = 5,
        on_progress: Optional[callable] = None,
    ) -> str:
        """
        Create a group from processed files.

        Args:
            file_ids: List of file IDs (must all have processing_status=SUCCESS)
            group_name: Name for the group
            wait_for_ready: If True, waits for graph building to complete
            timeout: Maximum time to wait for graph building in seconds (default: 1 hour)
            poll_interval: Time between status checks in seconds (default: 5)
            on_progress: Optional callback(status: str) for progress updates

        Returns:
            group_id

        Raises:
            Exception: If group creation or graph building fails
        """
        logger.info(
            f"Creating group '{group_name}' with {len(file_ids)} files: {file_ids}"
        )

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{self.api_base_url}/v1/groups",
                headers=self._headers,
                json={"group_name": group_name, "file_ids": file_ids},
            )
            data = await self._handle_response(response)

        group_id = data["group_id"]
        logger.info(f"Group created: {group_id}, status: {data.get('status')}")

        if wait_for_ready:
            logger.info(f"Waiting for group {group_id} to be ready...")
            await self.poll_group_until_ready(
                group_id,
                timeout=timeout,
                poll_interval=poll_interval,
                on_progress=on_progress,
            )
            logger.info(f"Group {group_id} is ready")

        return group_id

    async def get_group_status(self, group_id: str) -> GroupDetail:
        """
        Get the current status of a group.

        Args:
            group_id: The group ID

        Returns:
            GroupDetail object with current status
        """
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.api_base_url}/v1/groups/{group_id}",
                headers=self._headers,
            )
            data = await self._handle_response(response)
            return GroupDetail(**data)

    async def poll_group_until_ready(
        self,
        group_id: str,
        timeout: int = 3600,
        poll_interval: int = 5,
        on_progress: Optional[callable] = None,
    ) -> GroupDetail:
        """
        Poll a group until graph building completes (ready or failed).

        Args:
            group_id: The group ID to poll
            timeout: Maximum time to wait in seconds (default: 1 hour)
            poll_interval: Time between polls in seconds (default: 5)
            on_progress: Optional callback(status: str) called on each poll

        Returns:
            GroupDetail object with final status

        Raises:
            Exception: If graph building fails or times out
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            group = await self.get_group_status(group_id)

            if on_progress:
                on_progress(group.graph_status)

            if group.graph_status == "ready":
                return group

            if group.graph_status == "failed":
                error_msg = (
                    group.metadata.get("error_message")
                    if group.metadata
                    else "Unknown error"
                )
                raise Exception(f"Graph building failed: {error_msg}")

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise Exception(f"Graph building timed out after {timeout} seconds")

            await asyncio.sleep(poll_interval)

    async def list_groups(self) -> List[GroupListItem]:
        """
        List all groups for the authenticated user.

        Returns:
            List of GroupListItem objects (summary view)
        """
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.api_base_url}/v1/groups",
                headers=self._headers,
            )
            data = await self._handle_response(response)
            return [GroupListItem(**g) for g in data.get("groups", [])]

    async def query_group(
        self,
        group_id: str,
        query: str,
        return_source_data: bool = False,
        web_search: bool = False,
        reasoning_effort: Literal["low", "high", "ultra"] = "low",
    ) -> QueryResponse:
        """
        Query a group's unified knowledge graph.

        This is the recommended method for querying graphs. It returns a cleaner
        response structure where sources are mapped by citation keys.

        Args:
            group_id: The group ID to query
            query: Natural language query
            return_source_data: If True, include text content for documents and
                               time-limited signed URLs for images/videos in the response
            web_search: If True, augment the answer with web search results
            reasoning_effort: Level of reasoning effort for the query.
                             "low" (default): Faster response, skips deep re-analysis of sources.
                             "high": Full re-analysis of sources with Qwen/Molmo2.
                             "ultra": Maximum accuracy using Gemini 2.5 Pro for all sources.

        Returns:
            QueryResponse with:
                - answer: Generated answer with citation markers like [1], [2]
                - sources: Dictionary mapping citation keys to source metadata

        Raises:
            Exception: If group is not ready or query fails

        Example:
            >>> response = await client.query_group(group_id, "What are the main topics?")
            >>> print(response.answer)
            "The main topics include AI [1] and machine learning [2]..."
            >>> for key, source in response.sources.items():
            ...     print(f"{key}: {source['source']['node_type']}")
            "[1]": "document"
            "[2]": "video"
        """
        logger.info(f"Querying group {group_id}: {query}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{self.api_base_url}/v1/groups/{group_id}/query",
                headers=self._headers,
                json={
                    "query": query,
                    "return_source_data": return_source_data,
                    "web_search": web_search,
                    "reasoning_effort": reasoning_effort,
                },
            )
            data = await self._handle_response(response)
            return QueryResponse(
                answer=data.get("answer", ""),
                sources=data.get("sources", {}),
            )

    async def query_group_legacy(
        self,
        group_id: str,
        query: str,
        return_source_data: bool = False,
    ) -> QueryResponseLegacy:
        """
        Query a group's unified knowledge graph (legacy endpoint).

        .. deprecated::
            This method is deprecated and will be removed in a future version.
            Use :meth:`query_group` instead, which provides a cleaner response structure.

        Args:
            group_id: The group ID to query
            query: Natural language query
            return_source_data: If True, include text content for documents and
                               time-limited signed URLs for images/videos in the response

        Returns:
            QueryResponseLegacy with answer, sources list, and attention_nodes

        Raises:
            Exception: If group is not ready or query fails
        """
        warnings.warn(
            "query_group_legacy() is deprecated and will be removed in a future version. "
            "Use query_group() instead for improved response structure.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.info(f"Querying group (legacy) {group_id}: {query}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{self.api_base_url}/v1/groups/{group_id}/query-legacy",
                headers=self._headers,
                json={
                    "query": query,
                    "return_source_data": return_source_data,
                },
            )
            data = await self._handle_response(response)
            return QueryResponseLegacy(
                answer=data.get("answer", ""),
                sources=data.get("sources", []),
                attention_nodes=data.get("attention_nodes", []),
            )

    # ========================================================================
    # Convenience Methods
    # ========================================================================

    async def upload_process_and_create_group(
        self,
        file_paths: List[str],
        group_name: str,
        on_progress: Optional[callable] = None,
    ) -> str:
        """
        One-shot method: Upload files, process them, and create a group.

        This is the simplest way to create a knowledge base from files.

        Args:
            file_paths: List of local file paths
            group_name: Name for the group
            on_progress: Optional callback(step: str, current: int, total: int)

        Returns:
            group_id

        Raises:
            Exception: If any step fails
        """
        # Upload and process files
        file_objects = await self.upload_and_process_files(
            file_paths, poll_until_complete=True, on_progress=on_progress
        )

        # Extract file IDs
        file_ids = [f.file_id for f in file_objects]

        # Create group and wait for it to be ready
        group_id = await self.create_group(
            file_ids,
            group_name,
            wait_for_ready=True,
            on_progress=lambda status: (
                on_progress("building_graph", 0, 1) if on_progress else None
            ),
        )

        return group_id
