use up_rust::UPayloadFormat;
use up_rust::communication::{
    CallOptions, Publisher, SimplePublisher as RustSimplePublisher, UPayload as RustUPayload,
};
use up_rust::{
    LocalUriProvider, StaticUriProvider as RustStaticUriProvider, UListener,
    UMessage as RustUMessage, UTransport, local_transport::LocalTransport as RustLocalTransport,
};

use protobuf::well_known_types::wrappers::StringValue;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::sync::Arc;

/// Internal struct to bridge Python callbacks to Rust UListener trait
struct PythonListener {
    callback: PyObject,
}

#[async_trait::async_trait]
impl UListener for PythonListener {
    async fn on_receive(&self, msg: RustUMessage) {
        Python::with_gil(|py| {
            let py_msg = UMessage { inner: msg };
            if let Err(e) = self.callback.call1(py, (py_msg,)) {
                eprintln!("Error calling Python callback: {:?}", e);
            }
        });
    }
}

/// Represents a complete uProtocol message.
///
/// UMessage encapsulates both the payload and metadata for a uProtocol communication.
/// It is typically received by listener callbacks.
#[pyclass]
#[derive(Clone)]
pub struct UMessage {
    inner: RustUMessage,
}

#[pymethods]
impl UMessage {
    /// Extract string value from the message payload.
    ///
    /// Returns:
    ///     str | None: The extracted string if successful, None if the message
    ///                 doesn't contain a string value.
    ///
    /// Example:
    ///     >>> text = message.extract_string()
    ///     >>> if text:
    ///     ...     print(f"Received: {text}")
    fn extract_string(&self) -> PyResult<Option<String>> {
        match self.inner.extract_protobuf::<StringValue>() {
            Ok(value) => Ok(Some(value.value)),
            Err(_) => Ok(None),
        }
    }
}

/// Provides URI information for uProtocol entities.
///
/// StaticUriProvider creates and manages URIs for identifying entities
/// in the uProtocol network. It combines an authority (device/vehicle name),
/// entity ID, and version to create unique identifiers.
#[pyclass]
pub struct StaticUriProvider {
    pub inner: Arc<RustStaticUriProvider>,
}

#[pymethods]
impl StaticUriProvider {
    /// Create a new StaticUriProvider.
    ///
    /// Args:
    ///     authority (str): The authority name identifying the device/vehicle
    ///                     (e.g., "my-vehicle", "sensor-001").
    ///     entity_id (int): The entity ID (0 to 2^32-1, e.g., 0xa34b).
    ///     version (int): The version number (0 to 255, e.g., 0x01).
    ///
    /// Returns:
    ///     StaticUriProvider: A new URI provider instance.
    ///
    /// Example:
    ///     >>> provider = up_py_rs.StaticUriProvider("my-vehicle", 0xa34b, 0x01)
    #[new]
    fn new(authority: String, entity_id: u32, version: u8) -> Self {
        StaticUriProvider {
            inner: Arc::new(RustStaticUriProvider::new(&authority, entity_id, version)),
        }
    }
}

/// Provides local (in-process) transport for uProtocol communication.
///
/// LocalTransport enables communication between components within the same
/// process without network overhead. It manages listener registration and
/// message routing.
#[pyclass]
pub struct LocalTransport {
    pub inner: Arc<RustLocalTransport>,
    runtime: tokio::runtime::Runtime,
}

#[pymethods]
impl LocalTransport {
    /// Create a new LocalTransport instance.
    ///
    /// Returns:
    ///     LocalTransport: A new transport instance.
    ///
    /// Raises:
    ///     Exception: If the runtime creation fails.
    ///
    /// Example:
    ///     >>> transport = up_py_rs.LocalTransport()
    #[new]
    fn new() -> PyResult<Self> {
        let runtime = tokio::runtime::Runtime::new()
            .map_err(|e| PyException::new_err(format!("Failed to create runtime: {}", e)))?;
        Ok(LocalTransport {
            inner: Arc::new(RustLocalTransport::default()),
            runtime,
        })
    }

    /// Register a listener callback for a specific resource.
    ///
    /// Args:
    ///     uri_provider (StaticUriProvider): The URI provider identifying the entity.
    ///     resource_id (int): The resource ID to listen to (0 to 65535).
    ///     callback (callable): A Python function that accepts a UMessage parameter.
    ///                         Will be called when messages arrive.
    ///
    /// Raises:
    ///     Exception: If registration fails.
    ///
    /// Example:
    ///     >>> def my_handler(msg: UMessage):
    ///     ...     print(msg.extract_string())
    ///     >>> transport.register_listener(uri_provider, 0xb4c1, my_handler)
    fn register_listener(
        &mut self,
        _py: Python,
        uri_provider: &StaticUriProvider,
        resource_id: u16,
        callback: PyObject,
    ) -> PyResult<()> {
        let listener = Arc::new(PythonListener {
            callback: callback.clone(),
        });
        let uri = uri_provider.inner.get_resource_uri(resource_id);

        self.runtime.block_on(async {
            self.inner
                .register_listener(&uri, None, listener)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to register listener: {}", e)))
        })
    }

    /// Unregister a previously registered listener.
    ///
    /// Args:
    ///     uri_provider (StaticUriProvider): The URI provider used during registration.
    ///     resource_id (int): The resource ID to stop listening to.
    ///     callback (callable): The same Python function that was registered.
    ///
    /// Raises:
    ///     Exception: If unregistration fails or listener not found.
    ///
    /// Note:
    ///     Currently may fail due to listener instance comparison issues.
    ///     Consider letting listeners be cleaned up automatically.
    fn unregister_listener(
        &mut self,
        _py: Python,
        uri_provider: &StaticUriProvider,
        resource_id: u16,
        callback: PyObject,
    ) -> PyResult<()> {
        let listener = Arc::new(PythonListener {
            callback: callback.clone(),
        });
        let uri = uri_provider.inner.get_resource_uri(resource_id);

        self.runtime.block_on(async {
            self.inner
                .unregister_listener(&uri, None, listener)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to unregister listener: {}", e)))
        })
    }
}
