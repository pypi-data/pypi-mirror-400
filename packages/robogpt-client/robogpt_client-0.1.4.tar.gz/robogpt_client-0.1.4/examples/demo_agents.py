# ============================================================================
# Demo/Test Functions
# ============================================================================

import json

from robogpt_client import AgentClient

def demo_chat():
    """Demo bidirectional chat."""
    print("\n" + "="*60)
    print("Demo: Bidirectional Chat")
    print("="*60)
    def message_callback(msg: str) -> None:
        print(f"[CALLBACK] Received message: {msg}")
        return f"Hello from the client is {msg}!"
    
    with AgentClient() as client:
        client.stream_chat(sender="User",message_callback=message_callback)

def demo_unidirectional_prompts():
    """Demo unidirectional prompts."""
    print("\n" + "="*60)
    print("Demo: Unidirectional Prompts")
    print("="*60)
    def message_callback(msg: str) -> None:
        print(f"[CALLBACK] Received message: {msg}")
    
    with AgentClient() as client:
        client.read_prompt(message_callback=message_callback)

def demo_unidirectional_responses():
    """Demo unidirectional responses."""
    print("\n" + "="*60)
    print("Demo: Unidirectional Responses")
    print("="*60)
    
    with AgentClient() as client:
        while True:
            message = input("Enter message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Exiting...")
                break
            client.send_response(
                message=message,
                sender="Client"
            )

def demo_function_execution():
    """Demo function execution."""
    print("\n" + "="*60)
    print("Demo: Function Execution")
    print("="*60)
    
    with AgentClient() as client:
        # Example 1: Simple function call
        result = client.call_function(
            function_name="get_joint",
            arguments={"robot_to_use": 1}
        )
        
        # Example 2: Function with multiple arguments
        result = client.call_function(
            function_name="move_to_pose",
            arguments={
                "pose_name": "home",
                "robot_to_use": 1,
                "speed": 0.5
            }
        )


def demo_tool_discovery():
    """Demo tool discovery."""
    print("\n" + "="*60)
    print("Demo: Tool Discovery")
    print("="*60)
    
    with AgentClient() as client:
        # Get all tools
        tools = client.get_tools()
        
        if tools:
            print(f"\nTotal tools: {len(tools)}")
            
            # List tool names
            tool_names = client.list_tools()
            print(f"\nAll tools: {tool_names[:10]}...")
            
            # Get specific tool info
            if tool_names:
                tool_info = client.get_tool_info(tool_names[0])
                print(f"\nInfo for '{tool_names[0]}':")
                print(json.dumps(tool_info, indent=2))
            
            # Save to file
            client.save_tools_to_file("client_tools_metadata.json")


def demo_config_upload():
    """Demo configuration upload."""
    print("\n" + "="*60)
    print("Demo: Agent Config Upload")
    print("="*60)
    
    with AgentClient() as client:
        # Example config
        sample_config = """
                            AGENT_NAME=TestAgent
                            AGENT_VERSION=1.0.0
                            MAX_ITERATIONS=10
                            TEMPERATURE=0.7
                        """
        
        # Upload config
        success = client.upload_config(sample_config)
        
        if success:
            print("\n✓ Configuration uploaded successfully!")
        else:
            print("\n✗ Configuration upload failed!")


def main():
    """Interactive demo menu."""
    print("\n" + "="*60)
    print("RoboGPT Agent Client - Interactive Demo")
    print("="*60)
    
    while True:
        print("\nSelect a demo:")
        print("1. Bidirectional Chat")
        print("2. Unidirectional Prompts")
        print("3. Unidirectional Responses")
        print("4. Function Execution")
        print("5. Tool Discovery")
        print("6. Agent Config Upload")
        print("7. Run all demos (except chat)")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            demo_chat()
        elif choice == "2":
            demo_unidirectional_prompts()
        elif choice == "3":
            demo_unidirectional_responses()
        elif choice == "4":
            demo_function_execution()
        elif choice == "5":
            demo_tool_discovery()
        elif choice == "6":
            demo_config_upload()
        elif choice == "7":
            print("lund chalaye mera, sb demos!")
        elif choice == "0":
            print("\nExiting...")
            break
        else:
            print("\n✗ Invalid choice!")


if __name__ == "__main__":
    main()