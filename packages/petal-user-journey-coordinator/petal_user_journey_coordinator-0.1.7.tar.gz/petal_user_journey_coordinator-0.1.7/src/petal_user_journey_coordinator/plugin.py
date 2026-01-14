"""
Main plugin module for petal-user-journey-coordinator
"""

import asyncio
import math
import numpy as np
from typing import Dict, Any, List, Union, Optional, Callable
from datetime import datetime, timezone
import threading
from enum import Enum
import time

from . import logger
from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action, websocket_action
from petal_app_manager.proxies import (
    MQTTProxy,
    MavLinkExternalProxy,
    LocalDBProxy,
    RedisProxy
)
from petal_app_manager import Config
from petal_app_manager.models import MQTTMessage

import json, math
from pymavlink import mavutil
from pymavlink.dialects.v20 import all as mavlink_dialect

from pydantic import ValidationError
from fastapi import HTTPException
import asyncio

from .controllers import (
    # Parameter controllers
    BaseParameterHandler,
    RotorCountHandler,
    GPSModuleHandler,
    DistanceModuleHandler,
    OpticalFlowModuleHandler,
    GPSSpatialOffsetHandler,
    DistanceSpatialOffsetHandler,
    OpticalFlowSpatialOffsetHandler,
    ESCCalibrationLimitsHandler,
    KillSwitchConfigHandler,

    # Timeout controllers
    BaseTimeoutController,
    ESCCalibrationController,
    ESCForceRunAllController,
    ESCForceRunSingleController,
    BasePubSubController,
    RCChannelsController,

    # Pubsub controllers
    BasePubSubController,
    RCChannelsController,
    PositionChannelsController,
    KillSwitchController,
    MultiFunctionalSwitchAController,
    MultiFunctionalSwitchBController,

    # Custom controllers
    TrajectoryVerificationController,
    WifiOptitrackConnectivityController
)

from .data_model import (
    # generic payloads
    BulkParameterSetRequest,
    SubscribePayload,
    UnsubscribePayload,

    # Timeout payloads
    ESCCalibrationPayload,
    ESCCalibrationLimitsPayload,
    ESCForceRunAllPayload,
    ESCForceRunSinglePayload,
    VerifyPosYawDirectionsPayload,
    ConnectToWifiAndVerifyOptitrackPayload,
    WifiOptitrackConnectionResponse,
    SetStaticIpAddressPayload,
    SetStaticIpAddressResponse,

    # HTTP models
    ParameterRequestModel,
    ParameterBaseModel,
    ParameterResponseModel,
    MavlinkParameterResponseModel,
    MavlinkParametersResponseModel,
    RotorCountParameter,
    DistanceModulePayload,
    OpticalFlowModulePayload,
    BulkParameterSetRequest,
    BulkParameterGetRequest,
    BulkParameterResponse
)

from petal_app_manager.models.mavlink import (
    RebootAutopilotResponse
)

class OperationMode(Enum):
    """Enumeration of operation modes"""
    ESC_CALIBRATION = "esc_calibration"
    ESC_FORCE_RUN_ALL = "esc_force_run_all"
    ESC_FORCE_RUN_SINGLE = "esc_force_run_single"


def _json_safe(o):
    # Recursively replace NaN/±Inf with None and coerce numpy scalars to py types
    try:
        import numpy as np  # optional
        np_types = (np.floating, np.integer)
    except Exception:
        np_types = tuple()

    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if np_types and isinstance(o, np_types):
        py = o.item()
        return py if not (isinstance(py, float) and not math.isfinite(py)) else None
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_json_safe(v) for v in o]
    return o


class PetalUserJourneyCoordinator(Petal):
    """
    Main petal class for petal-user-journey-coordinator.
    
    This petal demonstrates the basic structure and includes a health endpoint
    that reports proxy requirements and status.
    """
    
    name = "petal-user-journey-coordinator"
    version = "0.1.0"
    use_mqtt_proxy = True  # Enable MQTT-aware startup

    def __init__(self):
        super().__init__()
        self._status_message = "Petal initialized successfully"
        self._startup_time = None
        self._mavlink_proxy = None
        self._mqtt_proxy = None
        self._loop = None  # Will be set when async context is available
        
        # Timeout controller instances
        self._operation_controllers: Dict[OperationMode, BaseTimeoutController] = {}
        self._parameter_handlers: Dict[str, BaseParameterHandler] = {}
        self._pubsub_controllers: Dict[str, BasePubSubController] = {}
        self._active_controllers: Dict[OperationMode, BaseTimeoutController] = {
            mode: None for mode in OperationMode
        }
        self._controller_locks = {mode: threading.Lock() for mode in OperationMode}
        self._trajectory_verification = None  # Initialize later in startup()
        
        # Active subscription tracking
        self._active_handlers: Dict[str, Dict[str, Any]] = {}  # stream_name -> subscription_info
        self._registration_lock = threading.Lock()
        
        # Trajectory verification configuration
        self.trajectory_collection_rate_hz: Optional[float] = None  # None = match pose controller rate

        # Trajectory verification parameters
        self.rectangle_a = 3.0  # width in meters
        self.rectangle_b = 3.0  # height in meters
        self.points_per_edge = 10  # Number of interpolated points per edge (including start point, excluding end point)
        self.corner_exclusion_radius = 1  # meters
        
    def startup(self) -> None:
        """Called when the petal is started."""
        super().startup()
        self._startup_time = datetime.now()
        self._status_message = f"Petal started at {self._startup_time.isoformat()}"
        logger.info(f"{self.name} petal started successfully")
        
        # Store proxy references (after inject_proxies has been called)
        self._mqtt_proxy: MQTTProxy = self._proxies["mqtt"]
        self._mavlink_proxy: MavLinkExternalProxy = self._proxies["ext_mavlink"]

        # Initialize trajectory verification controller
        self._trajectory_verification = TrajectoryVerificationController(
            mqtt_proxy=self._mqtt_proxy, 
            logger=logger,
            rectangle_a=self.rectangle_a,
            rectangle_b=self.rectangle_b,
            points_per_edge=self.points_per_edge,
            corner_exclusion_radius=self.corner_exclusion_radius,
            petal_name=self.name
        )

        # Initialize WiFi OptiTrack connectivity controller
        self._wifi_optitrack_controller = WifiOptitrackConnectivityController(self._mqtt_proxy, logger, petal_name=self.name)

        # Initialize operation controllers
        self._operation_controllers = {
            OperationMode.ESC_CALIBRATION: ESCCalibrationController(self._mavlink_proxy, logger),
            OperationMode.ESC_FORCE_RUN_ALL: ESCForceRunAllController(self._mavlink_proxy, logger),
            OperationMode.ESC_FORCE_RUN_SINGLE: ESCForceRunSingleController(self._mavlink_proxy, logger)
        }

        # Initialize parameter configuration handlers
        self._parameter_handlers = {
            "geometry": RotorCountHandler(self._mavlink_proxy, logger),
            "gps_module": GPSModuleHandler(self._mavlink_proxy, logger),
            "dist_module": DistanceModuleHandler(self._mavlink_proxy, logger),
            "oflow_module": OpticalFlowModuleHandler(self._mavlink_proxy, logger),
            "gps_spatial_offset": GPSSpatialOffsetHandler(self._mavlink_proxy, logger),
            "distance_spatial_offset": DistanceSpatialOffsetHandler(self._mavlink_proxy, logger),
            "optical_flow_spatial_offset": OpticalFlowSpatialOffsetHandler(self._mavlink_proxy, logger),
            "esc_update_calibration_limits": ESCCalibrationLimitsHandler(self._mavlink_proxy, logger)
        }

        # Pub/sub controllers will be initialized in async_startup once topic_base is available
        self._pubsub_controllers = None

        # Create parameter message handlers dynamically
        parameter_configs = {
            "geometry": "rotor count",
            "gps_module": "GPS module",
            "dist_module": "distance module",
            "oflow_module": "optical flow module",
            "gps_spatial_offset": "GPS spatial offset",
            "distance_spatial_offset": "distance spatial offset",
            "optical_flow_spatial_offset": "optical flow spatial offset",
            "esc_update_calibration_limits": "ESC calibration limits"
        }

        # Dynamically create parameter message handlers
        for handler_key, config_type in parameter_configs.items():
            handler_method_name = f"_{handler_key}_message_handler"
            handler_method = self._create_parameter_message_handler(handler_key, config_type)
            setattr(self, handler_method_name, handler_method)

        # Pub/Sub controller configurations
        pubsub_configs = {
            "rc_value_stream": "RC value stream",
            "pose_value_stream": "real-time pose stream",
            "ks_status_stream": "kill switch status stream",
            "mfs_a_status_stream": "multi-functional switch A stream",
            "mfs_b_status_stream": "multi-functional switch B stream"
        }

        # Dynamically create pub/sub message handlers
        for controller_key, stream_name in pubsub_configs.items():
            subscribe_handler, unsubscribe_handler = self._create_pubsub_message_handlers(controller_key, stream_name)
            setattr(self, f"_subscribe_{controller_key}_handler", subscribe_handler)
            setattr(self, f"_unsubscribe_{controller_key}_handler", unsubscribe_handler)

        # Topic configuration and command handlers will be set up in async_startup
        # once organization ID is available
        self._command_handlers = None
        self.mqtt_subscription_id = None

    def set_trajectory_collection_rate(self, rate_hz: Optional[float]) -> None:
        """
        Set the trajectory data collection rate.
        
        Args:
            rate_hz: Collection rate in Hz. If None, will match pose controller rate.
                    If pose controller rate cannot be determined, falls back to 10 Hz.
        """
        if rate_hz is not None and rate_hz <= 0:
            raise ValueError("Collection rate must be positive")
        
        self.trajectory_collection_rate_hz = rate_hz
        logger.info(f"Trajectory collection rate set to: {'auto (match pose controller)' if rate_hz is None else f'{rate_hz} Hz'}")

    def _track_subscription(self, stream_name: str, stream_id: str, rate_hz: float) -> None:
        """Track an active subscription for management purposes."""
        with self._registration_lock:
            self._active_handlers[stream_name] = {
                "stream_id": stream_id,
                "rate_hz": rate_hz,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "controller": self._pubsub_controllers.get(stream_name)
            }
        logger.info(f"Tracking subscription for {stream_name} (ID: {stream_id}, Rate: {rate_hz} Hz)")

    def _untrack_subscription(self, stream_name: str) -> None:
        """Stop tracking a subscription."""
        with self._registration_lock:
            if stream_name in self._active_handlers:
                del self._active_handlers[stream_name]
                logger.info(f"Stopped tracking subscription for {stream_name}")

    def get_active_handlers(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of all active handlers."""
        with self._registration_lock:
            return dict(self._active_handlers)

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
                "timestamp": datetime.now(timezone.utc).isoformat()
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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if failed_streams:
            result["failed_streams"] = failed_streams
            result["message"] += f", {len(failed_streams)} failed"
        
        logger.info(f"Unsubscribe all operation completed: {result['message']}")
        return result

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
        
        logger.info("User Journey Coordinator Petal async_startup completed (MQTT setup handled by main app)")
        pass

    async def _setup_mqtt_topics(self):
        """Set up MQTT topics and controllers once organization ID is available."""
        
        # Initialize pub/sub controllers now that topic_base is available
        self._pubsub_controllers: Dict[str, BasePubSubController] = {
            "rc_value_stream": RCChannelsController(
                self._mqtt_proxy, 
                self._mavlink_proxy, 
                logger, 
                petal_name=self.name
            ),
            "pose_value_stream": PositionChannelsController(
                mqtt_proxy=self._mqtt_proxy, 
                mavlink_proxy=self._mavlink_proxy, 
                logger=logger,
                rectangle_a=self.rectangle_a,
                rectangle_b=self.rectangle_b,
                points_per_edge=self.points_per_edge,
                corner_exclusion_radius=self.corner_exclusion_radius,
                max_matching_distance=self._trajectory_verification.max_matching_distance,
                corner_points=self._trajectory_verification.corner_points, # Pass corner points here
                reference_trajectory=self._trajectory_verification.reference_trajectory, # Pass reference trajectory here
                petal_name=self.name
            ),
            "ks_status_stream": KillSwitchController(
                self._mqtt_proxy, 
                self._mavlink_proxy, 
                logger,
                petal_name=self.name
            ),
            "mfs_a_status_stream": MultiFunctionalSwitchAController(
                self._mqtt_proxy, 
                self._mavlink_proxy, 
                logger,
                petal_name=self.name
            ),
            "mfs_b_status_stream": MultiFunctionalSwitchBController(
                self._mqtt_proxy, 
                self._mavlink_proxy, 
                logger,
                petal_name=self.name
            )
        }
        
        # Initialize command handlers registry
        self._command_handlers = self._setup_command_handlers()
        
        # Single topic subscription - the master handler will dispatch based on command
        self.mqtt_subscription_id = self._mqtt_proxy.register_handler(self._master_command_handler)
        if self.mqtt_subscription_id is None:
            logger.error("Failed to register MQTT handler for Flight Log Petal")
            return
        
        logger.info(f"Subscribed to MQTT topics successfully with subscription ID: {self.mqtt_subscription_id}")

    def _setup_command_handlers(self) -> Dict[str, Callable]:
        """Setup the command handlers registry mapping command names to handler methods."""
        return {
            # Test commands
            # "Update": self._test_esc_calibration_message_handler,
            # "Update": self._test_geometry_message_handler,
            # "Update": self._test_subscribe_rc_value_stream_handler,
            # "Update": self._test_subscribe_real_time_pose_handler,
            # "Update": self._test_kill_switch_stream_handler,
            # "Update": self._test_mfs_a_stream_handler,
            # "Update": self._test_mfs_b_stream_handler,
            # "Update": self._test_verify_pos_yaw_directions_handler,
            # "Update": self._test_connect_to_wifi_and_verify_optitrack_handler,
            # "Update": self._test_set_static_ip_address_handler,
            # "Update": self._test_unregister_all_handlers,

            # Timeout operation commands
            f"{self.name}/esc_calibration": self._esc_calibration_message_handler,
            f"{self.name}/esc_force_run_all": self._esc_force_run_all_message_handler,
            f"{self.name}/esc_force_run_single": self._esc_force_run_single_message_handler,

            # Parameter configuration commands
            f"{self.name}/geometry": self._geometry_message_handler,
            f"{self.name}/gps_module": self._gps_module_message_handler,
            f"{self.name}/dist_module": self._dist_module_message_handler,
            f"{self.name}/oflow_module": self._oflow_module_message_handler,
            f"{self.name}/gps_spatial_offset": self._gps_spatial_offset_message_handler,
            f"{self.name}/distance_spatial_offset": self._distance_spatial_offset_message_handler,
            f"{self.name}/optical_flow_spatial_offset": self._optical_flow_spatial_offset_message_handler,
            f"{self.name}/esc_update_calibration_limits": self._esc_update_calibration_limits_message_handler,
            f"{self.name}/bulk_set_parameters": self._bulk_set_parameter_message_handler,
            f"{self.name}/bulk_get_parameters": self._bulk_get_parameter_message_handler,
            
            # Pub/Sub stream commands
            f"{self.name}/subscribe_rc_value_stream": self._subscribe_rc_value_stream_handler,
            f"{self.name}/unsubscribe_rc_value_stream": self._unsubscribe_rc_value_stream_handler,
            f"{self.name}/subscribe_pose_value_stream": self._subscribe_pose_value_stream_handler,
            f"{self.name}/unsubscribe_pose_value_stream": self._unsubscribe_pose_value_stream_handler,
            f"{self.name}/subscribe_ks_status_stream": self._subscribe_ks_status_stream_handler,
            f"{self.name}/unsubscribe_ks_status_stream": self._unsubscribe_ks_status_stream_handler,
            f"{self.name}/subscribe_mfs_a_status_stream": self._subscribe_mfs_a_status_stream_handler,
            f"{self.name}/unsubscribe_mfs_a_status_stream": self._unsubscribe_mfs_a_status_stream_handler,
            f"{self.name}/subscribe_mfs_b_status_stream": self._subscribe_mfs_b_status_stream_handler,
            f"{self.name}/unsubscribe_mfs_b_status_stream": self._unsubscribe_mfs_b_status_stream_handler,
            f"{self.name}/unsubscribeall": self._unregister_all_handlers,
            
            # Trajectory verification commands
            f"{self.name}/verify_pos_yaw_directions": self._verify_pos_yaw_directions_handler,
            f"{self.name}/verify_pos_yaw_directions_complete": self._verify_pos_yaw_directions_complete_handler,
            
            # WiFi OptiTrack connectivity commands
            f"{self.name}/connect_to_wifi_and_verify_optitrack": self._connect_to_wifi_and_verify_optitrack_handler,
            f"{self.name}/set_static_ip_address": self._set_static_ip_address_handler,
            # Reboot command
            f"{self.name}/reboot_autopilot": self._reboot_px4_message_handler
        }

    async def _master_command_handler(self, topic: str, message: Dict[str, Any]):
        """
        Master command handler that dispatches to specific handlers based on command field.
        
        Args:
            topic: MQTT topic (should be command/edge for all commands)
            message: MQTT message containing command and payload
        """
        try:
            # Check if command handlers are initialized
            if self._command_handlers is None:
                error_msg = "Petal not fully initialized yet, command handlers not available"
                logger.warning(error_msg)
                return
                
            # Parse the MQTT message
            mqtt_msg = MQTTMessage(**message)
            command = mqtt_msg.command
            
            logger.info(f"Master handler received command: {command}")
            
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
                
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={
                            "status": "error", 
                            "message": error_msg, 
                            "error_code": "UNKNOWN_COMMAND",
                            "available_commands": list(self._command_handlers.keys())
                        }
                    )
                    
        except ValidationError as ve:
            error_msg = f"Invalid MQTT message format: {ve}"
            logger.error(error_msg)
            try:
                message_id = message.get("messageId", "unknown")
                wait_response = message.get("waitResponse", False)
                if wait_response:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                    )
            except Exception as e:
                logger.error(f"Failed to send error response: {e}")
                
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

    @http_action(method="POST", path="/test/esc-calibration")
    async def _test_esc_calibration_message_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for ESC calibration with enhanced workflow."""

        # Test Step 1: Initialize and configure ESC calibration
        test_payload = {
            "is_calibration_started": False,
            "safety_timeout_s": 3.0,
            "force_cancel_calibration": False,
            "esc_interface_signal_type": "PWM",
            "ca_rotor_count": 4,
            "throttle": None  # Just configure first
        }
        message["payload"] = test_payload
        logger.info("🔧 Step 1: Configuring ESC calibration...")
        await self._esc_calibration_message_handler(topic, message)
        
        # Wait a moment for configuration
        await asyncio.sleep(2)
        # Wait 5 seconds (simulate user powering up drone)
        logger.info("⏳ Waiting 5 seconds (simulate drone power-up)...")

        # Test Step 2: Send maximum throttle        
        t_start = time.time()
        logger.info("⚡ Step 2: Sending MAXIMUM throttle (ESC calibration high point)")
        while True:
            # Test Step 2: Send maximum throttle
            test_payload["throttle"] = "maximum"
            test_payload["is_calibration_started"] = True
            message["payload"] = test_payload
            await self._esc_calibration_message_handler(topic, message)
            await asyncio.sleep(0.1)

            if time.time() - t_start > 10:
                break
        
        # Wait a moment for configuration to simulate a timeout
        await asyncio.sleep(10)

        # Test Step 3: Send minimum throttle        
        t_start = time.time()
        while True:
            # Test Step 2: Send maximum throttle
            test_payload["throttle"] = "minimum"
            test_payload["is_calibration_started"] = True
            message["payload"] = test_payload
            logger.info("⬇️  Step 3: Sending MINIMUM throttle (ESC calibration low point)")
            await self._esc_calibration_message_handler(topic, message)
            asyncio.sleep(0.1)

            if time.time() - t_start > 5:
                break
        
        # Test Step 4: Stop motors (using force_cancel_calibration)
        test_payload["force_cancel_calibration"] = True
        message["payload"] = test_payload
        logger.info("🛑 Step 4: Stopping all motors safely")
        await self._esc_calibration_message_handler(topic, message)
        
        logger.info("✅ ESC calibration test sequence completed!")

    @http_action(method="POST", path="/test/geometry")
    async def _test_geometry_message_handler(self, topic: str, message: Dict[str, Any]):
        # intercept payload
        test_payload = {
            "rotor_count": 4,
        }
        message["payload"] = test_payload
        # Use the dynamically created handler directly
        await self._rotor_count_message_handler(topic, message)

    @http_action(method="POST", path="/test/dist-module")
    async def _test_dist_module_message_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for distance module configuration."""
        # Test with LiDAR Lite v3
        test_payload = {
            "dist_module": "LiDAR Lite v3"
        }
        message["payload"] = test_payload
        await self._dist_module_message_handler(topic, message)

    @http_action(method="POST", path="/test/oflow-module")
    async def _test_oflow_module_message_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for optical flow module configuration."""
        # Test with ARK Flow
        test_payload = {
            "oflow_module": "ARK Flow"
        }
        message["payload"] = test_payload
        await self._oflow_module_message_handler(topic, message)

    @http_action(method="POST", path="/test/subscribe-rc-value-stream")
    async def _test_subscribe_rc_value_stream_handler(self, topic: str, message: Dict[str, Any]):
        # intercept payload
        test_payload = {
            "subscribed_stream_id": "px4_rc_raw",
            "data_rate_hz": 50.0
        }
        message["payload"] = test_payload
        # Use the dynamically created handler directly
        await self._subscribe_rc_value_stream_handler(topic, message)

        # unsubscribe after 10 seconds
        await asyncio.sleep(100)

        test_payload = {
            "unsubscribed_stream_id": "px4_rc_raw"
        }
        message["payload"] = test_payload

        await self._unsubscribe_rc_value_stream_handler(topic, message)

    @http_action(method="POST", path="/test/subscribe-real-time-pose")
    async def _test_subscribe_real_time_pose_handler(self, topic: str, message: Dict[str, Any]):
        # intercept payload
        test_payload = {
            "subscribed_stream_id": "real_time_pose",
            "data_rate_hz": 20.0
        }
        message["payload"] = test_payload
        # Use the dynamically created handler directly
        await self._subscribe_real_time_pose_handler(topic, message)

        # unsubscribe after 15 seconds
        await asyncio.sleep(15)

        test_payload = {
            "unsubscribed_stream_id": "real_time_pose"
        }
        message["payload"] = test_payload

        await self._unsubscribe_real_time_pose_handler(topic, message)

    @http_action(method="POST", path="/test/kill-switch-stream")
    async def _test_kill_switch_stream_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for kill switch stream."""
        logger.info("Running kill switch stream test")
        
        # Subscribe to kill switch stream
        test_payload = {
            "subscribed_stream_id": "px4_ks_status",
            "data_rate_hz": 5.0  # 5 Hz for kill switch monitoring
        }
        message["payload"] = test_payload
        await self._subscribe_ks_status_stream_handler(topic, message)

        # Let it run for 30 seconds to monitor kill switch changess
        logger.info("Monitoring kill switch for 30 seconds...")
        await asyncio.sleep(3000)

        # Unsubscribe from kill switch stream
        test_payload = {
            "unsubscribed_stream_id": "px4_ks_status"
        }
        message["payload"] = test_payload
        await self._unsubscribe_ks_status_stream_handler(topic, message)
        
        logger.info("Kill switch stream test completed")

    @http_action(method="POST", path="/test/mfs-a-stream")
    async def _test_mfs_a_stream_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for Multi-functional Switch A stream."""
        logger.info("Running Multi-functional Switch A stream test")
        
        # Subscribe to MFS A stream
        test_payload = {
            "subscribed_stream_id": "px4_mfs_a_raw",
            "data_rate_hz": 10.0  # 10 Hz for MFS A monitoring
        }
        message["payload"] = test_payload
        await self._subscribe_mfs_a_value_stream_handler(topic, message)

        # Let it run for 20 seconds to monitor MFS A changes
        logger.info("Monitoring Multi-functional Switch A for 20 seconds...")
        await asyncio.sleep(20)

        # Unsubscribe from MFS A stream
        test_payload = {
            "unsubscribed_stream_id": "px4_mfs_a_raw"
        }
        message["payload"] = test_payload
        await self._unsubscribe_mfs_a_value_stream_handler(topic, message)
        
        logger.info("Multi-functional Switch A stream test completed")

    @http_action(method="POST", path="/test/mfs-b-stream")
    async def _test_mfs_b_stream_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for Multi-functional Switch B stream."""
        logger.info("Running Multi-functional Switch B stream test")
        
        # Subscribe to MFS B stream
        test_payload = {
            "subscribed_stream_id": "px4_mfs_b_raw",
            "data_rate_hz": 10.0  # 10 Hz for MFS B monitoring
        }
        message["payload"] = test_payload
        await self._subscribe_mfs_b_value_stream_handler(topic, message)

        # Let it run for 20 seconds to monitor MFS B changes
        logger.info("Monitoring Multi-functional Switch B for 20 seconds...")
        await asyncio.sleep(20)

        # Unsubscribe from MFS B stream
        test_payload = {
            "unsubscribed_stream_id": "px4_mfs_b_raw"
        }
        message["payload"] = test_payload
        await self._unsubscribe_mfs_b_value_stream_handler(topic, message)
        
        logger.info("Multi-functional Switch B stream test completed")

    @http_action(method="POST", path="/test/verify-pos-yaw-directions")
    async def _test_verify_pos_yaw_directions_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for trajectory verification with the new command structure."""
        
        logger.info("Running trajectory verification test with new command structure")
        
        # Configure trajectory collection rate (optional - demonstrates the feature)
        self.set_trajectory_collection_rate(15.0)  # 15 Hz collection rate
        
        # First, simulate user subscribing to pose data (as they would on page load)
        # Create new message with proper command structure
        pose_subscribe_message = {
            "waitResponse": True,
            "messageId": f"test-pose-subscribe-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/subscribe_pose_value_stream",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "subscribed_stream_id": "real_time_pose",
                "data_rate_hz": 10.0
            }
        }
        await self._master_command_handler(topic, pose_subscribe_message)
        
        # Wait a moment for streaming to start
        await asyncio.sleep(2)
        
        # Now start verification (which will check that pose stream is active)
        verify_start_message = {
            "waitResponse": True,
            "messageId": f"test-verify-start-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/verify_pos_yaw_directions",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "start": True
            }
        }
        await self._master_command_handler(topic, verify_start_message)
        
        # Wait for 30 seconds to collect trajectory data
        logger.info("Collecting trajectory data for 30 seconds...")
        await asyncio.sleep(30)
        
        # Complete verification
        verify_complete_message = {
            "waitResponse": True,
            "messageId": f"test-verify-complete-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/verify_pos_yaw_directions_complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {}
        }
        await self._master_command_handler(topic, verify_complete_message)
        
        # Optionally unsubscribe from pose data (simulating user cleanup)
        pose_unsubscribe_message = {
            "waitResponse": True,
            "messageId": f"test-pose-unsubscribe-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/unsubscribe_pose_value_stream",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "unsubscribed_stream_id": "real_time_pose"
            }
        }
        await self._master_command_handler(topic, pose_unsubscribe_message)
        
        logger.info("Trajectory verification test completed")

    @http_action(method="POST", path="/test/connect-to-wifi-and-verify-optitrack")
    async def _test_connect_to_wifi_and_verify_optitrack_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for WiFi and OptiTrack connectivity verification."""        
        logger.info("Running WiFi and OptiTrack connectivity verification test")
        
        # Create test message with proper command structure
        test_message = {
            "waitResponse": True,
            "messageId": f"test-wifi-optitrack-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/connect_to_wifi_and_verify_optitrack",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "positioning_system_network_wifi_ssid": "Rob-Lab-C00060",
                "positioning_system_network_wifi_pass": "kuri@1234!!",
                "positioning_system_network_wifi_subnet": "255.255.255.0",
                "positioning_system_network_server_ip_address": "10.0.0.27",
                "positioning_system_network_server_multicast_address": "239.255.42.99",
                "positioning_system_network_server_data_port": "1511"
            }
        }
        
        # Execute the WiFi OptiTrack connection test
        await self._master_command_handler(topic, test_message)
        logger.info("WiFi and OptiTrack connectivity test completed")

    @http_action(method="POST", path="/test/set-static-ip-address")
    async def _test_set_static_ip_address_handler(self, topic: str, message: Dict[str, Any]):
        """Test handler for static IP address configuration."""
        logger.info("Running static IP address configuration test")
        
        # Create test message with proper command structure
        test_message = {
            "waitResponse": True,
            "messageId": f"test-static-ip-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/set_static_ip_address",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "positioning_system_network_wifi_subnet": "255.255.255.0",
                "positioning_system_network_server_ip_address": "10.0.0.27"
            }
        }
        
        # Execute the static IP configuration test
        await self._master_command_handler(topic, test_message)
        logger.info("Static IP address configuration test completed")

    @http_action(method="POST", path="/test/unregister-all-handlers")
    async def _test_unregister_all_handlers(self, topic: str, message: Dict[str, Any]):
        """
        Test handler that subscribes to multiple streams and then tests unsubscribe all functionality.
        This demonstrates the complete workflow of subscription tracking and bulk unsubscribe.
        """
        logger.info("Running unsubscribe all functionality test")

        # List of streams to subscribe to for testing
        test_subscriptions = [
            {
                "command": f"{self.name}/subscribe_rc_value_stream",
                "stream_id": "px4_rc_raw",
                "data_rate_hz": 20.0
            },
            {
                "command": f"{self.name}/subscribe_pose_value_stream", 
                "stream_id": "real_time_pose",
                "data_rate_hz": 10.0
            },
        ]

        successful_subscriptions = []

        # Subscribe to all test streams using master command handler
        for subscription in test_subscriptions:
            try:
                logger.info(f"Subscribing to {subscription['stream_id']} at {subscription['data_rate_hz']} Hz")
                
                # Create subscription message with proper command structure
                subscribe_message = {
                    "waitResponse": True,
                    "messageId": f"test-subscribe-{subscription['stream_id']}-{datetime.now().timestamp()}",
                    "deviceId": message.get("deviceId", "test-device"),
                    "command": subscription["command"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {
                        "subscribed_stream_id": subscription["stream_id"],
                        "data_rate_hz": subscription["data_rate_hz"]
                    }
                }
                
                # Execute the subscription using master command handler
                await self._master_command_handler(topic, subscribe_message)
                successful_subscriptions.append(subscription)
                logger.info(f"Successfully subscribed to {subscription['stream_id']}")
                
            except Exception as e:
                logger.error(f"Failed to subscribe to {subscription['stream_id']}: {e}")

        # Wait a moment to let subscriptions establish
        logger.info("Waiting 3 seconds for subscriptions to establish...")
        await asyncio.sleep(3)

        # Check active subscriptions before unsubscribe all
        active_before = self.get_active_handlers()
        logger.info(f"Active subscriptions before unsubscribe all: {len(active_before)} streams")
        for stream_name, stream_info in active_before.items():
            logger.info(f"- {stream_name}: {stream_info.get('stream_id', 'unknown')}")

        # Now test the unsubscribe all functionality using master command handler
        logger.info("Testing unsubscribe all functionality...")
        unsubscribe_all_message = {
            "waitResponse": True,
            "messageId": f"test-unsubscribe-all-{datetime.now().timestamp()}",
            "deviceId": message.get("deviceId", "test-device"),
            "command": f"{self.name}/unsubscribeall",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {}
        }
        
        # Execute the unsubscribe all using master command handler
        await self._master_command_handler(topic, unsubscribe_all_message)

        # Wait a moment for unsubscribe operations to complete
        await asyncio.sleep(2)

        # Check active subscriptions after unsubscribe all
        active_after = self.get_active_handlers()
        logger.info(f"Active subscriptions after unsubscribe all: {len(active_after)} streams")

        # Prepare and log test results
        test_results = {
            "attempted_subscriptions": len(test_subscriptions),
            "successful_subscriptions": len(successful_subscriptions),
            "active_before_unsubscribe": len(active_before),
            "active_after_unsubscribe": len(active_after),
            "test_passed": len(active_after) == 0
        }

        logger.info("Unsubscribe all test completed:")
        logger.info(f"- Attempted subscriptions: {test_results['attempted_subscriptions']}")
        logger.info(f"- Successful subscriptions: {test_results['successful_subscriptions']}")
        logger.info(f"- Active before unsubscribe: {test_results['active_before_unsubscribe']}")
        logger.info(f"- Active after unsubscribe: {test_results['active_after_unsubscribe']}")
        logger.info(f"- Test passed: {test_results['test_passed']}")

        # Send response if requested (following the pattern of other test handlers)
        if message.get("waitResponse", False):
            try:
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get("messageId", "unknown"),
                    response_data={
                        "status": "success" if test_results['test_passed'] else "warning",
                        "message": f"Unsubscribe all test {'passed' if test_results['test_passed'] else 'had issues'} - {test_results['successful_subscriptions']} subscriptions created, {test_results['active_after_unsubscribe']} remaining after unsubscribe all",
                        "test_results": test_results,
                        "active_streams_before": list(active_before.keys()),
                        "active_streams_after": list(active_after.keys()),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send test response: {e}")

        logger.info("Unsubscribe all functionality test completed")

    async def _verify_pos_yaw_directions_handler(self, topic: str, message: Dict[str, Any]):
        """Handle trajectory verification start."""
        try:
            # Validate and parse payload
            mqtt_msg = MQTTMessage(**message)
            verify_payload = VerifyPosYawDirectionsPayload(**mqtt_msg.payload)
            
            if verify_payload.start:
                # Check if controllers are initialized and pose controller is available
                if self._pubsub_controllers is None:
                    error_msg = "Petal not fully initialized yet, controllers not available"
                    logger.warning(error_msg)
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": error_msg}
                        )
                    return
                    
                pose_controller = self._pubsub_controllers.get("pose_value_stream")
                if not pose_controller:
                    error_msg = "Pose controller not found"
                    logger.error(error_msg)
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": error_msg, "error_code": "CONTROLLER_NOT_FOUND"}
                        )
                    return
                
                if not pose_controller.is_active:
                    error_msg = "Pose controller is not streaming. Please subscribe to pose data first before starting verification."
                    logger.error(error_msg)
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": error_msg, "error_code": "STREAM_NOT_ACTIVE"}
                        )
                    return
                
                # Start verification process
                self._trajectory_verification.start_verification()
                
                # Create a background task to collect trajectory data from existing stream
                try:
                    asyncio.create_task(self._collect_trajectory_data())
                    logger.info("Started trajectory verification task successfully")
                except Exception as e:
                    logger.error(f"Failed to create trajectory verification task: {e}")
                    # Cleanup verification state on failure
                    self._trajectory_verification.stop_verification()
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": f"Failed to start trajectory verification: {e}"}
                        )
                    return
                
                logger.info("Started trajectory verification using existing pose data stream")
                
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={
                            "status": "success",
                            "message": "Trajectory verification started"
                        }
                    )
            
        except ValidationError as ve:
            error_msg = f"Invalid trajectory verification payload: {ve}"
            logger.error(error_msg)
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                )
        except Exception as e:
            error_msg = f"Trajectory verification handler error: {str(e)}"
            logger.error(error_msg)
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                )

    async def _verify_pos_yaw_directions_complete_handler(self, topic: str, message: Dict[str, Any]):
        """Handle trajectory verification completion."""
        try:
            # Validate and parse payload  
            mqtt_msg = MQTTMessage(**message)
            
            # Finish verification and get results (the trajectory data collection will stop automatically)
            results = await self._trajectory_verification.finish_verification(
                generate_plot=Config.PetalUserJourneyCoordinatorConfig.DEBUG_SQUARE_TEST,
                plot_filename="trajectory_verification_plot.png"
            )

            # dump trajectory_points to a json file for debugging
            with open("trajectory_points_debug.json", "w") as f:
                json.dump(self._trajectory_verification.trajectory_points, f, indent=4)

            logger.info(f"Trajectory verification completed: {results['was_successful']}")
            
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success",
                        "message": "Trajectory verification completed",
                        "verification_results": results
                    }
                )
                
        except Exception as e:
            error_msg = f"Trajectory verification completion handler error: {str(e)}"
            logger.error(error_msg)
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                )

    async def _collect_trajectory_data(self):
        """Background task to collect trajectory data from pose stream."""
        try:
            # Check if controllers are initialized
            if self._pubsub_controllers is None:
                logger.warning("Controllers not initialized yet, cannot collect trajectory data")
                return
                
            # Determine collection rate
            pose_controller: PositionChannelsController = self._pubsub_controllers.get("pose_value_stream")
            if self.trajectory_collection_rate_hz is not None:
                # Use configured collection rate
                collection_rate_hz = self.trajectory_collection_rate_hz
                logger.info(f"Using configured trajectory collection rate: {collection_rate_hz} Hz")
            elif pose_controller and hasattr(pose_controller, 'publish_rate_hz'):
                # Match pose controller's publish rate
                collection_rate_hz = pose_controller.publish_rate_hz
                logger.info(f"Matching pose controller rate for trajectory collection: {collection_rate_hz} Hz")
            else:
                # Fallback to 10 Hz if rate cannot be determined
                collection_rate_hz = 10.0
                logger.warning("Could not determine pose controller rate, using fallback 10 Hz for trajectory collection")
            
            pose_controller.reset_reference_position()

            collection_interval = 1.0 / collection_rate_hz
            
            while self._trajectory_verification.is_active:
                # Get pose controller
                if pose_controller and hasattr(pose_controller, '_get_sample_data'):
                    sample_data = pose_controller._get_sample_data()
                    
                    if sample_data and 'x' in sample_data and 'y' in sample_data and 'yaw' in sample_data:
                        self._trajectory_verification.add_trajectory_point(
                            sample_data['x'],
                            sample_data['y'], 
                            sample_data['yaw']
                        )
                
                await asyncio.sleep(collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Trajectory data collection cancelled")
        except Exception as e:
            logger.error(f"Error in trajectory data collection: {e}")

    async def _connect_to_wifi_and_verify_optitrack_handler(self, topic: str, message: Dict[str, Any]):
        """
        Handle WiFi connection and OptiTrack verification MQTT messages.
        
        This handler processes requests to:
        1. Connect to a specific WiFi network
        2. Verify the assigned IP is in the expected subnet
        3. Test connectivity to the OptiTrack server
        4. Send response with status and assigned IP
        """
        try:
            # Validate and parse message
            mqtt_msg = MQTTMessage(**message)
            logger.info(f"[{mqtt_msg.messageId}] Received WiFi OptiTrack connection request")
            
            # Process the connection request using the controller
            result = await self._wifi_optitrack_controller.connect_and_verify(
                payload=mqtt_msg.payload,
                message_id=mqtt_msg.messageId
            )
            
            # Send command response if requested
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success" if result["was_successful"] else "error",
                        "message": result["status_message"],
                        "assigned_ip_address": result.get("assigned_ip_address", ""),
                        "connection_details": {
                            "was_successful": result["was_successful"],
                            "status_message": result["status_message"],
                            "assigned_ip_address": result.get("assigned_ip_address", "")
                        }
                    }
                )
                
        except ValidationError as ve:
            error_msg = f"WiFi OptiTrack validation error: {str(ve)}"
            logger.error(f"[{message.get('messageId', 'unknown')}] {error_msg}")
            if message.get('waitResponse', False):
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get('messageId', 'unknown'),
                    response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                )
        except Exception as e:
            error_msg = f"WiFi OptiTrack handler error: {str(e)}"
            logger.error(f"[{message.get('messageId', 'unknown')}] {error_msg}")
            if message.get('waitResponse', False):
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get('messageId', 'unknown'),
                    response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                )

    async def _set_static_ip_address_handler(self, topic: str, message: Dict[str, Any]):
        """
        Handle static IP address configuration MQTT messages.
        
        This handler processes requests to set a static IP address within the
        OptiTrack network subnet, ensuring the current IP is within the expected
        gateway network.
        """
        try:
            # Validate and parse message
            mqtt_msg = MQTTMessage(**message)
            logger.info(f"[{mqtt_msg.messageId}] Received static IP address configuration request")
            
            # Process the static IP configuration request using the controller
            result = await self._wifi_optitrack_controller.set_static_ip_address(
                payload=mqtt_msg.payload,
                message_id=mqtt_msg.messageId
            )
            
            # Send command response if requested
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success" if result["was_successful"] else "error",
                        "message": "Static IP configuration completed",
                        "assigned_static_ip": result.get("assigned_static_ip", ""),
                        "static_ip_details": {
                            "assigned_static_ip": result.get("assigned_static_ip", ""),
                            "was_successful": result["was_successful"]
                        }
                    }
                )
                
        except ValidationError as ve:
            error_msg = f"Static IP validation error: {str(ve)}"
            logger.error(f"[{message.get('messageId', 'unknown')}] {error_msg}")
            if message.get('waitResponse', False):
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get('messageId', 'unknown'),
                    response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                )
        except Exception as e:
            error_msg = f"Static IP handler error: {str(e)}"
            logger.error(f"[{message.get('messageId', 'unknown')}] {error_msg}")
            if message.get('waitResponse', False):
                await self._mqtt_proxy.send_command_response(
                    message_id=message.get('messageId', 'unknown'),
                    response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                )

    async def _esc_calibration_message_handler(self, topic: str, message: Dict[str, Any]):
        """
        Handle ESC calibration MQTT messages.
        
        Workflow:
        1. Send is_calibration_started=false to initialize ESC calibration system
        2. Send is_calibration_started=true with throttle="maximum" to start motor commands
        3. Send is_calibration_started=true with throttle="minimum" to switch to minimum throttle
        4. Send force_cancel_calibration=true to emergency stop
        
        This design prevents deadlocks by using minimal lock scope and moving async operations outside locks.
        """
        mqtt_msg = None
        try:
            # Validate and parse payload
            mqtt_msg = MQTTMessage(**message)
            calibration_payload = ESCCalibrationPayload(**mqtt_msg.payload)
            
            # Get controller reference and current state (minimal lock scope)
            with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                controller = self._operation_controllers[OperationMode.ESC_CALIBRATION]
                
                # Safety check: clear active controller reference if controller is no longer active
                if self._active_controllers[OperationMode.ESC_CALIBRATION] == controller and not controller.is_active:
                    self._active_controllers[OperationMode.ESC_CALIBRATION] = None
                    logger.info("Cleared stale active controller reference (controller became inactive)")
                
                # Capture current state for decision making
                controller_is_active = controller.is_active
                active_controller = self._active_controllers[OperationMode.ESC_CALIBRATION]
                current_calibration_state = controller.calibration_state if hasattr(controller, 'calibration_state') else "idle"
            
                # Update timeout if provided
                controller.refresh_timeout(calibration_payload.safety_timeout_s)

            # Handle force cancel (outside lock)
            if calibration_payload.force_cancel_calibration:
                # Set the controller to inactive first (minimal lock)
                with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                    self._active_controllers[OperationMode.ESC_CALIBRATION] = None
                
                try:
                    await controller.emergency_stop(controller.get_operation_targets())
                    logger.info("Emergency stop completed for ESC calibration")
                except asyncio.TimeoutError:
                    logger.warning("ESC calibration emergency stop timed out")
                except Exception as e:
                    logger.error(f"Error during ESC calibration emergency stop: {e}")
                
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "success", "message": "ESC calibration cancelled"}
                    )
                return
            
            # Handle stop calibration (is_calibration_started=false when already active)
            if calibration_payload.safe_stop_calibration and controller_is_active:
                if active_controller == controller:
                    try:
                        await controller.stop_operation()
                        logger.info("Stopped ESC calibration")
                    except asyncio.TimeoutError:
                        logger.warning("ESC calibration stop operation timed out")
                    except Exception as e:
                        logger.error(f"Error stopping ESC calibration: {e}")
                    finally:
                        with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                            self._active_controllers[OperationMode.ESC_CALIBRATION] = None
            
            # Handle case where user tries to stop but calibration not active
            elif calibration_payload.safe_stop_calibration and not controller_is_active:
                logger.info("ESC calibration is not active, nothing to stop")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "success", "message": "ESC calibration is not active"}
                    )
                return

            # Handle workflow: is_calibration_started=false means initialize/setup
            if not calibration_payload.is_calibration_started and not controller_is_active:
                # Stop any active controller if it's different (outside lock)
                if active_controller is not None and active_controller != controller:
                    logger.warning("Another operation is already active, stopping it first")
                    try:
                        await active_controller.stop_operation()
                    except asyncio.TimeoutError:
                        logger.warning("Active controller stop operation timed out")
                    except Exception as e:
                        logger.error(f"Error stopping active controller: {e}")
                
                # Set as active controller and start operation (minimal lock for state change)
                with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                    self._active_controllers[OperationMode.ESC_CALIBRATION] = controller
                
                try:
                    await controller.start_operation(calibration_payload)
                    # calibration state set to "configured"
                    logger.info("Started ESC calibration task (initialization phase)")
                except asyncio.TimeoutError:
                    logger.error("ESC calibration start operation timed out")
                    with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                        self._active_controllers[OperationMode.ESC_CALIBRATION] = None
                except Exception as e:
                    logger.error(f"Error starting ESC calibration: {e}")
                    with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                        self._active_controllers[OperationMode.ESC_CALIBRATION] = None
            
            # Handle throttle state updates (is_calibration_started=true with active controller)
            elif calibration_payload.is_calibration_started and controller_is_active:
                # Update the throttle state - the running task will pick this up
                with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                    if calibration_payload.throttle:
                        if calibration_payload.throttle == "maximum":
                            controller.calibration_state = "maximum"
                            logger.info("Updated calibration state to MAXIMUM throttle")
                        elif calibration_payload.throttle == "minimum":
                            controller.calibration_state = "minimum"
                            logger.info("Updated calibration state to MINIMUM throttle")
            
            # Handle case where user sends is_calibration_started=true but controller not active
            elif calibration_payload.is_calibration_started and not controller_is_active:
                logger.warning("Received throttle command but ESC calibration not initialized. Send is_calibration_started=false first to initialize.")

            # Send response with current state
            if mqtt_msg.waitResponse:
                with self._controller_locks[OperationMode.ESC_CALIBRATION]:
                    current_state = controller.calibration_state if hasattr(controller, 'calibration_state') else "idle"
                    is_active = controller.is_active
                
                status_message = f"ESC calibration state: {current_state if is_active else 'stopped'}"
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success", 
                        "message": status_message,
                        "calibration_state": current_state,
                        "is_active": is_active
                    }
                )

        except Exception as e:
            logger.error(f"Error handling ESC calibration message: {e}")
            if mqtt_msg and mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": str(e)}
                )

    async def _esc_force_run_all_message_handler(self, topic: str, message: Dict[str, Any]):
        """Handle ESC force run all MQTT messages (stateful, idempotent)."""
        mqtt_msg = None
        try:
            mqtt_msg = MQTTMessage(**message)
            force_run_payload = ESCForceRunAllPayload(**mqtt_msg.payload)

            # Get controller reference and current state (minimal lock scope)
            with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                controller: ESCForceRunAllController = self._operation_controllers[OperationMode.ESC_FORCE_RUN_ALL]

                # Safety check: clear active controller reference if controller is no longer active
                if self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] == controller and not controller.is_active:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] = None
                    logger.info("Cleared stale active controller reference (ESC force run all became inactive)")

                # Capture current state for decision making
                controller_is_active = controller.is_active
                active_controller = self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL]

            # Emergency stop (outside lock)
            if force_run_payload.force_cancel:
                # Set the controller to inactive first (minimal lock)
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] = None

                try:
                    await controller.emergency_stop(controller.get_operation_targets())
                    logger.info("Emergency stop completed for ESC force run all")
                except asyncio.TimeoutError:
                    logger.warning("ESC force run all emergency stop timed out")
                except Exception as e:
                    logger.error(f"Error during ESC force run all emergency stop: {e}")
                
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "success", "message": "ESC force run all cancelled"}
                    )
                return

            # Start operation if not already active (outside lock)
            if not controller_is_active:
                if active_controller is not None:
                    logger.warning("Another operation is already active, stopping it first")
                    try:
                        await active_controller.stop_operation()
                    except asyncio.TimeoutError:
                        logger.warning("Active controller stop operation timed out")
                    except Exception as e:
                        logger.error(f"Error stopping active controller: {e}")
                
                # Set as active controller (minimal lock)
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] = controller
                
                try:
                    await controller.start_operation(force_run_payload)
                    logger.info("Started ESC force run all task")
                except asyncio.TimeoutError:
                    logger.error("ESC force run all start operation timed out")
                    with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                        self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] = None
                except Exception as e:
                    logger.error(f"Error starting ESC force run all: {e}")
                    with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                        self._active_controllers[OperationMode.ESC_FORCE_RUN_ALL] = None
            else:
                # Update command/state for running task
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                    controller.current_command_value = force_run_payload.motors_common_command
                
                controller.refresh_timeout(force_run_payload.safety_timeout_s)
                logger.info(f"Updated ESC force run all command to {force_run_payload.motors_common_command}")

            # Send response with current state
            if mqtt_msg.waitResponse:
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_ALL]:
                    is_active = controller.is_active
                    current_command = getattr(controller, 'current_command_value', None)
                
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success",
                        "message": f"ESC force run all state: {'active' if is_active else 'stopped'}",
                        "is_active": is_active,
                        "current_command_value": current_command
                    }
                )

        except Exception as e:
            logger.error(f"Error handling ESC force run all message: {e}")
            if mqtt_msg and mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": str(e)}
                )

    async def _esc_force_run_single_message_handler(self, topic: str, message: Dict[str, Any]):
        """Handle ESC force run single MQTT messages (stateful, idempotent)."""
        mqtt_msg = None
        try:
            mqtt_msg = MQTTMessage(**message)
            force_run_payload = ESCForceRunSinglePayload(**mqtt_msg.payload)

            # Get controller reference and current state (minimal lock scope)
            with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                controller: ESCForceRunSingleController = self._operation_controllers[OperationMode.ESC_FORCE_RUN_SINGLE]

                # Safety check: clear active controller reference if controller is no longer active
                if self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] == controller and not controller.is_active:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] = None
                    logger.info("Cleared stale active controller reference (ESC force run single became inactive)")

                # Capture current state for decision making
                controller_is_active = controller.is_active
                active_controller = self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE]

            # Emergency stop (outside lock)
            if force_run_payload.force_cancel:
                # Set the controller to inactive first (minimal lock)
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] = None

                try:
                    await controller.emergency_stop(controller.get_operation_targets())
                    logger.info("Emergency stop completed for ESC force run single")
                except asyncio.TimeoutError:
                    logger.warning("ESC force run single emergency stop timed out")
                except Exception as e:
                    logger.error(f"Error during ESC force run single emergency stop: {e}")
                
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "success", "message": "ESC force run single cancelled"}
                    )
                return

            # Start operation if not already active (outside lock)
            if not controller_is_active:
                if active_controller is not None:
                    logger.warning("Another operation is already active, stopping it first")
                    try:
                        await active_controller.stop_operation()
                    except asyncio.TimeoutError:
                        logger.warning("Active controller stop operation timed out")
                    except Exception as e:
                        logger.error(f"Error stopping active controller: {e}")
                
                # Set as active controller (minimal lock)
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                    self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] = controller
                
                try:
                    await controller.start_operation(force_run_payload)
                    logger.info("Started ESC force run single task")
                except asyncio.TimeoutError:
                    logger.error("ESC force run single start operation timed out")
                    with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                        self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] = None
                except Exception as e:
                    logger.error(f"Error starting ESC force run single: {e}")
                    with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                        self._active_controllers[OperationMode.ESC_FORCE_RUN_SINGLE] = None
            else:
                # Update command/state for running task
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                    controller.current_command_value = force_run_payload.motor_command
                    controller.target_motor = force_run_payload.motor_idx

                controller.refresh_timeout(force_run_payload.safety_timeout_s)
                logger.info(f"Updated ESC force run single command to {force_run_payload.motor_command} for motor {force_run_payload.motor_idx}")

            # Send response with current state
            if mqtt_msg.waitResponse:
                with self._controller_locks[OperationMode.ESC_FORCE_RUN_SINGLE]:
                    is_active = controller.is_active
                    current_command = getattr(controller, 'current_command_value', None)
                    target_motor = getattr(controller, 'target_motor', None)
                
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={
                        "status": "success",
                        "message": f"ESC force run single state: {'active' if is_active else 'stopped'}",
                        "is_active": is_active,
                        "current_command_value": current_command,
                        "target_motor": target_motor
                    }
                )

        except Exception as e:
            logger.error(f"Error handling ESC force run single message: {e}")
            if mqtt_msg and mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": str(e)}
                )

    @http_action(method="POST", path="/mqtt/bulk_set_parameters")
    async def _bulk_set_parameter_message_handler(self, topic: str, message: Dict[str, Any]):
        """
        Handle bulk set parameter MQTT messages.
        
        This handler processes requests to set multiple parameters in bulk,
        ensuring no active operations are in progress before applying changes.
        """
        try:
            # Parse base MQTT message
            mqtt_msg = MQTTMessage(**message)
            message_id = mqtt_msg.messageId
            
            # Check if controller is in emergency mode
            for controller in self._active_controllers.values():
                if controller is not None and controller.is_active:
                    error_msg = "Bulk parameter configuration blocked - Active operation in progress"
                    logger.warning(f"[{message_id}] {error_msg}")
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=message_id,
                            response_data={
                                "status": "error",
                                "message": error_msg,
                                "error_code": "OPERATION_ACTIVE"
                            }
                        )
                    return
            
            # Process payload using the mavlink proxy bulk set parameter helper
            payload = BulkParameterSetRequest(**mqtt_msg.payload)
            parameters = payload.parameters

            if not parameters:
                error_msg = "No parameters provided for bulk set"
                logger.error(f"[{message_id}] {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "NO_PARAMETERS_PROVIDED"
                        }
                    )
                return
            
            logger.info(f"Setting bulk PX4 parameters for {self.name}")

            results = {}
            set_param_dict = {}
            for parameter in parameters:
                set_param_dict[parameter.parameter_name] = (
                    parameter.parameter_value, 
                    parameter.parameter_type
                )

            confirmed = await self._mavlink_proxy.set_params_bulk_lossy(
                set_param_dict,
                max_in_flight=6,
                resend_interval=0.8,
                max_retries=5,
                timeout_total=10.0,
            )

            if not confirmed:
                error_msg = "No parameters were confirmed after bulk set"
                logger.error(f"[{message_id}] {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "NO_PARAMETERS_CONFIRMED"
                        }
                    )
                return

            # check that all requested parameters were confirmed
            success = True
            for parameter in parameters:
                pname = parameter.parameter_name
                if pname in confirmed:
                    results[pname] = confirmed[pname]
                    # check that the set value matches the requested value
                    confirmed_value = results[pname].get("value")
                    if confirmed_value == parameter.parameter_value:
                        results[pname]["success"] = True
                    else:
                        results[pname]["success"] = False
                        results[pname]["error"] = f"Parameter value mismatch: requested {parameter.parameter_value}, got {confirmed_value}"
                        success = False
                else:
                    results[pname] = {
                        "name": pname,
                        "error": "Parameter value could not be retrieved after set",
                        "success": False
                    }
                    success = False

            payload = {
                "results": results,
                "success": success,
                # timestamp must be string
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            payload = BulkParameterResponse(**payload)
            sanitized_response = _json_safe(payload.model_dump())

            logger.info(f"[{message_id}] Successfully processed bulk parameter configuration")

            # Send response if requested
            if mqtt_msg.waitResponse:
                if not success:
                    logger.warning(f"[{message_id}] Some parameters could not be set successfully")
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": f"Bulk parameter set completed - some parameters failed",
                            "data": sanitized_response
                        }
                    )
                else:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "success",
                            "message": f"Bulk parameter set completed - {len(results)} parameters processed",
                            "data": sanitized_response
                        }
                    )
                    
        except ValidationError as ve:
            error_msg = f"Invalid bulk parameter payload: {ve}"
            logger.error(f"Bulk parameter config validation error: {error_msg}")
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "error",
                        "message": error_msg,
                        "error_code": "VALIDATION_ERROR"
                    }
                )
                
        except Exception as e:
            error_msg = f"Bulk parameter handler error: {str(e)}"
            logger.error(f"Unexpected bulk parameter error: {error_msg}")
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "error",
                        "message": error_msg,
                        "error_code": "HANDLER_ERROR"
                    }
                )

    @http_action(method="POST", path="/mqtt/bulk_get_parameters")
    async def _bulk_get_parameter_message_handler(self, topic: str, message: Dict[str, Any]):
        """
        Handle bulk get parameter MQTT messages.
        
        This handler processes requests to get multiple parameters in bulk,
        ensuring no active operations are in progress before retrieving values.
        """
        try:
            # Parse base MQTT message
            mqtt_msg = MQTTMessage(**message)
            message_id = mqtt_msg.messageId
            
            # Check if controller is in emergency mode
            for controller in self._active_controllers.values():
                if controller is not None and controller.is_active:
                    error_msg = "Bulk parameter retrieval blocked - Active operation in progress"
                    logger.warning(f"[{message_id}] {error_msg}")
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=message_id,
                            response_data={
                                "status": "error",
                                "message": error_msg,
                                "error_code": "OPERATION_ACTIVE"
                            }
                        )
                    return
            
            # Process payload using the mavlink proxy bulk get parameter helper
            payload = BulkParameterGetRequest(**mqtt_msg.payload)
            parameter_names = payload.parameter_names

            if not parameter_names:
                error_msg = "No parameter names provided for bulk get"
                logger.error(f"[{message_id}] {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "NO_PARAMETER_NAMES_PROVIDED"
                        }
                    )
                return

            logger.info(f"Getting bulk PX4 parameters for {self.name}")

            parameters = await self._mavlink_proxy.get_params_bulk_lossy(
                names=parameter_names,
                max_in_flight=6,
                resend_interval=0.8,
                max_retries=5,
                timeout_total=10.0,
                inter_send_delay=0.05,
            )

            if not parameters:
                error_msg = "No parameters were confirmed after bulk get"
                logger.error(f"[{message_id}] {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "NO_PARAMETERS_CONFIRMED"
                        }
                    )

            success = True
            for parameter in parameter_names:
                if parameter not in parameters:
                    parameters[parameter] = {
                        "name": parameter,
                        "error": "Parameter value could not be retrieved",
                        "success": False
                    }
                    success = False
                else:
                    parameters[parameter]["success"] = True

            payload = {
                "results": parameters,
                "success": success,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            payload = BulkParameterResponse(**payload)
            sanitized_response = _json_safe(payload.model_dump())

            logger.info(f"[{message_id}] Successfully processed bulk parameter retrieval")

            # Send response if requested
            if mqtt_msg.waitResponse:
                if not success:
                    logger.warning(f"[{message_id}] Some parameters could not be retrieved successfully")
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": f"Bulk parameter get completed - some parameters failed",
                            "data": sanitized_response
                        }
                    )
                else:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "success",
                            "message": f"Bulk parameter get completed - {len(parameters)} parameters processed",
                            "data": sanitized_response
                        }
                    )
        
        except ValidationError as ve:
            error_msg = f"Invalid bulk parameter get payload: {ve}"
            logger.error(f"Bulk parameter get validation error: {error_msg}")
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "error",
                        "message": error_msg,
                        "error_code": "VALIDATION_ERROR"
                    }
                )

        except Exception as e:
            error_msg = f"Bulk parameter get handler error: {str(e)}"
            logger.error(f"Unexpected bulk parameter get error: {error_msg}")
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "error",
                        "message": error_msg,
                        "error_code": "HANDLER_ERROR"
                    }
                )

    @http_action(method="POST", path="/mqtt/reboot_px4")
    async def _reboot_px4_message_handler(self, topic: str, message: Dict[str, Any]):
        """Handle reboot PX4 MQTT messages."""
        try:
            # Parse base MQTT message
            mqtt_msg = MQTTMessage(**message)
            message_id = mqtt_msg.messageId

            # Check if controller is in emergency mode
            for controller in self._active_controllers.values():
                if controller is not None and controller.is_active:
                    error_msg = "PX4 reboot blocked - Active operation in progress"
                    logger.warning(f"[{message_id}] {error_msg}")
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=message_id,
                            response_data={
                                "status": "error",
                                "message": error_msg,
                                "error_code": "OPERATION_ACTIVE"
                            }
                        )

                    return
                
            logger.info(f"Restarting PX4 for {self.name} petal")
            reboot_response = await self._mavlink_proxy.reboot_autopilot(
                reboot_onboard_computer=False,
                timeout=5.0
            )

            if not reboot_response.success:
                error_msg = "PX4 reboot command failed or timed out"
                logger.error(f"[{message_id}] {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "REBOOT_FAILED",
                            "data": _json_safe(reboot_response.model_dump())
                        }
                    )
                return
            
            logger.info(f"[{message_id}] PX4 reboot command successful")

            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "success",
                        "message": "PX4 reboot command successful",
                        "data": _json_safe(reboot_response.model_dump())
                    }
                )
        except ValidationError as ve:
            error_msg = f"Invalid PX4 reboot payload: {ve}"
            logger.error(f"PX4 reboot validation error: {error_msg}")
            if mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data={
                        "status": "error",
                        "message": error_msg,
                        "error_code": "VALIDATION_ERROR"
                    }
                )
        except Exception as e:
            logger.error(f"Error handling PX4 reboot message: {e}")
            if mqtt_msg and mqtt_msg.waitResponse:
                await self._mqtt_proxy.send_command_response(
                    message_id=mqtt_msg.messageId,
                    response_data={"status": "error", "message": str(e)}
                )
                return

    def _create_parameter_message_handler(self, handler_key: str, config_type: str):
        """
        Factory method to create parameter message handlers with minimal boilerplate.
        
        Args:
            handler_key: Key for the parameter handler in self._parameter_handlers
            config_type: Human-readable configuration type for error messages
        
        Returns:
            Async function that handles the parameter configuration message
        """
        async def parameter_handler(topic: str, message: Dict[str, Any]):
            try:
                # Parse base MQTT message
                mqtt_msg = MQTTMessage(**message)
                message_id = mqtt_msg.messageId
                
                # Check if controller is in emergency mode
                for controller in self._active_controllers.values():
                    if controller is not None and controller.is_active:
                        error_msg = "Parameter configuration blocked - Active operation in progress"
                        logger.warning(f"[{message_id}] {error_msg}")
                        if mqtt_msg.waitResponse:
                            await self._mqtt_proxy.send_command_response(
                                message_id=message_id,
                                response_data={
                                    "status": "error",
                                    "message": error_msg,
                                    "error_code": "OPERATION_ACTIVE"
                                }
                            )
                        return
                

                # Process payload using the specified handler
                response_payload = await self._parameter_handlers[handler_key].process_payload(mqtt_msg.payload, message_id)
                
                logger.info(f"[{message_id}] Successfully processed {config_type} configuration")

                # Send response if requested
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data=response_payload
                    )
                        
            except ValidationError as ve:
                error_msg = f"Invalid {config_type} payload: {ve}"
                logger.error(f"Parameter config validation error: {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "VALIDATION_ERROR"
                        }
                    )
            except Exception as e:
                error_msg = f"{config_type.title()} handler error: {str(e)}"
                logger.error(f"Unexpected {config_type} error: {error_msg}")
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": error_msg,
                            "error_code": "HANDLER_ERROR"
                        }
                    )
        
        return parameter_handler

    async def _unregister_all_handlers(self, topic: str, message: Dict[str, Any]):
        """
        Handler for unsubscribe all command - stops all active PubSub streaming.
        
        Args:
            topic: MQTT topic that triggered this handler
            message: MQTT message containing command details
        """
        try:
            message_id = message.get("messageId", "unknown")
            wait_response = message.get("waitResponse", False)
            logger.info(f"[{message_id}] Processing unsubscribe all command")

            # Use the subscription management system to stop all streams
            result = await self.unsubscribe_all_streams()
            
            # Send response if requested
            if wait_response:
                success_count = result.get('stopped_count', 0)
                failed_count = result.get('failed_count', 0)
                total_count = success_count + failed_count
                
                status = "success" if failed_count == 0 else "partial_success" if success_count > 0 else "error"
                
                response_data = {
                    "status": status,
                    "message": f"Unsubscribe all completed - {success_count}/{total_count} streams stopped successfully",
                    "stopped_count": success_count,
                    "failed_count": failed_count,
                    "total_streams": total_count
                }
                
                if result.get('errors'):
                    response_data["errors"] = result['errors']
                
                await self._mqtt_proxy.send_command_response(
                    message_id=message_id,
                    response_data=response_data
                )
            
            logger.info(f"[{message_id}] Unsubscribe all completed - {result.get('stopped_count', 0)} streams stopped")

        except Exception as e:
            logger.error(f"Error in unsubscribe all handler: {e}")
            # Try to send error response if possible
            try:
                message_id = message.get("messageId", "unknown")
                wait_response = message.get("waitResponse", False)
                if wait_response:
                    await self._mqtt_proxy.send_command_response(
                        message_id=message_id,
                        response_data={
                            "status": "error",
                            "message": f"Unsubscribe all handler error: {str(e)}",
                            "error_code": "HANDLER_ERROR"
                        }
                    )
            except:
                pass  # If we can't send error response, just log it

    def _create_pubsub_message_handlers(self, controller_key: str, stream_name: str):
        """
        Factory method to create subscribe and unsubscribe message handlers with minimal boilerplate.
        
        Args:
            controller_key: Key for the pub/sub controller in self._pubsub_controllers
            stream_name: Human-readable stream name for error messages
        
        Returns:
            Tuple of (subscribe_handler, unsubscribe_handler) functions
        """
        async def subscribe_handler(topic: str, message: Dict[str, Any]):
            try:
                # Check if controllers are initialized
                if self._pubsub_controllers is None:
                    error_msg = "Petal not fully initialized yet, controllers not available"
                    logger.warning(error_msg)
                    return
                    
                # Parse MQTT message
                mqtt_msg = MQTTMessage(**message)
                subscribe_payload = SubscribePayload(**mqtt_msg.payload)
                
                controller = self._pubsub_controllers.get(controller_key)
                if not controller:
                    error_msg = f"{stream_name} controller not found"
                    logger.error(error_msg)
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": error_msg, "error_code": "CONTROLLER_NOT_FOUND"}
                        )
                    return
                
                # Start streaming
                await controller.start_streaming(
                    subscribe_payload.subscribed_stream_id,
                    subscribe_payload.data_rate_hz
                )
                
                # Track the subscription
                self._track_subscription(controller_key, subscribe_payload.subscribed_stream_id, subscribe_payload.data_rate_hz)
                
                # Send response if requested
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={
                            "status": "success",
                            "message": f"Started streaming {subscribe_payload.subscribed_stream_id} at {subscribe_payload.data_rate_hz} Hz"
                        }
                    )
                    
            except ValidationError as ve:
                error_msg = f"Invalid {stream_name} subscribe payload: {ve}"
                logger.error(error_msg)
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                    )
            except Exception as e:
                error_msg = f"{stream_name} subscribe handler error: {str(e)}"
                logger.error(error_msg)
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                    )

        async def unsubscribe_handler(topic: str, message: Dict[str, Any]):
            try:
                # Check if controllers are initialized
                if self._pubsub_controllers is None:
                    error_msg = "Petal not fully initialized yet, controllers not available"
                    logger.warning(error_msg)
                    return
                    
                # Parse MQTT message
                mqtt_msg = MQTTMessage(**message)
                unsubscribe_payload = UnsubscribePayload(**mqtt_msg.payload)
                
                controller = self._pubsub_controllers.get(controller_key)
                if not controller:
                    error_msg = f"{stream_name} controller not found"
                    logger.error(error_msg)
                    if mqtt_msg.waitResponse:
                        await self._mqtt_proxy.send_command_response(
                            message_id=mqtt_msg.messageId,
                            response_data={"status": "error", "message": error_msg, "error_code": "CONTROLLER_NOT_FOUND"}
                        )
                    return
                
                # Stop streaming
                await controller.stop_streaming()
                
                # Untrack the subscription
                self._untrack_subscription(controller_key)
                
                # Send response if requested
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={
                            "status": "success",
                            "message": f"Stopped streaming {unsubscribe_payload.unsubscribed_stream_id}"
                        }
                    )
                    
            except ValidationError as ve:
                error_msg = f"Invalid {stream_name} unsubscribe payload: {ve}"
                logger.error(error_msg)
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "error", "message": error_msg, "error_code": "VALIDATION_ERROR"}
                    )
            except Exception as e:
                error_msg = f"{stream_name} unsubscribe handler error: {str(e)}"
                logger.error(error_msg)
                if mqtt_msg.waitResponse:
                    await self._mqtt_proxy.send_command_response(
                        message_id=mqtt_msg.messageId,
                        response_data={"status": "error", "message": error_msg, "error_code": "HANDLER_ERROR"}
                    )
        
        return subscribe_handler, unsubscribe_handler

    async def async_shutdown(self) -> None:
        """Called when the petal is stopped, in async context."""
        # Await shutdown of all active controllers
        for mode, controller in self._active_controllers.items():
            with self._controller_locks[mode]:
                if controller is not None:
                    logger.info(f"Awaiting shutdown of active controller: {type(controller).__name__}")
                    try:
                        await controller.stop_operation()
                        logger.info(f"Controller {type(controller).__name__} shut down successfully")
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout while shutting down controller: {type(controller).__name__}")
                    except Exception as e:
                        logger.error(f"Error during shutdown of controller {type(controller).__name__}: {e}")
                    finally:
                        self._active_controllers[mode] = None

        # Cleanup all controllers
        for operation_mode, controller in self._operation_controllers.items():
            if hasattr(controller, 'stop_operation'):
                try:
                    await controller.stop_operation()
                    logger.info(f"Cleaned up {operation_mode.value} controller")
                except Exception as e:
                    logger.error(f"Error cleaning up {operation_mode.value} controller: {e}")
        
        # Clean up pub/sub controllers if they were initialized
        if self._pubsub_controllers is not None:
            for stream_name, controller in self._pubsub_controllers.items():
                if hasattr(controller, 'stop_streaming'):
                    try:
                        await controller.stop_streaming()
                        logger.info(f"Cleaned up {stream_name} controller")
                    except Exception as e:
                        logger.error(f"Error cleaning up {stream_name} controller: {e}")
        
        logger.info(f"All controllers cleaned up for {self.name} petal")

    def shutdown(self) -> None:
        """Called when the petal is stopped."""
        # Stop all active controllers
        for mode, controller in self._active_controllers.items():
            with self._controller_locks[mode]:
                if controller is not None:
                    # Mark controller as inactive but don't wait for async operations in sync context
                    logger.info(f"Shutting down active controller: {type(controller).__name__}")
                    self._active_controllers[mode] = None

        # Clear all controllers - actual cleanup will happen during async_shutdown if available
        for operation_mode, controller in self._operation_controllers.items():
            logger.info(f"Marking {operation_mode.value} controller for shutdown")
        
        # Clear pub/sub controllers if they were initialized
        if self._pubsub_controllers is not None:
            for stream_name, controller in self._pubsub_controllers.items():
                logger.info(f"Marking {stream_name} controller for shutdown")
        
        super().shutdown()
        self._status_message = "Petal is shutting down"
        logger.info(f"{self.name} petal shut down")
    
    def get_required_proxies(self) -> List[str]:
        """
        Return a list of proxy names that this petal requires.
        
        Override this method to specify which proxies your petal needs.
        Available proxies: 'redis', 'db', 'ext_mavlink'
        """
        
        return ["ext_mavlink", "mqtt"]  # Modify this list based on your petal's needs
    
    def get_optional_proxies(self) -> List[str]:
        """
        Return a list of proxy names that this petal can optionally use.
        
        Override this method to specify which proxies your petal can use
        but doesn't strictly require.
        """
        return []  # Modify this list based on your petal's needs
    
    def get_petal_status(self) -> Dict[str, Any]:
        """
        Return custom status information for this petal.
        
        Override this method to provide specific status information
        about your petal's internal state.
        """
        status = {
            "message": self._status_message,
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "uptime_seconds": (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
        }
        
        # Add any custom status information here
        # For example:
        # status["custom_metric"] = self._some_internal_counter
        # status["last_operation"] = self._last_operation_time
        
        return status
    
    @http_action(method="GET", path="/health")
    async def health_check(self):
        """
        Health check endpoint that reports proxy requirements and petal status.
        
        This endpoint provides information about:
        - Required and optional proxies
        - Custom petal status information
        """
        health_info = {
            "petal_name": self.name,
            "petal_version": self.version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "required_proxies": self.get_required_proxies(),
            "optional_proxies": self.get_optional_proxies(),
            "petal_status": self.get_petal_status()
        }
        
        return health_info
    
    @http_action(method="GET", path="/px4-parameter")
    async def get_px4_parameter(self, data: ParameterRequestModel) -> MavlinkParameterResponseModel:
        """
        Get a specific PX4 parameter value.
        """
        parameter_name = data.parameter_name
        logger.info(f"Getting PX4 parameter '{parameter_name}' for {self.name}")
        # Implement your logic to retrieve the PX4 parameter value here

        try:

            parameter_value = await self._mavlink_proxy.get_param(parameter_name)

            if not parameter_value:
                logger.error("No value found for PX4 parameter")
                raise HTTPException(
                    status_code=404,
                    detail="No value found",
                    headers={"source": "px4_parameter"}
                )
            return {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 parameter: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))
    
    @http_action(method="GET", path="/px4-parameters")
    async def get_all_parameters(self) -> MavlinkParametersResponseModel:
        """
        Get a specific PX4 parameter value.
        """
        logger.info(f"Getting PX4 parameters for {self.name}")
        # Implement your logic to retrieve the PX4 parameter value here

        try:

            parameters = await self._mavlink_proxy.get_all_params()

            if not parameters:
                logger.error("No value found for PX4 parameter")
                raise HTTPException(
                    status_code=404,
                    detail="No value found",
                    headers={"source": "px4_parameter"}
                )
            payload = {
                "parameters": parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return _json_safe(payload)   # ← sanitize before FastAPI encodes
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 parameter: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))
        
    @http_action(method="POST", path="/px4-parameter")
    async def set_px4_parameter(self, data: ParameterBaseModel) -> ParameterResponseModel:
        """
        Get a specific PX4 parameter value.
        """

        parameter_name = data.parameter_name
        parameter_value = data.parameter_value

        if parameter_name is None or parameter_value is None:
            logger.error("Missing parameter_name or parameter_value")
            raise HTTPException(
                status_code=400,
                detail="Missing parameter_name or parameter_value",
                headers={"source": "px4_parameter"}
            )

        logger.info(f"Setting PX4 parameter '{parameter_name}' to {parameter_value} for {self.name}")
        # Implement your logic to retrieve the PX4 parameter value here

        try:

            result = await self._mavlink_proxy.set_param(parameter_name, parameter_value) # same result as get_param()

            if not result:
                logger.error("No value found for PX4 parameter")
                raise HTTPException(
                    status_code=404,
                    detail="No value found",
                    headers={"source": "px4_parameter"}
                )
            payload = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return _json_safe(payload)   # ← sanitize before FastAPI encodes
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 parameter: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))

    @http_action(method="POST", path="/rotor-count")
    async def set_rotor_count(self, data: RotorCountParameter) -> ParameterResponseModel:
        """
        Get a specific PX4 parameter value.
        """

        parameter_name = "CA_ROTOR_COUNT"
        parameter_value = data.rotor_count

        if parameter_value is None:
            logger.error("Missing parameter_value")
            raise HTTPException(
                status_code=400,
                detail="Missing parameter_value",
                headers={"source": "px4_parameter"}
            )

        logger.info(f"Setting PX4 parameter '{parameter_name}' to {parameter_value} for {self.name}")
        # Implement your logic to retrieve the PX4 parameter value here

        try:
            result = await self._mavlink_proxy.set_param(
                name=parameter_name, 
                value=int(parameter_value),
                ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32
            ) # returns same result as get_param()

            if not result:
                logger.error("No value found for PX4 parameter")
                raise HTTPException(
                    status_code=404,
                    detail="No value found",
                    headers={"source": "px4_parameter"}
                )
            payload = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return _json_safe(payload)   # ← sanitize before FastAPI encodes
        except TimeoutError as exc:
            logger.error(f"Timeout while waiting for PX4 parameter: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))

    @http_action(method="POST", path="/bulk-px4-parameters")
    async def set_bulk_px4_parameters(self, data: BulkParameterSetRequest) -> BulkParameterResponse:
        """
        Set multiple PX4 parameters in bulk.
        """

        parameters = data.parameters

        if not parameters:
            logger.error("No parameters provided for bulk set")
            raise HTTPException(
                status_code=400,
                detail="No parameters provided",
                headers={"source": "bulk_px4_parameters"}
            )

        logger.info(f"Setting bulk PX4 parameters for {self.name}")

        results = {}
        try:
            set_param_dict = {}
            for parameter in parameters:
                set_param_dict[parameter.parameter_name] = (
                    parameter.parameter_value, 
                    parameter.parameter_type
                )

            confirmed = await self._mavlink_proxy.set_params_bulk_lossy(
                set_param_dict,
                max_in_flight=6,
                resend_interval=0.8,
                max_retries=5,
                timeout_total=10.0,
            )

            # confirmed[pname] = {
            #     "name": pname,
            #     "value": decoded_value,
            #     "raw": float(pkt.param_value),
            #     "type": pkt.param_type,
            #     "count": pkt.param_count,
            #     "index": pkt.param_index,
            # }

            if not confirmed:
                logger.error("No parameters were set in bulk PX4 parameter set")
                raise HTTPException(
                    status_code=500,
                    detail="No parameters were set",
                    headers={"source": "bulk_px4_parameters"}
                )

            # check that all requested parameters were confirmed
            success = True
            for parameter in parameters:
                pname = parameter.parameter_name
                if pname in confirmed:
                    results[pname] = confirmed[pname]
                    # check that the set value matches the requested value
                    confirmed_value = results[pname].get("value")
                    if confirmed_value == parameter.parameter_value:
                        results[pname]["success"] = True
                    else:
                        results[pname]["success"] = False
                        results[pname]["error"] = f"Parameter value mismatch: requested {parameter.parameter_value}, got {confirmed_value}"
                        success = False
                else:
                    results[pname] = {
                        "name": pname,
                        "error": "Parameter value could not be retrieved after set",
                        "success": False
                    }
                    success = False

            payload = {
                "results": results,
                "success": success,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            payload = BulkParameterResponse(**payload)
            return _json_safe(payload.model_dump())   # ← sanitize before FastAPI encodes

        except TimeoutError as exc:
            logger.error(f"Timeout while setting bulk PX4 parameters: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))
        except Exception as e:
            logger.error(f"Error while setting bulk PX4 parameters: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @http_action(method="GET", path="/bulk-px4-parameters")
    async def get_bulk_px4_parameters(self, data: BulkParameterGetRequest) -> BulkParameterResponse:
        """
        Get multiple PX4 parameters in bulk.
        """
        parameter_names = data.parameter_names

        if not parameter_names:
            logger.error("No parameter names provided for bulk get")
            raise HTTPException(
                status_code=400,
                detail="No parameter names provided",
                headers={"source": "bulk_px4_parameters"}
            )

        logger.info(f"Getting bulk PX4 parameters for {self.name}")

        try:

            parameters = await self._mavlink_proxy.get_params_bulk_lossy(
                names=parameter_names,
                timeout_total=6.0,
                max_retries=4,
                max_in_flight=6,
                resend_interval=0.8,
                inter_send_delay=0.02,
            )

            if not parameters:
                logger.error("No parameters were retrieved in bulk PX4 parameter get")
                raise HTTPException(
                    status_code=500,
                    detail="No parameters were retrieved",
                    headers={"source": "bulk_px4_parameters"}
                )
            
            success = True
            for parameter in parameter_names:
                if parameter not in parameters:
                    parameters[parameter] = {
                        "name": parameter,
                        "error": "Parameter value could not be retrieved",
                        "success": False
                    }
                    success = False
                else:
                    parameters[parameter]["success"] = True


            payload = {
                "success": success,
                "results": parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            parameters = BulkParameterResponse(**payload)
            return _json_safe(parameters.model_dump())   # ← sanitize before FastAPI encodes
        except TimeoutError as exc:
            logger.error(f"Timeout while getting bulk PX4 parameters: {str(exc)}")
            raise HTTPException(status_code=504, detail=str(exc))
            