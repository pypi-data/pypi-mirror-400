use crate::protocols::protocol::{Node, Nodes};
use reqwest::Client;
use std::time::Duration;
use anyhow::Result;

/// Discover peers from the bootstrap server
/// `node` parametresi artık sadece node_id, owner ve connections içeriyor
pub async fn discover_peers(
    bootstrap_url: &str,
    bearer_token: &str,
    node: &Node,
) -> Result<Nodes> {
    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .build()?;

    // POST request with JSON body (Node)
    let response = client
        .post(bootstrap_url)
        .header("Authorization", format!("Bearer {}", bearer_token))
        .json(node)  // sadece node_id, owner ve connections gönderilecek
        .send()
        .await?
        .error_for_status()?
        .json::<Nodes>()  // server’dan Nodes listesi bekliyoruz
        .await?;

    Ok(response)
}
