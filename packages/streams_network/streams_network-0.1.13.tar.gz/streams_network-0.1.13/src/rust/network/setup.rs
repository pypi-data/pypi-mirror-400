// src/network/setup.rs

use crate::protocols::protocol::{HelloCodec, HelloProtocol};
use libp2p::{
    identity, PeerId, SwarmBuilder, tcp, noise,
    yamux::Config as YamuxConfig,
    request_response::{Behaviour, Config, ProtocolSupport},
    swarm::SwarmEvent,
};
use std::time::Duration;
use futures::StreamExt;
use anyhow::Result;

pub fn generate_keypair() -> identity::Keypair {
    identity::Keypair::generate_ed25519()
}

pub fn keypair_to_peer_id(keypair: &identity::Keypair) -> PeerId {
    PeerId::from_public_key(&keypair.public())
}

pub async fn create_swarm(
    keypair: identity::Keypair,
    local_ip: &str,
    listen_port: u16,
) -> Result<(libp2p::Swarm<Behaviour<HelloCodec>>, PeerId, u16)> {
    
    let peer_id = keypair_to_peer_id(&keypair);
    
    let config = Config::default()
        .with_request_timeout(Duration::from_secs(30));

    let behaviour = Behaviour::with_codec(
        HelloCodec::default(),
        std::iter::once((HelloProtocol, ProtocolSupport::Full)),
        config,
    );

    let mut swarm = SwarmBuilder::with_existing_identity(keypair)
        .with_tokio()
        .with_tcp(
            tcp::Config::default().nodelay(true),
            noise::Config::new,
            YamuxConfig::default,
        )?
        .with_behaviour(|_| behaviour)?
        .with_swarm_config(|cfg| cfg.with_idle_connection_timeout(Duration::from_secs(60)))
        .build();

    let listen_addr = format!("/ip4/{}/tcp/{}", local_ip, listen_port);
    swarm.listen_on(listen_addr.parse()?)?;

    let listen_port: u16 = loop {
        match swarm.select_next_some().await {
            SwarmEvent::NewListenAddr { address, .. } => {
                if let Some(libp2p::multiaddr::Protocol::Tcp(port)) = 
                    address.iter().find(|p| matches!(p, libp2p::multiaddr::Protocol::Tcp(_)))
                {
                    break port;
                }
            }
            _ => {}
        }
    };

    Ok((swarm, peer_id, listen_port))
}