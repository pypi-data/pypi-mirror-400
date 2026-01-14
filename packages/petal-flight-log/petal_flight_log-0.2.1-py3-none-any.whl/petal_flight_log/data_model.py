
import asyncio
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid

# ========================= Redis Command Models =========================

class RedisCommandPayload(BaseModel):
    """Incoming Redis command message."""
    message_id: str
    command: str
    payload: Optional[Dict[str, Any]] = None


class RedisAckPayload(BaseModel):
    """Redis acknowledgment response."""
    message_id: Optional[str]
    command: str
    status: Literal["success", "error"]
    result: Optional[str] = None
    error: Optional[str] = None
    source: str = "petal-flight-log"

    @classmethod
    def success(cls, message_id: Optional[str], command: str, result: str) -> "RedisAckPayload":
        return cls(message_id=message_id, command=command, status="success", result=result)

    @classmethod
    def failure(cls, message_id: Optional[str], command: str, error: str) -> "RedisAckPayload":
        return cls(message_id=message_id, command=command, status="error", error=error)

# =========================== Request Models =============================

class GetFlightRecordsRequest(BaseModel):
    """Request model for get_flight_records command"""
    tolerance_seconds: int = Field(default=30, ge=1, le=300, description="Tolerance for timestamp matching in seconds (1-300)")
    start_time: Optional[str] = Field(..., description="Start time in ISO format (e.g., '2024-01-15T14:00:00Z')")
    end_time: Optional[str] = Field(..., description="End time in ISO format (e.g., '2024-01-15T16:00:00Z')")
    base: Optional[str] = Field(..., description="Base directory for file searches")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tolerance_seconds": 30,
                "start_time": "2024-01-15T14:00:00Z",
                "end_time": "2024-01-15T16:00:00Z",
                "base": "fs/microsd/log"
            }
        }
    }


class StartFlightRecordSyncRequest(BaseModel):
    """Request model for starting flight record sync"""
    flight_record_id: str = Field(..., description="Unique identifier for the flight record to sync")


class DeleteFlightRecordRequest(BaseModel):
    """Request model for deleting a flight record"""
    flight_record_id: str = Field(..., description="Unique identifier for the flight record to delete")

    model_config = {
        "json_schema_extra": {
            "example": {
                "flight_record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            }
        }
    }


class UlogFileRecord(BaseModel):
    """Model for individual file records"""
    id: str = Field(..., description="Unique file identifier")
    file_name: str = Field(..., description="Name of the file")
    file_path: Optional[str] = Field(None, description="Path to the file")
    file_type: Literal["ulg"] = Field(..., description="Type of file (ulg)")
    sd_card_path: str = Field(None, description="Path on the SD card")
    storage_type: Literal["pixhawk", "local"] = Field(..., description="Storage location (pixhawk, local)")
    size_bytes: int = Field(..., description="File size in bytes")
    size_kb: float = Field(..., description="File size in kilobytes")
    modified_timestamp_unix_s: int = Field(..., description="Unix timestamp of last modification")
    creation_timestamp_unix_s: Optional[int] = Field(None, description="Unix timestamp of file creation")
    log_duration_seconds: Optional[float] = Field(None, description="Duration of the log in seconds")
    date_str: str = Field(..., description="Human readable date string")
    qgc_index: Optional[int] = Field(None, description="QGroundControl log index")
    qgc_name: Optional[str] = Field(None, description="QGroundControl log name")
    s3_key: Optional[str] = Field(None, description="S3 key if stored in S3")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "file_name": "log_44_2024-01-15-14-30-22.ulg",
                "file_path": "/opt/log_44_2024-01-15-14-30-22.ulg",
                "file_type": "ulg",
                "sd_card_path": "/log/01-15-14/14-30-22.ulg",
                "storage_type": "pixhawk",
                "size_bytes": 1048576,
                "size_kb": 1024.0,
                "modified_timestamp_unix_s": 1705323022,
                "creation_timestamp_unix_s": 1705323022,
                "log_duration_seconds": 3600.0,
                "date_str": "2024-01-15-14-30-22",
                "qgc_index": 44,
                "qgc_name": "log_44_2024-01-15-14-30-22.ulg",
                "s3_key": "some/s3/key/for/log_44_2024-01-15-14-30-22.ulg"
            }
        }
    }


class RosbagFileRecord(BaseModel):
    """Model for individual file records"""
    id: str = Field(..., description="Unique file identifier")
    file_name: str = Field(..., description="Name of the file")
    file_path: str = Field(..., description="Path to the file")
    file_type: Literal["bag"] = Field(..., description="Type of file (bag)")
    storage_type: Literal["pixhawk", "local"] = Field(..., description="Storage location (pixhawk, local)")
    size_bytes: int = Field(..., description="File size in bytes")
    size_kb: float = Field(..., description="File size in kilobytes")
    modified_timestamp_unix_s: int = Field(..., description="Unix timestamp of last modification")
    creation_timestamp_unix_s: int = Field(..., description="Unix timestamp of file creation")
    log_duration_seconds: float = Field(..., description="Duration of the log in seconds")
    date_str: str = Field(..., description="Human readable date string")
    s3_key: Optional[str] = Field(None, description="S3 key if stored in S3")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "file_name": "log_44_2024-01-15-14-30-22.ulg",
                "file_path": "/opt/log_44_2024-01-15-14-30-22.ulg",
                "file_type": "ulg",
                "storage_type": "pixhawk",
                "size_bytes": 1048576,
                "size_kb": 1024.0,
                "modified_timestamp_unix_s": 1705323022,
                "creation_timestamp_unix_s": 1705323022,
                "log_duration_seconds": 3600.0,
                "date_str": "2024-01-15-14-30-22",
                "s3_key": "some/s3/key/for/log_44_2024-01-15-14-30-22.ulg"
            }
        }
    }


class AnalysisRosbagFileRecord(BaseModel):
    """Model for individual file records"""
    id: str = Field(..., description="Unique file identifier")
    file_name: str = Field(..., description="Name of the file")
    size_bytes: int = Field(..., description="File size in bytes")
    size_kb: float = Field(..., description="File size in kilobytes")
    modified_timestamp_unix_s: int = Field(..., description="Unix timestamp of last modification")
    creation_timestamp_unix_s: int = Field(..., description="Unix timestamp of file creation")
    date_str: str = Field(..., description="Human readable date string")
    s3_key: Optional[str] = Field(None, description="S3 key if stored in S3")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "file_name": "log_44_2024-01-15-14-30-22.ulg",
                "size_bytes": 1048576,
                "size_kb": 1024.0,
                "modified_timestamp_unix_s": 1705323022,
                "creation_timestamp_unix_s": 1705323022,
                "log_duration_seconds": 3600.0,
                "date_str": "2024-01-15-14-30-22",
                "s3_key": "some/s3/key/for/log_44_2024-01-15-14-30-22.ulg"
            }
        }
    }


class FlightContext(BaseModel):
    """Model for flight context"""
    environment: Optional[str] = Field(None, description="Flight environment, e.g., Bench, SITL, Real hardware")
    profile: Optional[str] = Field(None, description="Flight profile, e.g., indoor, outdoor")
    n_ekf: Optional[int] = Field(None, description="Number of EKF instances used during the flight")


class PreFlightLeafFCRecord(BaseModel):
    """Model for pre-flight Leaf FC record"""
    flight_mode: Optional[str] = Field(None, description="Flight mode during the record, e.g., RC Position, RC Stabilized, LeafSDK Mission, etc.")
    flight_context: Optional[FlightContext] = Field(None, description="Additional context for the flight e.g., Bench, SITL, Real hardware")
    dev_context: Optional[Dict[str, Any]] = Field(None, description="Development context information, e.g., debug, release, etc.")
    profile_client: Optional[Dict[str, Any]] = Field(None, description="Client profile information")
    profile_location: Optional[Dict[str, Any]] = Field(None, description="Client location information")
    leaf_fc_version: Optional[str] = Field(None, description="Version of the Leaf FC firmware")
    petal_app_manager_version: Optional[str] = Field(None, description="Version of the Petal App Manager used")
    px4_version: Optional[str] = Field(None, description="Version of the PX4 firmware used")
    controller_dashboard_version: Optional[str] = Field(None, description="Version of the controller dashboard used")

    model_config = {
        "json_schema_extra": {
            "example": {
                "flight_mode": "RC Position",
                "flight_context": {"environment": "Real hardware", "profile": "indoor", "n_ekf": 2},
                "dev_context": {"build": "release"},
                "profile_client": {"client_id": "client-123"},
                "profile_location": {"latitude": 37.7749, "longitude": -122.4194},
                "leaf_fc_version": "1.2.3",
                "petal_app_manager_version": "4.5.6",
                "px4_version": "1.12.0",
                "controller_dashboard_version": "2.3.4"
            }
        }
    }


class PostFlightLeafFCRecord(BaseModel):
    """Model for post-flight Leaf FC record"""
    stopping_timestamp: Optional[int] = Field(None, description="Unix timestamp when the flight was stopped")
    flight_time_seconds: Optional[float] = Field(None, description="Total flight time in seconds")
    ground_time_seconds: Optional[float] = Field(None, description="Total ground time in seconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "stopping_timestamp": 1705326625,
                "flight_time_seconds": 3600.0,
                "ground_time_seconds": 300.0
            }
        }
    }


class LeafFCRecord(BaseModel):
    """Model for Leaf FC flight record"""
    id: str = Field(..., description="Unique Leaf FC record identifier")
    bag_name: str = Field(..., description="Name of the Leaf FC bag")
    record_timestamp_unix_s: int = Field(..., description="Unix timestamp of the Leaf FC record")
    preflight_data: Optional[PreFlightLeafFCRecord] = Field(None, description="Pre-flight data associated with the Leaf FC record")
    postflight_data: Optional[PostFlightLeafFCRecord] = Field(None, description="Post-flight data associated with the Leaf FC record")

    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "12456789-e5f6-7890-abcd-1234567890ab",
                "bag_name": "LeafFC_Flight_2024-01-15-14-30-25.bag",
                "record_timestamp_unix_s": 1705323025,
                "preflight_data": {
                    "flight_mode": "RC Position",
                    "flight_context": {"environment": "Real hardware", "profile": "indoor", "n_ekf": 2},
                    "dev_context": {"build": "release"},
                    "profile_client": {"client_id": "client-123"},
                    "profile_location": {"latitude": 37.7749, "longitude": -122.4194},
                    "leaf_fc_version": "1.2.3",
                    "petal_app_manager_version": "4.5.6",
                    "px4_version": "1.12.0",
                    "controller_dashboard_version": "2.3.4"
                },
                "postflight_data": {
                    "stopping_timestamp": 1705326625,
                    "flight_time_seconds": 3600.0,
                    "ground_time_seconds": 300.0
                }
            }
        }
    }


class FlightRecordMatch(BaseModel):
    """Model for matched flight records"""
    id: str = Field(..., description="Unique flight record match identifier")
    ulog: Optional[UlogFileRecord] = Field(None, description="Matched ulog file (if found)")
    rosbag: Optional[RosbagFileRecord] = Field(None, description="Matched rosbag file (if found)")
    leaf_fc_record: Optional[LeafFCRecord] = Field(None, description="Matched Leaf FC record (if found)")
    analysis_rosbag: Optional[AnalysisRosbagFileRecord] = Field(None, description="Generated analysis rosbag file (if any)")
    analysis_results: Optional[Dict[str, Any]] = Field(None, description="Results from analysis processing")
    time_difference_seconds: Optional[float] = Field(None, description="Time difference between ulog and rosbag in seconds")
    arming_date_str: Optional[str] = Field(None, description="Arming date string from ulog metadata in YYYY-MM-DD format")
    arming_time_str: Optional[str] = Field(None, description="Arming time string from ulog metadata in HH:MM:SS format")
    disarming_date_str: Optional[str] = Field(None, description="Disarming date string from ulog metadata in YYYY-MM-DD format")
    disarming_time_str: Optional[str] = Field(None, description="Disarming time string from ulog metadata in HH:MM:SS format")
    log_duration_seconds: Optional[float] = Field(None, description="Duration of the log in seconds from ulog metadata")
    status: Optional[str] = Field(None, description="Status of the match (e.g., unavailable ulog, unavailable rosbag, unavailable leaf_fc_record, complete)")
    robot_instance_id: str = Field(..., description="Robot instance ID associated with the flight record")
    sync_job_status: Literal["pending", "in_progress", "completed", "cancelled", "error"] = Field(
        "unknown", description="Status of the sync job"
    )
    sync_job_id: Optional[str] = Field(None, description="Job ID for the sync operation (if applicable)")
    analysis_job_status: Literal["pending", "in_progress", "completed", "cancelled", "error"] = Field(
        "unknown", description="Status of the analysis job"
    )
    analysis_job_id: Optional[str] = Field(None, description="Job ID for the analysis operation (if applicable)")
    analysis_id: Optional[str] = Field(None, description="Identifier for the analysis results record (if applicable)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "23456789-e5f6-7890-abcd-1234567890ab",
                    "ulog": {
                        "id": "3456789-e5f6-7890-abcd-1234567890ab",
                        "file_name": "log_44_2024-01-15-14-30-22.ulg",
                        "file_path": "/opt/log_44_2024-01-15-14-30-22.ulg",
                        "file_type": "ulg",
                        "storage_type": "pixhawk",
                        "size_bytes": 1048576,
                        "size_kb": 1024.0,
                        "modified_timestamp_unix_s": 1705323022,
                        "creation_timestamp_unix_s": 1705323022,
                        "log_duration_seconds": 3600.0,
                        "date_str": "2024-01-15-14-30-22",
                        "qgc_index": 44,
                        "qgc_name": "log_44_2024-01-15-14-30-22.ulg",
                        "s3_key": "some/s3/key/for/log_44_2024-01-15-14-30-22.ulg"
                    },
                    "rosbag": {
                        "id": "7556789-e5f6-7890-abcd-1234567890ab",
                        "file_name": "flight_2024_01_15_14_30_25.bag",
                        "file_path": "/home/root/rosbag_records/flight_2024_01_15_14_30_25.bag",
                        "file_type": "bag",
                        "storage_type": "local",
                        "size_bytes": 2048576,
                        "size_kb": 2000.0,
                        "modified_timestamp_unix_s": 1705323025,
                        "creation_timestamp_unix_s": 1705323025,
                        "log_duration_seconds": 3597.0,
                        "date_str": "2024-01-15-14-30-25",
                        "s3_key": "some/s3/key/for/flight_2024_01_15_14_30_25.bag"
                    },
                    "leaf_fc_record": {
                        "id": "12456789-e5f6-7890-abcd-1234567890ab",
                        "bag_name": "LeafFC_Flight_2024-01-15-14-30-25.bag",
                        "record_timestamp_unix_s": 1705323025,
                        "preflight_data": {
                            "flight_mode": "RC Position",
                            "flight_context": {"environment": "Real hardware", "profile": "indoor", "n_ekf": 2},
                            "dev_context": {"build": "release"},
                            "profile_client": {"client_id": "client-123"},
                            "profile_location": {"latitude": 37.7749, "longitude": -122.4194},
                            "leaf_fc_version": "1.2.3",
                            "petal_app_manager_version": "4.5.6",
                            "px4_version": "1.12.0",
                            "controller_dashboard_version": "2.3.4"
                        },
                        "postflight_data": {
                            "stopping_timestamp": 1705326625,
                            "flight_time_seconds": 3600.0,
                            "ground_time_seconds": 300.0
                        }
                    },
                    "analysis_rosbag": {
                        "id": "8901234-e5f6-7890-abcd-1234567890ab",
                        "file_name": "analysis_2024_01_15_14_30_22.bag",
                        "size_bytes": 512000,
                        "size_kb": 500.0,
                        "modified_timestamp_unix_s": 1705327025,
                        "creation_timestamp_unix_s": 1705327025,
                        "date_str": "2024-01-15-14-37-05",
                        "s3_key": "some/s3/key/for/analysis_2024_01_15_14_30_22.bag"
                    },
                    "analysis_results": {
                        "max_altitude_m": 120.5,
                        "total_distance_m": 3500.0,
                        "average_speed_m_s": 15.2
                        # to be expanded with more analysis results
                    },
                    "time_difference_seconds": 3.0,
                    "arming_date_str": "2024-01-15",
                    "arming_time_str": "14:30:22",
                    "disarming_date_str": "2024-01-15",
                    "disarming_time_str": "15:30:22",
                    "log_duration_seconds": 3600.0,
                    "status": "complete",
                    "sync_job_id": "job-1234",
                    "robot_instance_id": "54546789-e5f6-7890-abcd-1234567890ab",
                    "sync_job_status": "completed",
                    "analysis_job_id": "analysis-job-5678",
                    "analysis_job_status": "completed",
                    "analysis_id": "analysis-9012"
                },
                {
                    "id": "23456789-e5f6-7890-abcd-1234567890ab",
                    "ulog": {
                    },
                    "rosbag": {
                    },
                    "leaf_fc_record": {
                        "id": "12456789-e5f6-7890-abcd-1234567890ab",
                        "bag_name": "LeafFC_Flight_2024-01-15-14-30-25.bag",
                        "record_timestamp_unix_s": 1705323025,
                        "preflight_data": {
                            "flight_mode": "RC Position",
                            "flight_context": {"environment": "Real hardware", "profile": "indoor", "n_ekf": 2},
                            "dev_context": {"build": "release"},
                            "profile_client": {"client_id": "client-123"},
                            "profile_location": {"latitude": 37.7749, "longitude": -122.4194},
                            "leaf_fc_version": "1.2.3",
                            "petal_app_manager_version": "4.5.6",
                            "px4_version": "1.12.0",
                            "controller_dashboard_version": "2.3.4"
                        },
                        "postflight_data": {
                            "stopping_timestamp": 1705326625,
                            "flight_time_seconds": 3600.0,
                            "ground_time_seconds": 300.0
                        }
                    },
                    "status": "unavailable ulog and rosbag",
                    "robot_instance_id": "54546789-e5f6-7890-abcd-1234567890ab"
                }
            ]
        }
    }


class ExistingFlightRecordMatch(FlightRecordMatch):
    """Model for existing flight records with minimal info"""
    sync_job_id: Optional[str] = Field(None, description="Job ID for the sync operation (if applicable)")
    sync_job_status: Literal["pending", "in_progress", "completed", "cancelled", "error"] = Field(
        "unknown", description="Status of the sync job"
    )


class SaveLeafFCRecordRequest(BaseModel):
    """Request model for saving Leaf FC record"""
    leaf_fc_record: LeafFCRecord = Field(..., description="Leaf FC record to be saved")


# ========================== Response Models =============================

class StartFlightRecordSyncResponse(BaseModel):
    """Response model for starting flight record sync"""
    status: Literal["success", "error"] = Field(..., description="Status message indicating success or error")
    message: Optional[str] = Field(None, description="Response message")
    error_code: Optional[str] = Field(None, description="Error code if status is error")
    sync_job_id: Optional[str] = Field(None, description="Unique identifier for the started sync job")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "message": "Started flight record sync job",
                "error_code": None,
                "sync_job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            }
        }
    }


class GetFlightRecordsResponse(BaseModel):
    """Response model for get_flight_records command"""
    was_successful: bool = Field(..., description="Indicates if the request was successful")
    data: Optional[Dict[str, List[FlightRecordMatch] | int | GetFlightRecordsRequest]] = Field(
        None, description="Response data containing flight records and query info"
    )
    n_flight_records: Optional[int] = Field(None, description="Number of flight records returned")
    status: Literal["success", "error"] = Field(..., description="Status message indicating success or error")
    error_code: Optional[str] = Field(None, description="Error code if status is error")
    message: Optional[str] = Field(None, description="Status message providing additional information")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "was_successful": True,
                "data": {
                    "flight_records": [
                        {
                            "ulog": {
                                "id": "ulog-456",
                                "file_name": "log_44_2024-01-15-14-30-22.ulg",
                                "file_path": "/opt/log_44_2024-01-15-14-30-22.ulg",
                                "file_type": "ulg",
                                "storage_type": "pixhawk",
                                "size_bytes": 1048576,
                                "size_kb": 1024.0,
                                "modified_timestamp_unix_s": 1705323022,
                                "creation_timestamp_unix_s": 1705323022,
                                "log_duration_seconds": 3600.0,
                                "date_str": "2024-01-15-14-30-22",
                                "qgc_index": 44,
                                "qgc_name": "log_44_2024-01-15-14-30-22.ulg"
                            },
                            "rosbag": {
                                "id": "bag-123",
                                "file_name": "flight_2024_01_15_14_30_25.bag",
                                "file_path": "/home/root/rosbag_records/flight_2024_01_15_14_30_25.bag",
                                "file_type": "bag",
                                "storage_type": "local",
                                "size_bytes": 2048576,
                                "size_kb": 2000.0,
                                "modified_timestamp_unix_s": 1705323025,
                                "creation_timestamp_unix_s": 1705323025,
                                "log_duration_seconds": 3597.0,
                                "date_str": "2024-01-15-14-30-25",
                            },
                            "leaf_fc_record": {
                                "id": "leaffc-123",
                                "bag_name": "LeafFC_Flight_2024-01-15-14-30-25",
                                "record_timestamp_unix_s": 1705323025,
                                "preflight_data": {
                                    "flight_mode": "RC Position",
                                    "flight_context": {"environment": "Real hardware"},
                                    "dev_context": {"build": "release"},
                                    "profile_client": {"client_id": "client-123"},
                                    "profile_location": {"latitude": 37.7749, "longitude": -122.4194},
                                    "leaf_fc_version": "1.2.3",
                                    "petal_app_manager_version": "4.5.6",
                                    "px4_version": "1.12.0",
                                    "controller_dashboard_version": "2.3.4"
                                },
                                "postflight_data": {
                                    "stopping_timestamp": 1705326625,
                                    "flight_time_seconds": 3600.0,
                                    "ground_time_seconds": 300.0
                                }
                            },
                            "time_difference_seconds": 3.0,
                            "arming_date_str": "2024-01-15",
                            "arming_time_str": "14:30:22",
                            "disarming_date_str": "2024-01-15",
                            "disarming_time_str": "15:30:22",
                            "log_duration_seconds": 3600.0,
                            "status": "complete",
                            "robot_instance_id": "54546789-e5f6-7890-abcd-1234567890ab"
                        }
                    ],
                    "query": {
                        "start_time": "2024-01-15T14:00:00Z",
                        "end_time": "2024-01-15T16:00:00Z",
                        "tolerance_seconds": 30
                    },
                    "total_matches": 1
                },
                "n_flight_records": 1,
                "status": "success",
                "error_code": None,
                "message": "Fetched flight records successfully"
            }
        }
    }


class GetExistingFlightRecordsResponse(BaseModel):
    """Response model for get_existing_flight_records command"""
    status: str = Field(..., description="Response status (success, error)")
    data: Optional[Dict[str, List[ExistingFlightRecordMatch] | int]] = Field(
        None, description="Response data containing existing flight records"
    )
    message: Optional[str] = Field(None, description="Response message")
    error_code: Optional[str] = Field(None, description="Error code if status is error")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "data": {
                    "flight_records": [
                        {
                            "ulog": {
                                "id": "ulog-456",
                                "file_name": "log_44_2024-01-15-14-30-22.ulg",
                                "file_path": "/opt/log_44_2024-01-15-14-30-22.ulg",
                                "file_type": "ulg",
                                "storage_type": "pixhawk",
                                "size_bytes": 1048576,
                                "size_kb": 1024.0,
                                "modified_timestamp_unix_s": 1705323022,
                                "creation_timestamp_unix_s": 1705323022,
                                "log_duration_seconds": 3600.0,
                                "date_str": "2024-01-15-14-30-22",
                                "qgc_index": 44,
                                "qgc_name": "log_44_2024-01-15-14-30-22.ulg"
                            },
                            "sync_job_id": "job-1234",
                            "sync_job_status": "completed",
                            "robot_instance_id": "54546789-e5f6-7890-abcd-1234567890ab"
                        }
                    ],
                    "total_matches": 1
                }
            }
        }
    }


class PX4MavLogDownloadProgressResponse(BaseModel):
    """Response model for PX4 log download progress"""
    type: Literal["progress"] = Field(..., description="Type of the response, always 'progress'")
    download_id: str = Field(..., description="Unique identifier for the download session")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Download progress percentage (0-100)")
    completed: bool = Field(None, description="Whether the download is completed")
    rate_kbps: Optional[float] = Field(None, ge=0, description="Download rate in KB/s")
    message: Optional[str] = Field(None, description="Additional message or status info")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "progress",
                "download_id": "example-download-id",
                "progress": 0,
                "completed": False,
                "rate_kbps": 0,
                "message": "Download started"
            }
        }
    }


class PX4LogDownloadProgressResponse(BaseModel):
    """Response model for PX4 log download progress"""
    type: Literal["progress"] = Field(..., description="Type of the response, always 'progress'")
    px4_path: str = Field(..., description="Path to the log file being downloaded")
    download_id: str = Field(..., description="Unique identifier for the download session")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Download progress percentage (0-100)")
    completed: bool = Field(None, description="Whether the download is completed")
    rate_kbps: Optional[float] = Field(None, ge=0, description="Download rate in KB/s")
    message: Optional[str] = Field(None, description="Additional message or status info")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "progress",
                "px4_path": "/fs/microsd/log/LOG001.ulg",
                "download_id": "example-download-id",
                "progress": 0,
                "completed": False,
                "rate_kbps": 0,
                "message": "Download started"
            }
        }
    }


class PX4LogCheckDownloadStatusResponse(BaseModel):
    """Response model for checking download status"""
    success: bool = Field(..., description="Whether the operation was successful")
    download_id: str = Field(..., description="Unique identifier for the download task")
    message: Optional[str] = Field(None, description="Status message")
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled", "error"]] = Field(None, description="Current status of the download task")
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Download progress percentage (0.0-100.0)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Download is already cancelled",
                "download_id": "example-download-id",
                "status": "cancelled",
                "progress": 45.0,
            }
        }
    }


class PX4LogCompletedResponse(BaseModel):
    """response model for completed sync PX4 log download"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Status message")
    file_path: Optional[str] = Field(None, description="Path to the downloaded ULog file")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Download completed successfully",
                "file_path": "/home/khalil/ulog_records/log_44_2025-06-16-14-30-00.ulg"
            }
        }
    }


class S3CheckResponse(BaseModel):
    """Response model for checking S3 upload status"""
    success: bool = Field(..., description="Whether the operation was successful")
    s3_task_id: str = Field(..., description="Unique identifier for the s3 task")
    message: Optional[str] = Field(None, description="Status message")
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled", "error"]] = Field(None, description="Current status of the s3 task")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "s3 task is already cancelled",
                "s3_task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "cancelled",
            }
        }
    }


class S3CompleteResponse(BaseModel):
    """Response model for completed S3 upload"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Status message")
    s3_key: Optional[str] = Field(None, description="S3 key of the uploaded file")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "s3 upload completed successfully",
                "s3_key": "uploads/org-123/ulog/log_44_2025-06-16-14-30-00.ulg"
            }
        }
    }


class S3UploadResponse(BaseModel):
    """Response model for starting S3 upload job"""
    success: bool = Field(..., description="Whether the operation was successful")
    job_id: str = Field(..., description="Unique identifier for the upload job")
    file_path: str = Field(..., description="Local file path being uploaded")
    s3_key: str = Field(..., description="S3 key where the file will be stored")
    status: Literal["pending", "in_progress", "completed", "error", "cancelled"] = Field(..., description="Current status of the upload job")
    message: Optional[str] = Field(None, description="Status message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "file_path": "/home/khalil/ulog_records/log_44_2025-06-16-14-30-00.ulg",
                "s3_key": "uploads/org-123/ulog/log_44_2025-06-16-14-30-00.ulg",
                "status": "in_progress",
                "message": "S3 upload started successfully"
            }
        }
    }


class ULogDownloadResponse(BaseModel):
    """Response model for starting ULog download job"""
    success: bool = Field(..., description="Whether the operation was successful")
    job_id: str = Field(..., description="Unique identifier for the download job")
    px4_path: str = Field(..., description="Path on Pixhawk")
    file_path: str = Field(..., description="Local destination file path")
    status: Literal["pending", "in_progress", "completed", "error", "cancelled"] = Field(..., description="Current status of the download job")
    message: Optional[str] = Field(None, description="Status message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "job_id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
                "px4_path": "/fs/microsd/log/2025-01-15/10_23_45.ulg",
                "file_path": "/home/khalil/ulog_records/log_42_2025-01-15-10-23-45.ulg",
                "status": "in_progress",
                "message": "ULog download started successfully"
            }
        }
    }


class FlightRecordSyncStartResponse(BaseModel):
    """Response model for starting flight record sync"""
    success: bool = Field(..., description="Whether the operation was successful")
    job_id: str = Field(..., description="Unique identifier for the sync job")
    flight_record_id: str = Field(..., description="Flight record ID being synced")
    status: Literal["pending", "in_progress", "completed", "cancelled", "error"] = Field(..., description="Current status of the sync job")
    message: str = Field(..., description="Status message")
    sub_jobs: Dict[str, Optional[str]] = Field(..., description="Sub-job IDs for tracking individual operations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "job_id": "abc-123-def-456",
                "flight_record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "in_progress",
                "message": "Flight record sync started successfully",
                "sub_jobs": {
                    "ulog_download": "download-job-uuid",
                    "s3_upload_ulog": "upload-ulog-job-uuid",
                    "s3_upload_rosbag": "upload-rosbag-job-uuid"
                }
            }
        }
    }


class FlightRecordCheckSyncStatusResponse(BaseModel):
    """Response model for checking sync status"""
    success: bool = Field(..., description="Whether the operation was successful")
    flight_record_id: str = Field(..., description="Unique identifier for the sync task")
    message: Optional[str] = Field(None, description="Status message")
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled", "error"]] = Field(None, description="Current status of the sync task")


class DeleteFlightRecordResponse(BaseModel):
    """Response model for deleting a flight record"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Status message")
    error_code: Optional[str] = Field(None, description="Error code if deletion failed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Flight record deleted successfully",
                "error_code": None
            }
        }
    }


class SaveLeafFCRecordResponse(BaseModel):
    """Response model for saving Leaf FC record"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Status message")
    error_code: Optional[str] = Field(None, description="Error code if saving failed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Leaf FC record saved successfully",
                "error_code": None
            }
        }
    }
# ==================== Job Stream Subscription Models ====================


class SubscribePayload(BaseModel):
    """Payload for subscription messages"""
    subscribed_stream_id: str = Field(..., description="Unique identifier for the stream")
    data_rate_hz: float = Field(..., ge=0.1, le=100.0, description="Data rate in Hz (0.1-100)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "subscribed_stream_id": "px4_rc_raw",
                "data_rate_hz": 10.0
            }
        }
    }


class UnsubscribePayload(BaseModel):
    """Payload for unsubscribe messages"""
    unsubscribed_stream_id: str = Field(..., description="Unique identifier for the stream to stop")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "unsubscribed_stream_id": "px4_rc_raw"
            }
        }
    }


class SubscribeJobStreamRequest(BaseModel):
    """Request model for subscribing to job progress stream"""
    subscribed_stream_id: str = Field(..., description="Job ID to subscribe to")
    data_rate_hz: Optional[float] = Field(2.0, ge=0.1, le=10.0, description="Publishing rate in Hz (0.1-10.0)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "subscribed_stream_id": "abc-123-def-456",
                "data_rate_hz": 2.0
            }
        }
    }


class SubscribeJobStreamResponse(BaseModel):
    """Response model for job stream subscription"""
    status: str = Field(..., description="Response status (success, error)")
    message: str = Field(..., description="Response message")
    subscribed_stream_id: Optional[str] = Field(None, description="Stream identifier")
    data_rate_hz: Optional[float] = Field(None, description="Publishing rate in Hz")
    mqtt_topic: Optional[str] = Field(None, description="MQTT topic for progress updates")
    job_state: Optional[Dict[str, Any]] = Field(None, description="Current job state if not active")
    error_code: Optional[str] = Field(None, description="Error code if status is error")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "message": "Subscribed to job abc-123-def-456 progress updates",
                "subscribed_stream_id": "abc-123-def-456",
                "data_rate_hz": 2.0,
                "mqtt_topic": "petal-flight-log/log_download/progress"
            }
        }
    }


class UnsubscribeJobStreamRequest(BaseModel):
    """Request model for unsubscribing from job progress stream"""
    unsubscribed_stream_id: str = Field(..., description="Job ID to unsubscribe from")

    model_config = {
        "json_schema_extra": {
            "example": {
                "unsubscribed_stream_id": "abc-123-def-456"
            }
        }
    }


class UnsubscribeJobStreamResponse(BaseModel):
    """Response model for job stream unsubscription"""
    status: str = Field(..., description="Response status (success, error)")
    message: str = Field(..., description="Response message")
    error_code: Optional[str] = Field(None, description="Error code if status is error")
    unsubscribed_stream_id: Optional[str] = Field(None, description="Stream identifier")
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "message": "Unsubscribed from job abc-123-def-456 progress updates",
                "unsubscribed_stream_id": "abc-123-def-456"
            }
        }
    }


# ==================== Job Progress Update Models ====================


class JobProgressUpdatePayload(BaseModel):
    """Generic job progress update payload"""
    job_id: str = Field(..., description="Job identifier")
    machine_id: str = Field(..., description="Machine/device identifier")
    stream_id: str = Field(..., description="Stream identifier")
    job_type: str = Field(..., description="Type of job")
    status: Literal["pending", "in_progress", "completed", "cancelled", "error"] = Field(..., description="Current job status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    rate_kbps: Optional[float] = Field(None, description="Transfer rate in KB/s")
    message: str = Field(..., description="Progress message")
    completed: bool = Field(..., description="Whether job is completed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_id": "abc-123",
                "machine_id": "robot-123",
                "stream_id": "stream-001",
                "job_type": "ULogDownloadJobMAVLink",
                "status": "in_progress",
                "progress": 45.5,
                "rate_kbps": 125.3,
                "message": "Downloading... 45.5%",
                "completed": False
            }
        }
    }


class SubscribeJobStreamPublishResponse(BaseModel):
    """Response model for publishing job stream subscription updates"""
    published_stream_id: str = Field(..., description="Stream identifier")
    stream_payload: Dict[str, Any] = Field(..., description="Payload containing job progress update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "published_stream_id": "abc-123-def-456",
                "stream_payload": {
                    "job_id": "abc-123",
                    "machine_id": "robot-123",
                    "stream_id": "stream-001",
                    "job_type": "ULogDownloadJobMAVLink",
                    "status": "in_progress",
                    "progress": 45.5,
                    "rate_kbps": 125.3,
                    "message": "Downloading... 45.5%",
                    "completed": False
                }
            }
        }
    }


class ULogDownloadProgressPayload(BaseModel):
    """ULog download progress update payload"""
    type: Literal["progress"] = Field("progress", description="Type of update")
    download_id: str = Field(..., description="Download job identifier")
    log_id: Optional[int] = Field(None, description="PX4 log ID (for MAVLink)")
    px4_path: Optional[str] = Field(None, description="PX4 path (for MAVFTP)")
    machine_id: str = Field(..., description="Machine/device identifier")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    completed: bool = Field(..., description="Whether download is completed")
    rate_kbps: Optional[float] = Field(None, description="Transfer rate in KB/s")
    message: str = Field(..., description="Progress message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "progress",
                "download_id": "abc-123",
                "log_id": 42,
                "machine_id": "robot-123",
                "progress": 45.5,
                "completed": False,
                "rate_kbps": 125.3,
                "message": "Downloading... 45.5%"
            }
        }
    }


class S3UploadProgressPayload(BaseModel):
    """S3 upload progress update payload"""
    type: Literal["progress"] = Field("progress", description="Type of update")
    upload_job_id: str = Field(..., description="Upload job identifier")
    s3_key: str = Field(..., description="S3 key")
    machine_id: str = Field(..., description="Machine/device identifier")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    completed: bool = Field(..., description="Whether upload is completed")
    message: str = Field(..., description="Progress message")
    file_size: int = Field(..., description="File size in bytes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "progress",
                "upload_job_id": "upload-123",
                "s3_key": "uploads/org-123/file.ulg",
                "machine_id": "robot-123",
                "progress": 75.0,
                "completed": False,
                "message": "Uploading... 75.0%",
                "file_size": 1048576
            }
        }
    }


class FlightRecordSyncProgressPayload(BaseModel):
    """Flight record sync progress update payload"""
    type: Literal["progress"] = Field("progress", description="Type of update")
    sync_job_id: str = Field(..., description="Sync job identifier")
    flight_record_id: str = Field(..., description="Flight record identifier")
    machine_id: str = Field(..., description="Machine/device identifier")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    completed: bool = Field(..., description="Whether sync is completed")
    message: str = Field(..., description="Progress message")
    sub_jobs: Dict[str, Optional[str]] = Field(..., description="Sub-job IDs")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "progress",
                "sync_job_id": "sync-123",
                "flight_record_id": "flight-456",
                "machine_id": "robot-123",
                "progress": 50.0,
                "completed": False,
                "message": "Uploading files to S3...",
                "sub_jobs": {
                    "ulog_download": "download-123",
                    "ulog_upload": "upload-456",
                    "rosbag_upload": "upload-789"
                }
            }
        }
    }
    ulog_download_status: Optional[PX4LogCheckDownloadStatusResponse] = Field(None, description="ULog download status")
    s3_upload_status_ulog: Optional[S3CheckResponse] = Field(None, description="S3 upload status for ULog file")
    s3_upload_status_rosbag: Optional[S3CheckResponse] = Field(None, description="S3 upload status for Rosbag file")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Sync is already cancelled",
                "flight_record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "cancelled",
                "ulog_download_status": {
                    "success": True,
                    "download_id": "example-download-id",
                    "message": "Download is already cancelled",
                    "status": "cancelled",
                    "progress": 45.0,
                },
                "s3_upload_status_ulog": {
                    "success": True,
                    "s3_task_id": "example-s3-task-id-ulog",
                    "message": "S3 upload for ULog is already cancelled",
                    "status": "cancelled",
                },
                "s3_upload_status_rosbag": {
                    "success": True,
                    "s3_task_id": "example-s3-task-id-rosbag",
                    "message": "S3 upload for Rosbag is already cancelled",
                    "status": "cancelled",
                },
            }
        }
    }