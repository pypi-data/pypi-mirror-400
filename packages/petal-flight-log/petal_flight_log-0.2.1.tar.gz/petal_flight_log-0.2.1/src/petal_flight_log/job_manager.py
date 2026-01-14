"""
Job Management System for Petal Flight Log

This module provides a comprehensive job management system with:
- Base Job class for all async operations
- Redis-based job state persistence
- Real-time progress tracking
- Cancellation support
- Job monitoring and cleanup
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict

from fastapi import WebSocket

from petal_app_manager.proxies import (
    MQTTProxy
)

from . import logger


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class JobProgress:
    """Job progress information"""
    percentage: float = 0.0  # 0-100
    current: int = 0
    total: int = 0
    message: str = ""
    rate_kbps: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class JobState:
    """Complete job state for persistence"""
    job_id: str
    job_type: str
    status: JobStatus
    progress: JobProgress
    created_at: float
    updated_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "progress": self.progress.to_dict() if isinstance(self.progress, JobProgress) else self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobState':
        """Create from dictionary"""
        progress_data = data.get("progress", {})
        progress = JobProgress(**progress_data) if isinstance(progress_data, dict) else JobProgress()
        
        return cls(
            job_id=data["job_id"],
            job_type=data["job_type"],
            status=JobStatus(data["status"]),
            progress=progress,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {})
        )


class Job(ABC):
    """
    Base class for all jobs in the flight log system.
    
    Features:
    - Automatic state persistence to Redis
    - Progress tracking
    - Cancellation support
    - Status monitoring
    - Error handling
    """
    
    def __init__(
        self,
        job_id: Optional[str] = None,
        redis_proxy=None,
        websocket_clients: Optional[Set[WebSocket]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a job.
        
        Args:
            job_id: Unique job identifier (auto-generated if not provided)
            redis_proxy: Redis proxy for state persistence
            websocket_clients: Set of WebSocket clients for broadcasting
            metadata: Additional metadata for the job
        """
        self.job_id = job_id or str(uuid.uuid4())
        self._redis_proxy = redis_proxy
        self._cancellation_event = asyncio.Event()
        self._completion_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        
        # Initialize state
        now = time.time()
        self._state = JobState(
            job_id=self.job_id,
            job_type=self.__class__.__name__,
            status=JobStatus.PENDING,
            progress=JobProgress(),
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        # Progress update callbacks
        self._progress_callbacks: List[Callable[[JobProgress], None]] = []
        
        # MQTT streaming attributes
        self._mqtt_proxy = None
        self._mqtt_device_id: Optional[str] = None
        self._mqtt_stream_id: Optional[str] = None
        self._mqtt_publish_rate_hz: float = 2.0  # Default 2 Hz
        self._mqtt_streaming_active: bool = False
        self._mqtt_stop_event = asyncio.Event()
        self._mqtt_publishing_task: Optional[asyncio.Task] = None
        self._mqtt_topic_base: Optional[str] = None
    
        self._websocket_clients = websocket_clients or set()

    @property
    def job_type(self) -> str:
        """Get job type"""
        return self._state.job_type
    
    @property
    def status(self) -> JobStatus:
        """Get current job status"""
        return self._state.status
    
    @property
    def progress(self) -> JobProgress:
        """Get current job progress"""
        return self._state.progress
    
    @property
    def is_running(self) -> bool:
        """Check if job is currently running"""
        return self._state.status == JobStatus.IN_PROGRESS
    
    @property
    def is_completed(self) -> bool:
        """Check if job is completed (success or cancelled or error)"""
        return self._state.status in [JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.ERROR]
    
    @property
    def is_cancelled(self) -> bool:
        """Check if job was cancelled"""
        return self._cancellation_event.is_set()
    
    def get_state(self) -> JobState:
        """Get current job state"""
        return self._state
    
    def add_progress_callback(self, callback: Callable[[JobProgress], None]):
        """Add a callback to be called on progress updates"""
        self._progress_callbacks.append(callback)
    
    async def _save_state(self):
        """Save job state to Redis"""
        if self._redis_proxy:
            try:
                redis_key = f"job:{self.job_id}"
                state_json = json.dumps(self._state.to_dict())
                await self._redis_proxy.set(redis_key, state_json, ex=86400)  # 24 hour expiry
            except Exception as e:
                logger.error(f"Failed to save job state for {self.job_id}: {e}")
    
    async def _update_status(self, status: JobStatus, error_message: Optional[str] = None):
        """Update job status and persist"""
        self._state.status = status
        self._state.updated_at = time.time()
        
        if error_message:
            self._state.error_message = error_message
        
        if status in [JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.ERROR]:
            self._state.completed_at = time.time()
            self._completion_event.set()
        
        await self._save_state()
    
    async def _update_progress(
        self,
        percentage: Optional[float] = None,
        current: Optional[int] = None,
        total: Optional[int] = None,
        message: Optional[str] = None,
        rate_kbps: Optional[float] = None
    ):
        """Update job progress and persist"""
        if percentage is not None:
            self._state.progress.percentage = min(100.0, max(0.0, percentage))
        if current is not None:
            self._state.progress.current = current
        if total is not None:
            self._state.progress.total = total
        if message is not None:
            self._state.progress.message = message
        if rate_kbps is not None:
            self._state.progress.rate_kbps = rate_kbps
        
        self._state.updated_at = time.time()
        await self._save_state()
        
        # Notify callbacks
        for callback in self._progress_callbacks:
            try:
                callback(self._state.progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def start(self) -> asyncio.Task:
        """
        Start the job asynchronously.
        
        Returns:
            The asyncio Task running the job
        """
        if self._task and not self._task.done():
            raise RuntimeError(f"Job {self.job_id} is already running")
        
        if self.is_completed:
            raise RuntimeError(f"Job {self.job_id} has already completed with status {self.status}")

        await self._update_status(JobStatus.IN_PROGRESS)
        self._task = asyncio.create_task(self._run_wrapper(), name=f"job_{self.job_id}")
        return self._task
    
    async def _run_wrapper(self):
        """Wrapper around the main run method to handle errors and state updates"""
        try:
            logger.info(f"Starting job {self.job_id} ({self.job_type})")
            await self.run()
            
            if not self.is_cancelled:
                await self._update_status(JobStatus.COMPLETED)
                await self._update_progress(percentage=100.0, message="Completed successfully")
                logger.info(f"Job {self.job_id} completed successfully")
        except asyncio.CancelledError:
            logger.info(f"Job {self.job_id} was cancelled")
            await self._update_status(JobStatus.CANCELLED)
            raise
        except Exception as e:
            error_msg = f"Job failed: {str(e)}"
            logger.error(f"Job {self.job_id} failed: {e}", exc_info=True)
            await self._update_status(JobStatus.ERROR, error_message=error_msg)
            raise
    
    @abstractmethod
    async def run(self):
        """
        Main job execution method. Must be implemented by subclasses.
        
        This method should:
        - Check self.is_cancelled periodically
        - Call self._update_progress() to report progress
        - Raise exceptions on errors
        """
        pass
    
    async def cancel(self) -> bool:
        """
        Cancel the job.
        
        Returns:
            True if cancellation was successful, False otherwise
        """
        if self.is_completed:
            logger.warning(f"Cannot cancel job {self.job_id}: already completed with status {self.status}")
            return False
        
        logger.info(f"Cancelling job {self.job_id}")
        self._cancellation_event.set()
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self._update_status(JobStatus.CANCELLED)
        return True
    
    async def wait_for_completion(self, timeout: Optional[float] = None) -> JobStatus:
        """
        Wait for job to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Final job status
        """
        try:
            await asyncio.wait_for(self._completion_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for job {self.job_id} to complete")
        
        return self.status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary representation"""
        return self._state.to_dict()
    
    async def subscribe_to_progress(
        self, 
        mqtt_proxy: 'MQTTProxy',  # Forward reference to avoid circular import
        mqtt_device_id: str, 
        stream_id: str, 
        mqtt_topic: str, 
        rate_hz: float = 2.0
    ) -> None:
        """
        Subscribe to job progress updates via MQTT publishing loop.
        
        Args:
            mqtt_proxy: MQTTProxy instance for publishing
            mqtt_device_id: Device ID for MQTT messages
            stream_id: Stream identifier for this subscription
            mqtt_topic_base: MQTT topic/command to publish to
            rate_hz: Publishing rate in Hz (default 2.0)
        """
        if self._mqtt_streaming_active:
            logger.info(f"Job {self.job_id} already streaming, updating rate to {rate_hz} Hz")
            self._mqtt_publish_rate_hz = rate_hz
            return
        
        self._mqtt_proxy = mqtt_proxy
        self._mqtt_device_id = mqtt_device_id
        self._mqtt_stream_id = stream_id
        self._mqtt_topic = mqtt_topic
        self._mqtt_publish_rate_hz = rate_hz
        self._mqtt_streaming_active = True
        self._mqtt_stop_event.clear()
        
        # Create the publishing task
        try:
            self._mqtt_publishing_task = asyncio.create_task(self._mqtt_publishing_loop())
            logger.info(f"Started MQTT streaming for job {self.job_id} at {rate_hz} Hz to {self._mqtt_topic}")
        except Exception as e:
            logger.error(f"Failed to create MQTT publishing loop task for job {self.job_id}: {e}")
            self._mqtt_streaming_active = False
            raise
    
    async def unsubscribe_from_progress(self) -> None:
        """Stop MQTT progress streaming."""
        if not self._mqtt_streaming_active:
            return
        
        logger.info(f"Stopping MQTT stream for job {self.job_id}")
        self._mqtt_streaming_active = False
        self._mqtt_stop_event.set()
        
        # Cancel publishing task
        if self._mqtt_publishing_task and not self._mqtt_publishing_task.done():
            self._mqtt_publishing_task.cancel()
            try:
                await self._mqtt_publishing_task
            except asyncio.CancelledError:
                pass
        
        self._mqtt_publishing_task = None
    
    async def _mqtt_publishing_loop(self) -> None:
        """Main MQTT publishing loop that sends progress updates at the specified rate."""
        from petal_app_manager.models import MQTTMessage
        from pydantic import ValidationError
        from .data_model import SubscribeJobStreamPublishResponse
        
        interval = 1.0 / self._mqtt_publish_rate_hz
        
        try:
            while not self._mqtt_stop_event.is_set() and self._mqtt_streaming_active and not self.is_completed:
                # Get current progress state (always returns Dict[str, Any])
                progress_data: Dict[str, Any] = self._get_mqtt_progress_data()
                
                # Only publish if we have valid data (not empty dict)
                if progress_data:
                    # Validate progress_data against the expected payload model
                    # This ensures subclasses are returning properly structured data
                    try:
                        self._validate_progress_payload(progress_data)
                    except ValidationError as e:
                        logger.error(f"Invalid progress data structure for job {self.job_id}: {e}")
                        continue
                    
                    payload = SubscribeJobStreamPublishResponse(
                        published_stream_id=self._mqtt_stream_id,
                        stream_payload=progress_data
                    )

                    mqtt_message_dict: Dict[str, Any] = {
                        "messageId": str(uuid.uuid4()),
                        "command": f"{self._mqtt_topic}",
                        "timestamp": datetime.now().isoformat(),
                        "data": payload.model_dump(),
                        "waitResponse": False
                    }
                    
                    try:
                        # Validate and publish using MQTTMessage model
                        mqtt_message = MQTTMessage(**mqtt_message_dict)
                        await self._mqtt_proxy.publish_message(payload=mqtt_message.model_dump())
                    except Exception as e:
                        logger.error(f"Error publishing MQTT progress for job {self.job_id}: {e}")
                
                    # Also broadcast to WebSocket clients
                    await self._broadcast_to_websockets(progress_data)

                # Wait for next publish interval
                await asyncio.sleep(interval)
            
            # Send final completion message if job is completed
            if self.is_completed:
                final_data: Dict[str, Any] = self._get_mqtt_progress_data()
                if final_data:
                    # Validate final completion data
                    try:
                        self._validate_progress_payload(final_data)
                    except ValidationError as e:
                        logger.error(f"Invalid final progress data structure for job {self.job_id}: {e}")
                    else:
                        mqtt_message_dict: Dict[str, Any] = {
                            "messageId": str(uuid.uuid4()),
                            "command": f"{self._mqtt_topic_base}/{self.job_id}",
                            "timestamp": datetime.now().isoformat(),
                            "data": final_data,
                            "waitResponse": False
                        }   
                        mqtt_message = MQTTMessage(**mqtt_message_dict)
                        await self._mqtt_proxy.publish_message(payload=mqtt_message.model_dump())
                
        except asyncio.CancelledError:
            logger.info(f"MQTT publishing loop for job {self.job_id} cancelled")
        except Exception as e:
            logger.error(f"Error in MQTT publishing loop for job {self.job_id}: {e}")
        finally:
            self._mqtt_streaming_active = False
    
    def _get_payload_model(self) -> type:
        """
        Get the expected Pydantic model for this job's progress payload.
        Override in subclasses to specify custom payload models.
        
        Returns:
            The Pydantic model class for validating progress data
        """
        from .data_model import JobProgressUpdatePayload
        return JobProgressUpdatePayload
    
    def _validate_progress_payload(self, progress_data: Dict[str, Any]) -> None:
        """
        Validate that progress_data conforms to the expected payload model.
        
        Args:
            progress_data: The progress data dictionary to validate
            
        Raises:
            ValidationError: If the data doesn't match the expected model
        """
        payload_model = self._get_payload_model()
        # This will raise ValidationError if data is invalid
        payload_model(**progress_data)
    
    def _get_mqtt_progress_data(self) -> Dict[str, Any]:
        """
        Get MQTT progress data. Override in subclasses for custom payload format.
        
        Returns:
            Dictionary with validated progress data from Pydantic model
        """
        if not self._mqtt_device_id:
            logger.warning(f"Job {self.job_id}: Cannot generate MQTT progress data without device_id")
            return {}
        
        # Import here to avoid circular dependency
        from .data_model import JobProgressUpdatePayload
        
        payload = JobProgressUpdatePayload(
            job_id=self.job_id,
            machine_id=self._mqtt_device_id,
            stream_id=self._mqtt_stream_id,
            job_type=self.job_type,
            status=self.status.value,
            progress=self._state.progress.percentage,
            rate_kbps=self._state.progress.rate_kbps,
            message=self._state.progress.message or "",
            completed=self.is_completed
        )
        return payload.model_dump()

    async def _broadcast_to_websockets(self, progress_data: Dict[str, Any]) -> None:
        """Broadcast progress to WebSocket clients"""
        if not self._websocket_clients:
            return
        
        for ws in list(self._websocket_clients):
            try:
                await ws.send_json(progress_data)
            except Exception:
                logger.warning(f"Failed to send progress update to WebSocket client: {ws}")
                self._websocket_clients.discard(ws)
    

class JobMonitor:
    """
    Centralized job monitoring service - fully Redis-based.
    
    Features:
    - All jobs stored in Redis (no in-memory cache)
    - Track active and completed jobs
    - Query jobs by status or type
    - Cleanup completed jobs
    
    Design:
    - Redis is the single source of truth
    - Job instances manage their own state
    - Monitor only tracks job IDs in registry
    """
    
    def __init__(self, redis_proxy):
        """
        Initialize job monitor.
        
        Args:
            redis_proxy: Redis proxy for state persistence
        """
        self._redis_proxy = redis_proxy
        self._lock = asyncio.Lock()
        # Keep track of active job instances (running jobs only)
        self._active_jobs: Dict[str, Job] = {}
    
    async def register_job(self, job: Job):
        """Register a job with the monitor and store in Redis"""
        async with self._lock:
            # Store job instance for active management
            self._active_jobs[job.job_id] = job
            # Save state to Redis (job:* key will be found by scan)
            await job._save_state()
            logger.debug(f"Registered job {job.job_id} ({job.job_type})")
    
    async def unregister_job(self, job_id: str):
        """Remove job from active tracking (job state remains in Redis)"""
        async with self._lock:
            if job_id in self._active_jobs:
                del self._active_jobs[job_id]
                logger.debug(f"Unregistered active job {job_id}")
    
    def get_active_job(self, job_id: str) -> Optional[Job]:
        """Get an active job instance (in-memory, for cancellation/control)"""
        return self._active_jobs.get(job_id)
    
    async def get_job_state(self, job_id: str) -> Optional[JobState]:
        """
        Get job state, loading from Redis if not in memory.
        
        Args:
            job_id: Job identifier
            
        Returns:
            JobState if found, None otherwise
        """
        # Check active jobs first
        job = self.get_active_job(job_id)
        if job:
            return job.get_state()
        
        # Try loading from Redis
        try:
            redis_key = f"job:{job_id}"
            state_json = await self._redis_proxy.get(redis_key)
            if state_json:
                state_data = json.loads(state_json)
                return JobState.from_dict(state_data)
        except Exception as e:
            logger.error(f"Failed to load job state for {job_id}: {e}")
        
        return None
    
    async def get_all_job_states_from_redis(self) -> List[JobState]:
        """
        Get all job states from Redis by scanning for job:* keys.
        
        Returns:
            List of JobState objects from Redis
        """
        try:
            # Scan for all job keys in Redis
            job_keys = await self._redis_proxy.scan_keys("job:*")
            job_states = []
            
            for redis_key in job_keys:
                try:
                    state_json = await self._redis_proxy.get(redis_key)
                    if state_json:
                        state_data = json.loads(state_json)
                        job_state = JobState.from_dict(state_data)
                        job_states.append(job_state)
                except Exception as e:
                    logger.error(f"Failed to load job state from key {redis_key}: {e}")
            
            return job_states
        except Exception as e:
            logger.error(f"Failed to get job states from Redis: {e}")
            return []
    
    async def get_all_job_states(self) -> List[JobState]:
        """Get all job states from Redis"""
        return await self.get_all_job_states_from_redis()
    
    async def get_jobs_by_status(self, status: JobStatus) -> List[JobState]:
        """Get all jobs with a specific status from Redis"""
        all_states = await self.get_all_job_states_from_redis()
        return [state for state in all_states if state.status == status]
    
    async def get_jobs_by_type(self, job_type: str) -> List[JobState]:
        """Get all jobs of a specific type from Redis"""
        all_states = await self.get_all_job_states_from_redis()
        return [state for state in all_states if state.job_type == job_type]
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        # Check if job is actively running (has instance)
        active_job = self.get_active_job(job_id)
        if active_job:
            return await active_job.cancel()
        
        # Check Redis for job state
        state = await self.get_job_state(job_id)
        if not state:
            logger.warning(f"Job {job_id} not found")
            return False
        
        # Cannot cancel already completed jobs
        if state.status in [JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.ERROR]:
            logger.warning(f"Cannot cancel job {job_id}: already completed with status {state.status.value}")
            return False
        
        # Job exists in Redis but not active - mark as cancelled
        logger.warning(f"Job {job_id} found in Redis but not active - marking as cancelled")
        state.status = JobStatus.CANCELLED
        state.completed_at = time.time()
        state.updated_at = time.time()
        redis_key = f"job:{job_id}"
        await self._redis_proxy.set(redis_key, json.dumps(state.to_dict()), ex=86400)
        return True
    
    async def cleanup_completed_jobs(self, max_age_seconds: float = 3600):
        """
        Clean up completed jobs older than max_age_seconds from Redis.
        
        Args:
            max_age_seconds: Maximum age of completed jobs to keep
        """
        now = time.time()
        to_remove = []
        
        # Get all job states from Redis
        all_states = await self.get_all_job_states_from_redis()
        
        for state in all_states:
            if state.status in [JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.ERROR]:
                completed_at = state.completed_at or state.updated_at
                age = now - completed_at
                if age > max_age_seconds:
                    to_remove.append(state.job_id)
        
        # Remove old jobs from Redis
        for job_id in to_remove:
            # Remove from active jobs if present
            await self.unregister_job(job_id)
            # Remove from Redis
            redis_key = f"job:{job_id}"
            await self._redis_proxy.delete(redis_key)
            logger.debug(f"Cleaned up job {job_id}")
        
        return len(to_remove)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get job statistics from Redis (all jobs)"""
        stats = {
            "total_jobs": 0,
            "active_jobs": len(self._active_jobs),
            "by_status": {},
            "by_type": {}
        }
        
        # Get all job states from Redis
        all_states = await self.get_all_job_states_from_redis()
        
        for state in all_states:
            stats["total_jobs"] += 1
            status_str = state.status.value
            stats["by_status"][status_str] = stats["by_status"].get(status_str, 0) + 1
            stats["by_type"][state.job_type] = stats["by_type"].get(state.job_type, 0) + 1
        
        return stats
