use libp2p::swarm::{
    ConnectionHandler, ConnectionHandlerEvent, SubstreamProtocol,
    handler::{ConnectionEvent, FullyNegotiatedInbound, FullyNegotiatedOutbound},
};
use libp2p::core::upgrade::{ReadyUpgrade, UpgradeInfo, InboundUpgrade, OutboundUpgrade};
use libp2p::StreamProtocol;
use libp2p::Stream:: { poll_write, poll_read };
use futures::{AsyncReadExt, AsyncWriteExt};
use std::task::{Context, Poll};
use std::io;
use std::pin::Pin;

#[derive(Debug)]
pub enum StreamHandlerInEvent {
    SendData(Vec<u8>),
}

#[derive(Debug)]
pub enum StreamHandlerOutEvent {
    Data(Vec<u8>),
    StreamClosed,
}

pub struct RawStreamUpgrade;

impl UpgradeInfo for RawStreamUpgrade {
    type Info = StreamProtocol;
    type InfoIter = std::iter::Once<Self::Info>;

    fn protocol_info(&self) -> Self::InfoIter {
        std::iter::once(StreamProtocol::new("/plotune/raw-stream/1.0.0"))
    }
}

impl<C> InboundUpgrade<C> for RawStreamUpgrade
where
    C: futures::AsyncRead + futures::AsyncWrite + Unpin + Send + 'static,
{
    type Output = C;
    type Error = io::Error;
    type Future = Pin<Box<dyn std::future::Future<Output = Result<Self::Output, Self::Error>> + Send>>;

    fn upgrade_inbound(self, socket: C, _: Self::Info) -> Self::Future {
        Box::pin(async move { Ok(socket) })
    }
}

impl<C> OutboundUpgrade<C> for RawStreamUpgrade
where
    C: futures::AsyncRead + futures::AsyncWrite + Unpin + Send + 'static,
{
    type Output = C;
    type Error = io::Error;
    type Future = Pin<Box<dyn std::future::Future<Output = Result<Self::Output, Self::Error>> + Send>>;

    fn upgrade_outbound(self, socket: C, _: Self::Info) -> Self::Future {
        Box::pin(async move { Ok(socket) })
    }
}

pub struct RawStreamHandler {
    outbound_stream: Option<libp2p::Stream>,
    inbound_stream: Option<libp2p::Stream>,
    pending_send: Option<Vec<u8>>,
}

impl RawStreamHandler {
    pub fn new() -> Self {
        Self {
            outbound_stream: None,
            inbound_stream: None,
            pending_send: None,
        }
    }
}

impl ConnectionHandler for RawStreamHandler {
    type FromBehaviour = StreamHandlerInEvent;
    type ToBehaviour = StreamHandlerOutEvent;
    type InboundProtocol = RawStreamUpgrade;
    type OutboundProtocol = RawStreamUpgrade;
    type InboundOpenInfo = ();
    type OutboundOpenInfo = ();

    fn listen_protocol(&self) -> SubstreamProtocol<Self::InboundProtocol, ()> {
        SubstreamProtocol::new(RawStreamUpgrade, ())
    }

    fn poll(
        &mut self,
        cx: &mut Context<'_>,
    ) -> Poll<ConnectionHandlerEvent<Self::OutboundProtocol, Self::OutboundOpenInfo, Self::ToBehaviour>> {
        if self.outbound_stream.is_none() && self.pending_send.is_some() {
            return Poll::Ready(ConnectionHandlerEvent::OutboundSubstreamRequest {
                protocol: SubstreamProtocol::new(RawStreamUpgrade, ()),
            });
        }

        if let Some(mut stream) = self.outbound_stream.take() {
            if let Some(data) = self.pending_send.take() {
                match Pin::new(&mut stream).poll_write(cx, &data) {
                    Poll::Ready(Ok(_)) => {
                        let _ = Pin::new(&mut stream).poll_flush(cx);
                        self.outbound_stream = Some(stream);
                    }
                    Poll::Ready(Err(_)) => {
                        return Poll::Ready(ConnectionHandlerEvent::NotifyBehaviour(StreamHandlerOutEvent::StreamClosed));
                    }
                    Poll::Pending => {
                        self.pending_send = Some(data);
                        self.outbound_stream = Some(stream);
                    }
                }
            } else {
                self.outbound_stream = Some(stream);
            }
        }

        if let Some(mut stream) = self.inbound_stream.take() {
            let mut buf = [0u8; 8192];
            match Pin::new(&mut stream).poll_read(cx, &mut buf) {
                Poll::Ready(Ok(0)) => {
                    return Poll::Ready(ConnectionHandlerEvent::NotifyBehaviour(StreamHandlerOutEvent::StreamClosed));
                }
                Poll::Ready(Ok(n)) => {
                    self.inbound_stream = Some(stream);
                    return Poll::Ready(ConnectionHandlerEvent::NotifyBehaviour(StreamHandlerOutEvent::Data(buf[..n].to_vec())));
                }
                Poll::Ready(Err(_)) => {
                    return Poll::Ready(ConnectionHandlerEvent::NotifyBehaviour(StreamHandlerOutEvent::StreamClosed));
                }
                Poll::Pending => self.inbound_stream = Some(stream),
            }
        }

        Poll::Pending
    }

    fn on_behaviour_event(&mut self, event: Self::FromBehaviour) {
        match event {
            StreamHandlerInEvent::SendData(data) => {
                self.pending_send = Some(data);
            }
        }
    }

    fn on_connection_event(
        &mut self,
        event: ConnectionEvent<Self::InboundProtocol, Self::OutboundProtocol, Self::InboundOpenInfo, Self::OutboundOpenInfo>,
    ) {
        match event {
            ConnectionEvent::FullyNegotiatedInbound(FullyNegotiatedInbound { protocol, .. }) => {
                self.inbound_stream = Some(protocol);
            }
            ConnectionEvent::FullyNegotiatedOutbound(FullyNegotiatedOutbound { protocol, .. }) => {
                self.outbound_stream = Some(protocol);
            }
            _ => {}
        }
    }
}