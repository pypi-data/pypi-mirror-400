use pyo3::prelude::*;
use pyo3::types::PyBytes;
use futures::StreamExt;
use tokio::task::JoinHandle;
use tokio::sync::Mutex;
use std::sync::Arc;
use std::collections::HashSet;

use libp2p::{request_response::Behaviour as RRBehaviour, swarm::SwarmEvent, PeerId};
use libp2p::request_response::{Event as RREvent, Message as RRMessage};

type MyBehaviour = RRBehaviour<crate::protocols::protocol::HelloCodec>;

pub async fn start_event_loop_impl(
    swarm: Arc<Mutex<libp2p::Swarm<MyBehaviour>>>,
    connected_peers: Arc<Mutex<HashSet<PeerId>>>,
    event_loop_handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    stream_manager: Arc<crate::network::stream::StreamManager>,
    handler: Option<PyObject>,
) -> Result<(), String> {
    let mut handle_guard = event_loop_handle.lock().await;
    if handle_guard.is_some() {
        return Ok(());
    }

    // Create a channel for communication between the swarm and event processing
    let (tx, mut rx) = tokio::sync::mpsc::channel(100);

    // Spawn a task that handles the swarm and sends events through the channel
    let swarm_for_swarm_task = Arc::clone(&swarm);
    let tx_clone = tx.clone();
    let swarm_task = tokio::task::spawn(async move {
        loop {
            let event = {
                let mut guard = swarm_for_swarm_task.lock().await;
                tokio::time::timeout(
                    std::time::Duration::from_millis(100),
                    guard.select_next_some(),
                ).await
            };

            match event {
                Ok(event) => {
                    if let Err(_) = tx_clone.send(event).await {
                        break;
                    }
                }
                Err(_) => {
                    tokio::time::sleep(std::time::Duration::from_millis(10)).await;
                }
            }
        }
    });

    // Processing task
    let swarm_for_processing = Arc::clone(&swarm);
    let connected_peers_for_processing = Arc::clone(&connected_peers);
    let stream_manager_for_processing = Arc::clone(&stream_manager);
    let handler_for_processing = handler.clone();

    let processing_task = tokio::task::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                SwarmEvent::Behaviour(RREvent::Message { peer, message, .. }) => {
                    if let Some(ref h) = handler_for_processing {
                        match message {
                            RRMessage::Request { request, channel, .. } => {
                                if request.0.len() > 0 && request.0[0] == 1u8 {
                                    let stream_data = request.0[1..].to_vec();
                                    Python::with_gil(|py| {
                                        match h.call_method1(py, "on_stream_message", (
                                            peer.to_string(),
                                            PyBytes::new(py, &stream_data),
                                        )) {
                                            Ok(_) => {
                                                let sm = stream_manager_for_processing.clone();
                                                let peer_id = peer;
                                                let data = stream_data.clone();
                                                tokio::task::spawn(async move {
                                                    sm.accumulate(peer_id, libp2p::bytes::Bytes::from(data)).await;
                                                });
                                            }
                                            Err(e) if e.is_instance_of::<pyo3::exceptions::PyAttributeError>(py) => {
                                            }
                                            Err(e) => {
                                            }
                                        }
                                    });
                                } else {
                                    let response_payload: Vec<u8> = Python::with_gil(|py| {
                                        h.call_method1(py, "on_message", (
                                            peer.to_string(),
                                            PyBytes::new(py, &request.0),
                                        ))
                                        .and_then(|res| res.extract(py))
                                        .unwrap_or_else(|_| Vec::new())
                                    });

                                    let mut guard = swarm_for_processing.lock().await;
                                    let _ = guard.behaviour_mut().send_response(
                                        channel,
                                        crate::protocols::protocol::HelloResponse(response_payload)
                                    );
                                }
                            }
                            RRMessage::Response { response, .. } => {
                                if response.0.len() > 0 && response.0[0] == 1u8 {
                                    let stream_data = response.0[1..].to_vec();
                                    Python::with_gil(|py| {
                                        let _ = h.call_method1(py, "on_stream_response", (
                                            peer.to_string(),
                                            PyBytes::new(py, &stream_data),
                                        ));
                                    });
                                } else {
                                    Python::with_gil(|py| {
                                        let _ = h.call_method1(py, "on_response", (
                                            peer.to_string(),
                                            PyBytes::new(py, &response.0),
                                        ));
                                    });
                                }
                            }
                        }
                    }
                }
                SwarmEvent::ConnectionEstablished { peer_id, endpoint, .. } => {
                    connected_peers_for_processing.lock().await.insert(peer_id);
                    if let Some(ref h) = handler_for_processing {
                        Python::with_gil(|py| {
                            let _ = h.call_method1(py, "on_peer_connected", (peer_id.to_string(),));
                        });
                    }
                }
                SwarmEvent::ConnectionClosed { peer_id, cause, .. } => {
                    connected_peers_for_processing.lock().await.remove(&peer_id);
                    if let Some(ref h) = handler_for_processing {
                        Python::with_gil(|py| {
                            let _ = h.call_method1(py, "on_peer_disconnected", (peer_id.to_string(),));
                        });
                    }
                }
                _ => {}
            }
        }
    });

    *handle_guard = Some(tokio::task::spawn(async move {
        let _ = tokio::join!(swarm_task, processing_task);
    }));

    Ok(())
}