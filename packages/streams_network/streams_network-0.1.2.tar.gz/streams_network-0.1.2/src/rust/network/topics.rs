use std::{collections::{HashMap, HashSet}, sync::Arc};
use bytes::Bytes;
use libp2p::PeerId;
use tokio::sync::Mutex;
use libp2p::{
    request_response::Behaviour as RRBehaviour
};
type MyBehaviour = RRBehaviour<crate::protocols::protocol::HelloCodec>;


pub struct TopicManager {
    subs: HashMap<String, HashSet<PeerId>>,
    stream_manager: Arc<crate::network::stream::StreamManager>,
}

impl TopicManager {
    pub fn new(stream_manager: Arc<crate::network::stream::StreamManager>) -> Self {
        Self { subs: HashMap::new(), stream_manager }
    }

    pub fn subscribe(&mut self, peer: PeerId, topic: &str) {
        self.subs.entry(topic.to_string())
            .or_default()
            .insert(peer);
    }

    pub fn unsubscribe(&mut self, peer: &PeerId, topic: &str) {
        if let Some(peers) = self.subs.get_mut(topic) {
            peers.remove(peer);
        }
    }

    pub fn get_peers(&self, topic: &str) -> Vec<PeerId> {
        self.subs.get(topic)
            .map(|s| s.iter().cloned().collect())
            .unwrap_or_default()
    }

    
    pub async fn publish(
        &self,
        topic: &str,
        data: Bytes,
        swarm: &Arc<Mutex<libp2p::Swarm<MyBehaviour>>>,
    ) -> Result<(), String> {
        let peers = self.get_peers(topic);

        if peers.is_empty() {
            return Ok(()); // nobody listening, silently ignore
        }

        let mut _guard = swarm.lock().await;
        for peer in peers {
            self.stream_manager
                .send_stream_message(
                    &mut *_guard,
                    &peer,
                    data.clone(),
                    false, // force = false → batching active
                )
                .await?;
        }

        Ok(())
    }
}
