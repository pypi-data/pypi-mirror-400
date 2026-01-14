#!/usr/bin/env python3
"""
RobogptVision gRPC Client

Unified client for RobogptVision gRPC services:
- Camera listing and initialization
- Detection results streaming
- Object pose fetching
"""

import json
import grpc
from typing import Dict, Iterable, Optional, Any, List
from datetime import datetime

from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

from robogpt_client.build import RobogptVision_pb2
from robogpt_client.build import RobogptVision_pb2_grpc


class VisionClient:
    """
    Unified client for all RobogptVision gRPC services.
    
    Provides methods for:
    - Camera listing and initialization
    - Detection results streaming
    - Object pose fetching
    """

    def __init__(self, server_address: str = "localhost", port: int = 50052):
        """
        Initialize the vision client.
        
        Args:
            server_address: gRPC server address (host:port)
        """
        self.server_address = f"{server_address}:{port}"
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = RobogptVision_pb2_grpc.RobogptVisionStub(self.channel)
        print(f"[VISION CLIENT] Connected to {self.server_address}")

    # ========================================================================
    # Camera Management
    # ========================================================================

    def get_camera_list(self, verbose: bool = True) -> Optional[List[Dict[str, str]]]:
        """
        Fetch available cameras from the server.
        
        Args:
            verbose: Print discovery details
            
        Returns:
            List of camera dictionaries or None on error
        """
        if verbose:
            print("[VISION CLIENT] Requesting camera list...")
        
        try:
            request = RobogptVision_pb2.CameraListRequest()
            response = self.stub.CameraList(request)
            
            if not response.success:
                if verbose:
                    print("[VISION CLIENT] ✗ Failed to retrieve cameras")
                return None
            
            cameras = [
                {
                    "camera_name": cam.camera_name,
                    "camera_type": cam.camera_type,
                    "serial_number": cam.serial_number,
                }
                for cam in response.cameras
            ]
            
            if verbose:
                print(f"[VISION CLIENT] ✓ Found {len(cameras)} camera(s)")
                for idx, cam in enumerate(cameras, 1):
                    print(f"  {idx}. {cam['camera_name']} ({cam['camera_type']}) - S/N: {cam['serial_number']}")
            
            return cameras
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    def initialize_camera(
        self,
        camera_name: str,
        camera_type: str = "RGB",
        serial_number: str = "",
        verbose: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Initialize/start a camera on the vision server.
        
        Args:
            camera_name: Human-readable camera name
            camera_type: Type of camera (e.g., "RGB", "RGBD")
            serial_number: Camera serial number or device index
            verbose: Print initialization details
            
        Returns:
            Dictionary with 'success', 'message', 'stream_link' keys or None on error
        """
        if verbose:
            print(f"[VISION CLIENT] Initializing camera '{camera_name}'...")
        
        try:
            request = RobogptVision_pb2.CameraInfo(
                camera_name=camera_name,
                camera_type=camera_type,
                serial_number=serial_number,
            )
            response = self.stub.IntializeCamera(request)
            
            result = {
                "success": response.success,
                "message": response.message,
                "stream_link": response.stream_link,
            }
            
            if verbose:
                if response.success:
                    print(f"[VISION CLIENT] ✓ {response.message}")
                    print(f"[VISION CLIENT] Stream: {response.stream_link}")
                else:
                    print(f"[VISION CLIENT] ✗ {response.message}")
            
            return result
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    # ========================================================================
    # Detection Results Streaming
    # ========================================================================

    def send_detection_results(
        self,
        detections: Iterable[Dict[str, Any]],
        camera_id: str = "default_camera",
        verbose: bool = True,
    ) -> bool:
        """
        Send detection results via client-streaming RPC.
        
        Args:
            detections: Iterable of detection dictionaries
            camera_id: Source camera identifier
            verbose: Print streaming details
            
        Returns:
            True if successful, False otherwise
        """
        if verbose:
            print(f"[VISION CLIENT] Starting detection stream for camera '{camera_id}'...")
        
        def request_iterator():
            """Generate detection result requests."""
            count = 0
            for detection in detections:
                count += 1
                payload = Struct()
                payload.update(detection)
                
                ts = Timestamp()
                ts.GetCurrentTime()
                
                yield RobogptVision_pb2.DetectionResultsRequest(
                    camera_id=camera_id,
                    timestamp=ts,
                    detection_data=payload,
                )
                
                if verbose:
                    print(f"[VISION CLIENT] Sent detection #{count}")
        
        try:
            response = self.stub.DetectionResults(request_iterator())
            
            if verbose:
                print("[VISION CLIENT] ✓ Detection stream completed")
            
            return True
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return False

    # ========================================================================
    # Object Pose Fetching
    # ========================================================================

    def fetch_object_pose(
        self,
        object_name: str,
        frame_name: str = "base_link",
        camera_id: Optional[str] = None,
        verbose: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch object pose for the given object name.
        
        Args:
            object_name: Name of the object to fetch
            frame_name: Reference frame name (e.g., "world", "camera", "base_link")
            camera_id: Optional specific camera to use
            verbose: Print fetch details
            
        Returns:
            Dictionary with 'success', 'message', 'pose', 'additional_info' keys or None on error
        """
        if verbose:
            print(f"[VISION CLIENT] Fetching pose for object '{object_name}'...")
        
        try:
            request = RobogptVision_pb2.FetchObjectPoseRequest(
                object_name=object_name,
                frame_name=frame_name,
                camera_id=camera_id or "",
            )
            response = self.stub.FetchObjectPose(request)
            
            result = {
                "success": response.success,
                "message": response.message,
                "pose": None,
                "additional_info": None,
            }
            
            if response.success and response.HasField("pose"):
                result["pose"] = {
                    "position": list(response.pose.position),
                    "orientation": list(response.pose.orientation),
                }
            
            if response.HasField("additional_info"):
                result["additional_info"] = dict(response.additional_info)
            
            if verbose:
                if response.success:
                    print(f"[VISION CLIENT] ✓ {response.message}")
                    if result["pose"]:
                        print(f"[VISION CLIENT] Position: {result['pose']['position']}")
                        print(f"[VISION CLIENT] Orientation: {result['pose']['orientation']}")
                else:
                    print(f"[VISION CLIENT] ✗ {response.message}")
            
            return result
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    # ========================================================================
    # Camera Control
    # ========================================================================

    def stop_camera(
        self,
        camera_name: str,
        verbose: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Stop a specific camera and clean up its resources.
        
        Args:
            camera_name: Name of the camera to stop
            verbose: Print stop details
            
        Returns:
            Dictionary with 'success' and 'message' keys or None on error
        """
        if verbose:
            print(f"[VISION CLIENT] Stopping camera '{camera_name}'...")
        
        try:
            # CameraInfo uses camera_name as a string field
            request = RobogptVision_pb2.CameraInfo(
                camera_name=camera_name,
            )
            response = self.stub.StopCamera(request)
            
            result = {
                "success": response.success,
                "message": response.message,
            }
            
            if verbose:
                if response.success:
                    print(f"[VISION CLIENT] ✓ {response.message}")
                else:
                    print(f"[VISION CLIENT] ✗ {response.message}")
            
            return result
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    def stop_all_cameras(
        self,
        verbose: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Stop all active cameras and clean up all resources.
        
        Args:
            verbose: Print stop details
            
        Returns:
            Dictionary with 'success' and 'message' keys or None on error
        """
        if verbose:
            print("[VISION CLIENT] Stopping all cameras...")
        
        try:
            request = RobogptVision_pb2.KillAllCameras()
            response = self.stub.StopAllCameras(request)
            
            result = {
                "success": response.success,
                "message": response.message,
            }
            
            if verbose:
                if response.success:
                    print(f"[VISION CLIENT] ✓ {response.message}")
                else:
                    print(f"[VISION CLIENT] ✗ {response.message}")
            
            return result
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    def get_camera_streams(
        self,
        verbose: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get information about all active camera streams.
        
        Args:
            verbose: Print stream details
            
        Returns:
            List of stream info dictionaries or None on error
        """
        if verbose:
            print("[VISION CLIENT] Requesting active camera streams...")
        
        try:
            request = RobogptVision_pb2.StreamRequest()
            response = self.stub.GetCameraStreams(request)
            
            if not response.success:
                if verbose:
                    print("[VISION CLIENT] ✗ Failed to retrieve camera streams")
                return None
            
            streams = [
                {
                    "camera_name": stream.camera_name,
                    "stream_link": stream.stream_link,
                    "is_streaming": stream.is_streaming,
                }
                for stream in response.stream_infos
            ]
            
            if verbose:
                print(f"[VISION CLIENT] ✓ Found {len(streams)} active stream(s)")
                for idx, stream in enumerate(streams, 1):
                    status = "🟢 Streaming" if stream['is_streaming'] else "🔴 Not Streaming"
                    print(f"  {idx}. {stream['camera_name']} - {status}")
                    print(f"     URL: {stream['stream_link']}")
            
            return streams
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[VISION CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            if verbose:
                print(f"[VISION CLIENT] Error: {e}")
            return None

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def save_camera_list(self, filepath: str = "cameras.json") -> bool:
        """
        Retrieve camera list and save to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        cameras = self.get_camera_list(verbose=False)
        
        if cameras is None:
            print(f"[VISION CLIENT] Failed to retrieve cameras")
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cameras, f, indent=2, ensure_ascii=False)
            
            print(f"[VISION CLIENT] Camera list saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"[VISION CLIENT] Error saving file: {e}")
            return False

    # ========================================================================
    # Connection Management
    # ========================================================================

    def close(self):
        """Close the gRPC channel."""
        self.channel.close()
        print("[VISION CLIENT] Connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
