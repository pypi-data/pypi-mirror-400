#!/usr/bin/env python3
"""
Simple test script to verify the trajectory plotting functionality.
"""

import pytest
import json
import asyncio
import time
import logging
import math
import os
import sys
sys.path.insert(0, 'src')

from petal_user_journey_coordinator.controllers import TrajectoryVerificationController
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_plotting():
    """Test the trajectory plotting functionality with sample data."""
    
    # Create a simple logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create a mock MQTT proxy
    mqtt_proxy = AsyncMock()
    
    # Create controller
    controller = TrajectoryVerificationController(
        mqtt_proxy=mqtt_proxy,
        logger=logger
    )
    
    # Configure trajectory parameters
    controller.rectangle_a = 2
    controller.rectangle_b = 2
    controller.points_per_edge = 20
    controller.position_tolerance = 0.5
    controller.yaw_tolerance = 10.0
    controller.corner_exclusion_radius = 0.2
    
    # Start verification to generate reference trajectory
    controller.start_verification()
    
    # Add some sample trajectory points (perfect rectangle with small noise)
    reference_points = controller.reference_trajectory
    for i, ref_point in enumerate(reference_points):
        # Add slight noise to position and yaw
        noise_x = 0.1 * math.sin(i * 0.3)
        noise_y = 0.1 * math.cos(i * 0.3)
        noise_yaw = math.radians(2.0 * math.sin(i * 0.5))  # ±2 degrees
        
        controller.add_trajectory_point(
            x=ref_point["x"] + noise_x,
            y=ref_point["y"] + noise_y,
            yaw=ref_point["yaw"] + noise_yaw
        )
    
    print(f"Added {len(controller.trajectory_points)} trajectory points")
    print(f"Reference trajectory has {len(controller.reference_trajectory)} points")
    
    # Test plot generation
    print("\n--- Testing plot generation ---")
    
    # Test 1: Basic plot without errors or corner exclusions
    plot_file1 = controller.plot_trajectories(
        output_file="test_basic_plot.png"
    )
    print(f"✓ Basic plot saved: {plot_file1}")
    
    # Test 2: Full-featured plot with errors and corner exclusions
    plot_file2 = controller.plot_trajectories(
        output_file="test_full_plot.png"
    )
    print(f"✓ Full plot saved: {plot_file2}")
    
    # Test 3: Auto-generated filename
    plot_file3 = controller.plot_trajectories()
    print(f"✓ Auto-named plot saved: {plot_file3}")
    
    # Test finish_verification with plotting
    print("\n--- Testing finish_verification with plotting ---")
    
    results = await controller.finish_verification(
        generate_plot=True,
        plot_filename="test_verification_plot.png"
    )
    
    print(f"✓ Verification completed with plot: {results.get('plot_file', 'No plot file in results')}")
    print(f"✓ Verification successful: {results['was_successful']}")
    
    # List generated files
    print("\n--- Generated files ---")
    plot_files = [f for f in os.listdir('.') if f.endswith('.png') and 'test' in f]
    for plot_file in plot_files:
        size = os.path.getsize(plot_file)
        print(f"  {plot_file} ({size:,} bytes)")
    
    print(f"\n🎉 Plotting functionality test completed successfully!")
    print(f"   Generated {len(plot_files)} plot files")


if __name__ == "__main__":
    asyncio.run(test_plotting())
