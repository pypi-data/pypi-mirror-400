#!/usr/bin/env python3
"""
Python example demonstrating the up-py bindings for up-rust.

This example mirrors the functionality of example.rs:
- Creates a LocalTransport and StaticUriProvider
- Registers a listener to receive messages
- Publishes a message
"""

from up_py_rs.communication import SimplePublisher, UPayload
from up_py_rs.local_transport import LocalTransport
from up_py_rs import StaticUriProvider


# Constants
ORIGIN_RESOURCE_ID = 0xb4c1

def console_printer(msg):
    """Callback function to handle received messages"""
    text = msg.extract_string()
    if text:
        print(f"received event: {text}")

def main():
    # Create URI provider
    uri_provider = StaticUriProvider("my-vehicle", 0xa34b, 0x01)
    
    # Create local transport
    transport = LocalTransport()
    
    # Register listener
    print("Registering listener...")
    transport.register_listener(uri_provider, ORIGIN_RESOURCE_ID, console_printer)
    
    # Create publisher
    publisher = SimplePublisher(transport, uri_provider)
    
    # Create and publish payload
    print("Publishing message...")
    payload = UPayload.from_string("Hello from Python!")
    publisher.publish(ORIGIN_RESOURCE_ID, payload)
    
    print("Done!")

if __name__ == "__main__":
    main()
