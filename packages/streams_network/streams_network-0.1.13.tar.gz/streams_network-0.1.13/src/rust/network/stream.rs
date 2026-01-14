use libp2p::bytes::{Bytes, BytesMut};
use libp2p::PeerId;
use std::collections::HashMap;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;
use std::sync::Arc;

const BATCH_SIZE: usize = 8192; // 8KB batches
const BATCH_TIMEOUT: Duration = Duration::from_millis(10); // 10ms batching

pub struct StreamManager {
    // Active streams with accumulated data
    pub(crate) active_streams: Arc<Mutex<HashMap<PeerId, StreamState>>>,
}

pub struct StreamState {
    buffer: BytesMut,
    last_callback: Instant,
    sample_count: usize,
}

impl StreamManager {
    pub fn new() -> Self {
        Self {
            active_streams: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    pub async fn get_active_streams(&self) -> Vec<PeerId> {
        let streams = self.active_streams.lock().await;
        streams.keys().cloned().collect()
    }

pub async fn send_stream_message(
    &self,
    swarm: &mut libp2p::Swarm<libp2p::request_response::Behaviour<crate::protocols::protocol::HelloCodec>>,
    peer_id: &PeerId,
    message: Bytes,
    force: bool,
) -> Result<(), String> {
    // 1) accumulate local buffer
    self.accumulate(*peer_id, message.clone()).await;

    // 2) decide to flush
    if force || self.should_notify(peer_id).await {
        let batch = self.get_batch(peer_id).await; // Bytes

        // prepend stream marker byte (1u8)
        let mut v = Vec::with_capacity(1 + batch.len());
        v.push(1u8);
        v.extend_from_slice(&batch);

        // convert to libp2p::bytes::Bytes
        let payload = LBytes::from(v);

        // wrap into your request type (HelloRequest örnek)
        let req = HelloRequest(payload.to_vec());

        // send via request-response
        swarm.behaviour_mut().send_request(peer_id, req);

        // opsiyonel: debug log
        //eprintln!("🦀 Sent stream batch to {} ({} bytes)", peer_id, payload.len());

        Ok(())
    } else {
        Ok(())
    }
}

    pub async fn add_stream(&self, peer_id: PeerId) {
        let mut streams = self.active_streams.lock().await;
        streams.insert(peer_id, StreamState {
            buffer: BytesMut::with_capacity(BATCH_SIZE * 2),
            last_callback: Instant::now(),
            sample_count: 0,
        });
    }

    pub async fn accumulate(&self, peer_id: PeerId, data: Bytes) {
        let mut streams = self.active_streams.lock().await;
        if let Some(state) = streams.get_mut(&peer_id) {
            state.buffer.extend_from_slice(&data);
            state.sample_count += 1;
        }
    }

    pub async fn should_notify(&self, peer_id: &PeerId) -> bool {
        let streams = self.active_streams.lock().await;
        if let Some(state) = streams.get(peer_id) {
            state.buffer.len() >= BATCH_SIZE || state.last_callback.elapsed() >= BATCH_TIMEOUT
        } else {
            false
        }
    }

    pub async fn get_batch(&self, peer_id: &PeerId) -> Bytes {
        let mut streams = self.active_streams.lock().await;
        if let Some(state) = streams.get_mut(peer_id) {
            let batch = state.buffer.split_to(state.buffer.len());
            state.last_callback = Instant::now();
            state.sample_count = 0;
            Bytes::from(batch)
        } else {
            Bytes::new()
        }
    }

    pub async fn close_stream(&self, peer_id: &PeerId) -> Result<Vec<u8>, String> {
        let mut streams = self.active_streams.lock().await;
        if let Some(state) = streams.remove(peer_id) {
            Ok(state.buffer.to_vec())
        } else {
            Err(format!("No active stream for peer {}", peer_id))
        }
    }
}


use libp2p::bytes::Bytes as LBytes;
use crate::protocols::protocol::HelloRequest; // eğer farklıysa kendi request tipini kullan

