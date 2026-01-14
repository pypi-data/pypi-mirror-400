"""
Quick dummy test for TrajectoryVerificationController

This is a simplified test file for quick validation of the trajectory verification
controller, especially the closest point approach and angle wrapping functionality.
"""

import math
import json
import sys
import os

# Mock classes for testing without dependencies
class MockMQTTProxy:
    async def publish(self, topic, payload):
        pass

class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

# Simple test implementation (without importing the actual controller)
class DummyTrajectoryVerificationController:
    """Dummy implementation for testing core algorithms."""
    
    def __init__(self):
        self.rectangle_a = 2.0
        self.rectangle_b = 2.0
        self.points_per_edge = 10
        self.position_tolerance = 0.5
        self.yaw_tolerance = 10.0
        self.corner_exclusion_radius = 0.2
        self.trajectory_points = []
        self.is_active = False
        self.reference_trajectory = self._generate_rectangle_trajectory()
        
    def _generate_rectangle_trajectory(self):
        """Generate reference rectangular trajectory."""
        trajectory = []
        corners = [
            {"x": 0.0, "y": 0.0, "yaw": 90.0},
            {"x": self.rectangle_a, "y": 0.0, "yaw": 0.0},
            {"x": self.rectangle_a, "y": self.rectangle_b, "yaw": -90.0},
            {"x": 0.0, "y": self.rectangle_b, "yaw": -180.0},
            {"x": 0.0, "y": 0.0, "yaw": 90.0},
        ]
        
        for i in range(len(corners) - 1):
            start_corner = corners[i]
            end_corner = corners[i + 1]
            
            for j in range(self.points_per_edge):
                t = j / self.points_per_edge
                x = start_corner["x"] + t * (end_corner["x"] - start_corner["x"])
                y = start_corner["y"] + t * (end_corner["y"] - start_corner["y"])
                
                if abs(end_corner["x"] - start_corner["x"]) > abs(end_corner["y"] - start_corner["y"]):
                    if end_corner["x"] > start_corner["x"]:
                        yaw = 90.0
                    else:
                        yaw = -90.0
                else:
                    if end_corner["y"] > start_corner["y"]:
                        yaw = 0.0
                    else:
                        yaw = -180.0
                
                trajectory.append({"x": x, "y": y, "yaw": yaw})
        
        trajectory.append(corners[-1])
        return trajectory
    
    def start_verification(self):
        self.is_active = True
        self.trajectory_points = []
    
    def add_trajectory_point(self, x, y, yaw_radians):
        if not self.is_active:
            return
        
        yaw_degrees = math.degrees(yaw_radians)
        while yaw_degrees > 180:
            yaw_degrees -= 360
        while yaw_degrees <= -180:
            yaw_degrees += 360
        
        self.trajectory_points.append({
            "x": x, "y": y, "yaw": yaw_degrees
        })
    
    def _calculate_trajectory_error(self):
        if not self.trajectory_points:
            return {"position_error": float('inf'), "yaw_error": float('inf'), "coverage": 0.0}
        
        position_errors = []
        yaw_errors = []
        matched_ref_indices = set()
        
        max_matching_distance = max(self.rectangle_a, self.rectangle_b) * 0.2
        
        corner_points = [
            {"x": 0.0, "y": 0.0},
            {"x": self.rectangle_a, "y": 0.0},
            {"x": self.rectangle_a, "y": self.rectangle_b},
            {"x": 0.0, "y": self.rectangle_b},
        ]
        
        for actual_point in self.trajectory_points:
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
            
            if closest_ref_point and min_dist <= max_matching_distance:
                matched_ref_indices.add(closest_ref_index)
                position_errors.append(min_dist)
                
                # Check corner exclusion
                near_corner = False
                for corner in corner_points:
                    corner_dist = math.sqrt(
                        (actual_point["x"] - corner["x"])**2 + 
                        (actual_point["y"] - corner["y"])**2
                    )
                    if corner_dist <= self.corner_exclusion_radius:
                        near_corner = True
                        break
                
                if not near_corner:
                    actual_yaw = actual_point["yaw"]
                    ref_yaw = closest_ref_point["yaw"]
                    
                    diff = actual_yaw - ref_yaw
                    while diff > 180:
                        diff -= 360
                    while diff <= -180:
                        diff += 360
                    
                    yaw_diff = abs(diff)
                    yaw_errors.append(yaw_diff)
        
        coverage = (len(matched_ref_indices) / len(self.reference_trajectory)) * 100 if self.reference_trajectory else 0
        position_rms = math.sqrt(sum(e**2 for e in position_errors) / len(position_errors)) if position_errors else float('inf')
        yaw_rms = math.sqrt(sum(e**2 for e in yaw_errors) / len(yaw_errors)) if yaw_errors else float('inf')
        
        return {
            "position_error": position_rms,
            "yaw_error": yaw_rms,
            "coverage": coverage,
            "matched_points": len(matched_ref_indices),
            "total_reference_points": len(self.reference_trajectory),
            "yaw_errors_calculated": len(yaw_errors),
            "position_errors_calculated": len(position_errors)
        }


def test_angle_wrapping():
    """Test angle wrapping functionality."""
    print("\n=== Testing Angle Wrapping ===")
    
    test_cases = [
        (-170.0, 170.0, 20.0),  # Should wrap to 20° difference
        (170.0, -170.0, 20.0),  # Should wrap to 20° difference
        (179.0, -179.0, 2.0),   # Should wrap to 2° difference
        (0.0, 0.0, 0.0),        # Same angle
        (90.0, 0.0, 90.0),      # 90° difference
        (0.0, 180.0, 180.0),    # Maximum difference
    ]
    
    for actual, reference, expected in test_cases:
        diff = actual - reference
        while diff > 180:
            diff -= 360
        while diff <= -180:
            diff += 360
        shortest_distance = abs(diff)
        
        result = "✓" if abs(shortest_distance - expected) < 0.001 else "✗"
        print(f"  {actual:6.1f}° to {reference:6.1f}° = {shortest_distance:5.1f}° (expected {expected:5.1f}°) {result}")


def test_closest_point_approach():
    """Test closest point matching approach."""
    print("\n=== Testing Closest Point Approach ===")
    
    controller = DummyTrajectoryVerificationController()
    controller.start_verification()
    
    # Test with a few strategic points
    test_points = [
        (0.1, 0.0, 90.0),   # Near start, on path
        (1.0, 0.0, 90.0),   # Middle of first edge
        (2.0, 0.1, 0.0),    # Near first corner
        (2.0, 1.0, 0.0),    # Middle of second edge
        (0.5, 0.5, 45.0),   # Off-path point
    ]
    
    for x, y, yaw_deg in test_points:
        controller.add_trajectory_point(x, y, math.radians(yaw_deg))
    
    errors = controller._calculate_trajectory_error()
    
    print(f"  Added {len(test_points)} trajectory points")
    print(f"  Reference trajectory has {len(controller.reference_trajectory)} points")
    print(f"  Matched reference points: {errors['matched_points']}")
    print(f"  Position errors calculated: {errors['position_errors_calculated']}")
    print(f"  Yaw errors calculated: {errors['yaw_errors_calculated']}")
    print(f"  Position RMS error: {errors['position_error']:.3f}m")
    print(f"  Yaw RMS error: {errors['yaw_error']:.1f}°")
    print(f"  Coverage: {errors['coverage']:.1f}%")


def test_corner_exclusion():
    """Test corner exclusion functionality."""
    print("\n=== Testing Corner Exclusion ===")
    
    controller = DummyTrajectoryVerificationController()
    corner_points = [
        {"x": 0.0, "y": 0.0},
        {"x": controller.rectangle_a, "y": 0.0},
        {"x": controller.rectangle_a, "y": controller.rectangle_b},
        {"x": 0.0, "y": controller.rectangle_b},
    ]
    
    test_points = [
        (0.1, 0.1, "should be near corner"),
        (0.0, 0.0, "exactly at corner"),
        (1.0, 1.0, "center, not near corner"),
        (2.1, 0.1, "just outside east corner"),
        (0.15, 0.15, "just outside start corner"),
    ]
    
    for x, y, description in test_points:
        near_corner = False
        for corner in corner_points:
            distance = math.sqrt((x - corner["x"])**2 + (y - corner["y"])**2)
            if distance <= controller.corner_exclusion_radius:
                near_corner = True
                break
        
        result = "✓ EXCLUDED" if near_corner else "○ INCLUDED"
        print(f"  Point ({x:4.1f}, {y:4.1f}) - {description}: {result}")


def load_and_test_json_data():
    """Load and test with JSON data."""
    print("\n=== Testing with JSON Data ===")
    
    try:
        # Try to load the test data
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'trajectory_test_data.json')
        
        if not os.path.exists(json_path):
            print(f"  JSON test data not found at {json_path}")
            return
        
        with open(json_path, 'r') as f:
            test_data = json.load(f)
        
        controller = DummyTrajectoryVerificationController()
        
        # Test with perfect rectangle case
        perfect_case = test_data["test_cases"]["perfect_rectangle"]
        controller.start_verification()
        
        for point in perfect_case["trajectory_points"]:
            controller.add_trajectory_point(
                point["x"], 
                point["y"], 
                math.radians(point["yaw"])
            )
        
        errors = controller._calculate_trajectory_error()
        
        print(f"  Perfect Rectangle Test:")
        print(f"    Position RMS error: {errors['position_error']:.3f}m")
        print(f"    Yaw RMS error: {errors['yaw_error']:.1f}°") 
        print(f"    Coverage: {errors['coverage']:.1f}%")
        print(f"    Expected: Low errors, high coverage")
        
        # Test angle wrapping case
        angle_case = test_data["test_cases"]["extreme_angle_wrapping"]
        controller.start_verification()
        
        for point in angle_case["trajectory_points"]:
            controller.add_trajectory_point(
                point["x"],
                point["y"], 
                math.radians(point["yaw"])
            )
        
        errors = controller._calculate_trajectory_error()
        
        print(f"  Extreme Angle Wrapping Test:")
        print(f"    Position RMS error: {errors['position_error']:.3f}m")
        print(f"    Yaw RMS error: {errors['yaw_error']:.1f}°")
        print(f"    Coverage: {errors['coverage']:.1f}%")
        print(f"    Expected: Yaw error should handle -170° vs 170° = 20°")
        
    except Exception as e:
        print(f"  Error loading JSON data: {e}")


def main():
    """Run all dummy tests."""
    print("Dummy Trajectory Verification Controller Tests")
    print("=" * 50)
    
    test_angle_wrapping()
    test_closest_point_approach()
    test_corner_exclusion()
    load_and_test_json_data()
    
    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    main()
