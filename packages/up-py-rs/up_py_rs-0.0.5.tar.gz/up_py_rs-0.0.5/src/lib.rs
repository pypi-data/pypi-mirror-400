pub mod communication;
pub mod local_transport;

use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::sync::Arc;

use protobuf::well_known_types::wrappers::StringValue;

use communication::{SimplePublisher, UPayload};
use local_transport::{LocalTransport, StaticUriProvider, UMessage};

#[pymodule]
fn up_py_rs(py: Python, m: &PyModule) -> PyResult<()> {
    // version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // communication submodule
    let communication_mod = PyModule::new(py, "communication")?;
    communication_mod.add_class::<UPayload>()?;
    communication_mod.add_class::<SimplePublisher>()?;
    m.add_submodule(communication_mod)?;

    // local transport submodule
    let local_transport_mod = PyModule::new(py, "local_transport")?;
    local_transport_mod.add_class::<LocalTransport>()?;
    m.add_submodule(local_transport_mod)?;

    // Add top-level classes
    m.add_class::<UMessage>()?;
    m.add_class::<StaticUriProvider>()?;

    Ok(())
}
