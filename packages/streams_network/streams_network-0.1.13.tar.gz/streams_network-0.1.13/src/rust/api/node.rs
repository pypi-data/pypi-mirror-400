use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3_asyncio::tokio as py_tokio;
use tokio::sync::Mutex;
use std::sync::Arc;
use std::collections::HashSet;

use crate::protocols::protocol::{
    Node, Nodes
};
use crate::network::{
    setup, bootstrap, connection, messaging, stream
};
use libp2p::{
    request_response::Behaviour as RRBehaviour, PeerId
};
use libp2p::request_response::{
    Event as RREvent, Message as RRMessage
};
use futures::StreamExt;
use tokio::task::JoinHandle;

type MyBehaviour = RRBehaviour<crate::protocols::protocol::HelloCodec>;
// Note: we use the concrete Swarm type inline where needed in other modules

use crate::api::bootstrap::BootstrapNetwork;
use crate::api::event_loop;

#[pyclass]
pub struct P2PNode {

    pub(crate) swarm: Arc<Mutex<libp2p::Swarm<MyBehaviour>>>,
    pub(crate) peer_id: PeerId,
    pub(crate) listen_port: u16,
    pub(crate) config: BootstrapNetwork,
    pub(crate) connected_peers: Arc<Mutex<HashSet<PeerId>>>,
    pub(crate) event_loop_handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    pub(crate) stream_manager: Arc<stream::StreamManager>,
    pub(crate) topic_manager: Arc<crate::network::topics::TopicManager>,

}

#[pymethods]
impl P2PNode {

    #[staticmethod]
    pub fn create(py: Python<'_>, config: Py<BootstrapNetwork>) -> PyResult<&PyAny> {

        let cfg = config.borrow(py).clone();
        
        py_tokio::future_into_py::<_, P2PNode>(py, async move {

            // Listen port artık connections'dan alınabilir; fallback olarak ilk LAN/Public connection
            let listen_addr = "0.0.0.0".to_string(); // NOTE: varsayılan olarak tüm arayüzlerde dinle

            let listen_port = cfg.connections
                .iter()
                .find(|c| c.con_type == "LAN" || c.con_type == "Public")
                .map(|c| c.port.parse::<u16>().unwrap_or(0))
                .unwrap_or(0);

            let (swarm, peer_id, _actual_port) = setup::create_swarm(
                cfg.keypair.clone(),
                &listen_addr,
                listen_port,
            ).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            let swarm_arc = Arc::new(Mutex::new(swarm));
            let connected_peers = Arc::new(Mutex::new(HashSet::new()));
            let stream_manager = Arc::new(stream::StreamManager::new());
            let topic_manager = Arc::new(crate::network::topics::TopicManager::new(
                Arc::clone(&stream_manager)
            ));

            let node = P2PNode {
                swarm: swarm_arc,
                peer_id,
                listen_port,
                config: cfg,
                connected_peers,
                event_loop_handle: Arc::new(Mutex::new(None)),
                stream_manager,
                topic_manager,
            };

            Ok(node)
        
        })
    
    }


    pub fn peer_discover<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {

        let config = self.config.clone();
        let peer_id = self.peer_id;

        py_tokio::future_into_py::<_, Nodes>(py, async move {

            // Artık Node struct'ı connections içeriyor
            let node = crate::protocols::protocol::Node::new(
                peer_id.to_string(),
                config.owner.clone(),
                config.connections.clone(), // burada tek IP yerine connection listesi
            );

            let url = format!("{}/connect", config.bootstrap_url);

            let nodes = bootstrap::discover_peers(&url, &config.bearer_token, &node).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            Ok(nodes)
        
        })
    
    }

    pub fn connect<'p>(&self, py: Python<'p>, peer_id_str: String, ip: String, port: String) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        let connected_peers = Arc::clone(&self.connected_peers);
        let peer_id_display = peer_id_str.clone();
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let mut guard = swarm.lock().await;
            connection::connect_peer(&mut *guard, &peer_id, &ip, &port)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            drop(guard);

            let start = std::time::Instant::now();
            let timeout = std::time::Duration::from_secs(10);
            
            loop {

                if start.elapsed() > timeout {

                    return Err(pyo3::exceptions::PyRuntimeError::new_err(
                        format!("Connection timeout to {
                        
                        }", peer_id)
                    ));
                
                }
                {

                    let peers = connected_peers.lock().await;
                    if peers.contains(&peer_id) {

                        return Ok(());
                    
                    }
                
                }
                tokio::time::sleep(std::time::Duration::from_millis(100)).await;
            
            }
        
        })
    
    }

    pub fn disconnect<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        let connected_peers = Arc::clone(&self.connected_peers);
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let mut guard = swarm.lock().await;
            connection::disconnect_peer(&mut *guard, &peer_id)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            connected_peers.lock().await.remove(&peer_id);
            
            Ok(())
        
        })
    
    }

    pub fn get_peers<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {

        let connected_peers = Arc::clone(&self.connected_peers);
        
        py_tokio::future_into_py::<_, Vec<String>>(py, async move {

            let peers = connected_peers.lock().await;
            Ok(peers.iter().map(|p| p.to_string()).collect())
        
        })
    
    }

    pub fn send_message<'p>(&self, py: Python<'p>, peer_id_str: String, msg: Vec<u8>) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let mut guard = swarm.lock().await;
            messaging::send_message(&mut *guard, &peer_id, msg)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Ok(())
        
        })
    
    }

    pub fn send_stream_message<'p>(&self, py: Python<'p>, peer_id_str: String, msg: Vec<u8>) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let msg_bytes = libp2p::bytes::Bytes::from(msg);
            let mut _guard = swarm.lock().await;
            stream_manager.send_stream_message(&mut *_guard, &peer_id, msg_bytes, true).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;
            
            Ok(())
        
        })
    
    }

    pub fn start_stream<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            stream_manager.add_stream(peer_id).await;
            Ok(())
        
        })
    
    }

    pub fn stream_ready<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, bool>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            Ok(stream_manager.should_notify(&peer_id).await)
        
        })
    
    }

    pub fn get_stream_batch<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, Vec<u8>>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let batch = stream_manager.get_batch(&peer_id).await;
            Ok(batch.to_vec())
        
        })
    
    }

    pub fn close_stream<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, Vec<u8>>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let data = stream_manager.close_stream(&peer_id).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Ok(data)
        
        })
    
    }

    pub fn get_active_streams<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {

        let stream_manager = Arc::clone(&self.stream_manager);
        
        py_tokio::future_into_py::<_, Vec<String>>(py, async move {

            let streams = stream_manager.get_active_streams().await;
            let result: Vec<String> = streams.into_iter().map(|p| p.to_string()).collect();
            Ok(result)
        
        })
    
    }

    pub fn broadcast<'p>(&self, py: Python<'p>, msg: Vec<u8>, exclude: Option<Vec<String>>) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        
        py_tokio::future_into_py::<_, ()>(py, async move {

            let exclude_peers: Vec<PeerId> = if let Some(list) = exclude {

                list.iter()
                    .filter_map(|s| s.parse::<PeerId>().ok())
                    .collect()
            
            } else {

                vec![]
            
            };
            
            let mut guard = swarm.lock().await;
            messaging::broadcast_message(&mut *guard, msg, &exclude_peers)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Ok(())
        
        })
    
    }

    pub fn start_event_loop<'p>(&self, py: Python<'p>, handler: Option<PyObject>) -> PyResult<&'p PyAny> {

        // delegate heavy lifting to event_loop module
        let swarm = Arc::clone(&self.swarm);
        let connected_peers = Arc::clone(&self.connected_peers);
        let event_loop_handle = Arc::clone(&self.event_loop_handle);
        let stream_manager = Arc::clone(&self.stream_manager);
        let handler = handler.clone();

        py_tokio::future_into_py::<_, ()>(py, async move {

            event_loop::start_event_loop_impl(
                swarm,
                connected_peers,
                event_loop_handle,
                stream_manager,
                handler,
            ).await.map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;
            Ok(())
        
        })
    
    }

    pub fn stop_event_loop<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {

        let event_loop_handle = Arc::clone(&self.event_loop_handle);

        py_tokio::future_into_py::<_, ()>(py, async move {

            let mut handle_guard = event_loop_handle.lock().await;
            if let Some(handle) = handle_guard.take() {

                handle.abort();
            
            }
            Ok(())
        
        })
    
    }

    pub fn peer_id(&self) -> String {

        self.peer_id.to_string()
    
    }

    pub fn listen_port(&self) -> u16 {

        self.listen_port
    
    }

    pub fn ping<'p>(&self, py: Python<'p>, peer_id_str: String) -> PyResult<&'p PyAny> {

        let swarm = Arc::clone(&self.swarm);
        
        py_tokio::future_into_py::<_, bool>(py, async move {

            let peer_id = peer_id_str.parse::<PeerId>()
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid peer_id: {
                
                }", e)))?;
            
            let mut guard = swarm.lock().await;
            messaging::send_message(&mut *guard, &peer_id, b"PING".to_vec())
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Ok(true)
        
        })
    
    }

}