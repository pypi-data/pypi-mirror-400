use libp2p::swarm::{
    NetworkBehaviour, ConnectionId, FromSwarm, THandler, THandlerInEvent,
    THandlerOutEvent, ToSwarm, NotifyHandler,
};
use libp2p::core::transport::PortUse;
use libp2p::core::{Endpoint, Multiaddr, PeerId};
use std::collections::{HashMap, VecDeque};
use std::task::{Context, Poll};
use std::io;
use tokio::sync::mpsc;

#[derive(Debug)]
pub enum StreamEvent {
    DataReceived { peer_id: PeerId, data: Vec<u8> },
    StreamOpened { peer_id: PeerId },
    StreamClosed { peer_id: PeerId },
}

pub struct RawStreamBehaviour {
    events: VecDeque<StreamEvent>,
    senders: HashMap<PeerId, mpsc::UnboundedSender<Vec<u8>>>,
}

impl RawStreamBehaviour {
    pub fn new() -> Self {
        Self {
            events: VecDeque::new(),
            senders: HashMap::new(),
        }
    }

    pub fn send_stream(&mut self, peer_id: &PeerId, data: Vec<u8>) -> Result<(), String> {
        if let Some(sender) = self.senders.get(peer_id) {
            sender.send(data).map_err(|e| format!("Send failed: {}", e))?;
            Ok(())
        } else {
            // İlk mesaj - handler'ı trigger et
            self.events.push_back(StreamEvent::StreamOpened { peer_id: *peer_id });
            let (tx, _rx) = mpsc::unbounded_channel();
            self.senders.insert(*peer_id, tx.clone());
            tx.send(data).map_err(|e| format!("Send failed: {}", e))?;
            Ok(())
        }
    }
}

impl NetworkBehaviour for RawStreamBehaviour {
    type ConnectionHandler = crate::network::handler::RawStreamHandler;
    type ToSwarm = StreamEvent;

    fn handle_established_inbound_connection(
        &mut self,
        _connection_id: ConnectionId,
        _peer: PeerId,
        _local_addr: &Multiaddr,
        _remote_addr: &Multiaddr,
    ) -> Result<THandler<Self>, libp2p::swarm::ConnectionDenied> {
        Ok(crate::network::handler::RawStreamHandler::new())
    }

    fn handle_established_outbound_connection(
        &mut self,
        _connection_id: ConnectionId,
        _peer: PeerId,
        _addr: &Multiaddr,
        _role_override: Endpoint,
        _port_use: libp2p::core::transport::PortUse, // Eksik olan 6. parametre
    ) -> Result<THandler<Self>, libp2p::swarm::ConnectionDenied> {
        Ok(crate::network::handler::RawStreamHandler::new())
    }

    fn on_connection_handler_event(
        &mut self,
        peer_id: PeerId,
        _connection_id: ConnectionId,
        event: THandlerOutEvent<Self>,
    ) {
        match event {
            crate::network::handler::StreamHandlerOutEvent::Data(data) => {
                self.events.push_back(StreamEvent::DataReceived { peer_id, data });
            }
            crate::network::handler::StreamHandlerOutEvent::StreamClosed => {
                self.events.push_back(StreamEvent::StreamClosed { peer_id });
                self.senders.remove(&peer_id);
            }
        }
    }

    fn on_swarm_event(&mut self, _event: FromSwarm) {}

    fn poll(
        &mut self,
        _cx: &mut Context<'_>,
    ) -> Poll<ToSwarm<Self::ToSwarm, THandlerInEvent<Self>>> {
        if let Some(event) = self.events.pop_front() {
            return Poll::Ready(ToSwarm::GenerateEvent(event));
        }
        Poll::Pending
    }
}