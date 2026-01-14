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

use crate::local_transport::{LocalTransport, StaticUriProvider};

/// Represents a message payload in uProtocol.
///
/// UPayload encapsulates the data being transmitted in a uProtocol message.
/// It can be created from strings or raw bytes.
#[pyclass]
#[derive(Clone)]
pub struct UPayload {
    inner: RustUPayload,
}

#[pymethods]
impl UPayload {
    /// Create a UPayload from a string value.
    ///
    /// Args:
    ///     value (str): The string content to wrap in the payload.
    ///
    /// Returns:
    ///     UPayload: A new payload instance containing the string.
    ///
    /// Raises:
    ///     Exception: If the payload creation fails.
    ///
    /// Example:
    ///     >>> payload = up_py_rs.UPayload.from_string("Hello, World!")
    #[staticmethod]
    fn from_string(value: String) -> PyResult<Self> {
        let string_value = StringValue {
            value,
            ..Default::default()
        };
        let payload = RustUPayload::try_from_protobuf(string_value)
            .map_err(|e| PyException::new_err(format!("Failed to create payload: {}", e)))?;
        Ok(UPayload { inner: payload })
    }

    /// Create a UPayload from raw bytes.
    ///
    /// Args:
    ///     data (list[int]): A list of bytes (0-255) to wrap in the payload.
    ///
    /// Returns:
    ///     UPayload: A new payload instance containing the binary data.
    ///
    /// Example:
    ///     >>> payload = up_py_rs.UPayload.from_bytes([72, 101, 108, 108, 111])
    #[staticmethod]
    fn from_bytes(data: Vec<u8>) -> PyResult<Self> {
        // Create a simple bytes payload with a generic format
        Ok(UPayload {
            inner: RustUPayload::new(
                data,
                UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            ),
        })
    }
}

/// Publisher for sending uProtocol messages.
///
/// SimplePublisher provides an easy-to-use interface for publishing messages
/// to specific resources in the uProtocol network.
#[pyclass]
pub struct SimplePublisher {
    inner: RustSimplePublisher,
    runtime: tokio::runtime::Runtime,
}

#[pymethods]
impl SimplePublisher {
    /// Create a new SimplePublisher.
    ///
    /// Args:
    ///     transport (LocalTransport): The transport to use for sending messages.
    ///     uri_provider (StaticUriProvider): The URI provider for the publishing entity.
    ///
    /// Returns:
    ///     SimplePublisher: A new publisher instance.
    ///
    /// Raises:
    ///     Exception: If the runtime creation fails.
    ///
    /// Example:
    ///     >>> transport = up_py_rs.LocalTransport()
    ///     >>> provider = up_py_rs.StaticUriProvider("device", 0x1234, 0x01)
    ///     >>> publisher = up_py_rs.SimplePublisher(transport, provider)
    #[new]
    fn new(transport: &LocalTransport, uri_provider: &StaticUriProvider) -> PyResult<Self> {
        let runtime = tokio::runtime::Runtime::new()
            .map_err(|e| PyException::new_err(format!("Failed to create runtime: {}", e)))?;
        Ok(SimplePublisher {
            inner: RustSimplePublisher::new(transport.inner.clone(), uri_provider.inner.clone()),
            runtime,
        })
    }

    /// Publish a message to a specific resource.
    ///
    /// Args:
    ///     resource_id (int): The target resource ID (0 to 65535).
    ///     payload (UPayload | None): The message payload, or None for empty messages.
    ///
    /// Raises:
    ///     Exception: If publishing fails.
    ///
    /// Example:
    ///     >>> payload = up_py_rs.UPayload.from_string("Hello")
    ///     >>> publisher.publish(0xb4c1, payload)
    ///     >>> # Or publish without payload:
    ///     >>> publisher.publish(0xb4c1, None)
    fn publish(
        &mut self,
        _py: Python,
        resource_id: u16,
        payload: Option<UPayload>,
    ) -> PyResult<()> {
        let payload_inner = payload.map(|p| p.inner);
        let call_options = CallOptions::for_publish(None, None, None);

        self.runtime.block_on(async {
            self.inner
                .publish(resource_id, call_options, payload_inner)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to publish: {}", e)))
        })
    }
}
