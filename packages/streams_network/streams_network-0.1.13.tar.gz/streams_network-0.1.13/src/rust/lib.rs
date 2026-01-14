pub mod protocols;
pub mod network;
pub mod api;

use pyo3::prelude::*;

use crate::api::{BootstrapNetwork, P2PNode};
use crate::protocols::protocol::{Node, Nodes, ConnectionInfo};

#[pymodule]
fn streams_network(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BootstrapNetwork>()?;
    m.add_class::<P2PNode>()?;
    m.add_class::<Node>()?;
    m.add_class::<Nodes>()?;
    m.add_class::<ConnectionInfo>()?;
    Ok(())
}