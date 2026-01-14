# core/file_transfer.py
import asyncio
import logging
from pathlib import Path
from typing import Dict
from uuid import uuid4

from ..models.messages import FileBatch

logger = logging.getLogger(__name__)

CHUNK_SIZE = 200  # bytes (intentionally small for reliability)


class FileTransferManager:
    """
    Simple chunk-based file transfer over P2P streams.

    - Sender splits file into FileBatch messages
    - Receiver reassembles in memory and writes to disk
    """

    def __init__(
        self,
        network,
        source_dir: str = "tests/source",
        target_dir: str = "tests/target",
    ):
        self.network = network
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)

        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # filename -> path
        self.shared_files: Dict[str, Path] = {}

        # batch_id -> transfer state
        self.receiving_transfers: Dict[str, Dict] = {}
        self.sending_transfers: Dict[str, Dict] = {}

        logger.info("FileTransferManager initialized")

    # ------------------------------------------------------------------
    # Shared files
    # ------------------------------------------------------------------

    def scan_shared_files(self) -> None:
        self.shared_files.clear()

        if not self.source_dir.exists():
            return

        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                self.shared_files[file_path.name] = file_path
                logger.info(
                    "Shared file registered: %s (%d bytes)",
                    file_path.name,
                    file_path.stat().st_size,
                )

    def list_shared_files(self) -> list[str]:
        return list(self.shared_files.keys())

    def has_file(self, filename: str) -> bool:
        return filename in self.shared_files

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    async def send_file(self, peer_id: str, filename: str) -> bool:
        if not self.has_file(filename):
            logger.error("File not found: %s", filename)
            return False

        path = self.shared_files[filename]
        batch_id = uuid4().hex[:8]

        try:
            data = path.read_bytes()
            size = len(data)
            total_chunks = (size + CHUNK_SIZE - 1) // CHUNK_SIZE

            logger.info(
                "Sending file '%s' → %s (%d bytes, %d chunks, batch=%s)",
                filename,
                peer_id[:12],
                size,
                total_chunks,
                batch_id,
            )

            self.sending_transfers[batch_id] = {
                "filename": filename,
                "peer_id": peer_id,
                "total_chunks": total_chunks,
                "sent_chunks": 0,
            }

            await self.network.start_stream(peer_id)

            for i in range(total_chunks):
                start = i * CHUNK_SIZE
                end = min(start + CHUNK_SIZE, size)

                batch = FileBatch(
                    batch_id=batch_id,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    data=data[start:end],
                )

                raw = batch.to_bytes()
                frame = len(raw).to_bytes(2, "big") + raw

                await self.network.send_stream_message(peer_id, frame)

                self.sending_transfers[batch_id]["sent_chunks"] = i + 1
                await asyncio.sleep(0.01)

            await self.network.close_stream(peer_id)

            logger.info("File sent successfully (batch=%s)", batch_id)
            del self.sending_transfers[batch_id]
            return True

        except Exception:
            logger.exception("Failed to send file '%s'", filename)
            self.sending_transfers.pop(batch_id, None)
            return False

    # ------------------------------------------------------------------
    # Receiving
    # ------------------------------------------------------------------

    def handle_file_batch(self, peer_id: str, batch: FileBatch) -> None:
        batch_id = batch.batch_id

        transfer = self.receiving_transfers.setdefault(
            batch_id,
            {
                "chunks": {},
                "total": batch.total_chunks,
                "peer_id": peer_id,
            },
        )

        # Ignore duplicate chunks
        if batch.chunk_index in transfer["chunks"]:
            return

        transfer["chunks"][batch.chunk_index] = batch.data
        received = len(transfer["chunks"])
        total = transfer["total"]

        if received % 10 == 0 or received == total:
            logger.info(
                "Receiving batch %s: %d/%d",
                batch_id,
                received,
                total,
            )

        if received == total:
            self._assemble_file(batch_id)

    def _assemble_file(self, batch_id: str) -> None:
        transfer = self.receiving_transfers[batch_id]
        chunks = transfer["chunks"]
        total = transfer["total"]

        try:
            data = b"".join(chunks[i] for i in range(total))

            output = self.target_dir / f"received_{batch_id}.bin"
            output.write_bytes(data)

            logger.info(
                "File received: %s (%d bytes)",
                output.name,
                len(data),
            )

            del self.receiving_transfers[batch_id]

        except Exception:
            logger.exception("Failed assembling batch %s", batch_id)

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------

    def get_send_progress(self) -> Dict:
        return self.sending_transfers.copy()

    def get_receive_progress(self) -> Dict:
        return {
            bid: {
                "received": len(t["chunks"]),
                "total": t["total"],
                "progress": len(t["chunks"]) / t["total"] * 100,
            }
            for bid, t in self.receiving_transfers.items()
        }
