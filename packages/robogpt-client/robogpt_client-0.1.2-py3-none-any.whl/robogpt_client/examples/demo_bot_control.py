#!/usr/bin/env python3
"""
Demo script for testing RobotControl gRPC Client

This script demonstrates various robot control operations including:
- Loading robots
- Moving to poses and joint positions
- Getting current TCP and joint states
- Digital I/O control
- Saving poses
"""

import sys
import os
import time

from robogpt_client import BotControlClient

def demo_basic_operations():
    """Demonstrate basic robot control operations."""
    print("=" * 60)
    print("RobotControl Client - Basic Operations Demo")
    print("=" * 60)
    
    # Create client instance
    client = BotControlClient('localhost:50051')
    
    try:
        # 1. Load Robot
        print("\n1. Loading robot...")
        success, message = client.load_robot(
            robot_names=['RG2'],
            robot_ip=['192.168.1.100'],
            use_simulation=True,
            robot_prefix=['robot1']
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        if not success:
            print("Failed to load robot. Exiting demo.")
            return
        
        time.sleep(1)
        
        # 2. Get Current Joints
        print("\n2. Getting current joint angles...")
        success, message, joints = client.get_current_joints(robot_id=1)
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        print(f"   Joints: {joints}")
        
        time.sleep(0.5)
        
        # 3. Get Current TCP
        print("\n3. Getting current TCP pose...")
        success, message, tcp_pose = client.get_current_tcp(robot_id=1)
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        print(f"   TCP Pose: {tcp_pose}")
        
        time.sleep(0.5)
        
        # 4. Save Current Pose
        print("\n4. Saving current pose as 'demo_pose'...")
        success, message = client.save_pose(
            robot_id=1,
            pose_name='demo_pose',
            pose_type='tcp'
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        time.sleep(0.5)
        
        # 5. Move to Joint Position
        print("\n5. Moving to joint position...")
        target_joints = [0.0, -30.0, 60.0, 0.0, 90.0, 0.0]
        success, message, exec_time = client.move_to_joint(
            robot_id=1,
            joint_angles=target_joints,
            speed=0.3,
            acceleration=0.3
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        print(f"   Execution Time: {exec_time}s")
        
        time.sleep(2)
        
        # 6. Move to Named Pose
        print("\n6. Moving to named pose 'home'...")
        success, message = client.move_to_pose(
            robot_id=1,
            pose_name='home',
            speed=0.5,
            acceleration=0.5
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        time.sleep(2)
        
        # 7. Digital I/O Operations
        print("\n7. Setting digital output pin...")
        success, message = client.set_digital_pin(
            robot_id=1,
            pin_number=1,
            value=True
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        time.sleep(0.5)
        
        print("\n8. Getting digital pin state...")
        success, message, value = client.get_digital_pin(
            robot_id=1,
            pin_number=1
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        print(f"   Pin Value: {value}")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
    finally:
        client.close()
        print("\n" + "=" * 60)
        print("Demo completed!")
        print("=" * 60)


def demo_context_manager():
    """Demonstrate using the client with context manager."""
    print("\n" + "=" * 60)
    print("RobotControl Client - Context Manager Demo")
    print("=" * 60)
    
    with BotControlClient('localhost:50051') as client:
        # Load robot
        print("\nLoading robot with context manager...")
        success, message = client.load_robot(
            robot_names=['RG2'],
            robot_ip=['192.168.1.100'],
            use_simulation=True
        )
        print(f"Result: {success}")
        print(f"Message: {message}")
        
        if success:
            # Get current state
            success, message, joints = client.get_current_joints(robot_id=1)
            print(f"\nCurrent joints: {joints}")
    
    print("\nContext manager demo completed (client auto-closed)")


def demo_multi_robot():
    """Demonstrate controlling multiple robots."""
    print("\n" + "=" * 60)
    print("RobotControl Client - Multi-Robot Demo")
    print("=" * 60)
    
    client = BotControlClient('localhost:50051')
    
    try:
        # Load multiple robots
        print("\nLoading multiple robots...")
        success, message = client.load_robot(
            robot_names=['RG2', 'RG6'],
            robot_ip=['192.168.1.100', '192.168.1.101'],
            use_simulation=True,
            robot_prefix=['robot1', 'robot2']
        )
        print(f"Result: {success}")
        print(f"Message: {message}")
        
        if not success:
            return
        
        # Control robot 1
        print("\nGetting joints for Robot 1...")
        success, message, joints1 = client.get_current_joints(robot_id=1)
        print(f"Robot 1 joints: {joints1}")
        
        # Control robot 2
        print("\nGetting joints for Robot 2...")
        success, message, joints2 = client.get_current_joints(robot_id=2)
        print(f"Robot 2 joints: {joints2}")
        
        # Move both robots
        print("\nMoving Robot 1 to home...")
        success, message = client.move_to_pose(robot_id=1, pose_name='home')
        print(f"Result: {success}")
        
        print("\nMoving Robot 2 to home...")
        success, message = client.move_to_pose(robot_id=2, pose_name='home')
        print(f"Result: {success}")
        
    except Exception as e:
        print(f"\nError during multi-robot demo: {str(e)}")
    finally:
        client.close()


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("RobotControl Client - Error Handling Demo")
    print("=" * 60)
    
    client = BotControlClient('localhost:50051')
    
    try:
        # Try to control robot before loading
        print("\n1. Attempting to control robot without loading...")
        success, message, joints = client.get_current_joints(robot_id=1)
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        # Load robot
        print("\n2. Loading robot...")
        success, message = client.load_robot(
            robot_names=['RG2'],
            robot_ip=['192.168.1.100'],
            use_simulation=True
        )
        print(f"   Result: {success}")
        
        # Try invalid robot ID
        print("\n3. Attempting to control invalid robot ID (99)...")
        success, message, joints = client.get_current_joints(robot_id=99)
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
        # Try invalid pose name
        print("\n4. Attempting to move to invalid pose...")
        success, message = client.move_to_pose(
            robot_id=1,
            pose_name='non_existent_pose'
        )
        print(f"   Result: {success}")
        print(f"   Message: {message}")
        
    except Exception as e:
        print(f"\nException caught: {str(e)}")
    finally:
        client.close()


def demo_save_and_recall_poses():
    """Demonstrate saving and recalling poses."""
    print("\n" + "=" * 60)
    print("RobotControl Client - Save & Recall Poses Demo")
    print("=" * 60)
    
    with BotControlClient('localhost:50051') as client:
        # Load robot
        success, message = client.load_robot(
            robot_names=['RG2'],
            robot_ip=['192.168.1.100'],
            use_simulation=True
        )
        
        if not success:
            print(f"Failed to load robot: {message}")
            return
        
        # Get current position
        print("\n1. Getting current position...")
        success, message, tcp1 = client.get_current_tcp(robot_id=1)
        print(f"   Current TCP: {tcp1}")
        
        # Save current TCP pose
        print("\n2. Saving current TCP pose as 'position_1'...")
        success, message = client.save_pose(
            robot_id=1,
            pose_name='position_1',
            pose_type='tcp'
        )
        print(f"   Result: {success}, {message}")
        
        # Save current joint pose
        print("\n3. Saving current joint pose as 'joints_1'...")
        success, message = client.save_pose(
            robot_id=1,
            pose_name='joints_1',
            pose_type='joint'
        )
        print(f"   Result: {success}, {message}")
        
        # Move to different position
        print("\n4. Moving to different position...")
        target_joints = [10.0, -20.0, 45.0, 0.0, 75.0, 10.0]
        success, message, _ = client.move_to_joint(
            robot_id=1,
            joint_angles=target_joints,
            speed=0.4
        )
        print(f"   Result: {success}")
        
        time.sleep(2)
        
        # Recall saved pose
        print("\n5. Recalling saved pose 'position_1'...")
        success, message = client.move_to_pose(
            robot_id=1,
            pose_name='position_1',
            speed=0.3
        )
        print(f"   Result: {success}, {message}")


def main():
    """Run all demos."""
    print("\n" + "#" * 60)
    print("# RobotControl gRPC Client - Comprehensive Demo Suite")
    print("#" * 60)
    
    demos = [
        ("Basic Operations", demo_basic_operations),
        ("Context Manager", demo_context_manager),
        ("Multi-Robot Control", demo_multi_robot),
        ("Error Handling", demo_error_handling),
        ("Save & Recall Poses", demo_save_and_recall_poses),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'#' * 60}")
        print(f"# Demo {i}/{len(demos)}: {name}")
        print(f"{'#' * 60}")
        
        try:
            demo_func()
        except Exception as e:
            print(f"\nDemo failed with exception: {str(e)}")
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")
    
    print("\n" + "#" * 60)
    print("# All demos completed!")
    print("#" * 60)


if __name__ == "__main__":
    # You can run all demos or individual ones
    import argparse
    
    parser = argparse.ArgumentParser(description='RobotControl Client Demo')
    parser.add_argument('--demo', type=str, choices=['all', 'basic', 'context', 'multi', 'error', 'poses'],
                        default='all', help='Which demo to run')
    
    args = parser.parse_args()
    
    if args.demo == 'all':
        main()
    elif args.demo == 'basic':
        demo_basic_operations()
    elif args.demo == 'context':
        demo_context_manager()
    elif args.demo == 'multi':
        demo_multi_robot()
    elif args.demo == 'error':
        demo_error_handling()
    elif args.demo == 'poses':
        demo_save_and_recall_poses()