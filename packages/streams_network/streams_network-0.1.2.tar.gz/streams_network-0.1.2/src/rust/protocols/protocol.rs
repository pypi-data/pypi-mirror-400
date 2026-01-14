// src/protocols/protocol.rs

use async_trait::async_trait;
use futures::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};
use libp2p::request_response::Codec;
use serde::{Deserialize, Serialize};
use pyo3::prelude::*;

// ============================================================================
// DATA STRUCTURES
// ============================================================================

#[pyclass]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ConnectionInfo {
    #[pyo3(get, set)]
    pub con_type: String,      // "LAN", "VPN", "Public"
    #[pyo3(get, set)]
    pub address: String,
    #[pyo3(get, set)]
    pub port: String,
}

#[pymethods]
impl ConnectionInfo {
    #[new]
    pub fn new(con_type: String, address: String, port: String) -> Self {
        ConnectionInfo { con_type, address, port }
    }
}


#[pyclass]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Node {
    #[pyo3(get, set)]
    pub node_id: String,
    #[pyo3(get, set)]
    pub owner: String,
    #[pyo3(get, set)]
    pub connections: Vec<ConnectionInfo>,
}

#[pymethods]
impl Node {
    #[new]
    pub fn new(
        node_id: String,
        owner: String,
        connections: Vec<ConnectionInfo>,
    ) -> Self {
        Node {
            node_id,
            owner,
            connections,
        }
    }
}

#[pyclass]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Nodes {
    #[pyo3(get, set)]
    pub nodes: Vec<Node>,
}

#[pymethods]
impl Nodes {
    #[new]
    pub fn new(nodes: Vec<Node>) -> Self {
        Nodes { nodes }
    }
}

// ============================================================================
// PROTOCOL
// ============================================================================

#[derive(Clone)]
pub struct HelloProtocol;

impl AsRef<str> for HelloProtocol {
    fn as_ref(&self) -> &str {
        "/plotune/streams/1.0.0"
    }
}

// ============================================================================
// CODEC
// ============================================================================

#[derive(Default, Clone, Debug)]
pub struct HelloCodec;

#[derive(Debug, Clone)]
pub struct HelloRequest(pub Vec<u8>);

#[derive(Debug, Clone)]
pub struct HelloResponse(pub Vec<u8>);

#[async_trait]
impl Codec for HelloCodec {
    type Protocol = HelloProtocol;
    type Request = HelloRequest;
    type Response = HelloResponse;

    async fn read_request<T>(&mut self, _: &HelloProtocol, io: &mut T) -> std::io::Result<HelloRequest>
    where
        T: AsyncRead + Unpin + Send,
    {
        let mut buf = Vec::new();
        io.read_to_end(&mut buf).await?;
        Ok(HelloRequest(buf))
    }

    async fn read_response<T>(&mut self, _: &HelloProtocol, io: &mut T) -> std::io::Result<HelloResponse>
    where
        T: AsyncRead + Unpin + Send,
    {
        let mut buf = Vec::new();
        io.read_to_end(&mut buf).await?;
        Ok(HelloResponse(buf))
    }

    async fn write_request<T>(
        &mut self,
        _: &HelloProtocol,
        io: &mut T,
        HelloRequest(data): HelloRequest,
    ) -> std::io::Result<()>
    where
        T: AsyncWrite + Unpin + Send,
    {
        io.write_all(&data).await?;
        io.close().await?;
        Ok(())
    }

    async fn write_response<T>(
        &mut self,
        _: &HelloProtocol,
        io: &mut T,
        HelloResponse(data): HelloResponse,
    ) -> std::io::Result<()>
    where
        T: AsyncWrite + Unpin + Send,
    {
        io.write_all(&data).await?;
        io.close().await?;
        Ok(())
    }
}