#!/usr/bin/env python3
"""
Demo script for RobogptVision gRPC Client

Demonstrates all vision client capabilities:
- Camera listing and initialization
- Detection results streaming
- Object pose fetching
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from robogpt_client.vision.vision_client import VisionClient


def demo_camera_list(client: VisionClient):
    """Demonstrate camera list retrieval."""
    print("\n" + "="*70)
    print("DEMO 1: Get Camera List")
    print("="*70)
    
    cameras = client.get_camera_list(verbose=True)
    
    if cameras:
        print(f"\n✓ Successfully retrieved {len(cameras)} camera(s)")
        return cameras
    else:
        print("\n✗ Failed to retrieve camera list")
        return None


def demo_camera_initialization(client: VisionClient):
    """Demonstrate camera initialization."""
    print("\n" + "="*70)
    print("DEMO 2: Initialize Camera")
    print("="*70)
    
    # Example 1: Initialize RGB camera with device index
    print("\n--- Initializing RGB Camera (index 0) ---")
    result1 = client.initialize_camera(
        camera_name="front_rgb_camera",
        camera_type="RGB",
        serial_number="0",
        verbose=True
    )
    
    if result1 and result1["success"]:
        print(f"✓ Camera initialized successfully")
        print(f"  Stream URL: {result1['stream_link']}")
    
    time.sleep(1)
    
    # Example 2: Initialize depth camera with serial number
    print("\n--- Initializing RGBD Camera (serial) ---")
    result2 = client.initialize_camera(
        camera_name="depth_camera",
        camera_type="RGBD",
        serial_number="RGBD-002",
        verbose=True
    )
    
    if result2 and result2["success"]:
        print(f"✓ Camera initialized successfully")
        print(f"  Stream URL: {result2['stream_link']}")
    
    return [result1, result2]


def demo_detection_streaming(client: VisionClient):
    """Demonstrate detection results streaming."""
    print("\n" + "="*70)
    print("DEMO 3: Stream Detection Results")
    print("="*70)
    
    # Simulate detection results from a vision pipeline
    detection_payloads = [
        {
            "frame_id": 1,
            "timestamp": time.time(),
            "objects": [
                {
                    "name": "red_box",
                    "class": "box",
                    "confidence": 0.95,
                    "bbox": [100, 150, 250, 300],
                    "pose": {
                        "position": [0.45, 0.12, 0.08],
                        "orientation": [0.0, 0.0, 0.0, 1.0],
                    },
                }
            ]
        },
        {
            "frame_id": 2,
            "timestamp": time.time(),
            "objects": [
                {
                    "name": "blue_cylinder",
                    "class": "cylinder",
                    "confidence": 0.88,
                    "bbox": [300, 200, 380, 320],
                    "pose": {
                        "position": [0.30, -0.15, 0.12],
                        "orientation": [0.0, 0.0, 0.383, 0.924],
                    },
                },
                {
                    "name": "green_sphere",
                    "class": "sphere",
                    "confidence": 0.92,
                    "bbox": [450, 180, 520, 250],
                    "pose": {
                        "position": [0.52, 0.08, 0.06],
                        "orientation": [0.0, 0.0, 0.0, 1.0],
                    },
                }
            ]
        },
        {
            "frame_id": 3,
            "timestamp": time.time(),
            "objects": [
                {
                    "name": "red_box",
                    "class": "box",
                    "confidence": 0.97,
                    "bbox": [105, 155, 255, 305],
                    "pose": {
                        "position": [0.46, 0.13, 0.08],
                        "orientation": [0.0, 0.0, 0.087, 0.996],
                    },
                }
            ]
        },
    ]
    
    print(f"\nStreaming {len(detection_payloads)} detection frames...")
    success = client.send_detection_results(
        detections=detection_payloads,
        camera_id="front_rgb_camera",
        verbose=True
    )
    
    if success:
        print("\n✓ Detection streaming completed successfully")
    else:
        print("\n✗ Detection streaming failed")
    
    return success


def demo_object_pose_fetching(client: VisionClient):
    """Demonstrate object pose retrieval."""
    print("\n" + "="*70)
    print("DEMO 4: Fetch Object Poses")
    print("="*70)
    
    test_objects = [
        ("red_box", "base_link", "front_rgb_camera"),
        ("blue_cylinder", "world", "depth_camera"),
        ("green_sphere", "camera_link", None),
        ("unknown_object", "base_link", None),  # This should fail gracefully
    ]
    
    results = []
    
    for obj_name, frame, camera in test_objects:
        print(f"\n--- Fetching pose for '{obj_name}' (frame: {frame}) ---")
        
        result = client.fetch_object_pose(
            object_name=obj_name,
            frame_name=frame,
            camera_id=camera,
            verbose=True
        )
        
        results.append(result)
        
        if result and result["success"]:
            print(f"✓ Successfully retrieved pose for '{obj_name}'")
            if result.get("additional_info"):
                print(f"  Source: {result['additional_info'].get('source', 'unknown')}")
        else:
            print(f"✗ Failed to retrieve pose for '{obj_name}'")
        
        time.sleep(0.5)
    
    return results


def demo_helper_methods(client: VisionClient):
    """Demonstrate helper methods."""
    print("\n" + "="*70)
    print("DEMO 5: Helper Methods")
    print("="*70)
    
    # Save camera list to JSON
    print("\n--- Saving Camera List to JSON ---")
    success = client.save_camera_list("cameras_output.json")
    
    if success:
        print("✓ Camera list saved successfully")
    else:
        print("✗ Failed to save camera list")
    
    return success


def run_full_demo():
    """Run complete vision client demonstration."""
    print("\n" + "="*70)
    print("RobogptVision Client - Full Demo")
    print("="*70)
    print("\nThis demo will showcase all vision client capabilities:")
    print("  1. Camera listing")
    print("  2. Camera initialization")
    print("  3. Detection results streaming")
    print("  4. Object pose fetching")
    print("  5. Helper methods")
    print("\nMake sure the vision gRPC server is running on localhost:50052")
    print("="*70)
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Create client instance (with context manager)
        with VisionClient(server_address="localhost:50052") as client:
            
            # Demo 1: Camera List
            cameras = demo_camera_list(client)
            time.sleep(1)
            
            # Demo 2: Camera Initialization
            init_results = demo_camera_initialization(client)
            time.sleep(1)
            
            # Demo 3: Detection Streaming
            stream_success = demo_detection_streaming(client)
            time.sleep(1)
            
            # Demo 4: Object Pose Fetching
            pose_results = demo_object_pose_fetching(client)
            time.sleep(1)
            
            # Demo 5: Helper Methods
            helper_success = demo_helper_methods(client)
            
            # Summary
            print("\n" + "="*70)
            print("DEMO SUMMARY")
            print("="*70)
            print(f"Camera List:         {'✓ Success' if cameras else '✗ Failed'}")
            print(f"Camera Init:         {'✓ Success' if any(r and r.get('success') for r in init_results) else '✗ Failed'}")
            print(f"Detection Streaming: {'✓ Success' if stream_success else '✗ Failed'}")
            print(f"Pose Fetching:       {'✓ Success' if any(r and r.get('success') for r in pose_results) else '✗ Failed'}")
            print(f"Helper Methods:      {'✓ Success' if helper_success else '✗ Failed'}")
            print("="*70)
            
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Demo Complete ===\n")


def run_quick_demo():
    """Run a quick demo with minimal output."""
    print("=== RobogptVision Client - Quick Demo ===\n")
    
    with VisionClient() as client:
        # Get cameras
        cameras = client.get_camera_list(verbose=False)
        print(f"✓ Found {len(cameras) if cameras else 0} camera(s)")
        
        # Initialize one camera
        result = client.initialize_camera("quick_cam", "RGB", "0", verbose=False)
        print(f"✓ Camera init: {result['message'] if result else 'Failed'}")
        
        # Send one detection
        detection = [{"objects": [{"name": "test_obj", "pose": {"position": [0,0,0], "orientation": [0,0,0,1]}}]}]
        success = client.send_detection_results(detection, verbose=False)
        print(f"✓ Detection sent: {success}")
        
        # Fetch pose
        pose = client.fetch_object_pose("test_obj", verbose=False)
        print(f"✓ Pose fetched: {pose['success'] if pose else False}")
    
    print("\n=== Quick Demo Complete ===")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RobogptVision Client Demo")
    parser.add_argument(
        "--mode",
        choices=["full", "quick"],
        default="full",
        help="Demo mode: 'full' for complete demo, 'quick' for quick test"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        run_full_demo()
    else:
        run_quick_demo()