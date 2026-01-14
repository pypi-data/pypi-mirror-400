use crate::protocols::protocol::HelloCodec;
use libp2p::{
    request_response::Behaviour,
    PeerId, Multiaddr,
};
use anyhow::Result;

pub fn connect_peer(
    swarm: &mut libp2p::Swarm<Behaviour<HelloCodec>>,
    peer_id: &PeerId,
    ip: &str,
    port: &str,
) -> Result<()> {
    let addr: Multiaddr = format!("/ip4/{}/tcp/{}", ip, port).parse()?;
    
    // First, add the address to the behavior's address book
    swarm.add_peer_address(*peer_id, addr.clone());
    
    // Then attempt to dial the address with the peer ID
    swarm.dial(addr.clone().with(libp2p::multiaddr::Protocol::P2p(*peer_id)))?;
    
    Ok(())
}

pub fn disconnect_peer(
    swarm: &mut libp2p::Swarm<Behaviour<HelloCodec>>,
    peer_id: &PeerId,
) -> Result<()> {
    swarm.disconnect_peer_id(*peer_id).map_err(|e| anyhow::anyhow!(format!("{:?}", e)))?;
    Ok(())
}