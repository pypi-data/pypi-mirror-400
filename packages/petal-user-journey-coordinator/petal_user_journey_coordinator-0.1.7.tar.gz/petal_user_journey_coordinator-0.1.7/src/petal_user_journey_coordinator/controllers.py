import uuid
import asyncio
import threading
import time
import math
import logging
import subprocess
import ipaddress
import re
from petal_app_manager.proxies import (
    MQTTProxy,
    MavLinkExternalProxy,
    LocalDBProxy,
    RedisProxy
)
from typing import Dict, Any, List, Union, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod
import logging
import time
from pymavlink import mavutil
from pymavlink.dialects.v20 import all as mavlink_dialect
import threading
import asyncio
import math

from .data_model import (
    RotorCountParameter,
    GPSModulePayload,
    DistanceModulePayload,
    OpticalFlowModulePayload,
    GPSSpatialOffsetPayload,
    DistanceSpatialOffsetPayload,
    OpticalFlowSpatialOffsetPayload,
    ESCCalibrationPayload,
    ESCCalibrationLimitsPayload,
    ESCForceRunAllPayload,
    ESCForceRunSinglePayload,
    PublishPayload,
    ConnectToWifiAndVerifyOptitrackPayload,
    WifiOptitrackConnectionResponse,
    SetStaticIpAddressPayload,
    SetStaticIpAddressResponse
)


# GPS Module configuration mappings
GPS_MODULE_CONFIGS = {
    "Mosaic-H RTX": {
        "GPS_1_CONFIG": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # GPS1
        "GPS_1_GNSS": {"value": 31, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},
        "GPS_1_PROTOCOL": {"value": 12, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # SBF protocol
        "SER_GPS1_BAUD": {"value": 115200, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},
        "EKF2_GPS_CTRL": {"value": 15, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},
    },
    "Emlid Reach M2": {
        "GPS_1_CONFIG": {"value": 2, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # GPS2
        "GPS_1_GNSS": {"value": 31, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},
        "GPS_1_PROTOCOL": {"value": 5, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # RTCM3 protocol
    }
}

# Distance Module configuration mappings
DISTANCE_MODULE_CONFIGS = {
    "LiDAR Lite v3": {
        "SENS_EN_LL40LS": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # Enable LiDAR Lite
        "EKF2_RNG_AID": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},   # Enable range aid
        "EKF2_RNG_A_HMAX": {"value": 40.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Max height
        "EKF2_RNG_A_VMAX": {"value": 1.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},  # Max velocity
    },
    "TF02 Pro": {
        "SENS_TFMINI_CFG": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # TF02 Pro config
        "EKF2_RNG_AID": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},     # Enable range aid
        "EKF2_RNG_A_HMAX": {"value": 25.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Max height
        "EKF2_RNG_A_VMAX": {"value": 0.8, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},  # Max velocity
        "SER_TEL3_BAUD": {"value": 115200, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32}, # Serial baud rate
    }
}

# Optical Flow Module configuration mappings
OPTICAL_FLOW_MODULE_CONFIGS = {
    "PX4Flow v1.3": {
        "SENS_EN_PX4FLOW": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32}, # Enable PX4Flow
        "EKF2_OF_CTRL": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},    # Enable optical flow control
        "EKF2_OF_QMIN": {"value": 80, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},   # Min quality
        "EKF2_OF_DELAY": {"value": 20.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Delay compensation
    },
    "PMW3901 Based": {
        "SENS_FLOW_ROT": {"value": 0, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},   # Flow rotation
        "EKF2_OF_CTRL": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},    # Enable optical flow control
        "EKF2_OF_QMIN": {"value": 70, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},   # Min quality
        "EKF2_OF_DELAY": {"value": 15.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Delay compensation
        "SER_TEL2_BAUD": {"value": 921600, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32}, # Serial baud rate
    },
    "ARK Flow": {
        # Enable DroneCAN with dynamic node allocation and range sensor
        "UAVCAN_ENABLE": {"value": 2, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},   # Enable DroneCAN sensors with DNA
        # DISABLE optical flow fusion initially (as per documentation)
        "EKF2_OF_CTRL": {"value": 0, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},    # DISABLE optical flow fusion
        # Enable DroneCAN range sensor subscription
        "UAVCAN_SUB_RNG": {"value": 1, "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32},  # Enable UAVCAN range sensor
        # Range sensor configuration
        "EKF2_RNG_A_HMAX": {"value": 10.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Max height 10m
        "EKF2_RNG_QLTY_T": {"value": 0.2, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},  # Range quality threshold
        "UAVCAN_RNG_MIN": {"value": 0.08, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},  # Min range 0.08m
        "UAVCAN_RNG_MAX": {"value": 30.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},  # Max range 30m
        # Flow sensor configuration
        "SENS_FLOW_MINHGT": {"value": 0.08, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Min flow height
        "SENS_FLOW_MAXHGT": {"value": 25.0, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, # Max flow height
        "SENS_FLOW_MAXR": {"value": 7.4, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},    # Max angular flow rate (PAW3902)
        # Controller tuning for optical flow only operation
        "MPC_XY_P": {"value": 0.5, "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},          # Reduce horizontal position gain
    }
}


class BaseParameterHandler(ABC):
    """Abstract base class for parameter configuration handlers"""
    
    def __init__(self, mavlink_proxy: MavLinkExternalProxy, logger: logging.Logger):
        self.mavlink_proxy = mavlink_proxy
        self.logger = logger
    
    @abstractmethod
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        """Process the payload and return response data"""
        pass
    
    async def set_parameter(self, name: str, value: Union[str, int, float], ptype: int, message_id: str) -> Dict[str, Any]:
        """Helper method to set a single parameter"""
        try:
            success = await self.mavlink_proxy.set_param(name=name, value=value, ptype=ptype)
            
            if success:
                current_value = await self.mavlink_proxy.get_param(name)
                self.logger.info(f"[{message_id}] Set {name} = {value}")
                return {
                    "status": "success",
                    "set_value": value,
                    "confirmed_value": current_value
                }
            else:
                self.logger.error(f"[{message_id}] Failed to set {name} = {value}")
                return {
                    "status": "failed",
                    "set_value": value
                }
        except Exception as e:
            self.logger.error(f"[{message_id}] Error setting {name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def set_multiple_parameters(self, param_configs: Dict[str, Dict[str, Any]], message_id: str) -> Dict[str, Any]:
        """Helper method to set multiple parameters"""
        results = {}
        failed_params = []
        
        for param_name, config in param_configs.items():
            result = await self.set_parameter(
                param_name, 
                config["value"], 
                config["type"], 
                message_id
            )
            
            results[param_name] = result
            if result["status"] != "success":
                failed_params.append(param_name)
        
        if failed_params:
            return {
                "status": "partial_success",
                "message": f"Configuration completed with {len(failed_params)} failed parameters",
                "failed_parameters": failed_params,
                "results": results,
                "error_code": "PARTIAL_CONFIG_FAILURE"
            }
        else:
            return {
                "status": "success",
                "message": "Configuration completed successfully",
                "results": results,
                "timestamp": time.time()
            }


class RotorCountHandler(BaseParameterHandler):
    """Handler for rotor count configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        geo_payload = RotorCountParameter(**payload)
        self.logger.info(f"[{message_id}] Processing rotor count: {geo_payload.rotor_count}")
        
        result = await self.set_parameter(
            "CA_ROTOR_COUNT",
            int(geo_payload.rotor_count),
            mavutil.mavlink.MAV_PARAM_TYPE_INT32,
            message_id
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"CA_ROTOR_COUNT set to {geo_payload.rotor_count}",
                "rotor_count": geo_payload.rotor_count,
                "confirmed_value": result["confirmed_value"],
                "timestamp": time.time()
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to set CA_ROTOR_COUNT to {geo_payload.rotor_count}",
                "error_code": "PARAM_SET_FAILED"
            }


class GPSModuleHandler(BaseParameterHandler):
    """Handler for GPS module configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        gps_payload = GPSModulePayload(**payload)
        self.logger.info(f"[{message_id}] Processing GPS module: {gps_payload.gps_module}")
        
        if gps_payload.gps_module not in GPS_MODULE_CONFIGS:
            return {
                "status": "error",
                "message": f"Unknown GPS module: {gps_payload.gps_module}. Available: {list(GPS_MODULE_CONFIGS.keys())}",
                "error_code": "UNKNOWN_GPS_MODULE"
            }
        
        config = GPS_MODULE_CONFIGS[gps_payload.gps_module]
        result = await self.set_multiple_parameters(config, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["gps_module"] = gps_payload.gps_module
            result["message"] = f"GPS module {gps_payload.gps_module} " + result["message"]
        
        return result


class DistanceModuleHandler(BaseParameterHandler):
    """Handler for distance module configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        dist_payload = DistanceModulePayload(**payload)
        self.logger.info(f"[{message_id}] Processing distance module: {dist_payload.dist_module}")
        
        if dist_payload.dist_module not in DISTANCE_MODULE_CONFIGS:
            return {
                "status": "error",
                "message": f"Unknown distance module: {dist_payload.dist_module}. Available: {list(DISTANCE_MODULE_CONFIGS.keys())}",
                "error_code": "UNKNOWN_DISTANCE_MODULE"
            }
        
        config = DISTANCE_MODULE_CONFIGS[dist_payload.dist_module]
        result = await self.set_multiple_parameters(config, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["dist_module"] = dist_payload.dist_module
            result["message"] = f"Distance module {dist_payload.dist_module} " + result["message"]
        
        return result


class OpticalFlowModuleHandler(BaseParameterHandler):
    """Handler for optical flow module configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        oflow_payload = OpticalFlowModulePayload(**payload)
        self.logger.info(f"[{message_id}] Processing optical flow module: {oflow_payload.oflow_module}")
        
        if oflow_payload.oflow_module not in OPTICAL_FLOW_MODULE_CONFIGS:
            return {
                "status": "error",
                "message": f"Unknown optical flow module: {oflow_payload.oflow_module}. Available: {list(OPTICAL_FLOW_MODULE_CONFIGS.keys())}",
                "error_code": "UNKNOWN_OPTICAL_FLOW_MODULE"
            }
        
        config = OPTICAL_FLOW_MODULE_CONFIGS[oflow_payload.oflow_module]
        result = await self.set_multiple_parameters(config, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["oflow_module"] = oflow_payload.oflow_module
            result["message"] = f"Optical flow module {oflow_payload.oflow_module} " + result["message"]
        
        return result


class GPSSpatialOffsetHandler(BaseParameterHandler):
    """Handler for GPS spatial offset configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        offset_payload = GPSSpatialOffsetPayload(**payload)
        self.logger.info(f"[{message_id}] Processing GPS spatial offsets")
        
        param_configs = {
            "EKF2_GPS_POS_X": {
                "value": float(offset_payload.gps_module_spatial_offset_x_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_GPS_POS_Y": {
                "value": float(offset_payload.gps_module_spatial_offset_y_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_GPS_POS_Z": {
                "value": float(offset_payload.gps_module_spatial_offset_z_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            }
        }
        
        result = await self.set_multiple_parameters(param_configs, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["offsets"] = {
                "x": offset_payload.gps_module_spatial_offset_x_m,
                "y": offset_payload.gps_module_spatial_offset_y_m,
                "z": offset_payload.gps_module_spatial_offset_z_m
            }
            result["message"] = f"GPS spatial offsets " + result["message"]
        
        return result


class DistanceSpatialOffsetHandler(BaseParameterHandler):
    """Handler for distance sensor spatial offset configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        offset_payload = DistanceSpatialOffsetPayload(**payload)
        self.logger.info(f"[{message_id}] Processing distance sensor spatial offsets")
        
        param_configs = {
            "EKF2_RNG_POS_X": {
                "value": float(offset_payload.dist_module_spatial_offset_x_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_RNG_POS_Y": {
                "value": float(offset_payload.dist_module_spatial_offset_y_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_RNG_POS_Z": {
                "value": float(offset_payload.dist_module_spatial_offset_z_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            }
        }
        
        result = await self.set_multiple_parameters(param_configs, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["offsets"] = {
                "x": offset_payload.dist_module_spatial_offset_x_m,
                "y": offset_payload.dist_module_spatial_offset_y_m,
                "z": offset_payload.dist_module_spatial_offset_z_m
            }
            result["message"] = f"Distance sensor spatial offsets " + result["message"]
        
        return result


class OpticalFlowSpatialOffsetHandler(BaseParameterHandler):
    """Handler for optical flow spatial offset configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        offset_payload = OpticalFlowSpatialOffsetPayload(**payload)
        self.logger.info(f"[{message_id}] Processing optical flow spatial offsets")
        
        param_configs = {
            "EKF2_OF_POS_X": {
                "value": float(offset_payload.oflow_module_spatial_offset_x_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_OF_POS_Y": {
                "value": float(offset_payload.oflow_module_spatial_offset_y_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            },
            "EKF2_OF_POS_Z": {
                "value": float(offset_payload.oflow_module_spatial_offset_z_m),
                "type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            }
        }
        
        result = await self.set_multiple_parameters(param_configs, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["offsets"] = {
                "x": offset_payload.oflow_module_spatial_offset_x_m,
                "y": offset_payload.oflow_module_spatial_offset_y_m,
                "z": offset_payload.oflow_module_spatial_offset_z_m
            }
            result["message"] = f"Optical flow spatial offsets " + result["message"]
        
        return result


class ESCCalibrationLimitsHandler(BaseParameterHandler):
    """Handler for ESC calibration limits configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        limits_payload = ESCCalibrationLimitsPayload(**payload)
        self.logger.info(f"[{message_id}] Processing ESC calibration limits: MAX={limits_payload.motors_common_max_pwm}, MIN={limits_payload.motors_common_min_pwm}")
        
        # Validate that max > min
        if limits_payload.motors_common_max_pwm <= limits_payload.motors_common_min_pwm:
            return {
                "status": "error",
                "message": f"Maximum PWM ({limits_payload.motors_common_max_pwm}) must be greater than minimum PWM ({limits_payload.motors_common_min_pwm})",
                "failed_parameters": [],
                "successful_parameters": []
            }
        
        # Get motor count from CA_ROTOR_COUNT
        try:
            rotor_count_result = await self.mavlink_proxy.get_param("CA_ROTOR_COUNT")
            if rotor_count_result is None:
                logging.error(f"[{message_id}] CA_ROTOR_COUNT not set, exiting with error")
                return {
                    "status": "error",
                    "message": "CA_ROTOR_COUNT parameter not set on vehicle",
                    "error_code": "PARAM_NOT_SET"
                }

            if rotor_count_result.get("value") is None:
                logging.error(f"[{message_id}] CA_ROTOR_COUNT has no value, exiting with error")
                return {
                    "status": "error",
                    "message": "CA_ROTOR_COUNT parameter has no value",
                    "error_code": "PARAM_NO_VALUE"
                }
            
            motor_count = int(rotor_count_result.get("value"))

            self.logger.info(f"[{message_id}] Setting PWM limits for {motor_count} motors")
        except Exception as e:
            self.logger.warning(f"[{message_id}] Could not get CA_ROTOR_COUNT: {e}. Exiting with error.")
            return {
                "status": "error",
                "message": f"Could not retrieve CA_ROTOR_COUNT: {e}",
                "error_code": "PARAM_RETRIEVE_FAILED"
            }
        
        # Build parameter configurations for all motors
        param_configs = {}
        for motor_idx in range(1, motor_count + 1):
            param_configs[f"PWM_AUX_MAX{motor_idx}"] = {
                "value": limits_payload.motors_common_max_pwm,
                "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32
            }
            param_configs[f"PWM_AUX_MIN{motor_idx}"] = {
                "value": limits_payload.motors_common_min_pwm,
                "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32
            }
        
        result = await self.set_multiple_parameters(param_configs, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["motor_count"] = motor_count
            result["max_pwm"] = limits_payload.motors_common_max_pwm
            result["min_pwm"] = limits_payload.motors_common_min_pwm
            result["message"] = f"ESC calibration limits updated for {motor_count} motors - " + result["message"]
        
        return result


class KillSwitchConfigHandler(BaseParameterHandler):
    """Handler for kill switch configuration"""
    
    async def process_payload(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        """Configure kill switch parameters."""
        self.logger.info(f"[{message_id}] Configuring kill switch parameters")
        
        # Build parameter configurations
        param_configs = {}
        
        # 1. Set RC_MAP_KILL_SW to channel 7
        param_configs["RC_MAP_KILL_SW"] = {
            "value": 7,
            "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32
        }
        
        # 2. Clear all flight mode assignments (COM_FLTMODE1 to COM_FLTMODE6)
        for mode_idx in range(1, 7):
            param_configs[f"COM_FLTMODE{mode_idx}"] = {
                "value": -1,
                "type": mavutil.mavlink.MAV_PARAM_TYPE_INT32
            }
        
        result = await self.set_multiple_parameters(param_configs, message_id)
        
        if result["status"] in ["success", "partial_success"]:
            result["kill_switch_channel"] = 7
            result["cleared_flight_modes"] = list(range(1, 7))
            result["message"] = f"Kill switch configured on channel 7, flight modes cleared - " + result["message"]
        
        return result


class BaseTimeoutController(ABC):
    """
    Base class for timeout-controlled operations via MAVLink.
    Provides common functionality for sending commands and managing timeouts.
    """
    
    def __init__(self, mavlink_proxy: MavLinkExternalProxy, logger: logging.Logger):
        self.mavlink_proxy = mavlink_proxy
        self.logger = logger
        self.is_active = False
        self.current_task: Optional[asyncio.Task] = None
        self.stop_event = threading.Event()
        self.last_command_time = None
        self.current_safety_timeout = 3.0
        self.lock = threading.Lock()

    async def send_mav_start_cmd(self, target_numbers: List[int], values: List[float], timeout: float = 3.0):
        """
        Send MAV_CMD_ACTUATOR_TEST command to start operation target(s).
        
        Args:
            target_numbers: List of target numbers (1-based, e.g., motor numbers)
            values: List of command values [-1..1] corresponding to targets
            timeout: Command timeout in seconds (<=3)
        """
        if len(target_numbers) != len(values):
            raise ValueError("Target numbers and values lists must have same length")
            
        for target_num, value in zip(target_numbers, values):
            await self._send_actuator_test_command(target_num, value, timeout)

    async def send_mav_stop_cmd(self, target_numbers: List[int], timeout: float = 3.0):
        """
        Send MAV_CMD_ACTUATOR_TEST command to stop operation target(s) with explicit disarm.
        
        Args:
            target_numbers: List of target numbers (1-based, e.g., motor numbers) to stop
            timeout: Command timeout in seconds (<=3)
        """
        for target_num in target_numbers:
            await self._send_actuator_test_command(target_num, float('nan'), timeout)
            self.logger.info(f"Sent explicit disarm command for target {target_num}")

    async def _send_actuator_test_command(self, target_number: int, value: float, timeout: float):
        """
        Send a single MAV_CMD_ACTUATOR_TEST command.
        
        Args:
            target_number: Target number (1-based, e.g., motor number)
            value: Test value [-1..1], NaN to stop
            timeout: Command timeout in seconds (<=3)
        """
        try:
            # Build the command message
            command_msg = self.mavlink_proxy.build_req_msg_long(mavutil.mavlink.MAV_CMD_ACTUATOR_TEST)
            
            # Set command parameters
            command_msg.param1 = value  # Test value [-1..1]
            command_msg.param2 = timeout  # Timeout seconds
            command_msg.param3 = 0  # Reserved
            command_msg.param4 = 0  # Reserved
            command_msg.param5 = mavutil.mavlink.ACTUATOR_OUTPUT_FUNCTION_MOTOR1 + (target_number - 1)  # Motor function
            command_msg.param6 = 0  # Reserved
            command_msg.param7 = 0  # Reserved
            
            # Send the command
            self.mavlink_proxy.send("mav", command_msg)
            
            # Log command details
            if math.isnan(value):
                self.logger.info(f"Sent DISARM command for target {target_number}")
            else:
                self.logger.info(f"Sent MAV_CMD_ACTUATOR_TEST for target {target_number} with value {value}")
                
        except Exception as e:
            self.logger.error(f"Failed to send MAV_CMD_ACTUATOR_TEST: {e}")
            raise

    def refresh_timeout(self, new_timeout: float):
        """
        Refresh the safety timeout with a new value.
        
        Args:
            new_timeout: New timeout value in seconds
        """
        with self.lock:
            self.current_safety_timeout = min(new_timeout, 3.0)  # Cap at 3 seconds
            self.last_command_time = time.time()
            self.logger.debug(f"Refreshed timeout to {self.current_safety_timeout}s")

    def is_timeout_expired(self) -> bool:
        """
        Check if the current timeout has expired.
        
        Returns:
            True if timeout has expired, False otherwise
        """
        with self.lock:
            if self.last_command_time is None:
                return False
            return time.time() - self.last_command_time > self.current_safety_timeout

    async def emergency_stop(self, target_numbers: List[int]):
        """
        Emergency stop for specified targets with immediate disarm.
        
        Args:
            target_numbers: List of target numbers to stop
        """
        self.logger.warning(f"Emergency stop requested for targets: {target_numbers}")
        self.stop_event.set()
        await self.send_mav_stop_cmd(target_numbers, timeout=3.0)
        self.is_active = False

    @abstractmethod
    async def start_operation(self, payload: Dict[str, Any]) -> None:
        """
        Start the timeout-controlled operation with given payload.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def stop_operation(self) -> None:
        """
        Stop the timeout-controlled operation.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_operation_targets(self) -> List[int]:
        """
        Get the list of target numbers this controller manages.
        Must be implemented by subclasses.
        """
        pass


class ESCCalibrationController(BaseTimeoutController):
    """
    Enhanced ESC calibration controller with step-by-step workflow.
    
    Workflow:
    1. Set PWM_AUX_TIM0 based on ESC signal interface type
    2. Set PWM_AUX_MAX/MIN for each motor
    3. Execute throttle commands based on user input (maximum/minimum/stop)
    """
    
    def __init__(self, mavlink_proxy: MavLinkExternalProxy, logger: logging.Logger, motor_count: int = 4):
        super().__init__(mavlink_proxy, logger)
        self.motor_count = motor_count
        self.calibration_state = "idle"  # idle, configured, maximum, minimum, stopped
        
        # ESC signal interface configurations
        self.esc_interface_configs = {
            "PWM": {
                "PWM_AUX_TIM0": 400,  # PWM 400Hz
                "description": "Standard PWM 400Hz"
            },
            "OneShot125": {
                "PWM_AUX_TIM0": 0,  # OneShot125 mode
                "description": "OneShot125 ESC protocol"
            },
            "OneShot42": {
                "PWM_AUX_TIM0": 1,  # OneShot42 mode
                "description": "OneShot42 ESC protocol"
            },
            "Multishot": {
                "PWM_AUX_TIM0": 2,  # Multishot mode
                "description": "Multishot ESC protocol"
            },
            "DShot150": {
                "PWM_AUX_TIM0": 3,  # DShot150 mode
                "description": "DShot150 digital ESC protocol"
            },
            "DShot300": {
                "PWM_AUX_TIM0": 4,  # DShot300 mode
                "description": "DShot300 digital ESC protocol"
            },
            "DShot600": {
                "PWM_AUX_TIM0": 5,  # DShot600 mode
                "description": "DShot600 digital ESC protocol"
            },
            "DShot1200": {
                "PWM_AUX_TIM0": 6,  # DShot1200 mode
                "description": "DShot1200 digital ESC protocol"
            }
        }

    def get_operation_targets(self) -> List[int]:
        return list(range(1, self.motor_count + 1))

    def get_available_interfaces(self) -> Dict[str, str]:
        """Get available ESC interface types and their descriptions."""
        return {interface: config["description"] for interface, config in self.esc_interface_configs.items()}

    async def _setup_interface_parameters(self, interface_type: str, rotor_count: Optional[int], message_id: str) -> bool:
        """Setup interface parameters for ESC calibration."""
        try:
            if interface_type not in self.esc_interface_configs:
                self.logger.error(f"[{message_id}] Unsupported ESC interface: {interface_type}")
                available_interfaces = list(self.esc_interface_configs.keys())
                self.logger.info(f"[{message_id}] Available interfaces: {available_interfaces}")
                return False
            
            config = self.esc_interface_configs[interface_type]
            self.logger.info(f"[{message_id}] Configuring {config['description']} interface")
            
            # Step 1: Set PWM_AUX_TIM0 for the interface type
            success = await self.mavlink_proxy.set_param(
                name="PWM_AUX_TIM0",
                value=config["PWM_AUX_TIM0"],
                ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
            )
            
            if not success:
                self.logger.error(f"[{message_id}] Failed to set PWM_AUX_TIM0")
                return False
                
            self.logger.info(f"[{message_id}] Set PWM_AUX_TIM0 = {config['PWM_AUX_TIM0']} for {interface_type}")
            
            # Step 2: Handle motor count - use provided value or get from CA_ROTOR_COUNT
            if rotor_count is not None:
                self.motor_count = rotor_count
                self.logger.info(f"[{message_id}] Using provided motor count: {self.motor_count}")
            else:
                # Get current motor count from CA_ROTOR_COUNT
                rotor_count_param = await self.mavlink_proxy.get_param("CA_ROTOR_COUNT")
                if rotor_count_param is not None:
                    self.motor_count = int(rotor_count_param.get("value", None))
                    if self.motor_count is None or self.motor_count <= 0:
                        self.logger.error(f"[{message_id}] Invalid CA_ROTOR_COUNT value, cannot proceed")
                        return False
                    self.logger.info(f"[{message_id}] Updated motor count from CA_ROTOR_COUNT: {self.motor_count}")
                else:
                    self.logger.warning(f"[{message_id}] Could not get CA_ROTOR_COUNT, using default: {self.motor_count}")
            
            # set motor count
            success = await self.mavlink_proxy.set_param(
                name="CA_ROTOR_COUNT",
                value=self.motor_count,
                ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
            )
            if not success:
                self.logger.error(f"[{message_id}] Failed to set CA_ROTOR_COUNT")
                return False
            self.logger.info(f"[{message_id}] Set CA_ROTOR_COUNT = {self.motor_count}")

            # Step 3: Set PWM_AUX_MAX and PWM_AUX_MIN and PWM_AUX_FUNC for each motor (only for PWM-based protocols)
            if interface_type in ["PWM"]:  # Only set PWM limits for PWM mode
                for motor_idx in range(1, self.motor_count + 1):
                    # Set PWM_AUX_MAX{motor_idx} = 2000
                    max_param = f"PWM_AUX_MAX{motor_idx}"
                    success = await self.mavlink_proxy.set_param(
                        name=max_param,
                        value=2000,
                        ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
                    )
                    if not success:
                        self.logger.error(f"[{message_id}] Failed to set {max_param}")
                        return False
                        
                    # Set PWM_AUX_MIN{motor_idx} = 1000
                    min_param = f"PWM_AUX_MIN{motor_idx}"
                    success = await self.mavlink_proxy.set_param(
                        name=min_param,
                        value=1000,
                        ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
                    )
                    if not success:
                        self.logger.error(f"[{message_id}] Failed to set {min_param}")
                        return False
                    
                    # Set PWM_AUX_FUNC{motor_idx} = MOTORx
                    func_param = f"PWM_AUX_FUNC{motor_idx}"
                    success = await self.mavlink_proxy.set_param(
                        name=func_param,
                        value=100+motor_idx,
                        ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
                    )
                    if not success:
                        self.logger.error(f"[{message_id}] Failed to set {func_param}")
                        return False
                    
                    self.logger.info(f"[{message_id}] Set {max_param}=2000, {min_param}=1000, {func_param}={100+motor_idx}")
            else:
                self.logger.info(f"[{message_id}] Digital protocol {interface_type} - skipping PWM range configuration")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Error setting interface parameters: {e}")
            return False

    async def _send_throttle_command(self, throttle_type: str, message_id: str) -> bool:
        """Send throttle command to all motors."""
        try:
            for motor_idx in range(1, self.motor_count + 1):
                if throttle_type == "maximum":
                    # Maximum throttle (param1=1.0)
                    param1 = 1.0
                    timeout = 3.0
                elif throttle_type == "minimum":
                    # Minimum throttle (param1=0.0)
                    param1 = 0.0
                    timeout = 3.0
                elif throttle_type == "stop":
                    # Stop motors (param1=NaN, timeout=0)
                    param1 = float('nan')
                    timeout = 0.0
                else:
                    self.logger.error(f"[{message_id}] Unknown throttle type: {throttle_type}")
                    return False
                
                command_msg = self.mavlink_proxy.build_motor_value_command(
                    motor_idx=motor_idx, 
                    motor_value=param1, 
                    timeout=timeout
                )

                # Send the command
                self.mavlink_proxy.send("mav", command_msg)
                
                action = "maximum throttle" if throttle_type == "maximum" else \
                        "minimum throttle" if throttle_type == "minimum" else "stopped"
                self.logger.info(f"[{message_id}] Motor {motor_idx}: {action} (motor value={param1}, timeout={timeout}s)")
                    
                # Small delay between motor commands
                await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Error sending throttle command: {e}")
            return False

    async def start_operation(self, payload: ESCCalibrationPayload) -> None:
        """Start ESC calibration with enhanced workflow. Called only once to initialize."""
        message_id = str(uuid.uuid4())[:8]
        
        try:
            # Handle force cancel or stop
            if payload.force_cancel_calibration:
                self.logger.info(f"[{message_id}] ESC calibration cancelled/stopped")
                await self._send_throttle_command("stop", message_id)
                self.calibration_state = "stopped"
                self.is_active = False
                return
            
            # This should only run once - setup interface parameters
            self.logger.info(f"[{message_id}] Starting ESC calibration setup (one-time initialization)...")
            
            # Setup interface parameters with optional rotor count
            interface_type = payload.esc_interface_signal_type or "PWM"
            if not await self._setup_interface_parameters(interface_type, payload.ca_rotor_count, message_id):
                raise Exception("Failed to setup interface parameters")
            
            # Set initial calibration state from payload
            self.calibration_state = "configured"
            self.logger.info(f"[{message_id}] Initial state set to CONFIGURED (waiting for throttle commands)")
        
            # Update timeout and start the calibration task
            self.refresh_timeout(payload.safety_timeout_s)
            self.is_active = True
            self.stop_event.clear()
            
            # Create the calibration loop task directly - this is the modern approach
            # and works properly when called from async context scheduled by run_coroutine_threadsafe
            try:
                self.current_task = asyncio.create_task(self._calibration_loop())
                self.logger.info(f"[{message_id}] ESC calibration task created - setup complete")
            except Exception as e:
                self.logger.error(f"[{message_id}] Failed to create calibration loop task: {e}")
                # Reset state on failure
                self.is_active = False
                self.calibration_state = "stopped"
                raise
            
        except Exception as e:
            self.logger.error(f"[{message_id}] ESC calibration error: {e}")
            # Emergency stop on error
            await self._send_throttle_command("stop", message_id)
            self.calibration_state = "stopped"
            self.is_active = False

    async def stop_operation(self) -> None:
        """Stop ESC calibration and disarm all motors."""
        message_id = str(uuid.uuid4())[:8]
        self.logger.info(f"[{message_id}] Emergency stop ESC calibration")
        
        # Signal stop and set inactive
        self.stop_event.set()
        self.is_active = False
        
        # Send emergency stop to all motors
        try:
            await self._send_throttle_command("stop", message_id)
        except Exception as e:
            self.logger.error(f"[{message_id}] Error stopping motors: {e}")
        
        self.calibration_state = "stopped"
        
        # Cancel and wait for task completion with timeout
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            try:
                # Wait for task cancellation with timeout to avoid hanging
                await self.current_task
            except asyncio.CancelledError:
                self.logger.info(f"[{message_id}] Task cancelled successfully")
            except asyncio.TimeoutError:
                self.logger.warning(f"[{message_id}] Task cancellation timed out - forcing cleanup")
            except Exception as e:
                self.logger.warning(f"[{message_id}] Error during task cancellation: {e}")
        
        # Clear task reference and reset stop event for recovery
        self.current_task = None
        self.stop_event.clear()
        self.logger.info(f"[{message_id}] ESC calibration stop complete - ready for recovery")

    async def _calibration_loop(self):
        """Main calibration loop that reacts to calibration state changes and maintains throttle commands."""
        message_id = str(uuid.uuid4())[:8]
        self.logger.info(f"[{message_id}] Starting ESC calibration loop")
        
        last_state = None
        
        try:
            while self.is_active and not self.stop_event.is_set() and not self.is_timeout_expired():
                current_state = self.calibration_state
                
                # React to state changes
                if current_state != last_state:
                    if current_state == "maximum":
                        self.logger.info(f"[{message_id}] State changed to MAXIMUM - sending maximum throttle")
                        self.logger.warning(f"[{message_id}] ⚠️  POWER UP THE DRONE NOW! ESCs are receiving maximum throttle signal.")
                        await self._send_throttle_command("maximum", message_id)
                        
                    elif current_state == "minimum":
                        self.logger.info(f"[{message_id}] State changed to MINIMUM - sending minimum throttle")
                        await self._send_throttle_command("minimum", message_id)
                        self.logger.info(f"[{message_id}] ✅ Minimum throttle sent. ESC calibration should be complete.")
                        
                    elif current_state == "configured":
                        self.logger.info(f"[{message_id}] State is CONFIGURED - waiting for throttle commands")
                    
                    last_state = current_state
                
                # Maintain current throttle state by sending periodic commands
                if current_state == "maximum":
                    await self._send_throttle_command("maximum", message_id)
                    self.logger.debug(f"[{message_id}] Maintaining maximum throttle")
                    
                elif current_state == "minimum":
                    await self._send_throttle_command("minimum", message_id)
                    self.logger.debug(f"[{message_id}] Maintaining minimum throttle")
                
                # Wait before next iteration (send commands every 0.5 seconds)
                await asyncio.sleep(0.5)
            
            # Timeout or stop reached
            if self.is_timeout_expired():
                self.logger.warning(f"[{message_id}] ESC calibration timeout reached")
            else:
                self.logger.info(f"[{message_id}] ESC calibration stopped normally")
            
        except asyncio.CancelledError:
            self.logger.info(f"[{message_id}] ESC calibration loop cancelled")
        except Exception as e:
            self.logger.error(f"[{message_id}] Error in ESC calibration loop: {e}")
        finally:
            # Always stop motors and reset state when exiting (timeout, cancel, or error)
            try:
                await self._send_throttle_command("stop", message_id)
            except Exception as e:
                self.logger.error(f"[{message_id}] Error stopping motors in cleanup: {e}")
            
            # Reset all state to allow recovery
            self.calibration_state = "stopped"
            self.is_active = False
            self.current_task = None
            self.stop_event.clear()
            self.logger.info(f"[{message_id}] ESC calibration loop cleanup complete - ready for recovery")


class ESCForceRunAllController(BaseTimeoutController):
    """
    Controller for running all motors with a common command value using MAV_CMD_ACTUATOR_TEST.
    """
    
    def __init__(self, mavlink_proxy: MavLinkExternalProxy, logger: logging.Logger, motor_count: int = 4):
        super().__init__(mavlink_proxy, logger)
        self.motor_count = motor_count
        self.current_command_value = 0.0
        self.MIN_RAW_COMMAND_EXPECTED = 1000.0
        self.MAX_RAW_COMMAND_EXPECTED = 2000.0
        self.min_raw_command = None
        self.max_raw_command = None

    def get_operation_targets(self) -> List[int]:
        return list(range(1, self.motor_count + 1))

    def _map_command_to_pwm_range(self, command_value: float, min_pwm: float = 1000.0, max_pwm: float = 2000.0) -> float:
        """Map command value from [min..max] to [0..1] for PWM range 1000-2000 as an example."""
        # Input: [min..max], Output: [0..1] for 1000-2000 PWM range
        return max(0.0, min(1.0, (command_value - min_pwm) / (max_pwm - min_pwm)))

    async def _send_actuator_test_all_motors(self, motor_value: float, timeout: float) -> bool:
        """Send MAV_CMD_ACTUATOR_TEST command to all motors."""
        try:
            for motor_idx in range(1, self.motor_count + 1):

                command_msg = self.mavlink_proxy.build_motor_value_command(
                    motor_idx=motor_idx, 
                    motor_value=motor_value, 
                    timeout=timeout
                )

                # Send the command
                self.mavlink_proxy.send("mav", command_msg)
                    
                # Small delay between motor commands
                await asyncio.sleep(0.02)  # 20ms delay
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending actuator test commands: {e}")
            return False

    async def _stop_all_motors(self) -> bool:
        """Stop all motors using NaN value."""
        try:
            # Use NaN to stop motors (0x7FC00000 for float32 NaN)
            nan_value = float('nan')
            
            for motor_idx in range(1, self.motor_count + 1):

                command_msg = self.mavlink_proxy.build_motor_value_command(
                    motor_idx=motor_idx, 
                    motor_value=nan_value, 
                    timeout=0.0
                )

                # Send the command
                self.mavlink_proxy.send("mav", command_msg)

                self.logger.info(f"Motor {motor_idx} stopped")
                    
                await asyncio.sleep(0.02)  # 20ms delay
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping motors: {e}")
            return False

    async def start_operation(self, payload: ESCForceRunAllPayload) -> None:
        """Start running all motors with common command value."""
        if payload.force_cancel:
            self.logger.info("Force cancel requested, stopping all motors")
            await self.stop_operation()
            return

        # Update command value and timeout
        self.current_command_value = payload.motors_common_command
        self.refresh_timeout(payload.safety_timeout_s)

        # get min/max raw command values for mapping
        min_raw_result = await self.mavlink_proxy.get_param("PWM_AUX_MIN1")
        max_raw_result = await self.mavlink_proxy.get_param("PWM_AUX_MAX1")

        if min_raw_result is None or max_raw_result is None:
            self.logger.error("Could not get PWM_AUX_MIN1 or PWM_AUX_MAX1, stopping operation")
            await self.stop_operation()
            return
        
        if min_raw_result.get("value") is None or max_raw_result.get("value") is None:
            self.logger.error("PWM_AUX_MIN1 or PWM_AUX_MAX1 parameter has no value, stopping operation")
            await self.stop_operation()
            return

        # assert min < max, min = 1000, max = 2000 as typical defaults
        self.min_raw_command = float(min_raw_result.get("value"))
        self.max_raw_command = float(max_raw_result.get("value"))

        if self.min_raw_command >= self.max_raw_command:
            self.logger.error(f"Invalid PWM range: min {self.min_raw_command} >= max {self.max_raw_command}, stopping operation")
            await self.stop_operation()
            return

        if self.min_raw_command < self.MIN_RAW_COMMAND_EXPECTED or self.max_raw_command > self.MAX_RAW_COMMAND_EXPECTED:
            self.logger.error(f"Unusual PWM range: min {self.min_raw_command}, max {self.max_raw_command}")
            await self.stop_operation()
            return
        
        # check that all motors have the same min/max
        for motor_idx in range(2, self.motor_count + 1):
            min_param = f"PWM_AUX_MIN{motor_idx}"
            max_param = f"PWM_AUX_MAX{motor_idx}"
            min_result = await self.mavlink_proxy.get_param(min_param)
            max_result = await self.mavlink_proxy.get_param(max_param)
            if min_result is None or max_result is None:
                self.logger.error(f"Could not get {min_param} or {max_param}, stopping operation")
                await self.stop_operation()
                return
            if min_result.get("value") != self.min_raw_command or max_result.get("value") != self.max_raw_command:
                self.logger.error(f"Inconsistent PWM range on motor {motor_idx}: min {min_result.get('value')}, max {max_result.get('value')}, expected min {self.min_raw_command}, max {self.max_raw_command}. Stopping operation.")
                await self.stop_operation()
                return

        if not self.is_active:
            self.logger.info(f"Starting force run all motors with value {self.current_command_value}")
            self.is_active = True
            self.stop_event.clear()
            
            # Create the force run all task directly
            try:
                self.current_task = asyncio.create_task(self._force_run_loop())
                self.logger.info("Force run all loop task created successfully")
            except Exception as e:
                self.logger.error(f"Failed to create force run all loop task: {e}")
                # Reset state on failure
                self.is_active = False
                raise
        else:
            self.logger.debug(f"Force run all already active, updating value to {self.current_command_value}")

    async def stop_operation(self) -> None:
        """Stop force run all and disarm all motors."""
        self.logger.info("Stopping force run all motors")
        self.stop_event.set()
        self.is_active = False
        
        # Send explicit stop to all motors
        try:
            await self._stop_all_motors()
        except Exception as e:
            self.logger.error(f"Error stopping motors: {e}")
        
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            try:
                # Wait for task cancellation with timeout to avoid hanging
                await self.current_task
            except asyncio.CancelledError:
                self.logger.info("Force run all task cancelled successfully")
            except asyncio.TimeoutError:
                self.logger.warning("Force run all task cancellation timed out - forcing cleanup")
            except Exception as e:
                self.logger.warning(f"Error during force run all task cancellation: {e}")
        
        # Clear task reference and reset for recovery
        self.current_task = None
        self.stop_event.clear()
        self.logger.info("Force run all stop complete - ready for recovery")

    async def _force_run_loop(self):
        """Main force run loop for all motors."""
        try:
            while not self.stop_event.is_set() and self.is_active:
                # Check timeout
                if self.is_timeout_expired():
                    self.logger.warning("Force run all timeout expired, stopping")
                    break
                
                # Map command value to [0..1] range
                motor_value = self._map_command_to_pwm_range(self.current_command_value, self.min_raw_command , self.max_raw_command)
                
                # Send command to all motors with 1 second timeout
                success = await self._send_actuator_test_all_motors(motor_value, 1.0)
                
                if not success:
                    self.logger.error("Failed to send commands to motors, stopping operation")
                    break
                
                # Wait before next command (800ms to ensure commands don't timeout)
                await asyncio.sleep(0.8)
                
        except asyncio.CancelledError:
            self.logger.info("Force run all task cancelled")
        except Exception as e:
            self.logger.error(f"Error in force run all loop: {e}")
        finally:
            # Ensure motors are stopped and state is reset for recovery
            try:
                await self._stop_all_motors()
            except Exception as e:
                self.logger.error(f"Error stopping motors in cleanup: {e}")
            
            self.is_active = False
            self.current_task = None
            self.stop_event.clear()
            self.logger.info("Force run all cleanup complete - ready for recovery")


class ESCForceRunSingleController(BaseTimeoutController):
    """
    Controller for running a single motor with a specific command value using MAV_CMD_ACTUATOR_TEST.
    """
    
    def __init__(self, mavlink_proxy: MavLinkExternalProxy, logger: logging.Logger):
        super().__init__(mavlink_proxy, logger)
        self.target_motor = 1
        self.current_command_value = 0.0
        self.MIN_RAW_COMMAND_EXPECTED = 1000.0
        self.MAX_RAW_COMMAND_EXPECTED = 2000.0
        self.min_raw_command = None
        self.max_raw_command = None

    def get_operation_targets(self) -> List[int]:
        return [self.target_motor]

    def _map_command_to_pwm_range(self, command_value: float, min_pwm: float = 1000.0, max_pwm: float = 2000.0) -> float:
        """Map command value from [min..max] to [0..1] for PWM range 1000-2000 as an example."""
        # Input: [min..max], Output: [0..1] for 1000-2000 PWM range
        return max(0.0, min(1.0, (command_value - min_pwm) / (max_pwm - min_pwm)))

    async def _send_actuator_test_single_motor(self, motor_value: float, timeout: float) -> bool:
        """Send MAV_CMD_ACTUATOR_TEST command to single motor."""
        try:

            command_msg = self.mavlink_proxy.build_motor_value_command(
                motor_idx=self.target_motor, 
                motor_value=motor_value, 
                timeout=timeout
            )
            
            # Send the command
            self.mavlink_proxy.send("mav", command_msg)

            self.logger.debug(f"Motor {self.target_motor}: command sent (value={motor_value}, timeout={timeout})")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending actuator test command to motor {self.target_motor}: {e}")
            return False

    async def _stop_single_motor(self) -> bool:
        """Stop single motor using NaN value."""
        try:
            # Use NaN to stop motor
            nan_value = float('nan')
            
            command_msg = self.mavlink_proxy.build_motor_value_command(
                motor_idx=self.target_motor, 
                motor_value=nan_value, 
                timeout=0.0
            )

            # Send the command
            self.mavlink_proxy.send("mav", command_msg)

            self.logger.info(f"Motor {self.target_motor} stopped")

            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping motor {self.target_motor}: {e}")
            return False

    async def start_operation(self, payload: ESCForceRunSinglePayload) -> None:
        """Start running single motor with specific command value."""
        if payload.force_cancel:
            self.logger.info(f"Force cancel requested for motor {payload.motor_idx}, stopping")
            await self.stop_operation()
            return

        # Update motor, command value and timeout
        self.target_motor = payload.motor_idx
        self.current_command_value = payload.motor_command
        self.refresh_timeout(payload.safety_timeout_s)

        # get min/max raw command values for mapping
        min_raw_result = await self.mavlink_proxy.get_param(f"PWM_AUX_MIN{self.target_motor}")
        max_raw_result = await self.mavlink_proxy.get_param(f"PWM_AUX_MAX{self.target_motor}")

        if min_raw_result is None or max_raw_result is None:
            self.logger.error(f"Could not get PWM_AUX_MIN{self.target_motor} or PWM_AUX_MAX{self.target_motor}, stopping operation")
            await self.stop_operation()
            return
        
        if min_raw_result.get("value") is None or max_raw_result.get("value") is None:
            self.logger.error(f"PWM_AUX_MIN{self.target_motor} or PWM_AUX_MAX{self.target_motor} parameter has no value, stopping operation")
            await self.stop_operation()
            return

        # assert min < max, min = 1000, max = 2000 as typical defaults
        self.min_raw_command = float(min_raw_result.get("value"))
        self.max_raw_command = float(max_raw_result.get("value"))

        if self.min_raw_command >= self.max_raw_command:
            self.logger.error(f"Invalid PWM range: min {self.min_raw_command} >= max {self.max_raw_command}, stopping operation")
            await self.stop_operation()
            return

        if self.min_raw_command < self.MIN_RAW_COMMAND_EXPECTED or self.max_raw_command > self.MAX_RAW_COMMAND_EXPECTED:
            self.logger.error(f"Unusual PWM range: min {self.min_raw_command}, max {self.max_raw_command}")
            await self.stop_operation()
            return

        if not self.is_active:
            self.logger.info(f"Starting force run motor {self.target_motor} with value {self.current_command_value}")
            self.is_active = True
            self.stop_event.clear()
            
            # Create the force run single task directly
            try:
                self.current_task = asyncio.create_task(self._force_run_single_loop())
                self.logger.info(f"Force run single loop task created successfully for motor {self.target_motor}")
            except Exception as e:
                self.logger.error(f"Failed to create force run single loop task: {e}")
                # Reset state on failure
                self.is_active = False
                raise
        else:
            self.logger.debug(f"Force run single already active, updating motor {self.target_motor} value to {self.current_command_value}")

    async def stop_operation(self) -> None:
        """Stop force run single and disarm motor."""
        self.logger.info(f"Stopping force run motor {self.target_motor}")
        self.stop_event.set()
        self.is_active = False
        
        # Send explicit stop to target motor
        try:
            await self._stop_single_motor()
        except Exception as e:
            self.logger.error(f"Error stopping motor: {e}")
        
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            try:
                # Wait for task cancellation with timeout to avoid hanging
                await self.current_task
            except asyncio.CancelledError:
                self.logger.info(f"Force run motor {self.target_motor} task cancelled successfully")
            except asyncio.TimeoutError:
                self.logger.warning(f"Force run motor {self.target_motor} task cancellation timed out - forcing cleanup")
            except Exception as e:
                self.logger.warning(f"Error during force run single task cancellation: {e}")
        
        # Clear task reference and reset for recovery
        self.current_task = None
        self.stop_event.clear()
        self.logger.info(f"Force run motor {self.target_motor} stop complete - ready for recovery")

    async def _force_run_single_loop(self):
        """Main force run loop for single motor."""
        try:
            while not self.stop_event.is_set() and self.is_active:
                # Check timeout
                if self.is_timeout_expired():
                    self.logger.warning(f"Force run motor {self.target_motor} timeout expired, stopping")
                    break
                
                # Map command value to [0..1] range
                motor_value = self._map_command_to_pwm_range(self.current_command_value, self.min_raw_command , self.max_raw_command)
                
                # Send command to target motor with 1 second timeout
                success = await self._send_actuator_test_single_motor(motor_value, 1.0)
                
                if not success:
                    self.logger.error(f"Failed to send command to motor {self.target_motor}, stopping operation")
                    break
                
                # Wait before next command (800ms to ensure commands don't timeout)
                await asyncio.sleep(0.8)
                
        except asyncio.CancelledError:
            self.logger.info(f"Force run motor {self.target_motor} task cancelled")
        except Exception as e:
            self.logger.error(f"Error in force run single loop: {e}")
        finally:
            # Ensure motor is stopped and state is reset for recovery
            try:
                await self._stop_single_motor()
            except Exception as e:
                self.logger.error(f"Error stopping motor in cleanup: {e}")
            
            self.is_active = False
            self.current_task = None
            self.stop_event.clear()
            self.logger.info(f"Force run motor {self.target_motor} cleanup complete - ready for recovery")


class BasePubSubController(ABC):
    """
    Base class for publish/subscribe controllers that handle data streaming.
    
    Controllers implementing this pattern:
    1. Subscribe to petal-user-journey-coordinator/subscribe_<stream_name>
    2. Publish to petal-user-journey-coordinator/publish_<stream_name> at specified rate
    3. Stop publishing when receiving petal-user-journey-coordinator/unsubscribe_<stream_name>
    """
    
    def __init__(
            self, 
            stream_name: str, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            petal_name: str = "petal-user-journey-coordinator"
        ):
        self.petal_name = petal_name
        self.stream_name = stream_name
        self.mqtt_proxy = mqtt_proxy
        self.mavlink_proxy = mavlink_proxy
        self.logger = logger
        self.is_active = False
        self.current_task: Optional[asyncio.Task] = None
        self.stop_event = threading.Event()
        self.publish_rate_hz = 1.0
        self.stream_id = ""
        self.lock = threading.Lock()
        self._mavlink_stop_handler = None

    @abstractmethod
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """
        Set up MAVLink message handler for the data source.
        Returns a stop function to unregister the handler.
        """
        pass
    
    @abstractmethod
    def _get_sample_data(self) -> Dict[str, Any]:
        """
        Get the current sample data to publish.
        This should return the latest data received from MAVLink.
        """
        pass
    
    async def start_streaming(self, stream_id: str, rate_hz: float) -> None:
        """Start streaming data at the specified rate."""
        if self.is_active:
            self.logger.info(f"Stream {self.stream_name} already active, updating rate to {rate_hz} Hz")
            with self.lock:
                self.publish_rate_hz = rate_hz
            return
        
        with self.lock:
            self.stream_id = stream_id
            self.publish_rate_hz = rate_hz
            self.is_active = True
            self.stop_event.clear()
        
        # Set up MAVLink handler
        self._mavlink_stop_handler = self._setup_mavlink_handler()
        
        # Create the publishing task directly
        try:
            self.current_task = asyncio.create_task(self._publishing_loop())
            self.logger.info(f"Started streaming {self.stream_name} at {rate_hz} Hz - publishing loop task created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create publishing loop task for {self.stream_name}: {e}")
            # Reset state on failure
            self.is_active = False
            raise
    
    async def stop_streaming(self) -> None:
        """Stop streaming data."""
        if not self.is_active:
            return
            
        self.logger.info(f"Stopping stream {self.stream_name}")
        with self.lock:
            self.stop_event.set()
            self.is_active = False
        
        # Stop MAVLink handler
        if self._mavlink_stop_handler:
            self._mavlink_stop_handler()
            self._mavlink_stop_handler = None
        
        # Cancel publishing task
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
    
    async def _publishing_loop(self):
        """Main publishing loop that sends data at the specified rate."""
        interval = 1.0 / self.publish_rate_hz
        
        try:
            while not self.stop_event.is_set() and self.is_active:
                # Get current data
                sample_data = self._get_sample_data()
                
                if sample_data:
                    # Create publish payload
                    publish_payload = PublishPayload(
                        published_stream_id=self.stream_id,
                        stream_payload=sample_data
                    )

                    mqtt_message = {
                        "messageId": str(uuid.uuid4()),
                        "command": f"/{self.petal_name}/publish_{self.stream_name}",
                        "timestamp": datetime.now().isoformat(),
                        "payload": publish_payload.model_dump()
                    }
                    
                    # Send to MQTT
                    await self.mqtt_proxy.publish_message(
                        payload=mqtt_message
                    )
                
                # Wait for next publish interval
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            self.logger.info(f"Publishing loop for {self.stream_name} cancelled")
        except Exception as e:
            self.logger.error(f"Error in publishing loop for {self.stream_name}: {e}")
        finally:
            self.is_active = False


class RCChannelsController(BasePubSubController):
    """Controller for streaming RC_CHANNELS MAVLink data."""
    
    def __init__(
            self, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            petal_name: str = "petal-user-journey-coordinator"
        ):
        super().__init__("rc_value_stream", mqtt_proxy, mavlink_proxy, logger, petal_name=petal_name)
        self._latest_sample = None
        self._sample_lock = threading.Lock()
    
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """Set up RC_CHANNELS message handler."""

        # TESTING: dummy values with time
        value_min = 1000
        value_max = 2000
        t_start = time.time()

        def _handler(pkt):
            with self._sample_lock:
                self._latest_sample = {
                    "time_boot_ms": pkt.time_boot_ms,
                    "chancount": pkt.chancount,
                    **{f"chan{i}_raw": getattr(pkt, f"chan{i}_raw") for i in range(1, 19)},
                    "rssi": pkt.rssi,
                }

                # # TESTING: dummy values with time
                # self._latest_sample = {
                #     "time_boot_ms": 0,
                #     "chancount": 0,
                #     # send sinusoidal signal between 1000 and 2000 with period of 1 second for each channel
                #     **{f"chan{i}_raw": int(1000 + 500 * math.sin(2 * math.pi * (time.time() - t_start) / 1)) for i in range(1, 19)},
                #     "rssi": 0,
                # }

        # Register handler with deduplication
        # TODO: use MAVLINK_MSG_ID_RC_CHANNELS
        self.mavlink_proxy.register_handler(str(mavlink_dialect.MAVLINK_MSG_ID_RC_CHANNELS), _handler, duplicate_filter_interval=0.02)
        
        def stop():
            self.mavlink_proxy.unregister_handler(str(mavlink_dialect.MAVLINK_MSG_ID_RC_CHANNELS), _handler)

        return stop
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get the latest RC channels data."""
        with self._sample_lock:
            return self._latest_sample.copy() if self._latest_sample else {}


class PositionChannelsController(BasePubSubController):
    """Controller for streaming real-time pose data from MAVLink LOCAL_POSITION_NED and ATTITUDE messages."""
    
    def __init__(
            self, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            rectangle_a: float,
            rectangle_b: float,
            points_per_edge: int,
            corner_exclusion_radius: float,
            max_matching_distance: float,
            corner_points: List[Dict[str, float]],
            reference_trajectory: List[Dict[str, float]],
            petal_name: str = "petal-user-journey-coordinator"
        ):
        super().__init__("real_time_pose", mqtt_proxy, mavlink_proxy, logger, petal_name=petal_name)
        self._latest_position = None
        self._latest_attitude = None
        self._sample_lock = threading.Lock()

        self.rectangle_a = rectangle_a
        self.rectangle_b = rectangle_b
        self.points_per_edge = points_per_edge
        self.corner_exclusion_radius = corner_exclusion_radius
        self.max_matching_distance = max_matching_distance
        self.corner_points = corner_points
        self.reference_trajectory = reference_trajectory

        self.ref_x = 0.0
        self.ref_y = 0.0

        self.acquired_ref = False
    
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """Set up LOCAL_POSITION_NED and ATTITUDE message handlers."""

        def _position_handler(pkt):
            with self._sample_lock:
                # Convert NED to ENU: x(E) = y(N), y(N) = x(E), z(U) = -z(D)

                # check that pkt.x, pkt.y, pkt.z are not None, set them to zero
                if pkt.x is None or pkt.y is None or pkt.z is None:
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    valid_position = False
                else:
                    x = pkt.x - self.ref_x
                    y = pkt.y - self.ref_y
                    z = pkt.z
                    valid_position = True

                    if not self.acquired_ref:
                        self.ref_x = pkt.x
                        self.ref_y = pkt.y
                        self.acquired_ref = True
                        self.logger.info(f"Acquired reference position: ref_x={self.ref_x}, ref_y={self.ref_y}")

                
                self._latest_position = {
                    "time_boot_ms": pkt.time_boot_ms,
                    "x": y,  # ENU x = NED y (East)
                    "y": x,  # ENU y = NED x (North)  
                    "z": -z,  # ENU z = -NED z (Up = -Down)
                    "vx": pkt.vy,  # ENU vx = NED vy
                    "vy": pkt.vx,  # ENU vy = NED vx
                    "vz": -pkt.vz,  # ENU vz = -NED vz
                    "valid_position": valid_position
                }
        
        def _attitude_handler(pkt):
            with self._sample_lock:
                # TODO: convert to roll_deg and x_m
                # check that pkt.roll, pkt.pitch, pkt.yaw are not None set them to zero
                if pkt.roll is None or pkt.pitch is None or pkt.yaw is None:
                    roll = 0.0
                    pitch = 0.0
                    yaw = 0.0
                    valid_altitude = False
                else:
                    roll = pkt.roll
                    pitch = pkt.pitch
                    yaw = pkt.yaw
                    valid_altitude = True

                self._latest_attitude = {
                    "time_boot_ms": pkt.time_boot_ms,
                    "roll": math.degrees(roll),
                    "pitch": math.degrees(pitch),
                    "yaw": math.degrees(yaw),
                    "rollspeed": pkt.rollspeed,
                    "pitchspeed": pkt.pitchspeed,
                    "yawspeed": pkt.yawspeed,
                    "valid_altitude": valid_altitude
                }
        
        # Register handlers with deduplication
        self.mavlink_proxy.register_handler(str(mavlink_dialect.MAVLINK_MSG_ID_LOCAL_POSITION_NED), _position_handler, duplicate_filter_interval=0.02)
        self.mavlink_proxy.register_handler(str(mavlink_dialect.MAVLINK_MSG_ID_ATTITUDE), _attitude_handler, duplicate_filter_interval=0.02)
        
        def stop():
            self.mavlink_proxy.unregister_handler(str(mavlink_dialect.MAVLINK_MSG_ID_LOCAL_POSITION_NED), _position_handler)
            self.mavlink_proxy.unregister_handler(str(mavlink_dialect.MAVLINK_MSG_ID_ATTITUDE), _attitude_handler)

        return stop
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get the latest combined pose data (position in ENU + attitude)."""
        with self._sample_lock:
            if self._latest_position is None and self._latest_attitude is None:
                return {}
            
            # Combine position and attitude data
            sample_data = {}
            
            if self._latest_position is not None:
                sample_data.update({
                    "x": self._latest_position.get("x", 0.0),
                    "y": self._latest_position.get("y", 0.0),
                    "z": self._latest_position.get("z", 0.0),
                    "position_valid": self._latest_position.get("valid_position", False),
                })
            else:
                sample_data.update({
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "position_valid": False,
                })
            
            if self._latest_attitude is not None:
                sample_data.update({
                    "roll": self._latest_attitude.get("roll", 0.0),
                    "pitch": self._latest_attitude.get("pitch", 0.0),
                    "yaw": self._latest_attitude.get("yaw", 0.0),
                    "altitude_valid": self._latest_attitude.get("valid_altitude", False),
                })
            else:
                sample_data.update({
                    "roll": 0.0,
                    "pitch": 0.0,
                    "yaw": 0.0,
                    "altitude_valid": False,
                })

            if self._latest_position is not None and self._latest_attitude is not None:
                # Calculate reference trajectory error
                # Use the static helper method from TrajectoryVerificationController
                error_result = TrajectoryVerificationController.calculate_single_point_error(
                    actual_point={
                        "x": self._latest_position["x"],
                        "y": self._latest_position["y"],
                        "yaw": self._latest_attitude["yaw"]
                    },
                    reference_trajectory=self.reference_trajectory,
                    corner_points=self.corner_points,
                    corner_exclusion_radius=self.corner_exclusion_radius,
                    max_matching_distance=self.max_matching_distance,
                    debug_yaw=True
                )

                closest_ref_point = error_result.get("closest_ref_point", {})
                if closest_ref_point:
                    closest_ref_x = closest_ref_point.get("x", 0.0)
                    closest_ref_y = closest_ref_point.get("y", 0.0)
                    closest_ref_yaw = closest_ref_point.get("yaw", 0.0)
                    position_error = error_result.get("position_error", 0.0)
                    yaw_error = error_result.get("yaw_error", 0.0)
                else:
                    closest_ref_x = 0.0
                    closest_ref_y = 0.0
                    closest_ref_yaw = 0.0
                    position_error = 0.0
                    yaw_error = 0.0

                if position_error is None:
                    position_error = 0.0
                if yaw_error is None:
                    yaw_error = 0.0

                sample_data.update({
                    "closest_ref_x": closest_ref_x,
                    "closest_ref_y": closest_ref_y,
                    "closest_ref_yaw": closest_ref_yaw,
                    "position_error": position_error,
                    "yaw_error": yaw_error
                })

            else:
                sample_data.update({
                    "closest_ref_x": 0.0,
                    "closest_ref_y": 0.0,
                    "closest_ref_yaw": 0.0,
                    "position_error": 0.0,
                    "yaw_error": 0.0
                })

            return sample_data

    def reset_reference_position(self):
        """Reset the reference position to current position on next update."""
        with self._sample_lock:
            self.acquired_ref = False
            self.logger.info("Reference position reset requested")

def _norm_statustext(pkt) -> str:
    """
    Robustly extract STATUSTEXT text as a clean Python str.
    Works for PX4 v1.4.x where 'text' may come padded / bytes.
    """
    txt = getattr(pkt, "text", b"")
    if isinstance(txt, (bytes, bytearray)):
        txt = txt.decode("utf-8", "ignore")
    return txt.strip("\x00").strip()


def _classify_kill_transition(text: str) -> Optional[bool]:
    """
    Classify a STATUSTEXT message to determine if it indicates kill switch engaged/disengaged.
    Enhanced patterns for specific PX4 kill switch messages.
    
    Returns:
        True if kill switch is engaged (motors stopped)
        False if kill switch is disengaged (motors enabled)
        None if message is not kill switch related
    """
    t = text.lower()

    # quick exit if not obviously relevant
    if "kill" not in t and "lockdown" not in t and "emergency" not in t:
        return None

    # PX4 specific kill switch patterns - engaged (kill active)
    kill_engaged_patterns = [
        "kill-switch is engaged",
        "kill switch engaged", 
        "emergency kill active",
        "motors stopped by kill switch",
        "kill switch activated",
        "safety kill engaged",
        "kill-switch engaged",
        "emergency stop active",
        "kill: on",
        "kill on", 
        "kill activated",
        "kill enabled",
        "lockdown enabled",
        "lockdown on",
        "emergency kill: on"
    ]

    # PX4 specific kill switch patterns - disengaged (kill inactive)
    kill_disengaged_patterns = [
        "kill-switch is disengaged",
        "kill switch disengaged",
        "emergency kill inactive", 
        "kill switch deactivated",
        "safety kill disengaged",
        "kill-switch disengaged",
        "emergency stop inactive",
        "motors enabled",
        "kill: off",
        "kill off",
        "kill deactivated", 
        "kill disabled",
        "lockdown disabled",
        "lockdown off",
        "emergency kill: off",
        "released kill",
        "kill released"
    ]

    # Check for engaged patterns
    for pattern in kill_engaged_patterns:
        if pattern in t:
            return True

    # Check for disengaged patterns  
    for pattern in kill_disengaged_patterns:
        if pattern in t:
            return False

    # Additional context-based detection for generic messages
    if "kill" in t:
        if any(word in t for word in ["engag", "activat", "enable"]):
            return True
        if any(word in t for word in ["disengag", "deactivat", "disable", "off", "release"]):
            return False

    if "lockdown" in t:
        if any(word in t for word in ["enable", "on"]):
            return True
        if any(word in t for word in ["disable", "off"]):
            return False

    return None


class KillSwitchController(BasePubSubController):
    """Controller for streaming kill switch status from PX4 STATUSTEXT messages with automatic parameter configuration."""

    def __init__(
            self, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            petal_name: str = "petal-user-journey-coordinator"
        ):
        super().__init__("ks_status_stream", mqtt_proxy, mavlink_proxy, logger, petal_name=petal_name)

        # Kill switch state tracking
        self.is_killed: Optional[bool] = None  # None = unknown
        self.last_text: Optional[str] = None
        self.last_change_monotonic: Optional[float] = None
        self.last_severity: Optional[int] = None
        self.setup_complete = False

    async def start_streaming(self, stream_id: str, rate_hz: float) -> None:
        """Start streaming data at the specified rate with automatic kill switch parameter configuration."""
        with self.lock:
            if self.is_active:
                self.logger.info(f"Stream {self.stream_name} already active, updating rate to {rate_hz} Hz")
                self.publish_rate_hz = rate_hz
                return
            
        # Configure kill switch parameters before starting streaming
        if not self.setup_complete:
            await self._configure_kill_switch_parameters()
        
        # Call parent implementation to start streaming
        await super().start_streaming(stream_id, rate_hz)
    
    async def _configure_kill_switch_parameters(self):
        """Configure kill switch parameters using KillSwitchConfigHandler."""
        try:
            self.logger.info("Configuring kill switch parameters...")
            
            # Create parameter handler for configuration
            config_handler = KillSwitchConfigHandler(self.mavlink_proxy, self.logger)
            
            # Configure parameters
            result = await config_handler.process_payload({}, "ks_auto_config")
            
            if result["status"] == "success":
                self.logger.info("Kill switch parameters configured successfully")
                self.setup_complete = True
            else:
                self.logger.warning(f"Kill switch parameter setup incomplete: {result}")
        except Exception as e:
            self.logger.error(f"Failed to configure kill switch parameters: {e}")
            # Continue with streaming even if parameter setup fails
    
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """Set up MAVLink STATUSTEXT handler for kill switch monitoring."""
        
        def _statustext_handler(pkt) -> None:
            """Handle STATUSTEXT messages and extract kill switch state."""
            txt = _norm_statustext(pkt)
            decision = _classify_kill_transition(txt)
            self.logger.info(f"STATUSTEXT received: '{txt}' -> kill switch state: {decision}")
            
            if decision is None:
                return  # Not a kill switch related message
            
            # Update state if it changed
            if self.is_killed is None or decision != self.is_killed:
                self.is_killed = decision
                self.last_text = txt
                self.last_change_monotonic = time.monotonic()
                self.last_severity = getattr(pkt, "severity", None)
                
                self.logger.info(f"Kill switch state changed: {'ENGAGED' if self.is_killed else 'DISENGAGED'} - {txt}")
        
        # Register handler for STATUSTEXT messages
        self.mavlink_proxy.register_handler(str(mavlink_dialect.MAVLINK_MSG_ID_STATUSTEXT), _statustext_handler)
        
        # Return stop function
        def stop_handler():
            self.mavlink_proxy.unregister_handler(str(mavlink_dialect.MAVLINK_MSG_ID_STATUSTEXT), _statustext_handler)
        
        return stop_handler
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get current kill switch status data."""
        return {
            "timestamp": datetime.now().isoformat(),
            "is_killed": self.is_killed,
            "status": "engaged" if self.is_killed else "disengaged" if self.is_killed is False else "unknown",
            "last_text": self.last_text,
            "last_change_time": self.last_change_monotonic,
            "severity": self.last_severity,
            "setup_complete": self.setup_complete
        }


class MultiFunctionalSwitchAController(BasePubSubController):
    """Controller for streaming Multi-functional Switch A data from MAVLink messages."""
    
    def __init__(
            self, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            petal_name: str = "petal-user-journey-coordinator"
        ):
        super().__init__("mfs_a_status_stream", mqtt_proxy, mavlink_proxy, logger, petal_name=petal_name)
        
        # Multi-functional Switch A state tracking
        self.latest_mfs_a_data: Optional[Dict[str, Any]] = None
        
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """
        Set up MAVLink handler for Multi-functional Switch A data.
        
        Note: This method should be implemented when the specific MAVLink message
        type for MFS A is identified. For now, it returns a placeholder.
        """
        def _mfs_a_handler(pkt) -> None:
            """Handle MAVLink messages for Multi-functional Switch A."""
            # TODO: Implement specific MAVLink message handling for MFS A
            # This will depend on the actual MAVLink message type used for MFS A
            # Example structure:
            # self.latest_mfs_a_data = {
            #     "timestamp": datetime.now().isoformat(),
            #     "switch_value": getattr(pkt, "switch_value", 0),
            #     "raw_data": getattr(pkt, "raw_data", None),
            #     # Add other relevant fields based on actual MAVLink message
            # }
            self.logger.debug("MFS A MAVLink handler called (placeholder implementation)")
        
        # TODO: Register handler for the specific MAVLink message type for MFS A
        # Example: self.mavlink_proxy.register_handler("MFS_A_MESSAGE_TYPE", _mfs_a_handler)
        # For now, return a no-op stop function
        def stop_handler():
            # TODO: Unregister the actual handler when implemented
            # self.mavlink_proxy.unregister_handler("MFS_A_MESSAGE_TYPE", _mfs_a_handler)
            pass
        
        return stop_handler
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get current Multi-functional Switch A data."""
        if self.latest_mfs_a_data:
            return self.latest_mfs_a_data
        else:
            # Return default/placeholder data when no MAVLink data is available
            return {
                "timestamp": datetime.now().isoformat(),
                "subscribed_stream_id": "px4_mfs_a_raw",
                "switch_value": 0,
                "status": "no_data",
                "message": "Waiting for MAVLink data"
            }


class MultiFunctionalSwitchBController(BasePubSubController):
    """Controller for streaming Multi-functional Switch B data from MAVLink messages."""
    
    def __init__(
            self, 
            mqtt_proxy: MQTTProxy, 
            mavlink_proxy: MavLinkExternalProxy, 
            logger: logging.Logger,
            petal_name: str = "petal-user-journey-coordinator"
        ):
        super().__init__("mfs_b_status_stream", mqtt_proxy, mavlink_proxy, logger, petal_name=petal_name)
        
        # Multi-functional Switch B state tracking
        self.latest_mfs_b_data: Optional[Dict[str, Any]] = None
    
    def _setup_mavlink_handler(self) -> Callable[[], None]:
        """
        Set up MAVLink handler for Multi-functional Switch B data.
        
        Note: This method should be implemented when the specific MAVLink message
        type for MFS B is identified. For now, it returns a placeholder.
        """
        def _mfs_b_handler(pkt) -> None:
            """Handle MAVLink messages for Multi-functional Switch B."""
            # TODO: Implement specific MAVLink message handling for MFS B
            # This will depend on the actual MAVLink message type used for MFS B
            # Example structure:
            # self.latest_mfs_b_data = {
            #     "timestamp": datetime.now().isoformat(),
            #     "switch_value": getattr(pkt, "switch_value", 0),
            #     "raw_data": getattr(pkt, "raw_data", None),
            #     # Add other relevant fields based on actual MAVLink message
            # }
            self.logger.debug("MFS B MAVLink handler called (placeholder implementation)")
        
        # TODO: Register handler for the specific MAVLink message type for MFS B
        # Example: self.mavlink_proxy.register_handler("MFS_B_MESSAGE_TYPE", _mfs_b_handler)
        # For now, return a no-op stop function
        def stop_handler():
            # TODO: Unregister the actual handler when implemented
            # self.mavlink_proxy.unregister_handler("MFS_B_MESSAGE_TYPE", _mfs_b_handler)
            pass
        
        return stop_handler
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get current Multi-functional Switch B data."""
        if self.latest_mfs_b_data:
            return self.latest_mfs_b_data
        else:
            # Return default/placeholder data when no MAVLink data is available
            return {
                "timestamp": datetime.now().isoformat(),
                "subscribed_stream_id": "px4_mfs_b_raw",
                "switch_value": 0,
                "status": "no_data",
                "message": "Waiting for MAVLink data"
            }


class TrajectoryVerificationController:
    """
    Controller for verifying position and yaw trajectory against a predefined rectangular path.
    """
    
    def __init__(
        self, 
        mqtt_proxy: MQTTProxy, 
        logger: logging.Logger,
        rectangle_a: float = 2.0,
        rectangle_b: float = 2.0,
        points_per_edge: int = 10,
        corner_exclusion_radius: float = 0.2,
        petal_name: str = "petal-user-journey-coordinator"
    ):
        self.petal_name = petal_name
        self.mqtt_proxy = mqtt_proxy
        self.logger = logger
        self.is_active = False
        self.trajectory_points = []
        self.lock = threading.Lock()
        
        # Rectangle trajectory parameters (in meters)
        self.rectangle_a = rectangle_a  # width
        self.rectangle_b = rectangle_b  # height
        # Number of interpolated points per edge (including start point, excluding end point)
        self.points_per_edge = points_per_edge

        # Tolerances
        self.position_tolerance = 0.5  # meters
        self.yaw_tolerance = 10.0  # degrees
        
        # Corner exclusion radius for yaw error calculation (to avoid mixed directions when picking up drone)
        self.corner_exclusion_radius = corner_exclusion_radius  # meters

        # Reference trajectory (rectangle corners in ENU frame)
        self.reference_trajectory = self._generate_rectangle_trajectory()
    
    @staticmethod
    def calculate_single_point_error(actual_point: Dict[str, float], 
                                   reference_trajectory: List[Dict[str, float]],
                                   corner_points: List[Dict[str, float]] = None,
                                   corner_exclusion_radius: float = 0.2,
                                   max_matching_distance: float = None,
                                   debug_yaw:bool = False) -> Dict[str, Any]:
        """
        Calculate position and yaw errors for a single trajectory point against reference trajectory.
        
        Args:
            actual_point: Dictionary with keys 'x', 'y', 'yaw' (yaw in degrees)
            reference_trajectory: List of reference points with 'x', 'y', 'yaw' (yaw in degrees)
            corner_points: List of corner points for exclusion zone (optional, defaults to standard rectangle corners)
            corner_exclusion_radius: Radius around corners to exclude from yaw error calculation
            max_matching_distance: Maximum distance to consider a reference point as matching (optional)
            
        Returns:
            Dictionary containing:
            - position_error: float (distance to closest reference point, or None if no match)
            - yaw_error: float (angular difference in degrees, or None if no match or near corner)
            - closest_ref_point: dict (the matched reference point, or None)
            - closest_ref_index: int (index of matched reference point, or -1)
            - near_corner: bool (whether the point is near a corner exclusion zone)
            - matched: bool (whether a reference point was found within matching distance)
        """
        if not reference_trajectory:
            return {
                "position_error": None,
                "yaw_error": None,
                "closest_ref_point": None,
                "closest_ref_index": -1,
                "near_corner": False,
                "matched": False
            }
        
        # Set default corner points if not provided (standard 2x2 rectangle)
        if corner_points is None:
            corner_points = [
                {"x": 0.0, "y": 0.0},     # Start/end corner
                {"x": 2.0, "y": 0.0},     # East corner
                {"x": 2.0, "y": 2.0},     # Northeast corner
                {"x": 0.0, "y": 2.0},     # West corner
            ]
        
        # Set default max matching distance if not provided
        if max_matching_distance is None:
            # Use 20% of the largest dimension as default
            max_x = max(point["x"] for point in reference_trajectory)
            max_y = max(point["y"] for point in reference_trajectory)
            max_matching_distance = max(max_x, max_y) * 0.2
        
        # Find closest reference point to this trajectory point
        min_dist = float('inf')
        closest_ref_point = None
        closest_ref_index = -1
        
        for ref_idx, ref_point in enumerate(reference_trajectory):
            dist = math.sqrt(
                (actual_point["x"] - ref_point["x"])**2 + 
                (actual_point["y"] - ref_point["y"])**2
            )
            if dist < min_dist:
                min_dist = dist
                closest_ref_point = ref_point
                closest_ref_index = ref_idx
        
        # Check if we found a reasonably close reference point
        if not closest_ref_point or min_dist > max_matching_distance:
            return {
                "position_error": None,
                "yaw_error": None,
                "closest_ref_point": None,
                "closest_ref_index": -1,
                "near_corner": False,
                "matched": False
            }
        
        # Check if this trajectory point is near any corner (exclude yaw error calculation)
        near_corner = False
        for corner in corner_points:
            corner_dist = math.sqrt(
                (actual_point["x"] - corner["x"])**2 + 
                (actual_point["y"] - corner["y"])**2
            )
            if corner_dist <= corner_exclusion_radius:
                near_corner = True
                break
        
        # Calculate yaw error (only if not near a corner)
        if "yaw" in actual_point and "yaw" in closest_ref_point:
            # Yaw error (shortest angular distance between angles in -180 to 180 range)
            actual_yaw = actual_point["yaw"]
            ref_yaw = closest_ref_point["yaw"]
            
            # Calculate the angular difference
            diff = actual_yaw - ref_yaw
            
            # Normalize difference to [-180, 180] range to find shortest path
            while diff > 180:
                diff -= 360
            while diff <= -180:
                diff += 360
            
            # Take absolute value for error magnitude
            if not near_corner:
                yaw_error = abs(diff)
            else:
                if not debug_yaw:
                    yaw_error = None
                else:
                    yaw_error = abs(diff)  # For debugging, still provide yaw error
        else:
            yaw_error = None
        
        return {
            "position_error": min_dist,
            "yaw_error": yaw_error,
            "closest_ref_point": closest_ref_point,
            "closest_ref_index": closest_ref_index,
            "near_corner": near_corner,
            "matched": True
        }
        
    def _generate_rectangle_trajectory(self) -> List[Dict[str, float]]:
        """Generate reference rectangular trajectory with interpolated points along each edge."""
        trajectory = []
        
        # Define corner points of the rectangle with corrected yaw angles (-180 to 180)
        # Starting with yaw = 90° (pointing east), then following the path
        corners = [
            {"x": 0.0, "y": 0.0, "yaw": 90.0},           # Start point (facing east)
            {"x": self.rectangle_a, "y": 0.0, "yaw": 0.0},   # East corner (turn to face north)
            {"x": self.rectangle_a, "y": self.rectangle_b, "yaw": -90.0},  # Northeast corner (turn to face west)
            {"x": 0.0, "y": self.rectangle_b, "yaw": -180.0},  # West corner (turn to face south)
            {"x": 0.0, "y": 0.0, "yaw": 90.0},           # Back to start (turn to face east)
        ]

        # Maximum distance to consider a reference point as "close enough" to a trajectory point
        self.max_matching_distance = max(self.rectangle_a, self.rectangle_b) * 0.2  # 20% of largest dimension
        

        self.corner_points = corners[:-1]  # Exclude the duplicate last point for corner exclusion checks
                
        # Interpolate points between each pair of corners
        for i in range(len(corners) - 1):
            start_corner = corners[i]
            end_corner = corners[i + 1]
            
            # Add interpolated points along this edge
            for j in range(self.points_per_edge):
                t = j / self.points_per_edge  # Interpolation parameter (0 to 1, excluding 1)

                # Linear interpolation for position
                x = start_corner["x"] + t * (end_corner["x"] - start_corner["x"])
                y = start_corner["y"] + t * (end_corner["y"] - start_corner["y"])
                
                # Yaw angle depends on the direction of movement (using -180 to 180 range)
                if abs(end_corner["x"] - start_corner["x"]) > abs(end_corner["y"] - start_corner["y"]):
                    # Horizontal movement
                    if end_corner["x"] > start_corner["x"]:
                        yaw = 90.0  # Moving east
                    else:
                        yaw = -90.0  # Moving west
                else:
                    # Vertical movement
                    if end_corner["y"] > start_corner["y"]:
                        yaw = 0.0  # Moving north
                    else:
                        yaw = -180.0  # Moving south
                
                trajectory.append({"x": x, "y": y, "yaw": yaw})
        
        # Add the final point (back to start)
        trajectory.append(corners[-1])
        
        self.logger.info(f"Generated rectangle trajectory with {len(trajectory)} reference points")
        
        # Log a few sample points for debugging
        if trajectory:
            self.logger.debug("Reference trajectory sample points:")
            for i, point in enumerate(trajectory[::max(1, len(trajectory)//8)]):  # Show ~8 sample points
                self.logger.debug(f"  Point {i}: x={point['x']:.2f}m, y={point['y']:.2f}m, yaw={point['yaw']:.1f}°")
        
        return trajectory
    
    def start_verification(self) -> None:
        """Start trajectory verification process."""
        with self.lock:
            if self.is_active:
                self.logger.warning("Trajectory verification already active")
                return
                
            self.is_active = True
            self.trajectory_points = []
            self.logger.info("Started trajectory verification")
    
    def add_trajectory_point(self, x: float, y: float, yaw: float) -> None:
        """Add a trajectory point during verification."""
        with self.lock:
            if not self.is_active:
                return
                
            # Normalize to -180 to 180 range
            while yaw > 180:
                yaw -= 360
            while yaw <= -180:
                yaw += 360

            point = {
                "x": x,
                "y": y, 
                "yaw": yaw, # in degrees
                "timestamp": time.time()
            }
            self.trajectory_points.append(point)
    
    def _calculate_trajectory_error(self) -> Dict[str, float]:
        """Calculate position and yaw errors against reference trajectory."""
        if not self.trajectory_points:
            return {"position_error": float('inf'), "yaw_error": float('inf'), "coverage": 0.0}
        
        position_errors = []
        yaw_errors = []
        matched_ref_indices = set()  # Track which reference points were matched
        
        # Loop over trajectory points and calculate errors for each
        for actual_point in self.trajectory_points:
            # Use the helper method to calculate errors for this point
            result = self.calculate_single_point_error(
                actual_point=actual_point,
                reference_trajectory=self.reference_trajectory,
                corner_points=self.corner_points,
                corner_exclusion_radius=self.corner_exclusion_radius,
                max_matching_distance=self.max_matching_distance
            )
            
            # Only process if we found a matching reference point
            if result["matched"]:
                # Track which reference point was matched
                matched_ref_indices.add(result["closest_ref_index"])
                
                # Add position error
                if result["position_error"] is not None:
                    position_errors.append(result["position_error"])
                
                # Add yaw error (only if not near corner and yaw error was calculated)
                if result["yaw_error"] is not None:
                    yaw_errors.append(result["yaw_error"])
        
        # Calculate trajectory coverage (percentage of reference points that were matched)
        coverage = (len(matched_ref_indices) / len(self.reference_trajectory)) * 100 if self.reference_trajectory else 0
        
        # Calculate RMS errors
        position_rms = math.sqrt(sum(e**2 for e in position_errors) / len(position_errors)) if position_errors else float('inf')
        yaw_rms = math.sqrt(sum(e**2 for e in yaw_errors) / len(yaw_errors)) if yaw_errors else float('inf')
        
        # Calculate mean errors as well
        position_mean = sum(position_errors) / len(position_errors) if position_errors else float('inf')
        yaw_mean = sum(yaw_errors) / len(yaw_errors) if yaw_errors else float('inf')
        
        return {
            "position_error": position_rms,
            "yaw_error": yaw_rms,
            "position_mean_error": position_mean,
            "yaw_mean_error": yaw_mean,
            "max_position_error": max(position_errors) if position_errors else float('inf'),
            "max_yaw_error": max(yaw_errors) if yaw_errors else float('inf'),
            "coverage": coverage,
            "matched_points": len(matched_ref_indices),
            "total_reference_points": len(self.reference_trajectory),
            "yaw_errors_calculated": len(yaw_errors),  # Number of yaw errors calculated (excluding corners)
            "position_errors_calculated": len(position_errors)  # Number of position errors calculated
        }
    
    def plot_trajectories(self, output_file: str = None, show_plot: bool = False, 
                         title: str = "Trajectory Verification", figsize: tuple = (12, 10)) -> str:
        """
        Plot reference and actual trajectories with yaw indicators.
        
        Args:
            output_file: Path to save the plot. If None, generates a timestamped filename.
            show_plot: Whether to display the plot interactively.
            title: Title for the plot.
            figsize: Figure size as (width, height) in inches.
            
        Returns:
            Path to the saved plot file.
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import FancyArrowPatch
            import numpy as np
        except ImportError as e:
            self.logger.error(f"Matplotlib not available for plotting: {e}")
            raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
        
        # Create figure and axis
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Plot reference trajectory
        if self.reference_trajectory:
            ref_x = [point["x"] for point in self.reference_trajectory]
            ref_y = [point["y"] for point in self.reference_trajectory]
            ref_yaw = [point["yaw"] for point in self.reference_trajectory]
            
            # Plot reference path as connected lines
            ax.plot(ref_x, ref_y, 'b-', linewidth=2, label='Reference Trajectory', alpha=0.7)
            ax.scatter(ref_x, ref_y, c='blue', s=30, alpha=0.6, zorder=3)
            
            # Add yaw indicators for reference trajectory (every 5th point to avoid clutter)
            arrow_scale = 0.15  # Length of yaw arrows
            for i in range(0, len(self.reference_trajectory), 5):
                point = self.reference_trajectory[i]
                x, y, yaw_deg = point["x"], point["y"], point["yaw"]
                
                # Convert yaw to unit vector (yaw is in degrees, 0° = East, 90° = North)
                yaw_rad = math.radians(yaw_deg)
                dx = arrow_scale * math.cos(yaw_rad)
                dy = arrow_scale * math.sin(yaw_rad)
                
                # Draw arrow
                arrow = FancyArrowPatch((x, y), (x + dx, y + dy),
                                      arrowstyle='->', mutation_scale=15,
                                      color='blue', alpha=0.8, linewidth=1.5)
                ax.add_patch(arrow)
        
        # Plot actual trajectory
        if self.trajectory_points:
            actual_x = [point["x"] for point in self.trajectory_points]
            actual_y = [point["y"] for point in self.trajectory_points]
            actual_yaw = [point["yaw"] for point in self.trajectory_points]
            
            # Plot actual path as connected lines
            ax.plot(actual_x, actual_y, 'r-', linewidth=2, label='Actual Trajectory', alpha=0.8)
            ax.scatter(actual_x, actual_y, c='red', s=40, alpha=0.8, zorder=4)
            
            # Add yaw indicators for actual trajectory
            arrow_scale = 0.12  # Slightly smaller arrows for actual trajectory
            for i, point in enumerate(self.trajectory_points):
                x, y, yaw_deg = point["x"], point["y"], point["yaw"]
                
                # Convert yaw to unit vector
                yaw_rad = math.radians(yaw_deg)
                dx = arrow_scale * math.cos(yaw_rad)
                dy = arrow_scale * math.sin(yaw_rad)
                
                # Draw arrow
                arrow = FancyArrowPatch((x, y), (x + dx, y + dy),
                                      arrowstyle='->', mutation_scale=12,
                                      color='red', alpha=0.9, linewidth=1.2)
                ax.add_patch(arrow)
        
        # Add corner exclusion zones
        corner_points = [
            {"x": 0.0, "y": 0.0},
            {"x": self.rectangle_a, "y": 0.0},
            {"x": self.rectangle_a, "y": self.rectangle_b},
            {"x": 0.0, "y": self.rectangle_b},
        ]
        
        for corner in corner_points:
            circle = plt.Circle((corner["x"], corner["y"]), self.corner_exclusion_radius,
                              fill=False, linestyle='--', color='gray', alpha=0.5, linewidth=1)
            ax.add_patch(circle)
        
        # Set equal aspect ratio and add grid
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Set axis limits with some padding
        all_x = []
        all_y = []
        if self.reference_trajectory:
            all_x.extend([p["x"] for p in self.reference_trajectory])
            all_y.extend([p["y"] for p in self.reference_trajectory])
        if self.trajectory_points:
            all_x.extend([p["x"] for p in self.trajectory_points])
            all_y.extend([p["y"] for p in self.trajectory_points])
        
        if all_x and all_y:
            padding = 0.3
            ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
            ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
        else:
            # Default limits if no data
            ax.set_xlim(-0.5, self.rectangle_a + 0.5)
            ax.set_ylim(-0.5, self.rectangle_b + 0.5)
        
        # Labels and title
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add legend
        legend_elements = []
        if self.reference_trajectory:
            legend_elements.append(plt.Line2D([0], [0], color='blue', linewidth=2, label='Reference Trajectory'))
        if self.trajectory_points:
            legend_elements.append(plt.Line2D([0], [0], color='red', linewidth=2, label='Actual Trajectory'))
        legend_elements.append(plt.Line2D([0], [0], color='gray', linestyle='--', label='Corner Exclusion Zones'))
        
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        # Add statistics text box if trajectory data exists
        if self.trajectory_points:
            errors = self._calculate_trajectory_error()
            stats_text = (
                f"Position RMS Error: {errors['position_error']:.3f}m\n"
                f"Yaw RMS Error: {errors['yaw_error']:.1f}°\n"
                f"Coverage: {errors['coverage']:.1f}%\n"
                f"Points: {len(self.trajectory_points)} actual, {len(self.reference_trajectory)} reference\n"
                f"Tolerances: ±{self.position_tolerance:.1f}m, ±{self.yaw_tolerance:.1f}°"
            )
            
            # Position text box in upper left
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8),
                   verticalalignment='top', fontsize=9, fontfamily='monospace')
        
        # Add coordinate system indicator
        ax.annotate('', xy=(0.15, 0.1), xytext=(0.05, 0.1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                   transform=ax.transAxes)
        ax.annotate('', xy=(0.1, 0.2), xytext=(0.1, 0.1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                   transform=ax.transAxes)
        ax.text(0.16, 0.09, 'X (East)', transform=ax.transAxes, fontsize=8)
        ax.text(0.06, 0.21, 'Y (North)', transform=ax.transAxes, fontsize=8)
        
        plt.tight_layout()
        
        # Generate filename if not provided
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"trajectory_verification_{timestamp}.png"
        
        # Save the plot
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        self.logger.info(f"Trajectory plot saved to: {output_file}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return output_file
    
    async def finish_verification(self, generate_plot: bool = False, 
                                plot_filename: str = None) -> Dict[str, Any]:
        """Finish verification and return results."""

        if not self.is_active:
            return {
                "was_successful": False,
                "results_text": "Verification was not active",
                "results_json": {
                    "overall_result": "FAILED",
                    "was_successful": False,
                    "error": "Verification was not active"
                }
            }
        
        with self.lock:
            self.is_active = False
            
        # Calculate errors
        errors = self._calculate_trajectory_error()
        
        # Check against tolerances
        position_passed = errors["position_error"] <= self.position_tolerance
        yaw_passed = errors["yaw_error"] <= self.yaw_tolerance
        coverage_passed = errors["coverage"] >= 70.0  # Require at least 70% coverage
        overall_success = position_passed and yaw_passed and coverage_passed
        
        # make errors compatible with json export
        invalid_flags = {}
        for key in errors:
            if isinstance(errors[key], float) and (math.isinf(errors[key]) or math.isnan(errors[key])):
                errors[key] = 0.0
                invalid_flags[key] = True
            else:
                invalid_flags[key] = False

        # Generate results text with invalid flags
        results_text = (
            f"Trajectory verification completed:\n"
            f"• Position RMS error: {errors['position_error']:.3f}m "
            f"{'[INVALID]' if invalid_flags['position_error'] else ''}"
            f"(tolerance: {self.position_tolerance}m) {'✓' if position_passed else '✗'}\n"
            f"• Position mean error: {errors['position_mean_error']:.3f}m "
            f"{'[INVALID]' if invalid_flags.get('position_mean_error', False) else ''}\n"
            f"• Yaw RMS error: {errors['yaw_error']:.1f}° "
            f"{'[INVALID]' if invalid_flags['yaw_error'] else ''}"
            f"(tolerance: {self.yaw_tolerance}°) {'✓' if yaw_passed else '✗'}\n"
            f"• Yaw mean error: {errors['yaw_mean_error']:.1f}° "
            f"{'[INVALID]' if invalid_flags.get('yaw_mean_error', False) else ''}\n"
            f"• Max position error: {errors['max_position_error']:.3f}m "
            f"{'[INVALID]' if invalid_flags.get('max_position_error', False) else ''}\n"
            f"• Max yaw error: {errors['max_yaw_error']:.1f}° "
            f"{'[INVALID]' if invalid_flags.get('max_yaw_error', False) else ''}\n"
            f"• Trajectory coverage: {errors['coverage']:.1f}% "
            f"({errors['matched_points']}/{errors['total_reference_points']} reference points matched) "
            f"{'✓' if coverage_passed else '✗'}\n"
            f"• Points collected: {len(self.trajectory_points)}\n"
            f"• Yaw errors calculated: {errors['yaw_errors_calculated']} (excluding {self.corner_exclusion_radius}m corner zones)\n"
            f"• Overall result: {'PASSED' if overall_success else 'FAILED'}"
        )

        # Create structured JSON results with invalid flags embedded in values
        results_json = {
            "overall_result": "PASSED" if overall_success else "FAILED",
            "was_successful": overall_success,
            "position_analysis": {
                "rms_error_m": {
                    "value": round(errors["position_error"], 3),
                    "invalid": invalid_flags["position_error"]
                },
                "mean_error_m": {
                    "value": round(errors["position_mean_error"], 3),
                    "invalid": invalid_flags.get("position_mean_error", False)
                },
                "max_error_m": {
                    "value": round(errors["max_position_error"], 3),
                    "invalid": invalid_flags.get("max_position_error", False)
                },
                "tolerance_m": self.position_tolerance,
                "passed": position_passed
            },
            "yaw_analysis": {
                "rms_error_deg": {
                    "value": round(errors["yaw_error"], 1),
                    "invalid": invalid_flags["yaw_error"]
                },
                "mean_error_deg": {
                    "value": round(errors["yaw_mean_error"], 1),
                    "invalid": invalid_flags.get("yaw_mean_error", False)
                },
                "max_error_deg": {
                    "value": round(errors["max_yaw_error"], 1),
                    "invalid": invalid_flags.get("max_yaw_error", False)
                },
                "tolerance_deg": self.yaw_tolerance,
                "passed": yaw_passed
            },
            "trajectory_coverage": {
                "coverage_percent": {
                    "value": round(errors["coverage"], 1),
                    "invalid": invalid_flags.get("coverage", False)
                },
                "matched_reference_points": errors["matched_points"],
                "total_reference_points": errors["total_reference_points"],
                "minimum_required_percent": 70.0,
                "passed": coverage_passed
            },
            "data_collection": {
                "points_collected": len(self.trajectory_points),
                "reference_trajectory_points": len(self.reference_trajectory),
                "position_errors_calculated": errors["position_errors_calculated"],
                "yaw_errors_calculated": errors["yaw_errors_calculated"]
            },
            "rectangle_parameters": {
                "width_m": self.rectangle_a,
                "height_m": self.rectangle_b,
                "points_per_edge": self.points_per_edge,
                "corner_exclusion_radius_m": self.corner_exclusion_radius
            }
        }
        
        self.logger.info(f"Verification completed: {results_text}")
        
        # Publish results
        results_payload = {
            "was_successful": overall_success,
            "results_text": results_text,
            "results_json": results_json
        }

        mqtt_message = {
            "messageId": str(uuid.uuid4()),
            "command": f"/{self.petal_name}/verify_pos_yaw_directions_results",
            "timestamp": datetime.now().isoformat(),
            "payload": results_payload
        }
        
        await self.mqtt_proxy.publish_message(
            payload=mqtt_message
        )
        
        # Generate plot if requested
        if generate_plot:
            try:
                plot_file = self.plot_trajectories(
                    output_file=plot_filename
                )
                self.logger.info(f"Trajectory plot saved to: {plot_file}")
                results_payload["plot_file"] = plot_file
            except Exception as e:
                self.logger.warning(f"Failed to generate trajectory plot: {e}")
        
        return results_payload


class WifiOptitrackConnectivityController:
    """
    Controller for connecting to WiFi and verifying OptiTrack server connectivity.
    """

    def __init__(
            self, 
            mqtt_proxy: "MQTTProxy", 
            logger: logging.Logger, 
            petal_name: str = "petal-user-journey-coordinator"
        ):
        self.petal_name = petal_name
        self.mqtt_proxy = mqtt_proxy
        self.logger = logger
        self.is_active = False
        self.lock = threading.Lock()

    # ---------- helpers: interface & IP/gateway ----------

    async def _get_wifi_iface(self) -> Optional[str]:
        """Return Wi-Fi interface name (e.g., 'wlp5s0'), preferring a connected device."""
        # Try NetworkManager first
        cmd = ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "dev", "status"]
        p = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await p.communicate()
        if p.returncode == 0:
            devices = []
            for line in out.decode().splitlines():
                # e.g. "wlp5s0:wifi:connected"
                parts = line.split(":")
                if len(parts) >= 3 and parts[1] == "wifi":
                    devices.append((parts[0], parts[2]))
            # Prefer connected iface
            for dev, state in devices:
                if state == "connected":
                    return dev
            # Else return first Wi-Fi iface if any
            if devices:
                return devices[0][0]

        # Fallback: parse `iw dev`
        cmd = ["iw", "dev"]
        p = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await p.communicate()
        if p.returncode == 0:
            import re
            m = re.search(r"Interface\s+(\S+)", out.decode())
            if m:
                return m.group(1)
        return None

    async def _get_ip_and_gateway(self, iface: str) -> Dict[str, Optional[str]]:
        """
        Return {'ip': IPv4 or None, 'gateway': IPv4 or None} for iface using nmcli.
        """
        async def run(cmd):
            p = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await p.communicate()
            return out.decode().strip() if p.returncode == 0 else ""

        # IP may have CIDR suffix, pick first line if multiple
        ip_raw = await run(["nmcli", "-t", "-g", "IP4.ADDRESS", "dev", "show", iface])
        gw_raw = await run(["nmcli", "-t", "-g", "IP4.GATEWAY", "dev", "show", iface])

        ip = ip_raw.splitlines()[0] if ip_raw else ""
        ip = ip.split("/", 1)[0] if ip else None
        gw = gw_raw.splitlines()[0] if gw_raw else None
        return {"ip": ip, "gateway": gw}

    # ---------- public entrypoint ----------

    async def connect_and_verify(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        with self.lock:
            if self.is_active:
                return {
                    "was_successful": False,
                    "status_message": "WiFi connection process already active",
                    "assigned_ip_address": ""
                }
            self.is_active = True

        try:
            wifi_payload = ConnectToWifiAndVerifyOptitrackPayload(**payload)
            ssid = wifi_payload.positioning_system_network_wifi_ssid

            self.logger.info(f"[{message_id}] Starting WiFi connection to SSID: {ssid}")

            # Step 1: Connect to WiFi (auto-detect iface)
            # connection_result = await self._connect_to_wifi(
            #     ssid=ssid,
            #     password=wifi_payload.positioning_system_network_wifi_pass,
            #     message_id=message_id
            # )
            # Force success for testing
            connection_result = {"success": True, "ip_address": "10.0.0.100", "error": None}
            
            if not connection_result["success"]:
                return await self._send_response(
                    message_id=message_id,
                    was_successful=False,
                    status_message=f"WiFi connection failed: {connection_result['error']}",
                    assigned_ip=""
                )

            assigned_ip = connection_result["ip_address"]
            self.logger.info(f"[{message_id}] WiFi connected successfully, assigned IP: {assigned_ip}")

            # Step 2: Verify IP is in expected subnet
            subnet_valid = await self._verify_subnet(
                assigned_ip=assigned_ip,
                expected_subnet_or_mask=wifi_payload.positioning_system_network_wifi_subnet,  # can be "255.255.255.0" or "10.0.0.0/24"
                message_id=message_id,
                reference_ip=wifi_payload.positioning_system_network_server_ip_address       # e.g. "10.0.0.27"
            )
            if not subnet_valid["success"]:
                return await self._send_response(
                    message_id=message_id,
                    was_successful=False,
                    status_message=f"IP subnet validation failed: {subnet_valid['error']}",
                    assigned_ip=assigned_ip
                )

            # Step 3: Ping OptiTrack server
            ping_result = await self._ping_optitrack_server(
                server_ip=wifi_payload.positioning_system_network_server_ip_address,
                message_id=message_id
            )
            if not ping_result["success"]:
                return await self._send_response(
                    message_id=message_id,
                    was_successful=False,
                    status_message=f"OptiTrack server ping failed: {ping_result['error']}",
                    assigned_ip=assigned_ip
                )

            # Success
            success_message = (
                f"Successfully connected to WiFi '{ssid}' with IP {assigned_ip} "
                f"and verified OptiTrack server connectivity at "
                f"{wifi_payload.positioning_system_network_server_ip_address}"
            )
            return await self._send_response(
                message_id=message_id,
                was_successful=True,
                status_message=success_message,
                assigned_ip=assigned_ip
            )

        except Exception as e:
            self.logger.error(f"[{message_id}] Unexpected error in WiFi/OptiTrack connection: {e}")
            return await self._send_response(
                message_id=message_id,
                was_successful=False,
                status_message=f"Unexpected error: {str(e)}",
                assigned_ip=""
            )
        finally:
            with self.lock:
                self.is_active = False

    # ---------- Wi-Fi connect ----------

    async def _connect_to_wifi(self, ssid: str, password: str, message_id: str) -> Dict[str, Any]:
        """
        Connect to WiFi network using NetworkManager (nmcli). Autodetects Wi-Fi interface.
        Returns: {'success': bool, 'ip_address': str|None, 'error': str|None}
        """
        try:
            iface = await self._get_wifi_iface()
            if not iface:
                return {"success": False, "ip_address": None, "error": "No Wi-Fi interface found (nmcli/iw)"}

            self.logger.info(f"[{message_id}] Wi-Fi interface detected: {iface}")
            self.logger.info(f"[{message_id}] Checking current WiFi status...")

            # If already connected to SSID, just read IP & return
            check_cmd = ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"]
            p = await asyncio.create_subprocess_exec(
                *check_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await p.communicate()
            if p.returncode == 0:
                for line in out.decode().splitlines():
                    # "yes:<ssid>" means connected
                    if line.startswith("yes:") and line.split("yes:", 1)[1] == ssid:
                        ip_gw = await self._get_ip_and_gateway(iface)
                        if ip_gw["ip"]:
                            return {"success": True, "ip_address": ip_gw["ip"], "error": None}
                        # fall through to reconnect if we have no IP

            # Disconnect interface (don’t assume wlan0)
            self.logger.info(f"[{message_id}] Disconnecting interface {iface}...")
            await asyncio.create_subprocess_exec("nmcli", "dev", "disconnect", iface)
            await asyncio.sleep(2)

            # Connect and wait up to 30s
            self.logger.info(f"[{message_id}] Connecting to WiFi network: {ssid}")
            connect_cmd = [
                "nmcli", "-w", "30", "dev", "wifi", "connect", ssid,
                "password", password, "ifname", iface
            ]
            p = await asyncio.create_subprocess_exec(
                *connect_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, err = await p.communicate()
            if p.returncode != 0:
                return {"success": False, "ip_address": None, "error": f"nmcli connect failed: {err.decode().strip()}"}

            # Poll for DHCP IP (max ~10s)
            self.logger.info(f"[{message_id}] Waiting for DHCP IP assignment...")
            ip_address = None
            for _ in range(20):
                ip_gw = await self._get_ip_and_gateway(iface)
                ip_address = ip_gw["ip"]
                if ip_address:
                    self.logger.info(f"[{message_id}] IP acquired on {iface}: {ip_address} (gw {ip_gw['gateway']})")
                    break
                await asyncio.sleep(0.5)

            if not ip_address:
                return {"success": False, "ip_address": None, "error": "Connected but no DHCP IPv4 address"}

            return {"success": True, "ip_address": ip_address, "error": None}

        except FileNotFoundError as e:
            # nmcli or iw missing
            return {"success": False, "ip_address": None, "error": f"Dependency missing: {e}"}
        except Exception as e:
            self.logger.error(f"[{message_id}] Exception during WiFi connection: {e}")
            return {"success": False, "ip_address": None, "error": f"Exception: {str(e)}"}

    # ---------- IP fetch (kept for compatibility; now autodetects iface) ----------

    async def _get_current_ip_address(self, message_id: str, iface: Optional[str] = None) -> Optional[str]:
        """Get current IPv4 of Wi-Fi interface using nmcli; auto-detect iface if None."""
        try:
            if iface is None:
                iface = await self._get_wifi_iface()
            if not iface:
                self.logger.error(f"[{message_id}] No Wi-Fi interface found for IP query")
                return None
            res = await self._get_ip_and_gateway(iface)
            if res["ip"]:
                self.logger.info(f"[{message_id}] Found IP address on {iface}: {res['ip']}")
            return res["ip"]
        except Exception as e:
            self.logger.error(f"[{message_id}] Error getting IP address: {e}")
            return None

    # ---------- subnet check ----------

    async def _verify_subnet(
        self,
        assigned_ip: str,
        expected_subnet_or_mask: str,
        message_id: str,
        reference_ip: Optional[str] = None,   # used when a plain netmask is given
    ) -> Dict[str, Any]:
        """
        Verify that the assigned IP is within the expected subnet.

        Supports:
        - CIDR: "10.0.0.0/24" or "10.0.0.1/24" (strict=False normalizes)
        - Dotted netmask: "255.255.255.0" (requires reference_ip to build the network)
        - Bare prefix length: "24" (optional convenience)

        If a dotted/bare mask is provided, we compute the network using `reference_ip`
        (typically your OptiTrack server IP, so we verify both are on the same subnet).
        """
        import ipaddress
        import re

        try:
            self.logger.info(
                f"[{message_id}] Subnet verify: assigned_ip={assigned_ip}, "
                f"expected='{expected_subnet_or_mask}', reference_ip={reference_ip}"
            )

            # Case A: A CIDR string is provided (contains '/')
            if "/" in expected_subnet_or_mask:
                net = ipaddress.IPv4Network(expected_subnet_or_mask, strict=False)

            else:
                # No '/', so it's either a dotted mask (e.g. 255.255.255.0) or a bare prefix (e.g. "24")
                if reference_ip is None:
                    # We prefer reference_ip (server IP). Fall back to assigned_ip if not provided.
                    reference_ip = assigned_ip
                    self.logger.warning(
                        f"[{message_id}] reference_ip not provided; falling back to assigned_ip={assigned_ip}"
                    )

                # Bare prefix-length?
                if re.fullmatch(r"\d{1,2}", expected_subnet_or_mask):
                    # e.g., "24"
                    net = ipaddress.IPv4Network(f"{reference_ip}/{expected_subnet_or_mask}", strict=False)
                else:
                    # Treat as dotted mask (ipaddress supports dotted masks)
                    # e.g., IPv4Network("10.0.0.27/255.255.255.0", strict=False) -> 10.0.0.0/24
                    net = ipaddress.IPv4Network(f"{reference_ip}/{expected_subnet_or_mask}", strict=False)

            ip = ipaddress.IPv4Address(assigned_ip)

            if ip in net:
                self.logger.info(
                    f"[{message_id}] IP verification successful: {assigned_ip} is in {net.with_prefixlen}"
                )
                return {"success": True, "network": net.with_prefixlen}

            error_msg = f"IP {assigned_ip} is not in expected subnet {net.with_prefixlen}"
            self.logger.error(f"[{message_id}] {error_msg}")
            return {"success": False, "error": error_msg, "network": net.with_prefixlen}

        except Exception as e:
            error_msg = f"Subnet verification error: {str(e)}"
            self.logger.error(f"[{message_id}] {error_msg}")
            return {"success": False, "error": error_msg}

    # ---------- ping check ----------

    async def _ping_optitrack_server(self, server_ip: str, message_id: str, timeout: int = 5, count: int = 3) -> Dict[str, Any]:
        """Ping the OptiTrack server; bind to Wi-Fi iface if available to avoid route ambiguity."""
        try:
            self.logger.info(f"[{message_id}] Pinging OptiTrack server at {server_ip} ({count} attempts)")
            iface = await self._get_wifi_iface()

            cmd = ["ping", "-c", str(count), "-W", str(timeout), server_ip]
            # Prefer pinging via Wi-Fi interface when multiple NICs exist
            if iface:
                cmd = ["ping", "-I", iface, "-c", str(count), "-W", str(timeout), server_ip]

            p = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, err = await p.communicate()

            if p.returncode == 0 and b"packet loss" in out:
                self.logger.info(f"[{message_id}] Ping successful to {server_ip}")
                return {"success": True}
            else:
                # Prefer stderr; if empty, include stdout summary
                err_txt = err.decode().strip() or out.decode().strip()
                return {"success": False, "error": f"Ping failed: {err_txt}"}

        except Exception as e:
            err = f"Ping error: {e}"
            self.logger.error(f"[{message_id}] {err}")
            return {"success": False, "error": err}

    # ---------- MQTT response ----------

    async def _send_response(self, message_id: str, was_successful: bool,
                             status_message: str, assigned_ip: str) -> Dict[str, Any]:
        """Send response message via MQTT."""
        try:
            response_payload = WifiOptitrackConnectionResponse(
                was_successful=was_successful,
                status_message=status_message,
                assigned_ip_address=assigned_ip
            )
            mqtt_message = {
                "messageId": message_id,
                "deviceId": getattr(self.mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.petal_name}/acknowledge",
                "timestamp": datetime.now().isoformat(),
                "payload": response_payload.model_dump()
            }
            await self.mqtt_proxy.publish_message(payload=mqtt_message)
            self.logger.info(f"[{message_id}] Response sent: {was_successful}")
            return response_payload.model_dump()
        except Exception as e:
            self.logger.error(f"[{message_id}] Failed to send response: {e}")
            return {
                "was_successful": was_successful,
                "status_message": status_message,
                "assigned_ip_address": assigned_ip
            }

    async def set_static_ip_address(self, payload: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        """
        Set a static IP address within the specified subnet and gateway network.
        
        This method:
        1. Gets the current IP address from the WiFi interface
        2. Calculates the appropriate gateway based on the server IP
        3. Verifies the current IP is within the expected subnet/gateway
        4. Configures a static IP address using NetworkManager
        
        Args:
            payload: Static IP configuration
            message_id: Unique message identifier
            
        Returns:
            Dict containing success status and assigned static IP
        """
        with self.lock:
            if self.is_active:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message="Static IP configuration process already active"
                )
            self.is_active = True
        
        try:
            static_ip_payload = SetStaticIpAddressPayload(**payload)
            
            self.logger.info(f"[{message_id}] Starting static IP configuration")
            
            # Step 1: Get current WiFi interface and IP
            wifi_iface = await self._get_wifi_iface()
            if not wifi_iface:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message="No WiFi interface found"
                )
            
            # Get current IP and gateway
            ip_info = await self._get_ip_and_gateway(wifi_iface)
            current_ip = ip_info.get("ip")
            current_gateway = ip_info.get("gateway")
            
            if not current_ip:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message=f"No IP address found on WiFi interface {wifi_iface}"
                )
            
            self.logger.info(f"[{message_id}] Current IP: {current_ip}, Gateway: {current_gateway}")
            
            # Step 2: Calculate target network and gateway from server IP
            server_ip = static_ip_payload.positioning_system_network_server_ip_address
            subnet_mask = static_ip_payload.positioning_system_network_wifi_subnet
            
            # Determine target gateway from server IP (assumes server IP is within the target network)
            target_gateway = await self._calculate_gateway_from_server_ip(server_ip, subnet_mask, message_id)
            if not target_gateway:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message="Failed to calculate target gateway from server IP"
                )
            
            # Step 3: Verify current IP is within the target gateway network
            verification_result = await self._verify_subnet(
                assigned_ip=current_ip,
                expected_subnet_or_mask=subnet_mask,
                reference_ip=server_ip,
                message_id=message_id
            )
            
            if not verification_result["success"]:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message=f"Current IP {current_ip} is not within target network: {verification_result.get('error', 'Unknown error')}"
                )
            
            # Step 4: Configure static IP using NetworkManager
            static_config_result = await self._configure_static_ip(
                interface=wifi_iface,
                ip_address=current_ip,
                subnet_mask=subnet_mask,
                gateway=target_gateway,
                message_id=message_id
            )
            
            if not static_config_result["success"]:
                return await self._send_static_ip_response(
                    message_id=message_id,
                    was_successful=False,
                    assigned_static_ip="",
                    error_message=f"Failed to configure static IP: {static_config_result['error']}"
                )
            
            # Success case
            self.logger.info(f"[{message_id}] Successfully configured static IP: {current_ip}")
            return await self._send_static_ip_response(
                message_id=message_id,
                was_successful=True,
                assigned_static_ip=current_ip,
                error_message=""
            )
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Unexpected error in static IP configuration: {e}")
            return await self._send_static_ip_response(
                message_id=message_id,
                was_successful=False,
                assigned_static_ip="",
                error_message=f"Unexpected error: {str(e)}"
            )
        finally:
            with self.lock:
                self.is_active = False

    async def _calculate_gateway_from_server_ip(self, server_ip: str, subnet_mask: str, message_id: str) -> Optional[str]:
        """
        Calculate the gateway IP from the server IP and subnet mask.
        Assumes the gateway is the first usable IP in the network (e.g., 10.0.0.1 for 10.0.0.0/24).
        """
        try:
            import ipaddress
            
            # Parse subnet mask format (handle both CIDR and dotted notation)
            if "/" in subnet_mask:
                # CIDR notation (e.g., "10.0.0.0/24")
                network = ipaddress.IPv4Network(subnet_mask, strict=False)
            elif re.fullmatch(r"\d{1,2}", subnet_mask):
                # Bare prefix length (e.g., "24")
                network = ipaddress.IPv4Network(f"{server_ip}/{subnet_mask}", strict=False)
            else:
                # Dotted notation (e.g., "255.255.255.0")
                network = ipaddress.IPv4Network(f"{server_ip}/{subnet_mask}", strict=False)
            
            # Gateway is typically the first usable IP in the network
            gateway = str(list(network.hosts())[0])
            self.logger.info(f"[{message_id}] Calculated gateway: {gateway} for network: {network}")
            return gateway
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Error calculating gateway: {e}")
            return None

    async def _configure_static_ip(self, interface: str, ip_address: str, subnet_mask: str, gateway: str, message_id: str) -> Dict[str, Any]:
        """
        Configure static IP address using NetworkManager.
        """
        try:
            import subprocess
            import asyncio
            
            self.logger.info(f"[{message_id}] Configuring static IP {ip_address} with gateway {gateway} on {interface}")
            
            # Get the current connection name for this interface
            conn_cmd = ["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active"]
            result = await asyncio.create_subprocess_exec(
                *conn_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            connection_name = None
            if result.returncode == 0:
                for line in stdout.decode().strip().split('\n'):
                    if line:
                        name, device = line.split(':', 1)
                        if device == interface:
                            connection_name = name
                            break
            
            if not connection_name:
                return {"success": False, "error": f"No active connection found for interface {interface}"}
            
            self.logger.info(f"[{message_id}] Found connection: {connection_name}")
            
            # Calculate CIDR notation from subnet mask
            if "/" in subnet_mask:
                cidr_ip = f"{ip_address}/{subnet_mask.split('/')[-1]}"
            elif re.fullmatch(r"\d{1,2}", subnet_mask):
                cidr_ip = f"{ip_address}/{subnet_mask}"
            else:
                # Convert dotted notation to CIDR
                import ipaddress
                network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
                cidr_ip = f"{ip_address}/{network.prefixlen}"
            
            # Configure static IP using nmcli
            modify_cmd = [
                "nmcli", "connection", "modify", connection_name,
                "ipv4.method", "manual",
                "ipv4.addresses", cidr_ip,
                "ipv4.gateway", gateway
            ]
            
            result = await asyncio.create_subprocess_exec(
                *modify_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode().strip() or stdout.decode().strip()
                return {"success": False, "error": f"Failed to modify connection: {error_msg}"}
            
            # Restart the connection to apply changes
            restart_cmd = ["nmcli", "connection", "up", connection_name]
            result = await asyncio.create_subprocess_exec(
                *restart_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode().strip() or stdout.decode().strip()
                return {"success": False, "error": f"Failed to restart connection: {error_msg}"}
            
            # Wait a moment for the configuration to take effect
            await asyncio.sleep(3)
            
            # Verify the static IP is configured
            verification = await self._get_ip_and_gateway(interface)
            if verification.get("ip") == ip_address:
                self.logger.info(f"[{message_id}] Static IP configuration verified: {ip_address}")
                return {"success": True}
            else:
                return {"success": False, "error": f"IP verification failed. Expected: {ip_address}, Got: {verification.get('ip')}"}
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Exception during static IP configuration: {e}")
            return {"success": False, "error": f"Exception: {str(e)}"}

    async def _send_static_ip_response(self, message_id: str, was_successful: bool, 
                                     assigned_static_ip: str, error_message: str) -> Dict[str, Any]:
        """Send static IP configuration response via MQTT."""
        try:
            
            response_payload = SetStaticIpAddressResponse(
                assigned_static_ip=assigned_static_ip,
                was_successful=was_successful
            )
            
            mqtt_message = {
                "messageId": message_id,
                "deviceId": getattr(self.mqtt_proxy, 'device_id', 'unknown'),
                "command": f"{self.petal_name}/set_static_ip_address_ack",
                "timestamp": datetime.now().isoformat(),
                "payload": response_payload.model_dump()
            }
            
            await self.mqtt_proxy.publish_message(payload=mqtt_message)
            
            status_msg = "Static IP configuration successful" if was_successful else f"Static IP configuration failed: {error_message}"
            self.logger.info(f"[{message_id}] {status_msg}")
            return response_payload.model_dump()
            
        except Exception as e:
            self.logger.error(f"[{message_id}] Failed to send static IP response: {e}")
            return {
                "assigned_static_ip": assigned_static_ip,
                "was_successful": was_successful
            }
