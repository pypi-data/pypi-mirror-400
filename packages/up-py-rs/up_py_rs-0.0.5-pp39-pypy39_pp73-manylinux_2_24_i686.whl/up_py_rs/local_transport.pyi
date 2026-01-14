from . import StaticUriProvider, UMessage

from typing import Callable

class LocalTransport:
    """
    Provides local (in-process) transport for uProtocol communication.
    
    LocalTransport enables communication between components within the same
    process without network overhead. It manages listener registration and
    message routing.
    """
    
    def __init__(self) -> None:
        """
        Create a new LocalTransport instance.
        
        Raises:
            Exception: If the runtime creation fails.
        
        Example:
            >>> from up_py_rs.local_transport import LocalTransport
            >>> transport = LocalTransport()
        """
        ...
    
    def register_listener(
        self,
        uri_provider: StaticUriProvider,
        resource_id: int,
        callback: Callable[[UMessage], None]
    ) -> None:
        """
        Register a listener callback for a specific resource.
        
        Args:
            uri_provider: The URI provider identifying the entity.
            resource_id: The resource ID to listen to (0 to 65535).
            callback: A Python function that accepts a UMessage parameter.
                        Will be called when messages arrive.
        
        Raises:
            Exception: If registration fails.
        
        Example:
            >>> from up_py_rs import UMessage
            >>> def my_handler(msg: UMessage):
            ...     print(msg.extract_string())
            >>> transport.register_listener(uri_provider, 0xb4c1, my_handler)
        """
        ...
    
    def unregister_listener(
        self,
        uri_provider: StaticUriProvider,
        resource_id: int,
        callback: Callable[[UMessage], None]
    ) -> None:
        """
        Unregister a previously registered listener.
        
        Args:
            uri_provider: The URI provider used during registration.
            resource_id: The resource ID to stop listening to.
            callback: The same Python function that was registered.
        
        Raises:
            Exception: If unregistration fails or listener not found.
        
        Note:
            Currently may fail due to listener instance comparison issues.
            Consider letting listeners be cleaned up automatically.
        """
        ...