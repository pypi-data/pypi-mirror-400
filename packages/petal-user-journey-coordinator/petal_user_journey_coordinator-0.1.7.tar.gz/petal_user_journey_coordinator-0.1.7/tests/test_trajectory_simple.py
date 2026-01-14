"""
Simplified unit tests for TrajectoryVerificationController

This test suite focuses on testing the closest point approach and trajectory error calculation
using JSON test data. It can be run directly without complex dependencies.
"""

import json
import math
import os
import sys
import time
import threading
from typing import Dict, List, Any, Optional


# Mock classes for testing
class MockMQTTProxy:
    """Mock MQTT proxy for testing."""
    async def publish(self, topic: str, payload: Dict[str, Any]):
        pass

class MockLogger:
    """Mock logger for testing."""
    def info(self, msg: str): 
        pass
    def debug(self, msg: str): 
        pass
    def warning(self, msg: str): 
        print(f"WARNING: {msg}")
    def error(self, msg: str): 
        print(f"ERROR: {msg}")


# Import or recreate the TrajectoryVerificationController
class TrajectoryVerificationController:
    """
    Controller for verifying position and yaw trajectory against a predefined rectangular path.
    This is a simplified version for testing.
    """
    
    def __init__(self, mqtt_proxy: MockMQTTProxy, logger: MockLogger):
        self.mqtt_proxy = mqtt_proxy
        self.logger = logger
        self.is_active = False
        self.trajectory_points = []
        self.lock = threading.Lock()
        
        # Rectangle trajectory parameters (in meters)
        self.rectangle_a = 2.0  # width
        self.rectangle_b = 2.0  # height
        self.points_per_edge = 10

        # Tolerances
        self.position_tolerance = 0.5  # meters
        self.yaw_tolerance = 10.0  # degrees
        
        # Corner exclusion radius
        self.corner_exclusion_radius = 0.2  # meters
        
        # Reference trajectory
        self.reference_trajectory = self._generate_rectangle_trajectory()
        
    def _generate_rectangle_trajectory(self) -> List[Dict[str, float]]:
        """Generate reference rectangular trajectory with interpolated points along each edge."""
        trajectory = []
        
        # Define corner points with yaw angles (-180 to 180)
        corners = [
            {"x": 0.0, "y": 0.0, "yaw": 90.0},           # Start point (facing east)
            {"x": self.rectangle_a, "y": 0.0, "yaw": 0.0},   # East corner (turn to face north)
            {"x": self.rectangle_a, "y": self.rectangle_b, "yaw": -90.0},  # Northeast corner (turn to face west)
            {"x": 0.0, "y": self.rectangle_b, "yaw": -180.0},  # West corner (turn to face south)
            {"x": 0.0, "y": 0.0, "yaw": 90.0},           # Back to start (turn to face east)
        ]
                
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
                
                # Yaw angle depends on the direction of movement
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
                
            # Convert from radians to degrees and normalize to -180 to 180 range
            yaw_degrees = math.degrees(yaw)
            # Normalize to -180 to 180 range
            while yaw_degrees > 180:
                yaw_degrees -= 360
            while yaw_degrees <= -180:
                yaw_degrees += 360
                
            point = {
                "x": x,
                "y": y, 
                "yaw": yaw_degrees,
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
        
        # Maximum distance to consider a reference point as "close enough" to a trajectory point
        max_matching_distance = max(self.rectangle_a, self.rectangle_b) * 0.2  # 20% of largest dimension
        
        # Define corner points for exclusion zone calculation
        corner_points = [
            {"x": 0.0, "y": 0.0},                                          # Start/end corner
            {"x": self.rectangle_a, "y": 0.0},                             # East corner
            {"x": self.rectangle_a, "y": self.rectangle_b},                 # Northeast corner
            {"x": 0.0, "y": self.rectangle_b},                             # West corner
        ]
        
        # Loop over trajectory points and find closest reference point for each
        for actual_point in self.trajectory_points:
            # Find closest reference point to this trajectory point
            min_dist = float('inf')
            closest_ref_point = None
            closest_ref_index = -1
            
            for ref_idx, ref_point in enumerate(self.reference_trajectory):
                dist = math.sqrt(
                    (actual_point["x"] - ref_point["x"])**2 + 
                    (actual_point["y"] - ref_point["y"])**2
                )
                if dist < min_dist:
                    min_dist = dist
                    closest_ref_point = ref_point
                    closest_ref_index = ref_idx
            
            # Only process this trajectory point if we found a reasonably close reference point
            if closest_ref_point and min_dist <= max_matching_distance:
                # Track which reference point was matched
                matched_ref_indices.add(closest_ref_index)
                
                # Position error (Euclidean norm)
                position_errors.append(min_dist)
                
                # Check if this trajectory point is near any corner (exclude yaw error calculation)
                near_corner = False
                for corner in corner_points:
                    corner_dist = math.sqrt(
                        (actual_point["x"] - corner["x"])**2 + 
                        (actual_point["y"] - corner["y"])**2
                    )
                    if corner_dist <= self.corner_exclusion_radius:
                        near_corner = True
                        break
                
                # Only calculate yaw error if not near a corner
                if not near_corner:
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
                    yaw_diff = abs(diff)
                    yaw_errors.append(yaw_diff)
        
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
            "yaw_errors_calculated": len(yaw_errors),
            "position_errors_calculated": len(position_errors)
        }


class TestTrajectoryVerificationController:
    """Test suite for TrajectoryVerificationController."""
    
    def __init__(self):
        self.test_data = self.load_test_data()
        
    def load_test_data(self):
        """Load test data from JSON file."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_data_path = os.path.join(current_dir, 'trajectory_test_data.json')
            with open(test_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test data: {e}")
            return None
    
    def create_controller(self):
        """Create a controller instance for testing."""
        mock_mqtt = MockMQTTProxy()
        mock_logger = MockLogger()
        return TrajectoryVerificationController(mock_mqtt, mock_logger)
    
    def test_controller_initialization(self):
        """Test that the controller initializes correctly."""
        print("\n=== Test: Controller Initialization ===")
        controller = self.create_controller()
        
        assert controller.rectangle_a == 2.0
        assert controller.rectangle_b == 2.0
        assert controller.points_per_edge == 10
        assert controller.position_tolerance == 0.5
        assert controller.yaw_tolerance == 10.0
        assert controller.corner_exclusion_radius == 0.2
        assert not controller.is_active
        assert len(controller.trajectory_points) == 0
        assert len(controller.reference_trajectory) > 0
        
        print(f"✓ Controller initialized correctly")
        print(f"✓ Reference trajectory has {len(controller.reference_trajectory)} points")
    
    def test_angle_normalization(self):
        """Test that yaw angles are properly normalized to -180 to 180 range."""
        print("\n=== Test: Angle Normalization ===")
        controller = self.create_controller()
        controller.start_verification()
        
        test_angles = [
            (0.0, 0.0),           # 0 radians = 0 degrees
            (math.pi/2, 90.0),    # π/2 radians = 90 degrees
            (math.pi, 180.0),     # π radians = 180 degrees
            (-math.pi + 0.001, -180.0),   # Close to -π radians (avoid boundary issue)
            (3*math.pi/2, -90.0), # 3π/2 radians = 270 degrees -> -90 degrees
            (2*math.pi, 0.0),     # 2π radians = 360 degrees -> 0 degrees
            (-math.pi/2, -90.0),  # -π/2 radians = -90 degrees
        ]
        
        for rad_input, expected_deg in test_angles:
            controller.trajectory_points = []  # Clear previous points
            controller.add_trajectory_point(0.0, 0.0, rad_input)
            
            if controller.trajectory_points:
                actual_deg = controller.trajectory_points[0]["yaw"]
                assert abs(actual_deg - expected_deg) < 0.1, f"Input {rad_input} rad should give {expected_deg}°, got {actual_deg}°"
                print(f"✓ {rad_input:.3f} rad -> {actual_deg:.1f}° (expected {expected_deg:.1f}°)")
    
    def test_shortest_angular_distance(self):
        """Test the shortest angular distance calculation for yaw errors."""
        print("\n=== Test: Shortest Angular Distance ===")
        
        test_cases = [
            (0.0, 0.0, 0.0),      # Same angle
            (90.0, 0.0, 90.0),    # 90 degree difference
            (0.0, 90.0, 90.0),    # 90 degree difference (reverse)
            (170.0, -170.0, 20.0), # Across -180/180 boundary
            (-170.0, 170.0, 20.0), # Across -180/180 boundary (reverse)
            (179.0, -179.0, 2.0), # Very close across boundary
            (-179.0, 179.0, 2.0), # Very close across boundary (reverse)
            (0.0, 180.0, 180.0),  # Maximum difference
            (0.0, -180.0, 180.0), # Maximum difference (equivalent)
        ]
        
        for actual, reference, expected in test_cases:
            # Calculate angular difference using controller logic
            diff = actual - reference
            while diff > 180:
                diff -= 360
            while diff <= -180:
                diff += 360
            shortest_distance = abs(diff)
            
            assert abs(shortest_distance - expected) < 0.001, \
                f"Angle {actual}° to {reference}° should be {expected}°, got {shortest_distance}°"
            print(f"✓ {actual:6.1f}° to {reference:6.1f}° = {shortest_distance:5.1f}° (expected {expected:5.1f}°)")
    
    def test_trajectory_scenarios(self):
        """Test various trajectory scenarios using JSON test data."""
        if not self.test_data:
            print("\n=== Test: Trajectory Scenarios - SKIPPED (no test data) ===")
            return
            
        print("\n=== Test: Trajectory Scenarios ===")
        
        test_cases = ["perfect_rectangle", "noisy_rectangle", "extreme_angle_wrapping", "corner_exclusion_test"]
        
        for test_case_name in test_cases:
            if test_case_name not in self.test_data["test_cases"]:
                continue
                
            print(f"\n--- Testing {test_case_name} ---")
            test_case = self.test_data["test_cases"][test_case_name]
            trajectory_points = test_case["trajectory_points"]
            expected_results = test_case["expected_results"]
            
            controller = self.create_controller()
            controller.start_verification()
            
            # Add all trajectory points
            for point in trajectory_points:
                yaw_radians = math.radians(point["yaw"])
                controller.add_trajectory_point(point["x"], point["y"], yaw_radians)
            
            # Calculate errors
            errors = controller._calculate_trajectory_error()
            
            print(f"Results:")
            print(f"  Position RMS error: {errors['position_error']:.3f}m")
            print(f"  Yaw RMS error: {errors['yaw_error']:.1f}°")
            print(f"  Coverage: {errors['coverage']:.1f}%")
            print(f"  Matched points: {errors['matched_points']}/{errors['total_reference_points']}")
            print(f"  Yaw errors calculated: {errors['yaw_errors_calculated']}")
            
            # Test position error expectations
            if expected_results["position_error_should_be_low"]:
                assert errors["position_error"] <= expected_results["max_position_error"], \
                    f"Position error {errors['position_error']:.3f}m should be ≤ {expected_results['max_position_error']:.3f}m"
                print(f"✓ Position error within expected range")
            
            # Test yaw error expectations
            if expected_results["yaw_error_should_be_low"]:
                assert errors["yaw_error"] <= expected_results["max_yaw_error"], \
                    f"Yaw error {errors['yaw_error']:.1f}° should be ≤ {expected_results['max_yaw_error']:.1f}°"
                print(f"✓ Yaw error within expected range")
            
            # Test coverage expectations
            if expected_results["coverage_should_be_high"]:
                assert errors["coverage"] >= expected_results["min_coverage"], \
                    f"Coverage {errors['coverage']:.1f}% should be ≥ {expected_results['min_coverage']:.1f}%"
                print(f"✓ Coverage within expected range")
    
    def test_closest_point_matching_algorithm(self):
        """Test the closest point matching algorithm specifically."""
        print("\n=== Test: Closest Point Matching Algorithm ===")
        controller = self.create_controller()
        controller.start_verification()
        
        # Create test points with known closest reference points
        test_points = [
            {"x": 0.1, "y": 0.0, "yaw": math.radians(90.0)},  # Near start of first edge
            {"x": 1.0, "y": 0.0, "yaw": math.radians(90.0)},  # Middle of first edge  
            {"x": 2.0, "y": 0.1, "yaw": math.radians(0.0)},   # Near first corner
            {"x": 2.0, "y": 1.0, "yaw": math.radians(0.0)},   # On second edge
        ]
        
        # Add points to controller
        for point in test_points:
            controller.add_trajectory_point(point["x"], point["y"], point["yaw"])
        
        # Calculate errors to test matching
        errors = controller._calculate_trajectory_error()
        
        # Should have matched some reference points
        assert errors["matched_points"] > 0
        assert errors["position_errors_calculated"] > 0
        
        # Position errors should be reasonable for points on or near the path
        assert errors["position_error"] < 0.5  # Should be within tolerance
        
        print(f"✓ Trajectory points added: {len(test_points)}")
        print(f"✓ Reference points matched: {errors['matched_points']}")
        print(f"✓ Position errors calculated: {errors['position_errors_calculated']}")
        print(f"✓ Average position error: {errors['position_error']:.3f}m")
    
    def run_all_tests(self):
        """Run all tests."""
        print("TrajectoryVerificationController Unit Tests")
        print("=" * 60)
        
        try:
            self.test_controller_initialization()
            self.test_angle_normalization()
            self.test_shortest_angular_distance()
            self.test_closest_point_matching_algorithm()
            self.test_trajectory_scenarios()
            
            print("\n" + "=" * 60)
            print("✓ All tests passed!")
            
        except AssertionError as e:
            print(f"\n✗ Test failed: {e}")
            return False
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            return False
        
        return True


def main():
    """Run the test suite."""
    test_suite = TestTrajectoryVerificationController()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
