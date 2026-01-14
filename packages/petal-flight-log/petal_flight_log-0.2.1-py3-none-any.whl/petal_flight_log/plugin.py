import uuid
import os
import re
from pathlib import Path
import json
from datetime import datetime, date, timezone
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Response
from pydantic_core import ValidationError
from pymavlink import mavutil, mavftp
from . import logger
import threading
import subprocess, yaml

from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action, websocket_action
from petal_app_manager.organization_manager import OrganizationManager, get_organization_manager
from petal_app_manager.proxies import (
    S3BucketProxy,
    MavLinkExternalProxy,
    MavLinkFTPProxy,
    RedisProxy,
    LocalDBProxy,
    CloudDBProxy,
    MQTTProxy,
)
from petal_app_manager.models import MQTTMessage

from .data_model import (
    GetFlightRecordsRequest,
    GetFlightRecordsResponse,
    GetExistingFlightRecordsResponse,
    FlightRecordMatch,
    ExistingFlightRecordMatch,
    RosbagFileRecord,
    UlogFileRecord,
    LeafFCRecord,
    PX4LogCompletedResponse,
    DeleteFlightRecordRequest,
    DeleteFlightRecordResponse,
    # S3 upload progress
    S3CompleteResponse,
    S3UploadResponse,
    ULogDownloadResponse,
    # sync tasks
    FlightRecordSyncStartResponse,
    StartFlightRecordSyncRequest, 
    StartFlightRecordSyncResponse,
    # Redis command payload
    RedisCommandPayload,
    RedisAckPayload,
    SaveLeafFCRecordRequest, 
    SaveLeafFCRecordResponse
)

# Import job management system
from .job_manager import JobMonitor, JobStatus, JobState
from .jobs import (
    S3UploadJob,
    ULogDownloadJobMAVLink,
    ULogDownloadJobMAVFTP,
    FlightRecordSyncJob
)

# WebSocket clients for progress updates
websocket_clients: Set[WebSocket] = set()

class MQTTCommands:

    # MQTT Command Topics (for legacy endpoints only)
    FETCH_FLIGHT_RECORDS_COMMAND = "fetch_flight_records"

    # Progress base topics (will be suffixed with /{job_id} for specific jobs)
    PX4_LOG_DOWNLOAD_PROGRESS_COMMAND = "log_download/progress"
    S3_UPLOAD_PROGRESS_COMMAND = "s3_upload/progress"
    FLIGHT_RECORD_SYNC_PROGRESS_COMMAND = "publish_sync_job_value_stream"

    # Cancel job topics (will be suffixed with /{job_id} for specific jobs)
    CANCEL_DOWNLOAD_MQTT_COMMAND = "cancel_log_download"
    CANCEL_S3_UPLOAD_MQTT_COMMAND = "cancel_s3_upload"
    CANCEL_SYNC_MQTT_COMMAND = "cancel_sync_job"

    # Check job status topics
    CHECK_DOWNLOAD_MQTT_COMMAND = "check_log_download"
    CHECK_S3_UPLOAD_MQTT_COMMAND = "check_s3_upload"
    CHECK_SYNC_MQTT_COMMAND = "check_sync_job"


class RedisChannels:

    # Redis Topics for QGC mission adapter communication
    REDIS_CMD_CHANNEL = "/petal/petal_flight_log/cmd"
    REDIS_ACK_CHANNEL = "/petal/petal_flight_log/ack"

class FlightLogPetal(Petal):
    name = "petal-flight-log"
    version = "1.0.0"
    use_mqtt_proxy = True  # Enable MQTT-aware startup

    def __init__(self):
        super().__init__()
        self._status_message = "Flight Log Petal initialized successfully"
        self._startup_time = None
        self._mqtt_proxy: Optional[MQTTProxy] = None
        self._redis_proxy: Optional[RedisProxy] = None
        self._loop = None
        
        # MQTT topic configuration
        self._command_handlers = None
        self.mqtt_subscription_id = None
        
        # Active subscription tracking
        self._active_handlers: Dict[str, Dict[str, Any]] = {}  # stream_name -> subscription_info
        self._registration_lock = threading.Lock()

        # Job monitoring system
        self._job_monitor: Optional[JobMonitor] = None

    def startup(self) -> None:
        """Called when the petal is started."""
        super().startup()
        self._startup_time = datetime.now()
        self._status_message = f"Flight Log Petal started at {self._startup_time.isoformat()}"
        logger.info(f"{self.name} petal started successfully")
        
        # Store proxy references (after inject_proxies has been called)
        self._mqtt_proxy: MQTTProxy = self._proxies.get("mqtt")
        self._redis_proxy: RedisProxy = self._proxies.get("redis")

        # Initialize job monitoring system
        self._job_monitor = JobMonitor(redis_proxy=self._redis_proxy)
        logger.info("Job monitoring system initialized")

    async def async_startup(self) -> None:
        """
        Called after startup to handle async operations like MQTT subscriptions.
        
        Note: The MQTT-aware startup logic (organization ID monitoring, event loop setup)
        is handled by the main application's _mqtt_aware_petal_startup function.
        This method will be called by that function after organization ID is available.
        """
        # This method is intentionally simple - the main app handles:
        # 1. Setting self._loop
        # 2. Waiting for organization ID
        # 3. Calling self._setup_mqtt_topics() when ready
        # 4. Starting organization ID monitoring if needed
        
        logger.info("Flight Log Petal async_startup completed (MQTT setup handled by main app)")
        self._setup_redis_command_listener()
        pass

    async def _setup_mqtt_topics(self):
        """Set up MQTT topics and handlers once organization ID is available."""
        
        # Initialize command handlers registry
        self._command_handlers = self._setup_command_handlers()
        
        # Single handler registration - the master handler will dispatch based on command
        self.mqtt_subscription_id = self._mqtt_proxy.register_handler(self._master_command_handler)
        if self.mqtt_subscription_id is None:
            logger.error("Failed to register MQTT handler for Flight Log Petal")
            return

        logger.info(f"Registered to MQTT with subscription ID: {self.mqtt_subscription_id}")

    def _setup_redis_command_listener(self):
        if self._redis_proxy is None:
            logger.warning("Redis proxy unavailable — Petal flight log commands disabled.")
            return False

        try:
            self._redis_proxy.subscribe(RedisChannels.REDIS_CMD_CHANNEL, self._handle_redis_command_message)
            logger.info(
                f"Subscribed to Petal flight log command channel: {RedisChannels.REDIS_CMD_CHANNEL}"
            )
            return True
        except Exception as exc:
            logger.error(f"Failed to subscribe to Petal flight log command channel: {exc}")
            return False

    def _publish_redis_ack(
        self,
        message_id: Optional[str],
        command: str,
        *,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Publish Redis acknowledgment using Pydantic model for type safety."""
        if self._redis_proxy is None:
            return

        if status == "success":
            ack_payload = RedisAckPayload.success(message_id=message_id, command=command, result=result or "")
        else:
            ack_payload = RedisAckPayload.failure(message_id=message_id, command=command, error=error or "Unknown error")

        try:
            serialized = ack_payload.model_dump_json()
        except Exception as exc:
            logger.error(f"Failed to serialize Petal flight log ack payload: {exc}")
            return

        try:
            self._redis_proxy.publish(channel=RedisChannels.REDIS_ACK_CHANNEL, message=serialized)
            if message_id:
                self._redis_proxy.publish(
                    channel=f"{RedisChannels.REDIS_ACK_CHANNEL}/{message_id}",
                    message=serialized,
                )
        except Exception as exc:
            logger.error(f"Failed to publish Petal flight log ack: {exc}")

    def _handle_redis_command_message(self, channel: str, data: str):
        try:
            cmd = RedisCommandPayload.model_validate_json(data)
        except Exception as exc:
            logger.warning(f"Invalid Petal flight log command payload received: {exc}")
            return False

        if cmd.command == "leaf-fc-record.write":
            if cmd.payload is None:
                self._publish_redis_ack(cmd.message_id, cmd.command, status="error", error="Mission payload missing")
                return False

            try:
                asyncio.run_coroutine_threadsafe(
                    self._save_leaf_fc_record_handler(cmd.message_id, cmd.payload),
                    self._event_loop,
                )
            except RuntimeError as exc:
                logger.error(f"Failed to execute mission handler: {exc}")
                self._publish_redis_ack(
                    cmd.message_id,
                    cmd.command,
                    status="error",
                    error="Internal error executing command",
                )
        else:
            logger.info(f"Ignoring unsupported Redis command: {cmd.command}")

    async def unsubscribe_all_streams(self) -> Dict[str, Any]:
        """
        Unsubscribe from all active pubsub streams.
        
        Returns:
            Dict containing the results of the unsubscribe operations
        """
        logger.info("Starting unsubscribe all streams operation...")

        # Get list of active handlers
        active_handlers = self.get_active_handlers()

        if not active_handlers:
            logger.info("No active handlers to unregister")
            return {
                "status": "success",
                "message": "No active handlers to unregister",
                "unsubscribed_streams": [],
                "timestamp": datetime.now().isoformat()
            }
        
        unsubscribed_streams = []
        failed_streams = []

        # Stop each active handler
        for stream_name, handler_info in active_handlers.items():
            try:
                logger.info(f"Stopping stream: {stream_name}")
                controller = handler_info.get("controller")

                if controller and hasattr(controller, 'stop_streaming'):
                    await controller.stop_streaming()
                    self._untrack_subscription(stream_name)
                    unsubscribed_streams.append({
                        "stream_name": stream_name,
                        "stream_id": handler_info.get("stream_id"),
                        "was_rate_hz": handler_info.get("rate_hz")
                    })
                    logger.info(f"Successfully stopped stream: {stream_name}")
                else:
                    logger.warning(f"No valid controller found for stream: {stream_name}")
                    failed_streams.append(stream_name)
                    
            except Exception as e:
                logger.error(f"Failed to stop stream {stream_name}: {e}")
                failed_streams.append(stream_name)
        
        # Build response
        result = {
            "status": "success" if not failed_streams else "partial_success",
            "message": f"Unsubscribed from {len(unsubscribed_streams)} streams",
            "unsubscribed_streams": unsubscribed_streams,
            "timestamp": datetime.now().isoformat()
        }
        
        if failed_streams:
            result["failed_streams"] = failed_streams
            result["message"] += f", {len(failed_streams)} failed"
        
        logger.info(f"Unsubscribe all operation completed: {result['message']}")
        return result

    def _setup_command_handlers(self) -> Dict[str, Callable]:
        """Setup the command handlers registry mapping command names to handler methods."""
        return {
            f"{self.name}/fetch_flight_records": self._fetch_flight_records_handler,
            f"{self.name}/fetch_existing_flight_records": self._fetch_existing_flight_records_handler,
            f"{self.name}/start_sync_flight_record": self._start_sync_flight_record_handler,
            # Pub/Sub stream commands
            f"{self.name}/subscribe_sync_job_value_stream": self._subscribe_job_stream_handler,
            f"{self.name}/unsubscribe_sync_job_value_stream": self._unsubscribe_job_stream_handler,
            # test handlers
            # "Update": self._test_fetch_flight_records_handler,
        }

    async def _master_command_handler(self, topic: str, message: Dict[str, Any]):
        """Master command handler that dispatches to specific handlers based on command field."""
        try:
            # Check if command handlers are initialized
            if self._command_handlers is None:
                error_msg = "Petal not fully initialized yet, command handlers not available"
                logger.warning(error_msg)
                return
            
            # Check if response topic is available
            if self._mqtt_proxy.organization_id is None:
                error_msg = "Petal MQTT topics not yet initialized, cannot process commands"
                logger.warning(error_msg)
                return

            # Parse the MQTT message
            command = message.get("command", "")
            
            logger.info(f"Flight Log Petal master handler received command: {command}")
            
            # Dispatch to appropriate handler
            if command in self._command_handlers:
                handler = self._command_handlers[command]
                await handler(topic, message)
            else:
                # if command does not start with petal-flight-log/, ignore it
                if not command.startswith(f"{self.name}/"):
                    logger.debug(f"Ignoring command not meant for this petal: {command}")
                    return
                error_msg = f"Unknown command: {command}"
                logger.error(error_msg)
                
                if message.get("waitResponse", False):
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data={
                            "status": "error", 
                            "message": error_msg, 
                            "error_code": "UNKNOWN_COMMAND",
                            "available_commands": list(self._command_handlers.keys())
                        }
                    )
                    
        except Exception as e:
            error_msg = f"Master command handler error: {str(e)}"
            logger.error(error_msg)
            try:
                message_id = message.get("messageId", "unknown")
                wait_response = message.get("waitResponse", False)
                if wait_response:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                    )
            except Exception as e:
                logger.error(f"Failed to send error response: {e}")

    def get_active_handlers(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of all active handlers."""
        with self._registration_lock:
            return dict(self._active_handlers)

    def _track_subscription(self, stream_name: str, stream_id: str, rate_hz: float) -> None:
        """Track an active subscription for management purposes."""
        with self._registration_lock:
            self._active_handlers[stream_name] = {
                "stream_id": stream_id,
                "rate_hz": rate_hz,
                "started_at": datetime.now().isoformat()
            }
        logger.info(f"Tracking subscription for {stream_name} (ID: {stream_id}, Rate: {rate_hz} Hz)")

    def _untrack_subscription(self, stream_name: str) -> None:
        """Stop tracking a subscription."""
        with self._registration_lock:
            if stream_name in self._active_handlers:
                del self._active_handlers[stream_name]
                logger.info(f"Stopped tracking subscription for {stream_name}")

    # ---------------------------- MQTT handlers -------------------------------- #

    @http_action(method="POST", path="/test_fetch_flight_records_handler")
    async def _fetch_flight_records_handler(self, topic: str, message: Dict[str, Any]):
        """Handle get_flight_records command to match rosbag files with PX4 ulog files based on timestamps."""
        mqtt_proxy: MQTTProxy = self._proxies.get("mqtt")
        local_db_proxy: LocalDBProxy = self._proxies.get("db")
        cloud_db_proxy: CloudDBProxy = self._proxies.get("cloud")

        try:
            logger.info("Processing get_flight_records command")
            
            # Extract and validate parameters using Pydantic
            data = message.get("data", {})
            try:
                request = GetFlightRecordsRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {e}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetFlightRecordsResponse(
                            was_successful=False,
                            status="error",
                            message=error_msg,
                            error_code="INVALID_PARAMETERS"
                        ).model_dump()
                    )
                return

            # clean up all jobs by cancelling any stale jobs in redis
            await self.cancel_all_syncs()
            
            # Parse timestamps
            try:
                start_dt = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
            except ValueError as e:
                error_msg = f"Invalid timestamp format: {e}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetFlightRecordsResponse(
                            was_successful=False,
                            status="error",
                            message=error_msg,
                            error_code="INVALID_TIMESTAMP"
                        ).model_dump()
                    )
                return
            
            # Get flight records using simplified logic
            flight_records = await self._construct_flight_records(
                robot_instance_id=self._mqtt_proxy._get_machine_id(),
                start_dt=start_dt, 
                end_dt=end_dt, 
                tolerance_seconds=request.tolerance_seconds, 
                base=request.base
            )
            
            # cache the flight records in redis for quick access later
            machine_id = self._mqtt_proxy._get_machine_id()
            cache_key = f"flight_records:{machine_id}"
            await self._redis_proxy.set(cache_key, json.dumps([record.model_dump() for record in flight_records]))

            # Store the flight records on the local and cloud databases
            for record in flight_records:
                # Save to local DB
                local_result = await local_db_proxy.set_item(
                    table_name="config-log-flight_record",
                    filter_key="id",
                    filter_value=record.id,
                    data=record.model_dump()
                )
                if "error" in local_result:
                    logger.error(f"Failed to save flight record {record.id} to local DB: {local_result['error']}")
                    continue

                # Save to cloud DB
                cloud_result = await cloud_db_proxy.set_item(
                    table_name="config-log-flight_record",
                    filter_key="id",
                    filter_value=record.id,
                    data=record.model_dump()
                )
                if "error" in cloud_result:
                    logger.error(f"Failed to save flight record {record.id} to cloud DB: {cloud_result['error']}")
                    continue

            # Prepare response
            response_data = GetFlightRecordsResponse(
                was_successful=True,
                status="success",
                data={
                    "flight_records": flight_records,
                    "query": {
                        "start_time": request.start_time,
                        "end_time": request.end_time,
                        "tolerance_seconds": request.tolerance_seconds,
                        "base": request.base
                    },
                    "total_records": len(flight_records)
                }
            )
            
            logger.info(f"Found {len(flight_records)} matched flight records")
            
            # Also publish to web command topic for dashboard updates
            mqtt_message = {
                "waitResponse": False,
                "messageId": str(uuid.uuid4()),
                "deviceId": getattr(mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.name}/{MQTTCommands.FETCH_FLIGHT_RECORDS_COMMAND}",
                "timestamp": datetime.now().isoformat(),
                "payload": response_data.model_dump()
            }

            mqtt_object = MQTTMessage(**mqtt_message)

            await self._mqtt_proxy.publish_message(payload=mqtt_object.model_dump())

            if message.get("waitResponse", False):
                try:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetFlightRecordsResponse(
                            was_successful=True,
                            status="success",
                            message="Flight records fetched successfully",
                        ).model_dump()
                    )
                except Exception as response_error:
                    logger.error(f"Failed to send error response: {response_error}") 

            return response_data.model_dump()
            
        except Exception as e:
            error_msg = f"Error processing get_flight_records command: {str(e)}"
            logger.error(error_msg)
            
            if message.get("waitResponse", False):
                try:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetFlightRecordsResponse(
                            was_successful=False,
                            status="error",
                            message=error_msg,
                            error_code="PROCESSING_ERROR"
                        ).model_dump()
                    )
                except Exception as response_error:
                    logger.error(f"Failed to send error response: {response_error}") 

    @http_action(method="POST", path="/test_fetch_existing_flight_records_handler")
    async def _fetch_existing_flight_records_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler to fetch existing flight records from local dynamoDB"""
        mqtt_proxy: MQTTProxy = self._proxies.get("mqtt")

        try:
            logger.info("Processing test_fetch_existing_flight_records command")
            
            cloud_db_proxy: CloudDBProxy = self._proxies.get("cloud")
            machine_id = self._mqtt_proxy._get_machine_id()
            
            # Query local DB for flight records matching machine_id
            result = await cloud_db_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            
            if "error" in result:
                logger.error(f"Failed to retrieve flight records: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records",
                    headers={"source": "get_flight_records"},
                    extra={"error": result["error"]}
                )
            records = result.get("data", [])
        
            if not records or len(records) == 0:
                logger.info("No flight records found for robot id %s", self._mqtt_proxy._get_machine_id())
                # If no records found, return an empty response should raise a 404
                raise HTTPException(
                    status_code=404,
                    detail="No flight records found",
                    headers={"source": "get_flight_records"}
                )
            
            flight_record_matches = []
            for record in records:
                try:
                    # validate using LeafFCRecord
                    flight_record_match = ExistingFlightRecordMatch(**record)
                except ValidationError as e:
                    logger.error(f"Validation error for flight record {record.get('id', 'unknown')}: {e}")
                    continue

                # check if the flight record match has an exiting job id in redis cache
                if self._job_monitor:
                    # Find job by flight_record_id in metadata
                    all_job_states:List[JobState] = await self._job_monitor.get_jobs_by_type("FlightRecordSyncJob")
                    matching_job_state = None
                    for state in all_job_states:
                        if state.metadata.get("flight_record_id") == flight_record_match.id:
                            matching_job_state = state
                            break
                    
                    if matching_job_state:
                        flight_record_match.sync_job_id = matching_job_state.job_id
                        flight_record_match.sync_job_status = matching_job_state.status.value

                flight_record_matches.append(flight_record_match)      

            logger.info(f"Found {len(flight_record_matches)} matched flight records")

            response_data = GetExistingFlightRecordsResponse(
                status="success",
                data={
                    "flight_records": flight_record_matches,
                    "total_matches": len(flight_record_matches)
                }
            )

            # Also publish to web command topic for dashboard updates
            mqtt_message = {
                "waitResponse": False,
                "messageId": str(uuid.uuid4()),
                "deviceId": getattr(mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.name}/{MQTTCommands.FETCH_FLIGHT_RECORDS_COMMAND}",
                "timestamp": datetime.now().isoformat(),
                "payload": response_data.model_dump()
            }

            mqtt_object = MQTTMessage(**mqtt_message)

            await self._mqtt_proxy.publish_message(payload=mqtt_object.model_dump())

            if message.get("waitResponse", False):
                try:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetExistingFlightRecordsResponse(
                            status="success",
                            message="Flight records fetched successfully",
                        ).model_dump()
                    )
                except Exception as response_error:
                    logger.error(f"Failed to send error response: {response_error}")

            return response_data.model_dump()
        
        except Exception as e:
            error_msg = f"Error processing test_fetch_existing_flight_records command: {str(e)}"
            logger.error(error_msg)
            if message.get("waitResponse", False):
                try:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=GetExistingFlightRecordsResponse(
                            status="error",
                            message=error_msg,
                            error_code="PROCESSING_ERROR"
                        ).model_dump()
                    )
                except Exception as response_error:
                    logger.error(f"Failed to send error response: {response_error}")

    @http_action(
        method="POST", 
        path="/test_start_sync_flight_record_handler",
        response_model=StartFlightRecordSyncResponse
    )         
    async def _start_sync_flight_record_handler(self, topic: str, message: Dict[str, Any]) -> StartFlightRecordSyncResponse:
        """Test handler to start flight record sync job"""
        try:
            logger.info("Processing test_start_sync_flight_record command")
            
            # Extract and validate parameters using Pydantic 
            data = message.get("data", {})
            try:
                request = StartFlightRecordSyncRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = StartFlightRecordSyncResponse(
                        status="error",
                        message=error_msg,
                        error_code="INVALID_PARAMETERS"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Start flight record sync job
            response = await self.start_sync_flight_record(
                flight_record_id=request.flight_record_id
            )
            
            logger.info(f"Started flight record sync job {response.job_id} for flight record {request.flight_record_id}")
            
            if message.get("waitResponse", False):
                response = StartFlightRecordSyncResponse(
                    status="success",
                    message=f"Started flight record sync job {response.job_id}",
                    sync_job_id=response.job_id
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )

            return response
        
        except Exception as e:
            error_msg = f"Error processing test_start_sync_flight_record command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if message.get("waitResponse", False):
                response = StartFlightRecordSyncResponse(
                    status="error",
                    message=error_msg,
                    error_code="INTERNAL_ERROR"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )

            return response

    @http_action(method="POST", path="/test_subscribe_job_stream_handler")
    async def _subscribe_job_stream_handler(self, topic: str, message: Dict[str, Any]):
        """Handle subscribe_job_stream command to add WebSocket client to job stream."""
        try:
            logger.info("Processing subscribe_job_stream command")
            
            # Extract and validate parameters using Pydantic
            from .data_model import SubscribeJobStreamRequest, SubscribeJobStreamResponse
            
            data = message.get("data", {})
            try:
                request = SubscribeJobStreamRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = SubscribeJobStreamResponse(
                        status="error",
                        message=error_msg,
                        error_code="INVALID_PARAMETERS"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Subscribe to a job_id stream
            if self._job_monitor is None:
                error_msg = "Job monitoring system not initialized"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = SubscribeJobStreamResponse(
                        status="error",
                        message=error_msg,
                        error_code="JOB_MONITOR_NOT_INITIALIZED"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Get the job from the monitor
            job = self._job_monitor.get_active_job(request.subscribed_stream_id)
            if not job:
                # Try loading from Redis
                job_state = await self._job_monitor.get_job_state(request.subscribed_stream_id)
                if not job_state:
                    error_msg = f"Job {request.subscribed_stream_id} not found"
                    logger.error(error_msg)
                    if message.get("waitResponse", False):
                        response = SubscribeJobStreamResponse(
                            status="error",
                            message=error_msg,
                            error_code="JOB_NOT_FOUND"
                        )
                        await self._mqtt_proxy.send_command_response(
                            message_id=message.get("messageId", "unknown"),
                            response_data=response.model_dump()
                        )
                    return
                
                # Job exists but not active - return current state
                logger.info(f"Job {request.subscribed_stream_id} found in Redis but not active")
                if message.get("waitResponse", False):
                    response = SubscribeJobStreamResponse(
                        status="success",
                        message="Job exists but is not active",
                        job_state=job_state.to_dict()
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Determine MQTT topic based on job type
            mqtt_topic = f"{self.name}/{MQTTCommands.PX4_LOG_DOWNLOAD_PROGRESS_COMMAND}"
            if isinstance(job, ULogDownloadJobMAVLink) or isinstance(job, ULogDownloadJobMAVFTP):
                mqtt_topic = f"{self.name}/{MQTTCommands.PX4_LOG_DOWNLOAD_PROGRESS_COMMAND}"
            elif isinstance(job, S3UploadJob):
                mqtt_topic = f"{self.name}/{MQTTCommands.S3_UPLOAD_PROGRESS_COMMAND}"
            elif isinstance(job, FlightRecordSyncJob):
                mqtt_topic = f"{self.name}/{MQTTCommands.FLIGHT_RECORD_SYNC_PROGRESS_COMMAND}"
            
            # Subscribe to job progress updates
            stream_id = request.subscribed_stream_id
            await job.subscribe_to_progress(
                mqtt_proxy=self._mqtt_proxy,
                mqtt_device_id=self._mqtt_proxy._get_machine_id(),
                stream_id=stream_id,
                mqtt_topic=mqtt_topic,
                rate_hz=request.data_rate_hz
            )
            
            logger.info(f"Subscribed to job {request.subscribed_stream_id} progress stream at {request.data_rate_hz} Hz")
            
            if message.get("waitResponse", False):
                response = SubscribeJobStreamResponse(
                    status="success",
                    message=f"Subscribed to job {request.subscribed_stream_id} progress updates",
                    subscribed_stream_id=stream_id,
                    data_rate_hz=request.data_rate_hz,
                    mqtt_topic=mqtt_topic
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )
        
        except Exception as e:
            error_msg = f"Error processing subscribe_job_stream command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if message.get("waitResponse", False):
                response = SubscribeJobStreamResponse(
                    status="error",
                    message=error_msg,
                    error_code="INTERNAL_ERROR"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )
    
    @http_action(method="POST", path="/test_unsubscribe_job_stream_handler")
    async def _unsubscribe_job_stream_handler(self, topic: str, message: Dict[str, Any]):
        """Handle unsubscribe_job_stream command to stop job progress updates."""
        try:
            logger.info("Processing unsubscribe_job_stream command")
            
            # Extract and validate parameters using Pydantic
            from .data_model import UnsubscribeJobStreamRequest, UnsubscribeJobStreamResponse
            
            data = message.get("data", {})
            try:
                request = UnsubscribeJobStreamRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = UnsubscribeJobStreamResponse(
                        status="error",
                        message=error_msg,
                        error_code="INVALID_PARAMETERS"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Get the job from the monitor
            job = self._job_monitor.get_active_job(request.unsubscribed_stream_id)
            if not job:
                error_msg = f"Job {request.unsubscribed_stream_id} not found or not active"
                logger.warning(error_msg)
                if message.get("waitResponse", False):
                    response = UnsubscribeJobStreamResponse(
                        status="error",
                        message=error_msg,
                        error_code="JOB_NOT_FOUND"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Unsubscribe from job progress updates
            await job.unsubscribe_from_progress()
            
            logger.info(f"Unsubscribed from job {request.unsubscribed_stream_id} progress stream")
            
            if message.get("waitResponse", False):
                response = UnsubscribeJobStreamResponse(
                    status="success",
                    message=f"Unsubscribed from job {request.unsubscribed_stream_id} progress updates",
                    unsubscribed_stream_id=request.unsubscribed_stream_id
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )
        
        except Exception as e:
            error_msg = f"Error processing unsubscribe_job_stream command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if message.get("waitResponse", False):
                response = UnsubscribeJobStreamResponse(
                    status="error",
                    message=error_msg,
                    error_code="INTERNAL_ERROR",
                    unsubscribed_stream_id=request.unsubscribed_stream_id
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )

    @http_action(method="POST", path="/test_cancel_sync_flight_record_handler")
    async def cancel_sync_flight_record_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler to cancel a specific flight record sync job"""
        try:
            logger.info("Processing cancel_sync_flight_record command")
            
            # Extract and validate parameters using Pydantic
            from .data_model import CancelFlightRecordSyncRequest, CancelFlightRecordSyncResponse
            
            data = message.get("data", {})
            try:
                request = CancelFlightRecordSyncRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = CancelFlightRecordSyncResponse(
                        status="error",
                        message=error_msg,
                        error_code="INVALID_PARAMETERS"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Cancel flight record sync job
            response = await self.cancel_sync_flight_record(
                flight_record_id=request.flight_record_id
            )

            response = CancelFlightRecordSyncResponse(**response)
            
            logger.info(f"Cancelled flight record sync job for flight record {request.flight_record_id}")
            
            if message.get("waitResponse", False):
                response = CancelFlightRecordSyncResponse(
                    status="success",
                    message=f"Cancelled flight record sync job"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )
        
        except Exception as e:
            error_msg = f"Error processing cancel_sync_flight_record command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if message.get("waitResponse", False):
                response = CancelFlightRecordSyncResponse(
                    status="error",
                    message=error_msg,
                    error_code="INTERNAL_ERROR"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )

    @http_action(method="DELETE", path="/test_delete_flight_record_handler")
    async def delete_flight_record_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler to delete a specific flight record from local DB"""

        bucket_proxy: S3BucketProxy = self._proxies.get("s3_bucket")
        local_db_proxy: LocalDBProxy = self._proxies.get("db")
        cloud_db_proxy: CloudDBProxy = self._proxies.get("cloud")

        try:
            logger.info("Processing delete_flight_record command")
            
            # Extract and validate parameters using Pydantic
            from .data_model import DeleteFlightRecordRequest, DeleteFlightRecordResponse
            
            data = message.get("data", {})
            try:
                request = DeleteFlightRecordRequest(**data)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = DeleteFlightRecordResponse(
                        status="error",
                        message=error_msg,
                        error_code="INVALID_PARAMETERS"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            # Delete ulog file from storage based on flight record info
            result = await cloud_db_proxy.get_item(
                table_name="config-log-flight_record",
                partition_key="id",
                partition_value=request.flight_record_id
            )
            if "error" in result:
                error_msg = f"Failed to retrieve flight record {request.flight_record_id}: {result['error']}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = DeleteFlightRecordResponse(
                        status="error",
                        message=error_msg,
                        error_code="RETRIEVE_FAILED"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            flight_record_data = result.get("data", None)
            if not flight_record_data:
                error_msg = f"Flight record {request.flight_record_id} not found"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = DeleteFlightRecordResponse(
                        status="error",
                        message=error_msg,
                        error_code="NOT_FOUND"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return

            flight_record = ExistingFlightRecordMatch(**flight_record_data)
            if flight_record.ulog and flight_record.ulog.file_path:
                # Delete the ulog file from local file system
                if flight_record.ulog.storage_type == "local" and flight_record.ulog.file_path:
                    if os.path.exists(flight_record.ulog.file_path):
                        try:
                            os.remove(flight_record.ulog.file_path)
                        except Exception as e:
                            logger.error(f"Failed to delete ulog file at {flight_record.ulog.file_path}: {str(e)}")
                    
                logger.info(f"Deleted ulog file at {flight_record.ulog.file_path}")

                if flight_record.ulog.s3_key:
                    # Delete from S3 by moving to 'deleted' folder
                    s3_proxy: S3BucketProxy = self._proxies.get("s3")
                    delete_result = await s3_proxy.move_file(
                        source_key=flight_record.ulog.s3_key,
                        dest_key=f"deleted/{flight_record.ulog.s3_key}"
                    )
                    if "error" in delete_result:
                        logger.error(f"Failed to delete ulog file from S3 at {flight_record.ulog.s3_key}: {delete_result['error']}")
                    else:
                        logger.info(f"Deleted ulog file from S3 at {flight_record.ulog.s3_key}")

                # TODO: delete ulog file from Pixhawk if applicable

            if flight_record.rosbag and flight_record.rosbag.file_path:
                # Delete the rosbag file from local file system
                if flight_record.rosbag.storage_type == "local" and os.path.exists(flight_record.rosbag.file_path):
                    try:
                        os.remove(flight_record.rosbag.file_path)
                    except Exception as e:
                        logger.error(f"Failed to delete rosbag file at {flight_record.rosbag.file_path}: {str(e)}")
                
                logger.info(f"Deleted rosbag file at {flight_record.rosbag.file_path}")

                if flight_record.rosbag.s3_key:
                    # Delete from S3 by moving to 'deleted' folder
                    s3_proxy: S3BucketProxy = self._proxies.get("s3")
                    delete_result = await s3_proxy.move_file(
                        source_key=flight_record.rosbag.s3_key,
                        dest_key=f"deleted/{flight_record.rosbag.s3_key}"
                    )
                    if "error" in delete_result:
                        logger.error(f"Failed to delete rosbag file from S3 at {flight_record.rosbag.s3_key}: {delete_result['error']}")
                    else:
                        logger.info(f"Deleted rosbag file from S3 at {flight_record.rosbag.s3_key}")

            # Delete flight record from cloud DB
            result = await cloud_db_proxy.delete_item(
                table_name="config-log-flight_record",
                filter_key="id",
                filter_value=request.flight_record_id
            )
            if "error" in result:
                error_msg = f"Failed to delete flight record {request.flight_record_id}: {result['error']}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = DeleteFlightRecordResponse(
                        success=False,
                        message=error_msg,
                        error_code="DELETE_FAILED"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return
            
            logger.info(f"Deleted flight record {request.flight_record_id} from cloud DB")
            
            # Delete flight record from local DB
            result = await local_db_proxy.delete_item(
                table_name="config-log-flight_record",
                filter_key="id",
                filter_value=request.flight_record_id
            )
            if "error" in result:
                error_msg = f"Failed to delete flight record {request.flight_record_id} from local DB: {result['error']}"
                logger.error(error_msg)
                if message.get("waitResponse", False):
                    response = DeleteFlightRecordResponse(
                        success=False,
                        message=error_msg,
                        error_code="DELETE_FAILED"
                    )
                    await self._mqtt_proxy.send_command_response(
                        message_id=message.get("messageId", "unknown"),
                        response_data=response.model_dump()
                    )
                return

            logger.info(f"Deleted flight record {request.flight_record_id} from local DB")
            
            if message.get("waitResponse", False):
                response = DeleteFlightRecordResponse(
                    success=True,
                    message=f"Deleted flight record {request.flight_record_id}"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )
        
        except Exception as e:
            error_msg = f"Error processing delete_flight_record command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if message.get("waitResponse", False):
                response = DeleteFlightRecordResponse(
                    success=False,
                    message=error_msg,
                    error_code="INTERNAL_ERROR"
                )
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data=response.model_dump()
                )

    # ---------------------------- Redis handlers ------------------------------- #

    @http_action(method="POST", path="/test_save_leaf_fc_record_handler")
    async def _save_leaf_fc_record_handler(self, message_id: str, payload: Dict[str, Any]):
        """Handle save_leaf_fc_record command from Redis to save LeafFC metadata record."""
        try:
            logger.info("Processing save_leaf_fc_record command from Redis")
            
            # Extract and validate parameters using Pydantic
            try:
                request = SaveLeafFCRecordRequest(**payload)
            except Exception as e:
                error_msg = f"Invalid request parameters: {str(e)}"
                logger.error(error_msg)
                response = SaveLeafFCRecordResponse(
                    success=False,
                    message=error_msg,
                    error_code="INVALID_PARAMETERS"
                )
            
            # Save LeafFC record
            try:
                await self._save_leaf_fc_record(
                    leaf_fc_record=request.leaf_fc_record
                )
            except Exception as e:
                error_msg = f"Failed to save LeafFC record: {str(e)}"
                logger.error(error_msg)
                response = SaveLeafFCRecordResponse(
                    success=False,
                    message=error_msg,
                    error_code="SAVE_FAILED"
                )
                return
            
            logger.info(f"Saved LeafFC record {request.leaf_fc_record.id}")
            
            response = SaveLeafFCRecordResponse(
                success=True,
                message="LeafFC record saved successfully"
            )
        
        except Exception as e:
            error_msg = f"Error processing save_leaf_fc_record command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            response = SaveLeafFCRecordResponse(
                success=False,
                message=error_msg,
                error_code="INTERNAL_ERROR"
            )

        return response.model_dump()
        
    # ------------------------------- helpers ----------------------------------- #
    
    async def _construct_flight_records(
            self, 
            tolerance_seconds: int, 
            robot_instance_id: str,
            start_dt: Optional[datetime] = None, 
            end_dt: Optional[datetime] = None,
            base: Optional[str] = None,
        ) -> List[FlightRecordMatch]:
        """Simple method to loop through ulog entries and find matching rosbag files."""
        try:
            
            # Get PX4 ulog files using existing method
            px4_ulog_files = await self._get_px4_ulog_files_updated(base)

            # Get rosbag files using existing method
            rosbag_files = await self._get_rosbag_files_updated()

            # Get LeafFC record for each rosbag file (by comparing name of rosbag to LeafFC metadata)
            partial_leaf_fc_records = await self._get_leaf_fc_records()
            partial_rosbag_records = await self._get_rosbag_records()
            partial_ulog_records = await self._get_ulog_records()

            logger.info(f"Processing {len(partial_leaf_fc_records)} Leaf FC records")
            partial_flight_records: List[FlightRecordMatch] = []

            for rosbag_file in rosbag_files:

                if not rosbag_file.file_name:
                    continue
                
                found_leaf_fc = False
                for partial_leaf_fc_record in partial_leaf_fc_records:

                    leaf_fc_data = partial_leaf_fc_record.leaf_fc_record
                    if not leaf_fc_data.bag_name:
                        continue

                    if rosbag_file.file_name == leaf_fc_data.bag_name:
                        matching_rosbag = rosbag_file
                        logger.info(f"Matched Rosbag: {rosbag_file.file_name} (ID: {rosbag_file.id}) with Leaf FC Record: {partial_leaf_fc_record.id}")

                        # check that the leaf_fc record does not contain a rosbag record already with the same name
                        partial_flight_record = FlightRecordMatch(
                            id=partial_leaf_fc_record.id,
                            rosbag=matching_rosbag,
                            leaf_fc_record=partial_leaf_fc_record.leaf_fc_record,
                            status="no ulog file matched yet",
                            robot_instance_id=robot_instance_id,
                            sync_job_status=partial_leaf_fc_record.sync_job_status,
                            sync_job_id=partial_leaf_fc_record.sync_job_id
                        )
                        found_leaf_fc = True
                        break
                else:
                    logger.info(f"No matching Leaf FC record found for Rosbag: {rosbag_file.file_name} (ID: {rosbag_file.id})")
                    
                if found_leaf_fc:
                    partial_flight_records.append(partial_flight_record)
                    continue

                # check that the rosbag record does not already exist in partial rosbag flight records to avoid duplicates
                rosbag_record_found = False
                for partial_rosbag_record in partial_rosbag_records:
                    if partial_rosbag_record.rosbag.file_name == rosbag_file.file_name:
                        logger.info(f"Rosbag: {rosbag_file.file_name} (ID: {rosbag_file.id}) already exists in partial rosbag flight records, skipping to avoid duplicate")
                        rosbag_record_found = True
                        break
                else:
                    logger.info(f"No matching record found in partial rosbag records for Rosbag: {rosbag_file.file_name} (ID: {rosbag_file.id})")
                
                if rosbag_record_found:
                    partial_flight_record = FlightRecordMatch(
                        id=partial_rosbag_record.id,
                        rosbag=rosbag_file,
                        leaf_fc_record=None,
                        status="no leaf fc record or ulog file matched yet",
                        robot_instance_id=robot_instance_id,
                        sync_job_status=partial_rosbag_record.sync_job_status,
                        sync_job_id=partial_rosbag_record.sync_job_id
                    )
                else:
                    partial_flight_record = FlightRecordMatch(
                        id=str(uuid.uuid4()),
                        rosbag=rosbag_file,
                        leaf_fc_record=None,
                        status="no leaf fc record or ulog file matched yet",
                        robot_instance_id=robot_instance_id,
                        sync_job_status="pending",
                        sync_job_id=None
                    )

                partial_flight_records.append(partial_flight_record)

            # Filter ulogs by time range
            if start_dt is None:
                start_dt = datetime.fromtimestamp(0, tz=timezone.utc)
            if end_dt is None:
                end_dt = datetime.now(tz=timezone.utc)
            px4_ulog_files_filtered = [f for f in px4_ulog_files if start_dt.timestamp() <= f.modified_timestamp_unix_s <= end_dt.timestamp()]
            
            logger.info(f"Processing {len(px4_ulog_files_filtered)} ulog files in time range")
            
            # Loop through every ulog entry
            final_flight_records = []
            for record in partial_flight_records:
                if not record.rosbag:
                    final_flight_records.append(record)
                    continue

                ulog_record_found = False
                # Find if an existing ulog record exists for 2this flight record
                for partial_ulog_record in partial_ulog_records:
                    if record.rosbag.file_name == partial_ulog_record.rosbag.file_name:
                        record.ulog = partial_ulog_record.ulog
                        record.status = "matched from existing ulog record"
                        ulog_record_found = True
                        break
                else:
                    logger.info(f"No existing ulog record found for Rosbag: {record.rosbag.file_name} (ID: {record.rosbag.id})")

                if ulog_record_found:
                    final_flight_records.append(record)
                    continue

                # Find matching ulog file based on timestamp within tolerance
                found_ulog_file = False
                best_ulog_file = None
                best_time_diff = float('inf')

                for ulog_file in px4_ulog_files_filtered:
                    ulog_timestamp = ulog_file.modified_timestamp_unix_s

                    time_diff = abs(ulog_timestamp - record.rosbag.modified_timestamp_unix_s)
                    if time_diff <= tolerance_seconds:
                        if not found_ulog_file or time_diff < best_time_diff:
                            best_time_diff = time_diff
                            found_ulog_file = True
                            best_ulog_file = ulog_file
            
                # Create flight record (rosbag can be None if no match found)
                if found_ulog_file:
                    record.ulog = best_ulog_file
                    record.time_difference_seconds = best_time_diff
                    record.status = "matched"
                else:
                    record.status = "no ulog file matched"

                final_flight_records.append(record)

            # Sort by ulog modified_timestamp_unix_s (newest first)
            final_flight_records.sort(key=lambda r: r.ulog.modified_timestamp_unix_s if r.ulog else 0, reverse=True)

            return final_flight_records
            
        except Exception as e:
            logger.error(f"Error constructing flight records: {e}")
            return []

    async def _get_rosbag_files_updated(self) -> List[RosbagFileRecord]:
        """Get rosbag files using existing _get_available_rosbags logic."""
        try:
            # Use existing method
            result = await self._get_available_rosbags()
            rosbag_data = result.get("rosbag_files", [])

            # Convert to RosbagFileRecord objects
            file_records = []
            for item in rosbag_data:
                metadata = item.get("metadata", {})
                file_record = RosbagFileRecord(
                    id=item["id"],
                    file_name=item["file_name"],
                    file_path=item["file_path"],
                    file_type=item["file_type"],
                    storage_type=item["storage_type"],
                    size_bytes=metadata.get("size_bytes", 0),
                    size_kb=metadata.get("size_kb", 0.0),
                    creation_timestamp_unix_s=metadata.get("creation_timestamp_unix_s", 0),
                    modified_timestamp_unix_s=metadata.get("modified_timestamp_unix_s", 0),
                    log_duration_seconds=metadata.get("time_interval_s", 0.0),
                    date_str=metadata.get("date", ""),
                    organization_id=item["organization_id"],
                    robot_instance_id=item["robot_instance_id"],
                    robot_type_id=item["robot_type_id"],
                    metadata=metadata
                )
                file_records.append(file_record)
            
            return file_records
            
        except Exception as e:
            logger.error(f"Error getting rosbag files: {e}")
            return []

    async def _get_px4_ulog_files_updated(self, base:str) -> List[UlogFileRecord]:
        """Get PX4 ulog files using existing _get_available_px4_ulogs logic."""
        try:
            # Use existing method
            result = await self._get_available_px4_ulogs({"base": base})
            ulog_data = result.get("px4_ulogs", [])
            
            # Convert to UlogFileRecord objects
            file_records = []
            for item in ulog_data:
                metadata = item.get("metadata", {})
                file_record = UlogFileRecord(
                    id=item["id"],
                    file_name=item["file_name"],
                    file_path=None,
                    file_type=item["file_type"],
                    sd_card_path=item["file_path"],
                    storage_type=item["storage_type"],
                    size_bytes=metadata.get("size_bytes", 0),
                    size_kb=metadata.get("size_kb", 0.0),
                    modified_timestamp_unix_s=metadata.get("modified_timestamp_unix_s", 0),
                    creation_timestamp_unix_s=metadata.get("modified_timestamp_unix_s", 0),
                    date_str=metadata.get("date", ""),
                    qgc_index=metadata.get("index", None),
                    qgc_name=metadata.get("qgc_name", None),
                    organization_id=item["organization_id"],
                    robot_instance_id=item["robot_instance_id"],
                    robot_type_id=item["robot_type_id"]
                )
                file_records.append(file_record)
            
            return file_records
            
        except Exception as e:
            logger.error(f"Error getting PX4 ulog files: {e}")
            return []

    async def _get_leaf_fc_records(self) -> List[FlightRecordMatch]:
        """
        Obtains LeafFC records from dynamoDB proxy by looking at table 'config-log-flight_record'
        """
        try:
            local_db_proxy: LocalDBProxy = self._proxies.get("db")
            if local_db_proxy is None:
                logger.error("LocalDBProxy not available in proxies")
                return []
            
            # Scan the table for LeafFC records
            result = await local_db_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            
            if "error" in result:
                logger.error(f"Failed to retrieve flight records: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records",
                    headers={"source": "get_flight_records"},
                    extra={"error": result["error"]}
                )
            records = result.get("data", [])

            if not records or len(records) == 0:
                logger.info("No flight records found for robot id %s", self._mqtt_proxy._get_machine_id())
                # If no records found, return an empty response should raise a 404
                raise HTTPException(
                    status_code=404,
                    detail="No flight records found",
                    headers={"source": "get_flight_records"}
                )

            # get leaf_fc records from local db
            leaf_fc_record_result = await local_db_proxy.scan_items(
                table_name="config-log-leaf_fc_record-edge"
            )

            if "error" in leaf_fc_record_result:
                logger.error(f"Failed to retrieve LeafFC records: {leaf_fc_record_result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve LeafFC records",
                    headers={"source": "get_leaf_fc_records"},
                    extra={"error": leaf_fc_record_result["error"]}
                )
            leaf_fc_records = leaf_fc_record_result.get("data", [])

            partial_leaf_fc_flight_records = []
            for leaf_fc_data in leaf_fc_records:

                try:
                    leaf_fc_data = LeafFCRecord(**leaf_fc_data)
                except ValidationError as e:
                    logger.error(f"Validation error for LeafFC record {record.id}: {e}")
                    continue

                for record in records:

                    try:
                        record = FlightRecordMatch(**record)
                    except ValidationError as e:
                        logger.error(f"Validation error for FlightRecordMatch record {record.id}: {e}")
                        continue


                    if record.leaf_fc_record:
                        if leaf_fc_data.bag_name == record.leaf_fc_record.bag_name:
                            logger.info(f"Matched LeafFC Record: {leaf_fc_data.bag_name} (ID: {record.id})")

                            partial_leaf_fc_flight_record = FlightRecordMatch(
                                id = record.id,
                                leaf_fc_record = leaf_fc_data,
                                robot_instance_id=self._mqtt_proxy._get_machine_id(),
                                sync_job_status= record.sync_job_status,
                                sync_job_id= record.sync_job_id
                            )
                            break
                else:
                    logger.info(f"No matching FlightRecordMatch found for LeafFC Record: {leaf_fc_data.bag_name}")
                    partial_leaf_fc_flight_record = FlightRecordMatch(
                        id=str(uuid.uuid4()),
                        leaf_fc_record=leaf_fc_data,
                        robot_instance_id=self._mqtt_proxy._get_machine_id(),
                        sync_job_status="pending",
                        sync_job_id=None
                    )
    
                    partial_leaf_fc_flight_records.append(partial_leaf_fc_flight_record)

            return partial_leaf_fc_flight_records
            
        except Exception as e:
            logger.error(f"Error getting LeafFC records: {e}")
            return []

    async def _get_rosbag_records(self) -> List[FlightRecordMatch]:
        """
        Obtains Rosbag records from dynamoDB proxy by looking at table 'config-log-flight_record'
        """
        try:
            cloud_db_proxy: LocalDBProxy = self._proxies.get("cloud")
            if cloud_db_proxy is None:
                logger.error("CloudDBProxy not available in proxies")
                return []
            
            # Scan the table for LeafFC records
            result = await cloud_db_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            
            if "error" in result:
                logger.error(f"Failed to retrieve flight records: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records",
                    headers={"source": "get_flight_records"},
                    extra={"error": result["error"]}
                )
            records = result.get("data", [])

            if not records or len(records) == 0:
                logger.info("No flight records found for robot id %s", self._mqtt_proxy._get_machine_id())
                # If no records found, return an empty response should raise a 404
                raise HTTPException(
                    status_code=404,
                    detail="No flight records found",
                    headers={"source": "get_flight_records"}
                )

            rosbag_records = []
            for record in records:
                try:
                    record = FlightRecordMatch(**record)
                except ValidationError as e:
                    logger.error(f"Validation error for FlightRecordMatch record {record.id}: {e}")
                    continue

                rosbag_data = record.rosbag
                if rosbag_data:
                    rosbag_record = FlightRecordMatch(
                        id = record.id,
                        rosbag = rosbag_data,
                        robot_instance_id=self._mqtt_proxy._get_machine_id(),
                        sync_job_status = record.sync_job_status,
                        sync_job_id = record.sync_job_id
                    )
                    rosbag_records.append(rosbag_record)

            return rosbag_records

        except Exception as e:
            logger.error(f"Error getting Rosbag records: {e}")
            return []

    async def _get_ulog_records(self) -> List[FlightRecordMatch]:
        """
        Obtains ULog records from dynamoDB proxy by looking at table 'config-log-flight_record'
        """
        try:
            cloud_db_proxy: LocalDBProxy = self._proxies.get("cloud")
            if cloud_db_proxy is None:
                logger.error("CloudDBProxy not available in proxies")
                return []
            
            # Scan the table for LeafFC records
            result = await cloud_db_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            
            if "error" in result:
                logger.error(f"Failed to retrieve flight records: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve flight records",
                    headers={"source": "get_flight_records"},
                    extra={"error": result["error"]}
                )
            records = result.get("data", [])

            if not records or len(records) == 0:
                logger.info("No flight records found for robot id %s", self._mqtt_proxy._get_machine_id())
                # If no records found, return an empty response should raise a 404
                raise HTTPException(
                    status_code=404,
                    detail="No flight records found",
                    headers={"source": "get_flight_records"}
                )

            ulog_records = []
            for record in records:
                
                try:
                    record = FlightRecordMatch(**record)
                except ValidationError as e:
                    logger.error(f"Validation error for FlightRecordMatch record {record.id}: {e}")
                    continue

                ulog_data = record.ulog
                rosbag_data = record.rosbag
                if ulog_data:
                    ulog_record = FlightRecordMatch(
                        id = record.id,
                        rosbag=rosbag_data,
                        ulog = ulog_data,
                        robot_instance_id=self._mqtt_proxy._get_machine_id()
                    )
                    ulog_records.append(ulog_record)

            return ulog_records

        except Exception as e:
            logger.error(f"Error getting ULog records: {e}")
            return []

    @http_action(method="GET", path="/available-bags")
    async def _get_available_rosbags(self):
        """List available local RosBag files."""
        # Define the directory where RosBag files are stored
        db_proxy: LocalDBProxy = self._proxies["db"]
        home_dir = os.path.expanduser("~")
        local_dir = os.path.join(home_dir, "rosbag_records")
        
        # Get the list of RosBag files recursively
        rosbag_files = []
        
        def find_bag_files_recursively(directory):
            if not os.path.exists(directory):
                return
                
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    # If it's a directory, search inside it
                    find_bag_files_recursively(item_path)
                elif os.path.isfile(item_path) and item.endswith(".bag"):
                    # If it's a bag file, add it to our results
                    stats = os.stat(item_path)
                    
                    try:
                        out = subprocess.check_output(["rosbag", "info", "--yaml", item_path])
                        meta = yaml.safe_load(out)
                    except Exception as e:
                        logger.error(f"Error reading {item_path}: {e}")
                        meta = {"start": "None", "end": "None", "duration": "None"}

                    start = meta["start"]               # epoch seconds (float)
                    end = meta["end"]                   # epoch seconds (float)
                    recording_secs = meta["duration"]   # seconds (float)

                    # Create record with metadata
                    item = {
                        "id": str(uuid.uuid4()),
                        "robot_instance_id": self._mqtt_proxy._get_machine_id(),
                        "robot_type_id": db_proxy.robot_type_id,
                        "organization_id": db_proxy.organization_id,
                        "address": self._mqtt_proxy._get_machine_id(),
                        "file_name": os.path.basename(item_path),
                        "file_path": item_path,
                        "file_type": "bag",
                        "storage_type": "local",
                        "deleted": False,
                        "metadata": {
                            "date": datetime.fromtimestamp(stats.st_mtime).isoformat().replace(':', '-').replace('T', '-').split('.')[0],
                            "size_bytes": stats.st_size,
                            "size_kb": round(stats.st_size / 1024, 2),
                            "modified_timestamp_unix_s": int(stats.st_mtime),
                            "start_time_s": start,
                            "end_time_s": end,
                            "time_interval_s": recording_secs
                        }
                    }
                    rosbag_files.append(item)
        
        # Start the recursive search
        find_bag_files_recursively(local_dir)
        
        # Store the records in the redis database
        redis_key = f"local_rosbags:{self._mqtt_proxy._get_machine_id()}"
        await self._redis_proxy.set(redis_key, json.dumps(rosbag_files))

        # Sort records by modified timestamp (newest first)
        rosbag_files.sort(key=lambda x: x["metadata"]["modified_timestamp_unix_s"], reverse=True)

        logger.info(f"Found {len(rosbag_files)} RosBag files in {local_dir}")
        
        return {"rosbag_files": rosbag_files}

    @http_action(method="POST", path="/available-px4-ulogs")
    async def _get_available_px4_ulogs(self, data: Dict[str, str] = None):
        """List available PX4 ULog files."""
        mavlink_proxy: MavLinkFTPProxy = self._proxies["ftp_mavlink"]
        local_db_proxy: LocalDBProxy = self._proxies["db"]

        if data is not None and "base" in data:
            base = data['base']
        else:
            base = None # defaults to default sd log path

        # Get ULog files from PX4 using MavLinkProxy
        ulog_files = await mavlink_proxy.list_ulogs(base=base)
        
        # Convert to the expected format
        log_records = []
        for file in ulog_files:
            # Convert UTC timestamp to formatted date
            timestamp = file.utc
            est_timestamp = timestamp - (5 * 3600)  # Subtract 5 hours in seconds
            dt = datetime.fromtimestamp(est_timestamp)
            date = dt.isoformat().replace('-', '-').replace(':', '-').replace('T', '-').split('.')[0]            
            index = file.index

            # Create record with metadata
            item = {
                "id": str(uuid.uuid4()),
                "robot_instance_id": local_db_proxy.machine_id,
                "robot_type_id": local_db_proxy.robot_type_id,
                "organization_id": local_db_proxy.organization_id,
                "address": local_db_proxy.machine_id,
                "file_name": os.path.basename(file.remote_path),
                "file_path": file.remote_path,
                "file_type": "ulg",
                "storage_type": "pixhawk",
                "deleted": False,
                "metadata": {
                    "index": file.index,
                    "date": date,
                    "size_bytes": file.size_bytes,
                    "size_kb": round(file.size_bytes / 1024, 2),
                    "modified_timestamp_unix_s": timestamp,
                    "qgc_name": f"log_{index}_{date}.ulg"  # QGroundControl compatible name
                }
            }
            log_records.append(item)
        
        # Sort records by modified_timestamp_unix_s (newest first)
        log_records.sort(key=lambda x: x["metadata"]["modified_timestamp_unix_s"], reverse=True)

        # store the records in the redis database
        redis_key = f"px4_ulogs:{local_db_proxy.machine_id}"
        await self._redis_proxy.set(redis_key, json.dumps(log_records))

        logger.info(f"Found {len(log_records)} PX4 ULog files for machine {local_db_proxy.machine_id} in organization {local_db_proxy.organization_id}")
            
        return {"px4_ulogs": log_records}

    async def _save_leaf_fc_record(self, leaf_fc_record: LeafFCRecord) -> None:
        """Save LeafFC record to local DB."""
        local_db_proxy: LocalDBProxy = self._proxies.get("db")
        if local_db_proxy is None:
            logger.error("LocalDBProxy not available in proxies")
            raise HTTPException(
                status_code=500,
                detail="LocalDBProxy not available",
                headers={"source": "save_leaf_fc_record"}
            )
        
        # Save the LeafFC record
        result = await local_db_proxy.set_item(
            table_name="config-log-leaf_fc_record-edge",
            filter_key="id",
            filter_value=leaf_fc_record.id,
            data=leaf_fc_record.model_dump()
        )
        
        if "error" in result:
            logger.error(f"Failed to save LeafFC record {leaf_fc_record.id}: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save LeafFC record {leaf_fc_record.id}",
                headers={"source": "save_leaf_fc_record"},
                extra={"error": result["error"]}
            )
        
        logger.info(f"Saved LeafFC record {leaf_fc_record.id} to local DB")
        return

    # WebSocket endpoint for progress updates
    @websocket_action(
        path="/ws/download-progress",
        name="WebSocket for download progress updates",
    )
    async def ws_download_progress(self, websocket: WebSocket):
        await websocket.accept()
        websocket_clients.add(websocket)
        try:
            while True:
                await websocket.receive_text()  # Keep the connection alive
        except WebSocketDisconnect:
            websocket_clients.discard(websocket)

    async def get_message(
        self,
        *,
        msg_id: str,
        request_msg: mavutil.mavlink.MAVLink_message,
        timeout: float = 3.0,
    ) -> mavutil.mavlink.MAVLink_message:
        """
        Send *request_msg* and return the **first** packet whose ID equals *msg_id*.
        """
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]
        holder: Dict[str, mavutil.mavlink.MAVLink_message] = {}

        def _collector(pkt):
            holder["msg"] = pkt
            return True                     # one packet is enough

        await mavlink_proxy.send_and_wait(
            match_key=msg_id,
            request_msg=request_msg,
            collector=_collector,
            timeout=timeout,
        )
        return holder["msg"]

    # --------------------------- Sync Actions ------------------------------ #

    @http_action(
        method="POST",
        path="/sync-flight-record/{flight_record_id}",
        response_model=FlightRecordSyncStartResponse,
        summary="Start flight record sync job",
        description="Sync a flight record to cloud. Handles ULog download from Pixhawk (if needed) and uploads ULog and Rosbag files to S3."
    )
    async def start_sync_flight_record(self, flight_record_id: str) -> FlightRecordSyncStartResponse:
        """Start a flight record sync job using the job management system."""
        try:
            # Get required proxies
            local_db_proxy: LocalDBProxy = self._proxies.get("db")
            cloud_db_proxy: CloudDBProxy = self._proxies.get("cloud")
            bucket_proxy: S3BucketProxy = self._proxies.get("bucket")
            mavftp_proxy: MavLinkFTPProxy = self._proxies.get("ftp_mavlink")

            if not all([local_db_proxy, bucket_proxy, self._redis_proxy, cloud_db_proxy]):
                raise HTTPException(
                    status_code=500,
                    detail="Required proxies not available",
                    headers={"source": "start_sync_flight_record"}
                )
            
            # Fetch flight record from cloud DB
            fetch_result = await cloud_db_proxy.get_item(
                table_name="config-log-flight_record",
                partition_key="id",
                partition_value=flight_record_id
            )
            
            if "error" in fetch_result or not fetch_result.get("data"):
                raise HTTPException(
                    status_code=404,
                    detail=f"Flight record {flight_record_id} not found",
                    headers={"source": "start_sync_flight_record"}
                )

            # Validate flight record
            flight_record_data = fetch_result["data"]
            try:
                flight_record = FlightRecordMatch(**flight_record_data)
            except ValidationError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid flight record data: {e}",
                    headers={"source": "start_sync_flight_record"}
                )
            
            # Create sub-jobs based on flight record state
            ulog_download_job = None
            s3_upload_ulog_job = None
            s3_upload_rosbag_job = None
            
            home_dir = os.path.expanduser("~")
            ulog_local_dir = os.path.join(home_dir, "ulog_records")
            os.makedirs(ulog_local_dir, exist_ok=True)
            
            # Check if ULog download is needed
            if flight_record.ulog and not flight_record.ulog.s3_key:
                if flight_record.ulog.storage_type == "pixhawk":
                    # Need to download from Pixhawk first
                    local_filename = flight_record.ulog.qgc_name if flight_record.ulog.qgc_name else f"log_{flight_record.ulog.file_name}"
                    local_path = os.path.join(ulog_local_dir, local_filename)
                    
                    ulog_download_job = ULogDownloadJobMAVFTP(
                        px4_path=flight_record.ulog.sd_card_path,
                        file_path=local_path,
                        mavftp_proxy=mavftp_proxy,
                        size_bytes=flight_record.ulog.size_bytes,
                        redis_proxy=self._redis_proxy,
                        metadata={
                            "flight_record_id": flight_record_id,
                            "log_id": flight_record.ulog.qgc_index
                        }
                    )
            
            # Create S3 upload job for ULog if not already uploaded
            if flight_record.ulog and not flight_record.ulog.s3_key:
                s3_key = f"{flight_record.robot_instance_id}/{flight_record.id}/ulog/{flight_record.ulog.file_name}"
                
                s3_upload_ulog_job = S3UploadJob(
                    s3_key=s3_key,
                    bucket_proxy=bucket_proxy,
                    redis_proxy=self._redis_proxy,
                    metadata={
                        "flight_record_id": flight_record_id,
                        "file_type": "ulog"
                    }
                )
            
            # Create S3 upload job for Rosbag if not already uploaded
            if flight_record.rosbag and not flight_record.rosbag.s3_key:
                s3_key = f"{flight_record.robot_instance_id}/{flight_record.id}/rosbag/{flight_record.rosbag.file_name}"
                
                s3_upload_rosbag_job = S3UploadJob(
                    s3_key=s3_key,
                    bucket_proxy=bucket_proxy,
                    redis_proxy=self._redis_proxy,
                    metadata={
                        "flight_record_id": flight_record_id,
                        "file_type": "rosbag"
                    }
                )
            
            # Ensure that there is no previous FlightRecordSyncJob for this flight_record_id
            existing_job_states: List[JobState] = await self._job_monitor.get_jobs_by_type("FlightRecordSyncJob")
            for state in existing_job_states:
                if state.metadata.get("flight_record_id") == flight_record_id:
                    # cancel and remove existing job
                    await self._job_monitor.cancel_job(state.job_id)
                    logger.info(f"Cancelled existing FlightRecordSyncJob {state.job_id} for flight record {flight_record_id}")
                    await self._job_monitor.unregister_job(state.job_id)
                    logger.info(f"Unregistered existing FlightRecordSyncJob {state.job_id} for flight record {flight_record_id}")

            # Create composite sync job
            sync_job = FlightRecordSyncJob(
                flight_record_id=flight_record_id,
                ulog_download_job=ulog_download_job,
                s3_upload_ulog_job=s3_upload_ulog_job,
                s3_upload_rosbag_job=s3_upload_rosbag_job,
                redis_proxy=self._redis_proxy,
                cloud_db_proxy=cloud_db_proxy,
                local_db_proxy=local_db_proxy,
                metadata={
                    "flight_record_id": flight_record_id,
                    "robot_instance_id": flight_record.robot_instance_id
                }
            )
            
            # Register with monitor
            await self._job_monitor.register_job(sync_job)

            # update job ID in database
            flight_record.sync_job_id = sync_job.job_id
            flight_record.sync_job_status = sync_job.status.value

            result = await cloud_db_proxy.set_item(
                table_name="config-log-flight_record",
                filter_key="id",
                filter_value=flight_record_id,
                data=flight_record.model_dump()
            )

            if "error" in result:
                logger.error(f"Failed to update flight record with sync job ID: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update flight record with sync job ID",
                    headers={"source": "start_sync_flight_record"}
                )
            
            result = await local_db_proxy.set_item(
                table_name="config-log-flight_record",
                filter_key="id",
                filter_value=flight_record_id,
                data=flight_record.model_dump()
            )

            if "error" in result:
                logger.error(f"Failed to update local flight record with sync job ID: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update local flight record with sync job ID",
                    headers={"source": "start_sync_flight_record"}
                )
            
            # Start the sync job
            await sync_job.start()
            
            logger.info(f"Flight record sync job started: {sync_job.job_id} for flight record {flight_record_id}")
            
            # Return job info using response model
            return FlightRecordSyncStartResponse(
                success=True,
                job_id=sync_job.job_id,
                flight_record_id=flight_record_id,
                status=sync_job.status.value,
                message="Flight record sync started successfully",
                sub_jobs={
                    "ulog_download": ulog_download_job.job_id if ulog_download_job else None,
                    "s3_upload_ulog": s3_upload_ulog_job.job_id if s3_upload_ulog_job else None,
                    "s3_upload_rosbag": s3_upload_rosbag_job.job_id if s3_upload_rosbag_job else None
                }
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting flight record sync: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error starting sync: {str(e)}",
                headers={"source": "start_sync_flight_record"}
            )

    #--------------------------- Sync Management -----------------------------#

    @http_action(
        method="POST",
        path="/cancel-sync/{flight_record_id}",
        response_model=Dict[str, Any],
        summary="Cancel sync job (job-based API)",
        description="Cancel a flight record sync job and all sub-jobs."
    )
    async def cancel_sync(self, flight_record_id: str) -> Dict[str, Any]:
        """Cancel a flight record sync job."""
        if not flight_record_id:
            raise HTTPException(
                status_code=400,
                detail="Flight record ID parameter required",
                headers={"source": "cancel_sync"}
            )

        try:
            # Find job by flight_record_id in metadata
            all_job_states = await self._job_monitor.get_jobs_by_type("FlightRecordSyncJob")
            matching_job_state = None
            for state in all_job_states:
                if state.metadata.get("flight_record_id") == flight_record_id:
                    matching_job_state = state
                    break
            
            if not matching_job_state:
                raise HTTPException(
                    status_code=404,
                    detail="Sync job not found",
                    headers={"source": "cancel_sync"}
                )
            
            # Cancel the sync job (this will cancel all sub-jobs)
            success = await self._job_monitor.cancel_job(matching_job_state.job_id)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="Sync job not found or cannot be cancelled",
                    headers={"source": "cancel_sync"}
                )
            
            response = {
                "success": True,
                "flight_record_id": flight_record_id,
                "job_id": matching_job_state.job_id,
                "status": "cancelled",
                "message": "Flight record sync cancelled successfully"
            }
            
            # Publish to MQTT
            message_id = str(uuid.uuid4())
            mqtt_message = {
                "waitResponse": False,
                "messageId": message_id,
                "deviceId": getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.name}/{MQTTCommands.CANCEL_SYNC_MQTT_COMMAND}",
                "timestamp": datetime.now().isoformat(),
                "payload": response
            }
            mqtt_object = MQTTMessage(**mqtt_message)
            await self._mqtt_proxy.publish_message(payload=mqtt_object.model_dump())
            
            logger.info(f"Flight record sync cancelled: {flight_record_id}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling sync for flight record {flight_record_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error cancelling sync",
                headers={"source": "cancel_sync"}
            )

    @http_action(
        method="POST",
        path="/cancel-sync",
        response_model=Dict[str, Any],
        summary="Cancel all sync jobs (job-based API)",
        description="Cancel all flight record sync jobs and their sub-jobs."
    )
    async def cancel_all_syncs(self) -> Dict[str, Any]:
        """Cancel all flight record sync jobs."""
        try:
            # Get all FlightRecordSyncJob jobs
            all_job_states = await self._job_monitor.get_jobs_by_type("FlightRecordSyncJob")
            cancelled_jobs = []
            
            for state in all_job_states:
                success = await self._job_monitor.cancel_job(state.job_id)
                if success:
                    cancelled_jobs.append(state.job_id)
            
            response = {
                "success": True,
                "cancelled_jobs": cancelled_jobs,
                "message": f"Cancelled {len(cancelled_jobs)} flight record sync jobs"
            }
            
            logger.info(f"All flight record sync jobs cancelled: {len(cancelled_jobs)} jobs")
            return response
            
        except Exception as e:
            logger.error(f"Error cancelling all sync jobs: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error cancelling all sync jobs",
                headers={"source": "cancel_all_syncs"}
            )

    @http_action(
        method="GET",
        path="/check-sync/{flight_record_id}",
        response_model=Dict[str, Any],
        summary="Check sync status (job-based API)",
        description="Check the status of a flight record sync job."
    )
    async def check_sync(self, flight_record_id: str) -> Dict[str, Any]:
        """Check the status of a flight record sync job."""

        if not flight_record_id:
            raise HTTPException(
                status_code=400,
                detail="Flight record ID parameter required",
                headers={"source": "check_sync"}
            )

        try:
            # Find job by flight_record_id in metadata
            all_job_states = await self._job_monitor.get_jobs_by_type("FlightRecordSyncJob")
            matching_job_state = None
            for state in all_job_states:
                if state.metadata.get("flight_record_id") == flight_record_id:
                    matching_job_state = state
                    break
            
            if not matching_job_state:
                raise HTTPException(
                    status_code=404,
                    detail="Sync job not found",
                    headers={"source": "check_sync"}
                )
            
            # Get job status from Redis
            state = await self._job_monitor.get_job_state(matching_job_state.job_id)
            if not state:
                raise HTTPException(
                    status_code=404,
                    detail="Sync job not found",
                    headers={"source": "check_sync"}
                )
            
            # Get sub-job statuses
            sub_job_ids = state.metadata
            ulog_download_job_id = sub_job_ids.get("ulog_download_job_id")
            s3_upload_ulog_job_id = sub_job_ids.get("s3_upload_ulog_job_id")
            s3_upload_rosbag_job_id = sub_job_ids.get("s3_upload_rosbag_job_id")
            
            sub_job_statuses = {}
            
            if ulog_download_job_id:
                ulog_job_state: JobState = self._job_monitor.get_job_state(ulog_download_job_id)
                if ulog_job_state:
                    sub_job_statuses["ulog_download"] = {
                        "job_id": ulog_job_state.job_id,
                        "status": ulog_job_state.status.value,
                        "progress": ulog_job_state.progress.percentage if ulog_job_state.progress else 0.0,
                        "message": ulog_job_state.progress.message if ulog_job_state.progress else None
                    }


            if s3_upload_ulog_job_id:
                s3_ulog_job_state: JobState = self._job_monitor.get_job_state(s3_upload_ulog_job_id)
                if s3_ulog_job_state:
                    sub_job_statuses["s3_upload_ulog"] = {
                        "job_id": s3_ulog_job_state.job_id,
                        "status": s3_ulog_job_state.status.value,
                        "progress": s3_ulog_job_state.progress.percentage if s3_ulog_job_state.progress else 0.0
                    }


            if s3_upload_rosbag_job_id:
                s3_rosbag_job_state: JobState = self._job_monitor.get_job_state(s3_upload_rosbag_job_id)
                if s3_rosbag_job_state:
                    sub_job_statuses["s3_upload_rosbag"] = {
                        "job_id": s3_rosbag_job_state.job_id,
                        "status": s3_rosbag_job_state.status.value,
                        "progress": s3_rosbag_job_state.progress.percentage if s3_rosbag_job_state.progress else 0.0
                    }

            response = {
                "success": True,
                "flight_record_id": flight_record_id,
                "job_id": state.job_id,
                "status": state.status.value,
                "progress": state.progress.percentage if state.progress else 0.0,
                "message": state.progress.message if state.progress else None,
                "sub_jobs": sub_job_statuses,
                "created_at": datetime.fromtimestamp(state.created_at).isoformat(),
                "updated_at": datetime.fromtimestamp(state.updated_at).isoformat(),
                "error_message": state.error_message
            }
            
            # Publish to MQTT
            message_id = str(uuid.uuid4())
            mqtt_message = {
                "waitResponse": False,
                "messageId": message_id,
                "deviceId": getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.name}/{MQTTCommands.CHECK_SYNC_MQTT_COMMAND}",
                "timestamp": datetime.now().isoformat(),
                "payload": response
            }
            mqtt_object = MQTTMessage(**mqtt_message)
            await self._mqtt_proxy.publish_message(payload=mqtt_object.model_dump())
            
            logger.info(f"Sync status checked for flight record {flight_record_id}: {state.status.value}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking sync status for flight record {flight_record_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error checking sync status",
                headers={"source": "check_sync"}
            )

    #---------------------------- DEBUG Actions ------------------------------#

    @http_action(method="GET", path="/debug/localdb-flight-records")
    async def get_localdb_flight_records(self):
        """Get flight records from local database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        result = await local_db_proxy.scan_items(
            table_name="config-log-flight_record",
            filters=None
        )
        if "error" in result:
            logger.error(f"Error retrieving flight records from local DB: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving flight records from local DB",
                headers={"source": "get_localdb_flight_records"}
            )
        
        return {"localdb_flight_records": result.get("data", []), "count": len(result.get("data", []))}

    @http_action(method="GET", path="/debug/cloud-flight-records")
    async def get_cloud_flight_records(self):
        """Get flight records from cloud database."""
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        result = await cloud_proxy.scan_items(
            table_name="config-log-flight_record",
            filters=None
        )
        if "error" in result:
            logger.error(f"Error retrieving flight records from cloud DB: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving flight records from cloud DB",
                headers={"source": "get_cloud_flight_records"}
            )
        
        return {"cloud_flight_records": result.get("data", []), "count": len(result.get("data", []))}

    @http_action(method="DELETE", path="/debug/localdb-flight-records")
    async def delete_localdb_flight_records(self):
        """Delete all flight records from local database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        try:
            result = await local_db_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            if "error" in result:
                logger.error(f"Error scanning flight records for deletion: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Error scanning flight records for deletion",
                    headers={"source": "delete_localdb_flight_records"}
                )
            
            for item in result.get("data", []):
                item_id = item.get("id")
                if item_id:
                    del_result = await local_db_proxy.delete_item(
                        table_name="config-log-flight_record",
                        filter_key="id",
                        filter_value=item_id
                    )
                    if "error" in del_result:
                        logger.error(f"Error deleting flight record ID {item_id}: {del_result['error']}")
            logger.info("All flight records deleted from local database")
            return {"success": True, "message": "All flight records deleted from local database"}
        except Exception as e:
            logger.error(f"Error deleting flight records from local DB: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting flight records from local DB: {str(e)}",
                headers={"source": "delete_localdb_flight_records"}
            )

    @http_action(method="DELETE", path="/debug/cloud-flight-records")
    async def delete_cloud_flight_records(self):
        """Delete all flight records from local database."""
        cloud_proxy: CloudDBProxy = self._proxies["cloud"]
        try:
            result = await cloud_proxy.scan_items(
                table_name="config-log-flight_record"
            )
            if "error" in result:
                logger.error(f"Error scanning flight records for deletion: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Error scanning flight records for deletion",
                    headers={"source": "delete_cloud_flight_records"}
                )
            
            for item in result.get("data", []):
                item_id = item.get("id")
                if item_id:
                    del_result = await cloud_proxy.delete_item(
                        table_name="config-log-flight_record",
                        filter_key="id",
                        filter_value=item_id
                    )
                    if "error" in del_result:
                        logger.error(f"Error deleting flight record ID {item_id}: {del_result['error']}")
            logger.info("All flight records deleted from cloud database")
            return {"success": True, "message": "All flight records deleted from cloud database"}
        except Exception as e:
            logger.error(f"Error deleting flight records from cloud DB: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting flight records from cloud DB: {str(e)}",
                headers={"source": "delete_cloud_flight_records"}
            )

    @http_action(method="GET", path="/debug/leaf-fc-records")
    async def get_leaf_fc_flight_records(self):
        """Get LeafFC records from local database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        result = await local_db_proxy.scan_items(
            table_name="config-log-leaf_fc_record-edge",
            filters=None
        )
        if "error" in result:
            logger.error(f"Error retrieving LeafFC records from local DB: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving LeafFC records from local DB",
                headers={"source": "get_leaf_fc_flight_records"}
            )
        
        return {"leaf_fc_records": result.get("data", []), "count": len(result.get("data", []))}
    
    @http_action(method="DELETE", path="/debug/leaf-fc-records")
    async def delete_leaf_fc_flight_records(self):
        """Delete all LeafFC records from local database."""
        local_db_proxy: LocalDBProxy = self._proxies["db"]
        try:
            result = await local_db_proxy.scan_items(
                table_name="config-log-leaf_fc_record-edge"
            )
            if "error" in result:
                logger.error(f"Error scanning LeafFC records for deletion: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail="Error scanning LeafFC records for deletion",
                    headers={"source": "delete_leaf_fc_flight_records"}
                )
            
            for item in result.get("data", []):
                item_id = item.get("id")
                if item_id:
                    del_result = await local_db_proxy.delete_item(
                        table_name="config-log-leaf_fc_record-edge",
                        filter_key="id",
                        filter_value=item_id
                    )
                    if "error" in del_result:
                        logger.error(f"Error deleting LeafFC record ID {item_id}: {del_result['error']}")
            logger.info("All LeafFC records deleted from local database")
            return {"success": True, "message": "All LeafFC records deleted from local database"}
        except Exception as e:
            logger.error(f"Error deleting LeafFC records from local DB: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting LeafFC records from local DB: {str(e)}",
                headers={"source": "delete_leaf_fc_flight_records"}
            )

    #------------------------------ S3 Actions -------------------------------#

    @http_action(
        method="POST", 
        path="/s3-upload",
        response_model=S3UploadResponse,
        summary="Start S3 upload (job-based API)",
        description="Start an S3 upload job for the specified file and return job_id for tracking."
    )
    async def start_s3_upload_endpoint(self, file_path: str, s3_key: str) -> S3UploadResponse:
        """Start S3 upload job and return immediately with job_id."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File path {file_path} does not exist")
                raise HTTPException(
                    status_code=404,
                    detail="File path does not exist",
                    headers={"source": "start_s3_upload"}
                )
            
            # Get proxies
            bucket_proxy = self._proxies.get("s3_bucket")
            
            if not bucket_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="S3 bucket proxy not available",
                    headers={"source": "start_s3_upload"}
                )
            
            # Create S3 upload job
            upload_job = S3UploadJob(
                file_path=str(file_path_obj),
                s3_key=s3_key,
                bucket_proxy=bucket_proxy,
                redis_proxy=self._redis_proxy,
                metadata={
                    "file_path": str(file_path_obj),
                    "s3_key": s3_key
                }
            )
            
            # Register with job monitor
            await self._job_monitor.register_job(upload_job)
            
            # Start the upload job
            await upload_job.start()
            
            logger.info(f"S3 upload job started: {upload_job.job_id} for {file_path} -> {s3_key}")
            
            return S3UploadResponse(
                success=True,
                job_id=upload_job.job_id,
                file_path=str(file_path_obj),
                s3_key=s3_key,
                status=upload_job.status.value,
                message="S3 upload started successfully"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting S3 upload: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error starting S3 upload: {str(e)}",
                headers={"source": "start_s3_upload"}
            )

    @http_action(
        method="POST", 
        path="/s3-upload-wait",
        response_model=S3CompleteResponse,
        summary="Start S3 upload and wait for completion (job-based API)",
        description="Start an S3 upload job and wait for it to complete before returning."
    )
    async def s3_upload_and_wait(self, file_path: str, s3_key: str) -> S3CompleteResponse:
        """Start S3 upload job and wait for completion."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File path {file_path} does not exist")
                raise HTTPException(
                    status_code=404,
                    detail="File path does not exist",
                    headers={"source": "s3_upload_and_wait"}
                )
            
            # Get proxies
            bucket_proxy = self._proxies.get("s3_bucket")
            
            if not bucket_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="S3 bucket proxy not available",
                    headers={"source": "s3_upload_and_wait"}
                )
            
            # Create S3 upload job
            upload_job = S3UploadJob(
                file_path=str(file_path_obj),
                s3_key=s3_key,
                bucket_proxy=bucket_proxy,
                redis_proxy=self._redis_proxy,
                metadata={
                    "file_path": str(file_path_obj),
                    "s3_key": s3_key
                }
            )
            
            # Register with job monitor
            await self._job_monitor.register_job(upload_job)
            
            # Start the upload job
            await upload_job.start()
            
            logger.info(f"S3 upload job started: {upload_job.job_id}, waiting for completion...")
            
            # Wait for completion
            await upload_job.wait_for_completion()
            
            if upload_job.status == JobStatus.COMPLETED:
                logger.info(f"S3 upload completed successfully: {s3_key}")
                return S3CompleteResponse(
                    success=True,
                    message="S3 upload completed successfully",
                    s3_key=s3_key
                )
            elif upload_job.status == JobStatus.CANCELLED:
                raise HTTPException(
                    status_code=400,
                    detail="S3 upload was cancelled",
                    headers={"source": "s3_upload_and_wait"}
                )
            else:
                error_msg = upload_job._state.error_message or "Unknown error"
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 upload failed: {error_msg}",
                    headers={"source": "s3_upload_and_wait"}
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during S3 upload: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error starting S3 upload: {str(e)}",
                headers={"source": "s3_upload_and_wait"}
            )

    #--------------------------- MAVFTP Actions ------------------------------#

    @http_action(
        method="POST", 
        path="/start-ulog-download-mavftp",
        response_model=ULogDownloadResponse,
        summary="Start ULog file download from Pixhawk via MAVFTP (job-based API)",
        description="Initiates a ULog download job from the Pixhawk using MAVFTP protocol with the job management system."
    )
    async def start_ulog_download_mavftp(
        self, 
        px4_path: str,
        file_path: str,
        size_bytes: Optional[int] = None
    ) -> ULogDownloadResponse:
        """Start ULog download job from Pixhawk via MAVFTP."""
        try:
            # Get proxies
            mavftp_proxy = self._proxies.get("ftp_mavlink")
            
            if not mavftp_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="MAVFTP proxy not available",
                    headers={"source": "start_ulog_download_mavftp"}
                )
            
            # Ensure directory exists
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Create MAVFTP download job
            download_job = ULogDownloadJobMAVFTP(
                px4_path=px4_path,
                file_path=file_path,
                mavftp_proxy=mavftp_proxy,
                size_bytes=size_bytes,
                redis_proxy=self._redis_proxy,
                websocket_clients=websocket_clients,
                mqtt_proxy=self._mqtt_proxy,
                mqtt_device_id=getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                metadata={
                    "px4_path": px4_path,
                    "file_path": file_path,
                    "size_bytes": size_bytes
                }
            )
            
            # Register with job monitor
            await self._job_monitor.register_job(download_job)
            
            # Start the download job
            await download_job.start()
            
            logger.info(f"MAVFTP download job started: {download_job.job_id} for {px4_path} -> {file_path}")
            
            return ULogDownloadResponse(
                success=True,
                job_id=download_job.job_id,
                px4_path=px4_path,
                file_path=file_path,
                status=download_job.status.value,
                message="ULog download started successfully"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting MAVFTP download: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error starting ULog download: {str(e)}",
                headers={"source": "start_ulog_download_mavftp"}
            )

    @http_action(
        method="POST",
        path="/px4-log-download-mavftp",
        summary="Download PX4 flight log and wait for completion (job-based API)",
        description="Download a specific PX4 flight log file via MAVFTP using the job system and wait for completion.",
        response_model=PX4LogCompletedResponse,
        status_code=200,
    )
    async def download_px4_log_mavftp(
        self,
        px4_path: str, 
        file_path: str, 
        size_bytes: Optional[int] = None
    ) -> PX4LogCompletedResponse:
        """Download a specific PX4 flight log file via MAVFTP and wait for completion."""
        try:
            # Get proxies
            mavftp_proxy = self._proxies.get("ftp_mavlink")
            
            if not mavftp_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="MAVFTP proxy not available",
                    headers={"source": "download_px4_log_mavftp"}
                )
            
            # Ensure directory exists
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Create MAVFTP download job
            download_job = ULogDownloadJobMAVFTP(
                px4_path=px4_path,
                file_path=file_path,
                mavftp_proxy=mavftp_proxy,
                size_bytes=size_bytes,
                redis_proxy=self._redis_proxy,
                websocket_clients=websocket_clients,
                mqtt_proxy=self._mqtt_proxy,
                mqtt_device_id=getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                metadata={
                    "px4_path": px4_path,
                    "file_path": file_path,
                    "size_bytes": size_bytes
                }
            )
            
            # Register with job monitor
            await self._job_monitor.register_job(download_job)
            
            # Start the download job
            await download_job.start()
            
            logger.info(f"MAVFTP download job started: {download_job.job_id}, waiting for completion...")
            
            # Wait for completion
            await download_job.wait_for_completion()
            
            if download_job.status == JobStatus.COMPLETED:
                logger.info(f"MAVFTP download completed successfully: {file_path}")
                return PX4LogCompletedResponse(
                    success=True,
                    message="PX4 log download completed",
                    file_path=file_path
                )
            elif download_job.status == JobStatus.CANCELLED:
                raise HTTPException(
                    status_code=400,
                    detail="Download was cancelled",
                    headers={"source": "download_px4_log_mavftp"}
                )
            else:
                error_msg = download_job._state.error_message or "Unknown error"
                raise HTTPException(
                    status_code=500,
                    detail=f"Download failed: {error_msg}",
                    headers={"source": "download_px4_log_mavftp"}
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during MAVFTP download: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading ULog: {str(e)}",
                headers={"source": "download_px4_log_mavftp"}
            )

    #-------------------------- PX4 support actions --------------------------#

    @http_action(
        method="GET", 
        path="/get-px4-time",
        summary="Get PX4 time",
        description="Retrieve the PX4 autopilot time using MAVLink.",
        response_model=Dict[str, Any],
        status_code=200,
        responses={
            200: {
                "description": "Successfully retrieved PX4 time",
                "content": {
                    "application/json": {
                        "example": {
                            "timestamp_s": 1718593200,
                            "utc_human": "2025-06-16 14:30:00",
                            "source_msg": "AUTOPILOT_VERSION"
                        }
                    }
                }
            },
            404: {
                "description": "PX4 time not found",
                "content": {
                    "application/json": {
                        "example": {"error": "No valid PX4 time information found"}
                    }
                }
            },
            500: {
                "description": "Server error",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to retrieve PX4 time"}
                    }
                }
            },
            504: {
                "description": "Timeout while waiting for PX4 time",
                "content": {
                    "application/json": {
                        "example": {"error": "Timeout while waiting for PX4 time"}
                    }
                }
            }
        }
    )
    async def get_px4_time(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Return PX4 time (best-effort) using the new proxy infrastructure.
        """
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]

        try:
            msg_id = str(mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION)
            msg = mavlink_proxy.build_req_msg_long(message_id=msg_id)
            msg = await self.get_message(msg_id=msg_id, request_msg=msg, timeout=timeout)

            # ---- identical timestamp extraction logic to your original function ----
            if hasattr(msg, "time_utc") and msg.time_utc:
                ts = int(msg.time_utc)
                logger.debug(f"PX4 time_utc: {ts}")
                return dict(
                    time_unix_usec=ts * 1_000_000,
                    time_boot_ms=None,
                    timestamp_s=ts,
                    utc_human=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
                    source_msg="AUTOPILOT_VERSION",
                )

            # fallbacks
            for fld in ("time_boot_ms", "time_usec", "_timestamp"):
                if hasattr(msg, fld):
                    raw = getattr(msg, fld)
                    ts = int(
                        raw
                        / (
                            1000
                            if fld == "time_boot_ms"
                            else 1_000_000
                            if fld == "time_usec"
                            else 1
                        )
                    )
                    logger.debug(f"PX4 {fld}: {ts}")
                    return dict(
                        time_unix_usec=raw,
                        time_boot_ms=raw if fld == "time_boot_ms" else None,
                        timestamp_s=ts,
                        utc_human=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
                        source_msg=f"AUTOPILOT_VERSION[{fld}]",
                    )
            logger.error("No valid PX4 time information found in AUTOPILOT_VERSION message")
            raise HTTPException(
                status_code=404, 
                detail="No valid PX4 time information found",
                headers={"source_msg": "AUTOPILOT_VERSION (no time fields available)"}
            )
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 time: {str(exc)}")
            raise HTTPException(
                status_code=504, 
                detail=str(exc),
                headers={"source": "get_px4_time"}
            )
        except Exception as exc:
            logger.error(f"Unexpected error while waiting for PX4 time: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=str(exc),
                headers={"source": "get_px4_time"}
            )

    @http_action(
        method="GET",
        path="/px4-log-entries",
        summary="Get flight-log directory",
        description="Return the list of available ULog files on the PX4 SD card.",
        response_model=Dict[int, Dict[str, int]],
        status_code=200,
    )
    async def px4_log_entries(self, timeout: float = 8.0):
        mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]
        try:
            msg_id = str(mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY)
            msg = mavlink_proxy.build_req_msg_log_request(message_id=msg_id)
            msg =  await mavlink_proxy.get_log_entries(msg_id=msg_id, request_msg=msg, timeout=timeout)
            if not msg:
                logger.error("No log entries found in PX4 logs")
                raise HTTPException(
                    status_code=404, 
                    detail="No log entries found",
                    headers={"source": "px4_log_entries"}
                )
            return msg
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 log entries: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))
        except Exception as exc:
            logger.error(f"Unexpected error while waiting for PX4 log entries: {str(exc)}")
            raise HTTPException(status_code=500, detail=str(exc))

    #------------------------ Mavlink External Actions -----------------------#

    @http_action(
        method="POST",
        path="/px4-log-start-mavlink/{log_id}",
        response_model=ULogDownloadResponse,
        summary="Start PX4 flight log download via MAVLink (job-based API)",
        description="Initiates a ULog download job from PX4 SD card via MAVLink LOG_DATA stream using the job management system.",
        status_code=200,
    )
    async def px4_log_start_download_mavlink(self, log_id: int, timeout: float = 8.0, timeout_log_entries: float = 3.0) -> ULogDownloadResponse:
        """Start PX4 log download job via MAVLink."""
        try:
            mavlink_proxy: MavLinkExternalProxy = self._proxies.get("ext_mavlink")
            
            if not mavlink_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="MAVLink proxy not available",
                    headers={"source": "px4_log_start_download_mavlink"}
                )

            home_dir = os.path.expanduser("~")
            local_dir = os.path.join(home_dir, "ulog_records")
            os.makedirs(local_dir, exist_ok=True)

            # Get log entries to determine size and filename
            entries = await mavlink_proxy.get_log_entries(
                msg_id=str(mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY),
                request_msg=mavlink_proxy.build_req_msg_log_request(
                    message_id=mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY
                ),
                timeout=timeout_log_entries,
            )

            entry = entries.get(log_id) or entries.get(str(log_id))
            if not entry:
                raise HTTPException(
                    status_code=404,
                    detail=f"Log id {log_id} not found",
                    headers={"source": "px4_log_start_download_mavlink"},
                )

            # Convert UTC timestamp to formatted date
            timestamp = entry["utc"]
            est_timestamp = timestamp - (5 * 3600)  # Subtract 5 hours in seconds
            dt = datetime.fromtimestamp(est_timestamp)
            date = dt.isoformat().replace('-', '-').replace(':', '-').replace('T', '-').split('.')[0]            

            local_filename = f"log_{log_id}_{date}.ulg"
            local_path = os.path.join(local_dir, local_filename)
            size_bytes = entry["size"]

            # Create MAVLink download job
            download_job = ULogDownloadJobMAVLink(
                log_id=log_id,
                file_path=local_path,
                mavlink_proxy=mavlink_proxy,
                size_bytes=size_bytes,
                redis_proxy=self._redis_proxy,
                timeout=timeout,
                websocket_clients=websocket_clients,
                mqtt_proxy=self._mqtt_proxy,
                mqtt_device_id=getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                metadata={
                    "log_id": log_id,
                    "file_path": local_path,
                    "size_bytes": size_bytes
                }
            )

            # Register with job monitor
            await self._job_monitor.register_job(download_job)

            # Start the download job
            await download_job.start()

            logger.info(f"MAVLink download job started: {download_job.job_id} for log_id={log_id} -> {local_path}")

            return ULogDownloadResponse(
                success=True,
                job_id=download_job.job_id,
                px4_path=f"log_id_{log_id}",
                file_path=local_path,
                status=download_job.status.value,
                message="PX4 log download started successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting MAVLink download: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error starting PX4 log download: {str(e)}",
                headers={"source": "px4_log_start_download_mavlink"}
            )

    @http_action(
        method="POST",
        path="/px4-log-download-mavlink/{log_id}",
        summary="Download PX4 flight log and wait for completion (job-based API)",
        description="Download a specific PX4 flight log file via MAVLink using the job system and wait for completion.",
        response_model=PX4LogCompletedResponse,
        status_code=200,
    )
    async def download_px4_log_mavlink(self, log_id: int, timeout: float = 8.0, timeout_log_entries: float = 3.0) -> PX4LogCompletedResponse:
        """Download a specific PX4 flight log file via MAVLink and wait for completion."""
        try:
            mavlink_proxy: MavLinkExternalProxy = self._proxies.get("ext_mavlink")
            
            if not mavlink_proxy:
                raise HTTPException(
                    status_code=500,
                    detail="MAVLink proxy not available",
                    headers={"source": "download_px4_log_mavlink"}
                )

            home_dir = os.path.expanduser("~")
            local_dir = os.path.join(home_dir, "ulog_records")
            os.makedirs(local_dir, exist_ok=True)

            # Get log entries
            try:
                entries = await mavlink_proxy.get_log_entries(
                    msg_id=str(mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY),
                    request_msg=mavlink_proxy.build_req_msg_log_request(
                        message_id=mavutil.mavlink.MAVLINK_MSG_ID_LOG_ENTRY
                    ),
                    timeout=timeout_log_entries,
                )
            except TimeoutError as exc:
                logger.error(f"Timeout while retrieving PX4 log entries: {exc}")
                raise HTTPException(status_code=504, detail=str(exc))

            entry = entries.get(log_id) or entries.get(str(log_id))
            if not entry:
                raise HTTPException(
                    status_code=404,
                    detail=f"Log id {log_id} not found",
                    headers={"source": "download_px4_log_mavlink"},
                )

            # Build file path
            timestamp = entry["utc"]
            est_timestamp = timestamp - (5 * 3600)
            dt = datetime.fromtimestamp(est_timestamp)
            date = dt.isoformat().replace('-', '-').replace(':', '-').replace('T', '-').split('.')[0]
            local_filename = f"log_{log_id}_{date}.ulg"
            local_path = os.path.join(local_dir, local_filename)
            size_bytes = entry["size"]

            # Create MAVLink download job
            download_job = ULogDownloadJobMAVLink(
                log_id=log_id,
                file_path=local_path,
                mavlink_proxy=mavlink_proxy,
                size_bytes=size_bytes,
                redis_proxy=self._redis_proxy,
                timeout=timeout,
                websocket_clients=websocket_clients,
                mqtt_proxy=self._mqtt_proxy,
                mqtt_device_id=getattr(self._mqtt_proxy, 'device_id', 'unknown'),
                metadata={
                    "log_id": log_id,
                    "file_path": local_path,
                    "size_bytes": size_bytes
                }
            )

            # Register with job monitor
            await self._job_monitor.register_job(download_job)

            # Start and wait for completion
            await download_job.start()
            logger.info(f"MAVLink download job started: {download_job.job_id}, waiting for completion...")
            
            await download_job.wait_for_completion()

            if download_job.status == JobStatus.COMPLETED:
                logger.info(f"MAVLink download completed successfully: {local_path}")
                return PX4LogCompletedResponse(
                    success=True,
                    message="PX4 log download completed",
                    file_path=local_path
                )
            elif download_job.status == JobStatus.CANCELLED:
                raise HTTPException(
                    status_code=400,
                    detail="Download was cancelled",
                    headers={"source": "download_px4_log_mavlink"}
                )
            else:
                error_msg = download_job._state.error_message or "Unknown error"
                raise HTTPException(
                    status_code=500,
                    detail=f"Download failed: {error_msg}",
                    headers={"source": "download_px4_log_mavlink"}
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during MAVLink download: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading PX4 log: {str(e)}",
                headers={"source": "download_px4_log_mavlink"}
            )
    
    # ======================== JOB MANAGEMENT ENDPOINTS ========================
    
    @http_action(
        method="GET",
        path="/jobs/{job_id}/status",
        response_model=Dict[str, Any],
        summary="Get job status (new job-based API)",
        description="Get the status of a job by its ID."
    )
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a job.
        
        Returns:
            Dictionary with job status and progress information
        """
        try:
            # Get job state from Redis (single source of truth)
            state = await self._job_monitor.get_job_state(job_id)
            if not state:
                raise HTTPException(
                    status_code=404,
                        detail=f"Job not found: {job_id}",
                        headers={"source": "get_job_status"}
                    )
            
            # Return status information
            return {
                "success": True,
                "job_id": state.job_id,
                "job_type": state.job_type,
                "status": state.status.value,
                "progress": {
                    "percentage": state.progress.percentage,
                    "current": state.progress.current,
                    "total": state.progress.total,
                    "message": state.progress.message,
                    "rate_kbps": state.progress.rate_kbps
                } if state.progress else None,
                "created_at": datetime.fromtimestamp(state.created_at).isoformat(),
                "updated_at": datetime.fromtimestamp(state.updated_at).isoformat(),
                "error_message": state.error_message,
                "metadata": state.metadata
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting job status: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error getting job status: {str(e)}",
                headers={"source": "get_job_status"}
            )
    
    @http_action(
        method="POST",
        path="/jobs/{job_id}/cancel",
        response_model=Dict[str, Any],
        summary="Cancel a job (new job-based API)",
        description="Cancel a running job by its ID."
    )
    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a job.
        
        Returns:
            Dictionary with cancellation status
        """
        try:
            success = await self._job_monitor.cancel_job(job_id)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Job not found or cannot be cancelled: {job_id}",
                    headers={"source": "cancel_job"}
                )
            
            logger.info(f"Job cancelled: {job_id}")
            
            return {
                "success": True,
                "job_id": job_id,
                "status": "cancelled",
                "message": "Job cancelled successfully"
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling job: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error cancelling job: {str(e)}",
                headers={"source": "cancel_job"}
            )
    
    @http_action(
        method="GET",
        path="/jobs",
        response_model=Dict[str, Any],
        summary="List all jobs (new job-based API)",
        description="Get a list of all jobs, optionally filtered by status or type."
    )
    async def list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all jobs, optionally filtered.
        
        Args:
            status: Filter by status (pending, in_progress, completed, cancelled, error)
            job_type: Filter by job type (S3UploadJob, ULogDownloadJobMAVLink, etc.)
        
        Returns:
            Dictionary with list of jobs
        """
        try:
            # Get all job states from Redis
            if status:
                try:
                    status_enum = JobStatus(status)
                    job_states = await self._job_monitor.get_jobs_by_status(status_enum)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid status: {status}",
                        headers={"source": "list_jobs"}
                    )
            elif job_type:
                job_states = await self._job_monitor.get_jobs_by_type(job_type)
            else:
                job_states = await self._job_monitor.get_all_job_states()
            
            # Convert to response format
            job_list = []
            for state in job_states:
                job_list.append({
                    "job_id": state.job_id,
                    "job_type": state.job_type,
                    "status": state.status.value,
                    "progress_percentage": state.progress.percentage if state.progress else 0.0,
                    "created_at": datetime.fromtimestamp(state.created_at).isoformat(),
                    "updated_at": datetime.fromtimestamp(state.updated_at).isoformat(),
                    "metadata": state.metadata
                })
            
            # Sort by created_at descending (newest first)
            job_list.sort(key=lambda x: x["created_at"], reverse=True)
            
            return {
                "success": True,
                "count": len(job_list),
                "jobs": job_list
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing jobs: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error listing jobs: {str(e)}",
                headers={"source": "list_jobs"}
            )
    
    @http_action(
        method="GET",
        path="/jobs/statistics",
        response_model=Dict[str, Any],
        summary="Get job statistics (new job-based API)",
        description="Get statistics about jobs (counts by status, type, etc.)."
    )
    async def get_job_statistics(self) -> Dict[str, Any]:
        """
        Get job statistics.
        
        Returns:
            Dictionary with job statistics
        """
        try:
            stats = await self._job_monitor.get_statistics()
            return {
                "success": True,
                **stats
            }
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error getting job statistics: {str(e)}",
                headers={"source": "get_job_statistics"}
            )
    
    @http_action(
        method="POST",
        path="/jobs/cleanup",
        response_model=Dict[str, Any],
        summary="Cleanup completed jobs (new job-based API)",
        description="Remove completed jobs older than specified age."
    )
    async def cleanup_jobs(self, max_age_hours: float = 24.0) -> Dict[str, Any]:
        """
        Cleanup old completed jobs.
        
        Args:
            max_age_hours: Maximum age in hours for completed jobs to keep
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            removed = await self._job_monitor.cleanup_completed_jobs(max_age_seconds=max_age_hours * 3600)
            logger.info(f"Cleaned up {removed} old jobs")
            
            return {
                "success": True,
                "removed_count": removed,
                "max_age_hours": max_age_hours
            }
        except Exception as e:
            logger.error(f"Error cleaning up jobs: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error cleaning up jobs: {str(e)}",
                headers={"source": "cleanup_jobs"}
            )