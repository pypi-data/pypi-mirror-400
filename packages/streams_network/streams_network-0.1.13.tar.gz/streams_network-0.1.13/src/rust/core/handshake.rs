use libp2p::{
    PeerId,
    request_response::{Behaviour, Event, Message},
    swarm::Swarm,
};
use crate::protocols::protocol::{HelloRequest, HelloResponse, HelloCodec};
/// Gelen requestleri ve response'ları handle eder
pub async fn handle_event(
    swarm: &mut Swarm<Behaviour<HelloCodec>>,
    event: Event<HelloRequest, HelloResponse>,
) {
    match event {
        Event::Message { message, peer, .. } => match message {
            Message::Request { request, channel, .. } => {
                println!("REQ from {}: {:?}", peer, String::from_utf8_lossy(&request.0));
                let _ = swarm.behaviour_mut().send_response(channel, HelloResponse(b"world".to_vec()));
            }
            Message::Response { response, .. } => {
                println!("RESP: {:?}", String::from_utf8_lossy(&response.0));
            }
        },
        _ => {}
    }
}

/// ConnectionEstablished geldiğinde hello gönder
pub fn handle_connection_established(
    swarm: &mut Swarm<Behaviour<HelloCodec>>,
    peer_id: &PeerId,
) {
    let _ = swarm.behaviour_mut().send_request(&peer_id, HelloRequest(b"hello".to_vec()));
}
