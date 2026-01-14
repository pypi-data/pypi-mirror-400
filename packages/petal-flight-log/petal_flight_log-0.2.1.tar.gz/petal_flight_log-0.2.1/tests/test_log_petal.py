from __future__ import annotations
import asyncio, sys, time, uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, AsyncMock
from petal_flight_log.plugin import FlightLogPetal, MQTTCommands, RedisChannels
from petal_app_manager.proxies.localdb import LocalDBProxy

from fastapi import HTTPException

import pytest


class TestFlightLogPetalInitialization:
    """Test petal initialization and basic configuration."""
    
    def test_petal_initialization(self):
        """Test that the petal initializes with correct defaults."""
        petal = FlightLogPetal()
        
        assert petal.name == "petal-flight-log"
        assert petal.version == "1.0.0"
        assert petal.use_mqtt_proxy is True
        assert petal._mqtt_proxy is None  # Not set until startup
        assert petal._redis_proxy is None  # Not set until startup
        assert petal._job_monitor is None  # Not set until startup
        assert petal._active_handlers == {}
    
    def test_mqtt_commands_constants(self):
        """Test that MQTT command constants are properly defined."""
        assert MQTTCommands.FETCH_FLIGHT_RECORDS_COMMAND == "fetch_flight_records"
        assert MQTTCommands.PX4_LOG_DOWNLOAD_PROGRESS_COMMAND == "log_download/progress"
        assert MQTTCommands.S3_UPLOAD_PROGRESS_COMMAND == "s3_upload/progress"
        assert MQTTCommands.FLIGHT_RECORD_SYNC_PROGRESS_COMMAND == "publish_sync_job_value_stream"
        assert MQTTCommands.CANCEL_DOWNLOAD_MQTT_COMMAND == "cancel_log_download"
        assert MQTTCommands.CANCEL_S3_UPLOAD_MQTT_COMMAND == "cancel_s3_upload"
        assert MQTTCommands.CANCEL_SYNC_MQTT_COMMAND == "cancel_sync_job"
    
    def test_redis_channels_constants(self):
        """Test that Redis channel constants are properly defined."""
        assert RedisChannels.REDIS_CMD_CHANNEL == "/petal/petal_flight_log/cmd"
        assert RedisChannels.REDIS_ACK_CHANNEL == "/petal/petal_flight_log/ack"


class TestFlightLogPetalStartup:
    """Test petal startup behavior."""
    
    def test_startup_sets_status_message(self):
        """Test that startup sets the status message."""
        petal = FlightLogPetal()
        
        # Mock the proxies that startup expects
        mock_mqtt_proxy = MagicMock()
        mock_redis_proxy = MagicMock()
        petal._proxies = {
            "mqtt": mock_mqtt_proxy,
            "redis": mock_redis_proxy
        }
        
        petal.startup()
        
        assert "Flight Log Petal started" in petal._status_message
        assert petal._startup_time is not None
        assert petal._mqtt_proxy == mock_mqtt_proxy
        assert petal._redis_proxy == mock_redis_proxy
        assert petal._job_monitor is not None


class TestFlightLogPetalDataModels:
    """Test data model imports and validation."""
    
    def test_data_model_imports(self):
        """Test that all required data models can be imported."""
        from petal_flight_log.data_model import (
            GetFlightRecordsRequest,
            GetFlightRecordsResponse,
            GetExistingFlightRecordsResponse,
            FlightRecordMatch,
            ExistingFlightRecordMatch,
            RosbagFileRecord,
            UlogFileRecord,
            LeafFCRecord,
            DeleteFlightRecordRequest,
            DeleteFlightRecordResponse,
            StartFlightRecordSyncRequest,
            StartFlightRecordSyncResponse,
        )
        
        # Just verify they're importable
        assert GetFlightRecordsRequest is not None
        assert GetFlightRecordsResponse is not None
        assert FlightRecordMatch is not None
    
    def test_get_flight_records_request_validation(self):
        """Test GetFlightRecordsRequest model validation."""
        from petal_flight_log.data_model import GetFlightRecordsRequest
        
        # Valid request
        request = GetFlightRecordsRequest(
            tolerance_seconds=30,
            start_time="2024-01-15T14:00:00Z",
            end_time="2024-01-15T16:00:00Z",
            base="fs/microsd/log"
        )
        assert request.tolerance_seconds == 30
        assert request.start_time == "2024-01-15T14:00:00Z"
    
    def test_delete_flight_record_request_validation(self):
        """Test DeleteFlightRecordRequest model validation."""
        from petal_flight_log.data_model import DeleteFlightRecordRequest
        
        request = DeleteFlightRecordRequest(
            flight_record_id="f47ac10b-58cc-4372-a567-0e02b2c3d479"
        )
        assert request.flight_record_id == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    
    def test_start_flight_record_sync_request_validation(self):
        """Test StartFlightRecordSyncRequest model validation."""
        from petal_flight_log.data_model import StartFlightRecordSyncRequest
        
        request = StartFlightRecordSyncRequest(
            flight_record_id="test-flight-record-id"
        )
        assert request.flight_record_id == "test-flight-record-id"