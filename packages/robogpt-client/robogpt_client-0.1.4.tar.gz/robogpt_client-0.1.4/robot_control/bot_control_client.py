#!/usr/bin/env python3
"""
RoboGPT gRPC Client for Robot control
"""

import grpc
import sys
import os
from typing import List, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build import RobotControl_pb2
from build import RobotControl_pb2_grpc


class BotControlClient:
    def __init__(self, server_address: str = "localhost", port: int = 50052):

        """
        Initialize the BotControl gRPC client.
        
        Args:
            server_address: Address of the gRPC server (default: 'localhost:50051')
        """
        self.server_address = f"{server_address}:{port}"
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = RobotControl_pb2_grpc.RobotControlStub(self.channel)
        print(f"[BOT CONTROL CLIENT] Connected to {self.server_address}")
        

    def load_robot(self, robot_names: List[str], robot_ip: List[str], 
                   use_simulation: bool = False, robot_prefix: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Load/initialize robot instances.
        
        Args:
            robot_names: List of robot model names
            robot_ip: List of robot IP addresses
            use_simulation: Whether to use simulation mode
            robot_prefix: Optional list of robot prefixes
            
        Returns:
            Tuple of (success, message)
        """
        if robot_prefix is None:
            robot_prefix = []
            
        request = RobotControl_pb2.LoadRobotRequest(
            robot_names=robot_names,
            robot_ip=robot_ip,
            use_simulation=use_simulation,
            robot_prefix=robot_prefix
        )
        
        response = self.stub.LoadRobot(request)
        return response.success, response.message

    def move_to_pose(self, robot_id: int, pose_name: str, speed: float = 0.5, 
                     acceleration: float = 0.5, user_frame: int = 0) -> Tuple[bool, str]:
        """
        Move robot to a named pose.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            pose_name: Name of the target pose
            speed: Tool velocity (default: 0.5)
            acceleration: Tool acceleration (default: 0.5)
            user_frame: User frame number (default: 0)
            
        Returns:
            Tuple of (success, message)
        """
        request = RobotControl_pb2.MoveToPoseRequest(
            robot_id=robot_id,
            pose_name=pose_name,
            speed=speed,
            acceleration=acceleration,
            user_frame=user_frame
        )
        
        response = self.stub.MoveToPose(request)
        return response.success, response.message

    def move_to_joint(self, robot_id: int, joint_angles: List[float], 
                      speed: float = 0.5, acceleration: float = 0.5) -> Tuple[bool, str, float]:
        """
        Move robot to specific joint angles.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            joint_angles: Target joint angles
            speed: Joint velocity (default: 0.5)
            acceleration: Joint acceleration (default: 0.5)
            
        Returns:
            Tuple of (success, message, execution_time)
        """
        request = RobotControl_pb2.MoveToJointRequest(
            robot_id=robot_id,
            joint_angles=joint_angles,
            speed=speed,
            acceleration=acceleration
        )
        
        response = self.stub.MoveToJoint(request)
        return response.success, response.message, response.execution_time

    def get_current_tcp(self, robot_id: int, user_frame: int = 0, 
                        tool_number: int = 0) -> Tuple[bool, str, Optional[List[float]]]:
        """
        Get current TCP position.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            user_frame: User frame number (default: 0)
            tool_number: Tool number (default: 0)
            
        Returns:
            Tuple of (success, message, tcp_pose)
        """
        request = RobotControl_pb2.GetCurrentTcpRequest(
            robot_id=robot_id,
            user_frame=user_frame,
            tool_number=tool_number
        )
        
        response = self.stub.GetCurrentTcp(request)
        tcp_pose = list(response.tcp_pose.pose) if response.success else None
        return response.success, response.message, tcp_pose

    def get_current_joints(self, robot_id: int) -> Tuple[bool, str, Optional[List[float]]]:
        """
        Get current joint angles.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            
        Returns:
            Tuple of (success, message, joint_angles)
        """
        request = RobotControl_pb2.GetCurrentJointsRequest(robot_id=robot_id)
        
        response = self.stub.GetCurrentJoints(request)
        joint_angles = list(response.joint_angles) if response.success else None
        return response.success, response.message, joint_angles

    def set_digital_pin(self, robot_id: int, pin_number: int, value: bool) -> Tuple[bool, str]:
        """
        Set digital output pin.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            pin_number: Pin number
            value: Pin value (True/False)
            
        Returns:
            Tuple of (success, message)
        """
        request = RobotControl_pb2.SetDigitalPinRequest(
            robot_id=robot_id,
            pin_number=pin_number,
            value=value
        )
        
        response = self.stub.SetDigitalPin(request)
        return response.success, response.message

    def get_digital_pin(self, robot_id: int, pin_number: int) -> Tuple[bool, str, bool]:
        """
        Get digital input/output pin state.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            pin_number: Pin number
            
        Returns:
            Tuple of (success, message, value)
        """
        request = RobotControl_pb2.GetDigitalPinRequest(
            robot_id=robot_id,
            pin_number=pin_number
        )
        
        response = self.stub.GetDigitalPin(request)
        return response.success, response.message, response.value

    def save_pose(self, robot_id: int, pose_name: str, pose_type: str = "tcp",
                  user_frame: int = 0, tool_number: int = 0) -> Tuple[bool, str]:
        """
        Save current robot pose with a name.
        
        Args:
            robot_id: Robot identifier (1-indexed)
            pose_name: Name for the saved pose
            pose_type: Type of pose ("tcp" or "joint", default: "tcp")
            user_frame: User frame number (default: 0)
            tool_number: Tool number (default: 0)
            
        Returns:
            Tuple of (success, message)
        """
        request = RobotControl_pb2.SavePoseRequest(
            robot_id=robot_id,
            pose_name=pose_name,
            pose_type=pose_type,
            user_frame=user_frame,
            tool_number=tool_number
        )
        
        response = self.stub.SavePose(request)
        return response.success, response.message

    def close(self):
        """Close the gRPC channel."""
        self.channel.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Using context manager
    with BotControlClient('localhost:50051') as client:
        # Load robots
        success, message = client.load_robot(
            robot_names=['robot1'],
            robot_ip=['192.168.1.100'],
            use_simulation=True
        )
        print(f"Load robot: {success}, {message}")
        
        # Get current joints
        success, message, joints = client.get_current_joints(robot_id=1)
        print(f"Current joints: {success}, {joints}")
        
        # Move to pose
        success, message = client.move_to_pose(robot_id=1, pose_name='home')
        print(f"Move to pose: {success}, {message}")