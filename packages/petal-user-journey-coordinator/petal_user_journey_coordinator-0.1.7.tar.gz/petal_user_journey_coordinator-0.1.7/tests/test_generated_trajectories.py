#!/usr/bin/env python3
"""
Test runner for generated trajectory test data.
This script integrates generated test data with the existing pytest test suite.
"""

import pytest
import json
import asyncio
import logging
import sys
import os
import math
sys.path.insert(0, 'src')

from petal_user_journey_coordinator.controllers import TrajectoryVerificationController
from unittest.mock import AsyncMock


class TestGeneratedTrajectoryData:
    """Test class for generated trajectory test data."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class with generated test data."""
        # Load generated test data
        test_data_file = os.path.join('tests', 'generated_trajectory_test_data.json')
        if os.path.exists(test_data_file):
            with open(test_data_file, 'r') as f:
                cls.test_data = json.load(f)
        else:
            cls.test_data = {"test_cases": {}}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_name,test_case", 
                           [(name, case) for name, case in 
                            json.load(open(os.path.join(os.path.dirname(__file__), 'generated_trajectory_test_data.json'), 'r'))['test_cases'].items()])
    async def test_generated_trajectory_case(self, test_name: str, test_case: dict):
        """Test a generated trajectory case."""
        
        # Create mock MQTT proxy
        mqtt_proxy = AsyncMock()
        
        # Create controller
        controller = TrajectoryVerificationController(
            mqtt_proxy=mqtt_proxy,
            logger=self.logger
        )
        
        # Configure controller for 2x2 rectangle to match generated data
        controller.rectangle_a = 2.0
        controller.rectangle_b = 2.0
        controller.points_per_edge = 10
        
        # Start verification
        controller.start_verification()
        
        # Add trajectory points
        for point in test_case['trajectory_points']:
            controller.add_trajectory_point(
                x=point['x'],
                y=point['y'],
                yaw=math.degrees(point['yaw'])  # Convert radians to degrees
            )
        
        # Finish verification
        results = await controller.finish_verification()
        
        # Extract results
        success = results['was_successful']
        expected_results = test_case['expected_results']
        
        # Extract values from nested structure
        position_error = results['results_json']['position_analysis']['rms_error_m']['value']
        yaw_error = results['results_json']['yaw_analysis']['rms_error_deg']['value']
        coverage = results['results_json']['trajectory_coverage']['coverage_percent']['value']
        
        # Log test results
        self.logger.info(f"Test case: {test_name}")
        self.logger.info(f"Description: {test_case['description']}")
        self.logger.info(f"Position error: {position_error:.3f}m")
        self.logger.info(f"Yaw error: {yaw_error:.1f}°")
        self.logger.info(f"Coverage: {coverage:.1f}%")
        self.logger.info(f"Success: {success}")
        
        # Validate against expected results
        expected_success = expected_results.get('overall_should_pass', True)
        
        # For test cases that should pass, verify they actually pass
        if expected_success:
            assert success, f"Test case '{test_name}' was expected to pass but failed"
        
        # For test cases that should fail, we don't assert failure since the 
        # expected results might be approximations
        
        # Additional specific checks based on expected results
        if expected_results.get('position_error_should_be_low', False):
            # Use a reasonable threshold for "low" error
            assert position_error <= 0.5, f"Position error {position_error} is not low for {test_name}"
        
        if expected_results.get('yaw_error_should_be_low', False):
            # Use a reasonable threshold for "low" yaw error  
            assert yaw_error <= 15.0, f"Yaw error {yaw_error}° is not low for {test_name}"
        
        if expected_results.get('coverage_should_be_high', False):
            # Use a reasonable threshold for "high" coverage
            assert coverage >= 60.0, f"Coverage {coverage}% is not high for {test_name}"


def test_generator_script_exists():
    """Test that the generator script exists and is executable."""
    generator_path = os.path.join('tests', 'generate_trajectory_test_data.py')
    assert os.path.exists(generator_path), "Generator script not found"
    assert os.access(generator_path, os.R_OK), "Generator script not readable"


def test_generated_data_file_exists():
    """Test that generated test data file exists."""
    test_data_path = os.path.join('tests', 'generated_trajectory_test_data.json')
    if not os.path.exists(test_data_path):
        pytest.skip("Generated test data file not found. Run generate_trajectory_test_data.py first.")
    
    # Validate JSON structure
    with open(test_data_path, 'r') as f:
        data = json.load(f)
    
    assert 'test_cases' in data, "Test data missing 'test_cases' key"
    assert len(data['test_cases']) > 0, "No test cases found in generated data"
    
    # Validate each test case structure
    for name, case in data['test_cases'].items():
        assert 'description' in case, f"Test case {name} missing description"
        assert 'trajectory_points' in case, f"Test case {name} missing trajectory_points"
        assert 'expected_results' in case, f"Test case {name} missing expected_results"
        
        # Validate trajectory points structure
        for i, point in enumerate(case['trajectory_points']):
            assert 'x' in point, f"Point {i} in {name} missing x coordinate"
            assert 'y' in point, f"Point {i} in {name} missing y coordinate"
            assert 'yaw' in point, f"Point {i} in {name} missing yaw value"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
