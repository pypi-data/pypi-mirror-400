from typing import Optional
from . import StaticUriProvider
from .local_transport import LocalTransport


class UPayload:
    """
    Represents a message payload in uProtocol.
    
    UPayload encapsulates the data being transmitted in a uProtocol message.
    It can be created from strings or raw bytes.
    """
    
    @staticmethod
    def from_string(value: str) -> 'UPayload':
        """
        Create a UPayload from a string value.
        
        Args:
            value: The string content to wrap in the payload.
        
        Returns:
            A new payload instance containing the string.
        
        Raises:
            Exception: If the payload creation fails.
        
        Example:
            >>> from up_py_rs.communication import UPayload
            >>> payload = UPayload.from_string("Hello, World!")
        """
        ...
    
    @staticmethod
    def from_bytes(data: list[int]) -> 'UPayload':
        """
        Create a UPayload from raw bytes.
        
        Args:
            data: A list of bytes (0-255) to wrap in the payload.
        
        Returns:
            A new payload instance containing the binary data.
        
        Example:
            >>> from up_py_rs.communication import UPayload
            >>> payload = UPayload.from_bytes([72, 101, 108, 108, 111])
        """
        ...

class SimplePublisher:
    """
    Publisher for sending uProtocol messages.
    
    SimplePublisher provides an easy-to-use interface for publishing messages
    to specific resources in the uProtocol network.
    """
    
    def __init__(self, transport: 'LocalTransport', uri_provider: StaticUriProvider) -> None:
        """
        Create a new SimplePublisher.
        
        Args:
            transport: The transport to use for sending messages.
            uri_provider: The URI provider for the publishing entity.
        
        Raises:
            Exception: If the runtime creation fails.
        
        Example:
            >>> from up_py_rs.communication import SimplePublisher
            >>> from up_py_rs.local_transport import LocalTransport
            >>> from up_py_rs import StaticUriProvider
            >>> transport = LocalTransport()
            >>> provider = StaticUriProvider("device", 0x1234, 0x01)
            >>> publisher = SimplePublisher(transport, provider)
        """
        ...
    
    def publish(self, resource_id: int, payload: Optional['UPayload']) -> None:
        """
        Publish a message to a specific resource.
        
        Args:
            resource_id: The target resource ID (0 to 65535).
            payload: The message payload, or None for empty messages.
        
        Raises:
            Exception: If publishing fails.
        
        Example:
            >>> from up_py_rs.communication import UPayload
            >>> payload = UPayload.from_string("Hello")
            >>> publisher.publish(0xb4c1, payload)
            >>> # Or publish without payload:
            >>> publisher.publish(0xb4c1, None)
        """
        ...