#!/usr/bin/env python3
"""
RoboGPT gRPC Client

Unified client for all RoboGPT gRPC services:
- Bidirectional streaming for chat prompts
- Function/tool execution
- Tool discovery
- Agent configuration upload
"""

import json
import threading
import grpc
from typing import Optional, Dict, List, Any, Callable, Iterator
from google.protobuf import struct_pb2

from build import RobogptAgents_pb2
from build import RobogptAgents_pb2_grpc


class AgentClient:
    """
    Unified client for all RoboGPT gRPC services.
    
    Provides methods for:
    - Bidirectional and Unidirectional chat streaming
    - Function/tool execution
    - Tool discovery
    - Agent configuration upload
    """
    
    def __init__(self, server_address: str = "localhost", port: int = 50051):
        """
        Initialize the agent client.
        
        Args:
            server_address: gRPC server address (host:port)
        """

        self.server_address = f"{server_address}:{port}"
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = RobogptAgents_pb2_grpc.RobogptAgentsStub(self.channel)
        self._stop_event = threading.Event()

        self.callback_output = "Client is Successfully connected with Chatbox !!"
        
        print(f"[CLIENT] Connected to {self.server_address}")
    
    # ========================================================================
    # Prompts / Responses  - Bidirectional and Unidirectional Streaming
    # ========================================================================
    
    def send_response(
        self,
        message: str,
        sender: str = "Client"
        ):
        """
        Send messages to server (unidirectional stream from client to server).
        
        Args:
            message: Message content to send
            sender: Name of the message sender
        """
        def message_generator() -> Iterator[RobogptAgents_pb2.PromptResponse]:
            """Generate message to send to server."""
            yield RobogptAgents_pb2.PromptResponse(
                responder=sender,
                content=message
            )

        try:
            print(f"[CLIENT] Sending message to server...")
            
            # Send message stream to server
            response = self.stub.ReadResponse(message_generator())
            
            print(f"[CLIENT] Message sent successfully")
            
        except grpc.RpcError as e:
            print(f"[CLIENT] RPC Error: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"[CLIENT] Error: {e}")

    def read_prompt(
        self, 
        message_callback: Optional[Callable[[str], None]] = None
        ):
        """
        Listen to server messages (unidirectional stream from server to client).
        
        Args:
            message_callback: Optional callback to handle received messages
        """
        try:
            print(f"[CLIENT] Connecting to server stream...")
            
            # Create empty request to initiate stream
            request = RobogptAgents_pb2.PromptRequest()
            
            # Start unidirectional stream from server
            responses = self.stub.StreamPrompts(request)
            
            print("[CLIENT] Listening for server messages...\n")
            
            # Receive messages from server
            for response in responses:
                message = f"[{response.sender}]: {response.content}"
                print(message)
                
                if message_callback:
                    message_callback(response.content)
                
                # Stop after receiving first message
                print("[CLIENT] Received hello, stopping stream...")
                break
                    
        except grpc.RpcError as e:
            print(f"[CLIENT] RPC Error: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"[CLIENT] Error: {e}")

    def stream_chat(
        self, 
        sender: str = "Client",
        message_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Start bidirectional streaming chat.
        
        Args:
            sender: Name of the message sender
            message_callback: Optional callback to handle received messages
        """
        def message_generator() -> Iterator[RobogptAgents_pb2.PromptResponse]:
            """Generate messages from user input."""
            print(f"[CLIENT] Starting chat as '{sender}'")
            print("[CLIENT] Type messages (or 'exit' to quit):\n")
            
            while not self._stop_event.is_set():
                try:
                    if self.callback_output is not None:
                        content = self.callback_output

                        if content.lower() == 'exit':
                            print("[CLIENT] Exiting chat...")
                            break
                        
                        if content.strip():
                            # Client sends PromptResponse with 'responder' field
                            yield RobogptAgents_pb2.PromptResponse(
                                responder=sender,
                                content=content
                            )

                        self.callback_output = None
                    else:
                        continue
                        
                except EOFError:
                    break
                except Exception as e:
                    print(f"[CLIENT] Error: {e}")
                    break
        
        try:
            print(f"[CLIENT] Starting bidirectional stream...")
            
            # Start bidirectional stream
            responses = self.stub.Prompts(message_generator())
            
            print("[CLIENT] Connected! Listening for server messages...\n")
            
            # Receive PromptMessage from server with 'sender' field
            for response in responses:
                message = f"[{response.sender}]: {response.content}"
                print(message)
                
                if message_callback:
                    self.callback_output = message_callback(response.content)

            
        except grpc.RpcError as e:
            print(f"[CLIENT] RPC Error: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"[CLIENT] Error: {e}")
    
    # ========================================================================
    # Function Execution
    # ========================================================================
    
    def call_function(
        self, 
        function_name: str, 
        arguments: Optional[Dict[str, Any]] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a function on the server.
        
        Args:
            function_name: Name of the function to execute
            arguments: Dictionary of function arguments
            verbose: Print execution details
            
        Returns:
            Dictionary with 'success', 'output', 'error' keys
        """
        if verbose:
            print(f"\n[CLIENT] Calling function: {function_name}")
            if arguments:
                print(f"[CLIENT] Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            # Convert arguments dict to protobuf Struct
            args_struct = struct_pb2.Struct()
            if arguments:
                args_struct.update(arguments)
            
            # Create request
            request = RobogptAgents_pb2.FunctionCallRequest(
                function_name=function_name,
                arguments=args_struct
            )
            
            # Call server
            response = self.stub.CallFunction(request)
            
            result = {
                'success': response.success,
                'output': response.output,
                'error': response.error
            }
            
            if verbose:
                if response.success:
                    print(f"[CLIENT] ✓ Success")
                    print(f"[CLIENT] Output: {response.output}")
                else:
                    print(f"[CLIENT] ✗ Failed")
                    print(f"[CLIENT] Error: {response.error}")
            
            return result
            
        except grpc.RpcError as e:
            error_msg = f"RPC Error: {e.code()} - {e.details()}"
            if verbose:
                print(f"[CLIENT] {error_msg}")
            return {
                'success': False,
                'output': '',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Client error: {str(e)}"
            if verbose:
                print(f"[CLIENT] {error_msg}")
            return {
                'success': False,
                'output': '',
                'error': error_msg
            }
    
    # ========================================================================
    # Tool Discovery
    # ========================================================================
    
    def get_tools(self, tool_skill_set: Optional[List[str]] = None, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve all available tools and their metadata.
        
        Args:
            verbose: Print discovery details
            
        Returns:
            Dictionary containing tools metadata or None on error
        """
        if verbose:
            print(f"[CLIENT] Requesting tools from server...")
        
        try:
            request = RobogptAgents_pb2.ToolsRequest()
            response = self.stub.GetTools(request)
            
            if verbose:
                print(f"[CLIENT] Received {response.total_count} tools")

            if tool_skill_set is not None:
                print(f"[CLIENT] Filtering tools for skill set: {tool_skill_set}")
                request.skill_set.extend(tool_skill_set)
            
            # Parse JSON metadata
            tools_metadata = json.loads(response.tools_metadata_json)
            
            if verbose:
                sample_tools = list(tools_metadata.keys())[:5]
                print(f"[CLIENT] Sample tools: {sample_tools}")
            
            return tools_metadata
            
        except grpc.RpcError as e:
            if verbose:
                print(f"[CLIENT] RPC Error: {e.code()} - {e.details()}")
            return None
        except json.JSONDecodeError as e:
            if verbose:
                print(f"[CLIENT] JSON Parse Error: {e}")
            return None
        except Exception as e:
            if verbose:
                print(f"[CLIENT] Error: {e}")
            return None
    
    def save_tools_to_file(self, filepath: str = "tools_metadata.json") -> bool:
        """
        Retrieve tools and save to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        tools = self.get_tools(verbose=False)
        
        if tools is None:
            print(f"[CLIENT] Failed to retrieve tools")
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tools, f, indent=2, ensure_ascii=False)
            
            print(f"[CLIENT] Tools metadata saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"[CLIENT] Error saving file: {e}")
            return False
    
    def list_tools(self) -> Optional[list]:
        """
        Get a simple list of tool names.
        
        Returns:
            List of tool names or None on error
        """
        tools = self.get_tools(verbose=False)
        if tools:
            return list(tools.keys())
        return None
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool metadata dictionary or None if not found
        """
        tools = self.get_tools(verbose=False)
        if tools:
            return tools.get(tool_name)
        return None
    
    # ========================================================================
    # Agent Configuration Upload
    # ========================================================================
    
    def upload_config(self, config_data: str, verbose: bool = True) -> bool:
        """
        Upload agent configuration to server.
        
        Args:
            config_data: Configuration content as string
            verbose: Print upload details
            
        Returns:
            True if upload successful, False otherwise
        """
        if verbose:
            print(f"[CLIENT] Uploading agent configuration ({len(config_data)} chars)...")
        
        try:
            request = RobogptAgents_pb2.AgentConfigUploadRequest(
                config_data=config_data
            )
            
            response = self.stub.UploadAgentConfig(request)
            
            if response.success:
                if verbose:
                    print("[CLIENT] ✓ Configuration uploaded successfully")
                return True
            else:
                if verbose:
                    print("[CLIENT] ✗ Configuration upload failed")
                return False
                
        except grpc.RpcError as e:
            if verbose:
                print(f"[CLIENT] RPC Error: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            if verbose:
                print(f"[CLIENT] Error: {e}")
            return False
    
    def upload_config_from_file(self, filepath: str) -> bool:
        """
        Upload agent configuration from a file.
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = f.read()
            
            print(f"[CLIENT] Loaded configuration from {filepath}")
            return self.upload_config(config_data)
            
        except FileNotFoundError:
            print(f"[CLIENT] Error: File not found: {filepath}")
            return False
        except Exception as e:
            print(f"[CLIENT] Error reading file: {e}")
            return False
    
    # ========================================================================
    # Connection Management
    # ========================================================================
    
    def close(self):
        """Close the gRPC channel and cleanup resources."""
        self._stop_event.set()
        self.channel.close()
        print("[CLIENT] Connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


