from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Dict, Any, List, Literal, Union, Optional, Callable
from datetime import datetime

class ParameterBaseModel(BaseModel):
    """Base fields for flight records"""
    parameter_name: str = Field(..., description="Parameter name")
    parameter_value: Union[str,int,float] = Field(..., description="Value of the parameter")
    parameter_type: Optional[Literal['UINT8','INT8','UINT16','INT16','UINT32','INT32','UINT64','INT64','REAL32','REAL64']] = Field(default=None, description="Type of the parameter")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameter_name": "CA_ROTOR_COUNT",
                "parameter_value": 4,
                "parameter_type": "UINT8"
            }
        }
    }


class ParameterResult(BaseModel):
    """Individual parameter result"""
    name: str = Field(..., description="Name of the parameter")
    value: Optional[Union[str,int,float]] = Field(None, description="Decoded value of the parameter")
    raw: Optional[Union[str,int,float]] = Field(None, description="Raw value of the parameter")
    type: Optional[int] = Field(None, description="Type of the parameter")
    count: Optional[int] = Field(None, description="Total number of parameters")
    index: Optional[int] = Field(None, description="Index of the parameter")
    error: Optional[str] = Field(default=None, description="Error message if setting the parameter failed")
    success: Optional[bool] = Field(default=None, description="Whether setting the parameter was successful")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "CA_ROTOR_COUNT",
                "value": 4,
                "raw": 4.0,
                "type": 6,
                "count": 1053,
                "index": 65535,
                "error": None,
                "success": True
            }
        }
    }


class ParameterRequestModel(BaseModel):
    """Base fields for flight records"""
    parameter_name: str = Field(..., description="Parameter name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameter_name": "CA_ROTOR_COUNT"
            }
        }
    }


class RotorCountParameter(BaseModel):
    """Flight record input model"""
    # File paths and IDs
    rotor_count: int = Field(..., description="Value of the parameter")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "rotor_count": 4
            }
        }
    }


class ESCCalibrationRequest(BaseModel):
    """ESC calibration request model"""
    motor_number: int = Field(..., description="Motor number (1-based)")
    calibration_value: float = Field(..., description="Calibration value [-1..1]")
    safety_timeout_s: float = Field(default=3.0, description="Safety timeout in seconds (<=3)")
    period: float = Field(default=1.0, description="Period between commands in seconds")
    repetitions: Optional[int] = Field(default=None, description="Number of repetitions (None for infinite)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motor_number": 1,
                "calibration_value": 0.2,
                "safety_timeout_s": 2.5,
                "period": 1.0,
                "repetitions": 10
            }
        }
    }


class ESCCalibrationResponse(BaseModel):
    """ESC calibration response model"""
    motor_number: int = Field(..., description="Motor number")
    status: str = Field(..., description="Calibration status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motor_number": 1,
                "status": "started",
                "message": "ESC calibration started for motor 1",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
    }


class ESCCalibrationStop(BaseModel):
    """ESC calibration stop request model"""
    motor_number: Optional[int] = Field(default=None, description="Motor number to stop (None for all)")
    force_stop: bool = Field(default=True, description="Force stop calibration")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motor_number": 1,
                "force_stop": True
            }
        }
    }


class ESCCalibrationPayload(BaseModel):
    """ESC calibration MQTT payload model"""
    is_calibration_started: bool = Field(..., description="Whether calibration is started")
    safety_timeout_s: float = Field(..., ge=0, le=3, description="Safety timeout in seconds (0-3)")
    force_cancel_calibration: bool = Field(default=False, description="Force cancel calibration")
    throttle: Optional[str] = Field(default=None, description="Throttle command: 'maximum' or 'minimum'")
    esc_interface_signal_type: Optional[str] = Field(default="PWM", description="ESC signal interface type (PWM, OneShot125, DShot, etc.)")
    ca_rotor_count: Optional[int] = Field(default=None, description="Number of rotors/motors")
    safe_stop_calibration: Optional[bool] = Field(default=False, description="Whether to perform a safe stop of the calibration process")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "is_calibration_started": True,
                "safety_timeout_s": 2.5,
                "force_cancel_calibration": False,
                "throttle": "maximum",
                "esc_interface_signal_type": "PWM",
                "ca_rotor_count": 4,
                "safe_stop_calibration": True
            }
        }
    }


class ESCCalibrationLimitsPayload(BaseModel):
    """ESC calibration limits update payload model"""
    motors_common_max_pwm: int = Field(..., ge=1000, le=2000, description="Common maximum PWM value for all motors (1000-2000)")
    motors_common_min_pwm: int = Field(..., ge=1000, le=2000, description="Common minimum PWM value for all motors (1000-2000)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motors_common_max_pwm": 2000,
                "motors_common_min_pwm": 1000
            }
        }
    }


class ESCForceRunAllPayload(BaseModel):
    """ESC force run all motors MQTT payload model"""
    motors_common_command: float = Field(..., ge=1000, le=1200, description="Common command value for all motors [1000..1200]")
    safety_timeout_s: float = Field(..., ge=0, le=3, description="Safety timeout in seconds (0-3)")
    force_cancel: bool = Field(default=False, description="Force cancel operation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motors_common_command": 1000,
                "safety_timeout_s": 2.0,
                "force_cancel": False
            }
        }
    }


class ESCForceRunSinglePayload(BaseModel):
    """ESC force run single motor MQTT payload model"""
    motor_idx: int = Field(..., ge=1, description="Motor index (1-based)")
    motor_command: float = Field(..., ge=1000, le=2000, description="Motor command value [1000..2000]")
    safety_timeout_s: float = Field(..., ge=0, le=3, description="Safety timeout in seconds (0-3)")
    force_cancel: bool = Field(default=False, description="Force cancel operation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "motor_idx": 1,
                "motor_command": 1000,
                "safety_timeout_s": 2.5,
                "force_cancel": False
            }
        }
    }


class GPSModulePayload(BaseModel):
    """GPS module configuration payload"""
    gps_module: str = Field(..., description="GPS module type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "gps_module": "Mosaic-H RTX"
            }
        }
    }


class DistanceModulePayload(BaseModel):
    """Distance module configuration payload"""
    dist_module: str = Field(..., description="Distance module type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "dist_module": "LiDAR Lite v3"
            }
        }
    }


class OpticalFlowModulePayload(BaseModel):
    """Optical flow module configuration payload"""
    oflow_module: str = Field(..., description="Optical flow module type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "oflow_module": "ARK Flow"
            }
        }
    }


class GPSSpatialOffsetPayload(BaseModel):
    """GPS spatial offset configuration payload"""
    gps_module_spatial_offset_x_m: float = Field(..., description="GPS X offset in meters")
    gps_module_spatial_offset_y_m: float = Field(..., description="GPS Y offset in meters") 
    gps_module_spatial_offset_z_m: float = Field(..., description="GPS Z offset in meters")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "gps_module_spatial_offset_x_m": 0.1,
                "gps_module_spatial_offset_y_m": 0.0,
                "gps_module_spatial_offset_z_m": -0.05
            }
        }
    }


class DistanceSpatialOffsetPayload(BaseModel):
    """Distance sensor spatial offset configuration payload"""
    dist_module_spatial_offset_x_m: float = Field(..., description="Distance sensor X offset in meters")
    dist_module_spatial_offset_y_m: float = Field(..., description="Distance sensor Y offset in meters") 
    dist_module_spatial_offset_z_m: float = Field(..., description="Distance sensor Z offset in meters")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "dist_module_spatial_offset_x_m": 0.05,
                "dist_module_spatial_offset_y_m": 0.0,
                "dist_module_spatial_offset_z_m": -0.1,
            }
        }
    }


class OpticalFlowSpatialOffsetPayload(BaseModel):
    """Optical flow spatial offset configuration payload"""
    oflow_module_spatial_offset_x_m: float = Field(..., description="Optical flow X offset in meters")
    oflow_module_spatial_offset_y_m: float = Field(..., description="Optical flow Y offset in meters") 
    oflow_module_spatial_offset_z_m: float = Field(..., description="Optical flow Z offset in meters")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "oflow_module_spatial_offset_x_m": 0.0,
                "oflow_module_spatial_offset_y_m": 0.0,
                "oflow_module_spatial_offset_z_m": -0.02
            }
        }
    }


class ParameterResponseModel(BaseModel):
    """Response model for parameter requests"""
    parameter_name: str = Field(..., description="Name of the parameter")
    parameter_value: Union[int,str,float] = Field(..., description="Value of the parameter")
    timestamp: datetime = Field(..., description="Timestamp of the parameter value")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameter_name": "CA_ROTOR_COUNT",
                "parameter_value": 4,
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
    }


class MavlinkParameterData(BaseModel):

    """Response model for mavlink parameter requests"""
    value: Union[str, int, float, None] = Field(None, description="Parameter value (nullable, optional)")
    raw:   Union[str, int, float, None] = Field(None, description="Raw parameter value (nullable, optional)")
    type: int = Field(..., description="Parameter type")
    count: int = Field(..., description="Parameter count")
    index: int = Field(..., description="Parameter index")

    model_config = {
        "json_schema_extra": {
            "example": {
                "value": 4,
                "raw": 4.0,
                "type": 6,
                "count": 1053,
                "index": 65535
            }
        }
    }


class MavlinkParametersResponseModel(BaseModel):

    parameters: Dict[str,MavlinkParameterData] = Field(..., description="List of MAVLink parameters")
    timestamp: datetime = Field(..., description="Timestamp of the parameter values")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameters": {
                    "CA_ROTOR_COUNT": {
                        "value": 4,
                        "raw": 4.0,
                        "type": 6,
                        "count": 1053,
                        "index": 65535
                    },
                    "VTO_LOITER_ALT": {
                        "value": 80.0,
                        "raw": 80.0,
                        "type": 9,
                        "index": 1047,
                        "count": 1053
                    }
                },
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
    }


class MavlinkNamedParameterData(BaseModel):

    """Response model for mavlink parameter requests"""
    name: str = Field(..., description="Parameter name")
    value: Union[str, int, float] = Field(..., description="Parameter value")
    raw: Union[str, int, float] = Field(..., description="Raw parameter value")
    type: int = Field(..., description="Parameter type")
    count: int = Field(..., description="Parameter count")
    index: int = Field(..., description="Parameter index")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "CA_ROTOR_COUNT",
                "value": 4,
                "raw": 4.0,
                "type": 6,
                "count": 1053,
                "index": 65535
            }
        }
    }


class MavlinkParameterResponseModel(BaseModel):
    """Response model for parameter requests"""
    parameter_name: str = Field(..., description="Name of the parameter")
    parameter_value: MavlinkNamedParameterData = Field(..., description="Value of the parameter")
    timestamp: datetime = Field(..., description="Timestamp of the parameter value")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameter_name": "CA_ROTOR_COUNT",
                "parameter_value": {
                    "name": "CA_ROTOR_COUNT",
                    "value": 4,
                    "raw": 4.0,
                    "type": 6,
                    "count": 1053,
                    "index": 65535
                },
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
    }


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


class PublishPayload(BaseModel):
    """Payload for publish messages"""
    published_stream_id: str = Field(..., description="Unique identifier for the stream")
    stream_payload: Dict[str, Any] = Field(..., description="The actual data payload")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "published_stream_id": "px4_rc_raw",
                "stream_payload": {
                    "time_boot_ms": 12345,
                    "chancount": 8,
                    "chan1_raw": 1500,
                    "chan2_raw": 1600,
                    "rssi": 255
                }
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


class VerifyPosYawDirectionsPayload(BaseModel):
    """Payload for position and yaw verification start"""
    start: bool = Field(..., description="Start verification process")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "start": True
            }
        }
    }


class VerifyPosYawDirectionsResultsPayload(BaseModel):
    """Payload for position and yaw verification results"""
    was_successful: bool = Field(..., description="Whether verification was successful")
    results_text: str = Field(..., description="Detailed results text")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "was_successful": True,
                "results_text": "Position error: 0.15m, Yaw error: 2.3°. Verification passed."
            }
        }
    }


class ConnectToWifiAndVerifyOptitrackPayload(BaseModel):
    """Payload for connecting to WiFi and verifying OptiTrack connectivity"""
    positioning_system_network_wifi_ssid: str = Field(..., description="WiFi SSID to connect to")
    positioning_system_network_wifi_pass: str = Field(..., description="WiFi password")
    positioning_system_network_wifi_subnet: str = Field(..., description="Expected subnet (e.g., '192.168.1.0/24')")
    positioning_system_network_server_ip_address: str = Field(..., description="OptiTrack server IP address to ping")
    positioning_system_network_server_multicast_address: str = Field(..., description="Multicast address for OptiTrack")
    positioning_system_network_server_data_port: str = Field(..., description="Data port for OptiTrack communication")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "positioning_system_network_wifi_ssid": "OptiTrack_Network",
                "positioning_system_network_wifi_pass": "password123",
                "positioning_system_network_wifi_subnet": "192.168.1.0/24",
                "positioning_system_network_server_ip_address": "192.168.1.100",
                "positioning_system_network_server_multicast_address": "239.255.42.99",
                "positioning_system_network_server_data_port": "1511"
            }
        }
    }


class WifiOptitrackConnectionResponse(BaseModel):
    """Response payload for WiFi and OptiTrack connection attempt"""
    was_successful: bool = Field(..., description="Whether the connection was successful")
    status_message: str = Field(..., description="Detailed status message")
    assigned_ip_address: str = Field(default="", description="Assigned IP address if successful")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "was_successful": True,
                "status_message": "Successfully connected to WiFi and verified OptiTrack server connectivity",
                "assigned_ip_address": "192.168.1.45"
            }
        }
    }


class SetStaticIpAddressPayload(BaseModel):
    """Payload for setting static IP address within OptiTrack network"""
    positioning_system_network_wifi_subnet: str = Field(..., description="Subnet mask (e.g., '255.255.255.0' or '10.0.0.0/24')")
    positioning_system_network_server_ip_address: str = Field(..., description="OptiTrack server IP address for gateway calculation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "positioning_system_network_wifi_subnet": "255.255.255.0",
                "positioning_system_network_server_ip_address": "10.0.0.27"
            }
        }
    }


class SetStaticIpAddressResponse(BaseModel):
    """Response payload for static IP address configuration"""
    assigned_static_ip: str = Field(default="", description="The static IP address that was assigned")
    was_successful: bool = Field(..., description="Whether the static IP configuration was successful")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "assigned_static_ip": "10.0.0.25",
                "was_successful": True
            }
        }
    }


class BulkParameterSetRequest(BaseModel):
    """Request model for bulk parameter setting"""
    parameters: List[ParameterBaseModel] = Field(..., description="List of parameters to set")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameters": [
                    {
                        "parameter_name": "CA_ROTOR_COUNT",
                        "parameter_value": 4,
                        "parameter_type": "UINT8"
                    },
                    {
                        "parameter_name": "VTO_LOITER_ALT",
                        "parameter_value": 80.0,
                        "parameter_type": "REAL32"
                    }
                ]
            }
        }   
    }


class BulkParameterGetRequest(BaseModel):
    """Request model for bulk parameter getting"""
    parameter_names: List[str] = Field(..., description="List of parameter names to get")

    model_config = {
        "json_schema_extra": {
            "example": {
                "parameter_names": [
                    "CA_ROTOR_COUNT",
                    "VTO_LOITER_ALT"
                ]
            }
        }   
    }


class BulkParameterResponse(BaseModel):
    """Response model for bulk parameter setting"""
    success: bool = Field(..., description="Whether all parameters were set successfully")
    results: Dict[str, ParameterResult] = Field(..., description="Results for each parameter set attempt")
    timestamp: str = Field(..., description="Timestamp of the operation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "results": {
                    "CA_ROTOR_COUNT": {
                        "name": "CA_ROTOR_COUNT",
                        "value": 4,
                        "raw": 4.0,
                        "type": 6,
                        "count": 1053,
                        "index": 65535,
                        "error": None,
                        "success": True
                    },
                    "VTO_LOITER_ALT": {
                        "name": "VTO_LOITER_ALT",
                        "value": 80.0,
                        "raw": 80.0,
                        "type": 9,
                        "count": 1053,
                        "index": 1047,
                        "error": None,
                        "success": True
                    }
                },
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
    }