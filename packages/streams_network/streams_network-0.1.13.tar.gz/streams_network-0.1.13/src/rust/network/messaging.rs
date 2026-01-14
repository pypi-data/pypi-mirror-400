// src/network/messaging.rs

use crate::protocols::protocol::{HelloCodec, HelloRequest};
use libp2p::{request_response::Behaviour, PeerId};
use anyhow::Result;

pub fn send_message(
    swarm: &mut libp2p::Swarm<Behaviour<HelloCodec>>,
    peer_id: &PeerId,
    msg: Vec<u8>,
) -> Result<()> {
    swarm.behaviour_mut().send_request(peer_id, HelloRequest(msg));
    Ok(())
}

pub fn broadcast_message(
    swarm: &mut libp2p::Swarm<Behaviour<HelloCodec>>,
    msg: Vec<u8>,
    exclude: &[PeerId],
) -> Result<()> {
    let connected_peers: Vec<PeerId> = swarm.connected_peers().cloned().collect();
    
    for peer in connected_peers {
        if !exclude.contains(&peer) {
            swarm.behaviour_mut().send_request(&peer, HelloRequest(msg.clone()));
        }
    }
    
    Ok(())
}