use pyo3::prelude::*;
use crate::network::setup;

use libp2p::identity::Keypair;
use crate::protocols::protocol::ConnectionInfo;

/// Bootstrap configuration for a node
#[pyclass]
#[derive(Clone)]
pub struct BootstrapNetwork {
    #[pyo3(get, set)]
    pub bootstrap_url: String,
    #[pyo3(get, set)]
    pub bearer_token: String,
    #[pyo3(get, set)]
    pub owner: String,
    #[pyo3(get, set)]
    pub connections: Vec<ConnectionInfo>, // artık tek ip/port yerine connections listesi
    pub peer_id: String,
    pub keypair: Keypair,
}

#[pymethods]
impl BootstrapNetwork {
    #[new]
    pub fn new(
        bearer_token: String,
        connections: Option<Vec<ConnectionInfo>>,
        bootstrap_url: Option<String>,
        owner: Option<String>,
    ) -> Self {
        let keypair = setup::generate_keypair();
        let peer_id = setup::keypair_to_peer_id(&keypair);

        BootstrapNetwork {
            bootstrap_url: bootstrap_url.unwrap_or_else(|| "https://stream.plotune.net".to_string()),
            bearer_token,
            connections: connections.unwrap_or_else(Vec::new),
            owner: owner.unwrap_or_else(|| "anonymous".to_string()),
            peer_id: peer_id.to_string(),
            keypair,
        }
    }

    pub fn get_peer_id(&self) -> String {
        self.peer_id.clone()
    }

    /// Add a new connection to this node
    pub fn add_connection(&mut self, con_type: String, address: String, port: String) {
        self.connections.push(ConnectionInfo::new(con_type, address, port));
    }
}
