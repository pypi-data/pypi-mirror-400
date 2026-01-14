from typing import Optional

class StaticUriProvider:
    """
    Provides URI information for uProtocol entities.
    
    StaticUriProvider creates and manages URIs for identifying entities
    in the uProtocol network. It combines an authority (device/vehicle name),
    entity ID, and version to create unique identifiers.
    """
    
    def __init__(self, authority: str, entity_id: int, version: int) -> None:
        """
        Create a new StaticUriProvider.
        
        Args:
            authority: The authority name identifying the device/vehicle
                      (e.g., "my-vehicle", "sensor-001").
            entity_id: The entity ID (0 to 2^32-1, e.g., 0xa34b).
            version: The version number (0 to 255, e.g., 0x01).
        
        Example:
            >>> from up_py_rs import StaticUriProvider
            >>> provider = StaticUriProvider("my-vehicle", 0xa34b, 0x01)
        """
        ...

class UMessage:
    """
    Represents a complete uProtocol message.
    
    UMessage encapsulates both the payload and metadata for a uProtocol communication.
    It is typically received by listener callbacks.
    """
    
    def extract_string(self) -> Optional[str]:
        """
        Extract string value from the message payload.
        
        Returns:
            The extracted string if successful, None if the message
            doesn't contain a string value.
        
        Example:
            >>> text = message.extract_string()
            >>> if text:
            ...     print(f"Received: {text}")
        """
        ...

__version__: str
