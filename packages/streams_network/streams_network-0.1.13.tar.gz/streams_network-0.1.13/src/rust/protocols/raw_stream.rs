use bytes::Bytes;
use futures_codec::{Decoder, Encoder, BytesMut};
use std::io;
use unsigned_varint::decode;

pub struct RawStreamCodec;

impl RawStreamCodec {
    pub fn new() -> Self {
        Self
    }
}

impl Decoder for RawStreamCodec {
    type Item = BytesMut;
    type Error = io::Error;

    fn decode(&mut self, src: &mut BytesMut) -> Result<Option<Self::Item>, Self::Error> {
        let (payload_len, len_of_varint) = match decode::u64(src) {
            Ok((len, rest)) => (len as usize, src.len() - rest.len()),
            Err(decode::Error::Insufficient) => return Ok(None),
            Err(e) => return Err(io::Error::new(io::ErrorKind::InvalidData, e)),
        };

        if src.len() < len_of_varint + payload_len {
            return Ok(None);
        }

        let _header = src.split_to(len_of_varint);
        Ok(Some(src.split_to(payload_len)))
    }
}

impl Encoder for RawStreamCodec {
    type Item = Bytes;
    type Error = io::Error;

    fn encode(&mut self, item: Self::Item, dst: &mut BytesMut) -> Result<(), Self::Error> {
        let mut buffer = unsigned_varint::encode::u64_buffer();
        let header = unsigned_varint::encode::u64(item.len() as u64, &mut buffer);
        
        dst.extend_from_slice(header);
        dst.extend_from_slice(&item);
        
        Ok(())
    }
}

pub const RAW_STREAM_PROTOCOL: &str = "/plotune/raw-stream/1.0.0";