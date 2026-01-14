from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional, Union, cast

import requests


class QrustyClient:
    """
    Python client for the qrusty priority queue API.

    Example usage:
        client = QrustyClient(base_url="http://localhost:6784")
        client.create_queue(name="orders", ordering="MaxFirst", allow_duplicates=True)
        client.publish(queue="orders", priority=100, payload={"order_id": 123})
        message = client.consume(queue="orders", consumer_id="worker-1")
        if message is not None:
            client.ack(queue="orders", message_id=message["id"], consumer_id="worker-1")
    """

    def __init__(self, base_url: str):
        """
        Initialize the client with the base URL of the qrusty API server.
        :param base_url: Base URL of the qrusty server (e.g., http://localhost:6784)
        """
        self.base_url = base_url.rstrip("/")

    def health(self) -> str:
        """Check server health."""
        resp = requests.get(f"{self.base_url}/health", timeout=10)
        resp.raise_for_status()
        return cast(str, resp.text)

    def create_queue(
        self,
        name: str,
        ordering: str = "MaxFirst",
        allow_duplicates: bool = True,
    ) -> None:
        """Create or configure a queue."""
        data: Dict[str, Any] = {
            "name": name,
            "config": {"ordering": ordering, "allow_duplicates": allow_duplicates},
        }
        resp = requests.post(f"{self.base_url}/create-queue", json=data, timeout=10)
        resp.raise_for_status()

    def rename_queue(
        self,
        from_name: str,
        to_name: str,
        ordering: str = "MaxFirst",
        allow_duplicates: bool = True,
    ) -> None:
        """Rename a queue and optionally update its configuration."""
        data: Dict[str, Any] = {
            "from": from_name,
            "to": to_name,
            "config": {"ordering": ordering, "allow_duplicates": allow_duplicates},
        }
        resp = requests.post(f"{self.base_url}/rename-queue", json=data, timeout=10)
        resp.raise_for_status()

    def delete_queue(self, queue: str) -> Dict[str, Any]:
        """Delete a queue and all of its messages."""
        resp = requests.delete(f"{self.base_url}/delete-queue/{queue}", timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def publish(
        self,
        queue: str,
        priority: int,
        payload: Union[Mapping[str, Any], str],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Publish a message to a queue.
        :param queue: Queue name
        :param priority: Message priority
        :param payload: Message payload (dict or a pre-serialized JSON string)
        :param max_retries: Maximum retry count
        :return: Response JSON from server
        """
        payload_str = payload if isinstance(payload, str) else json.dumps(dict(payload))
        data: dict[str, Any] = {
            "queue": queue,
            "priority": priority,
            "payload": payload_str,
            "max_retries": max_retries,
        }
        resp = requests.post(f"{self.base_url}/publish", json=data, timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def consume(
        self, queue: str, consumer_id: str, timeout_seconds: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Consume a message from a queue.
        :param queue: Queue name
        :param consumer_id: Consumer identifier
        :param timeout_seconds: Lock timeout in seconds
        :return: Message JSON from server, or None if the queue is empty
        """
        data: Dict[str, Any] = {
            "consumer_id": consumer_id,
            "timeout_seconds": timeout_seconds,
        }
        resp = requests.post(f"{self.base_url}/consume/{queue}", json=data, timeout=10)
        resp.raise_for_status()
        return cast(Optional[Dict[str, Any]], resp.json())

    def ack(self, queue: str, message_id: str, consumer_id: str) -> bool:
        """
        Acknowledge a message as processed.
        :param queue: Queue name
        :param message_id: Message ID
        :param consumer_id: Consumer identifier
        :return: True if acked, False if not found/not locked by this consumer
        """
        data: Dict[str, Any] = {"consumer_id": consumer_id}
        resp = requests.post(
            f"{self.base_url}/ack/{queue}/{message_id}", json=data, timeout=10
        )
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return False

    def nack(self, queue: str, message_id: str, consumer_id: str) -> bool:
        """Negative-acknowledge a message."""
        data: Dict[str, Any] = {"consumer_id": consumer_id}
        resp = requests.post(
            f"{self.base_url}/nack/{queue}/{message_id}", json=data, timeout=10
        )
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return False

    def purge(self, queue: str) -> dict[str, Any]:
        """
        Purge all messages from a queue.
        :param queue: Queue name
        :return: Response JSON from server
        """
        resp = requests.post(f"{self.base_url}/purge-queue/{queue}", timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def stats(self) -> dict[str, Any]:
        """
        Get statistics for all queues.
        :return: Stats JSON from server
        """
        resp = requests.get(f"{self.base_url}/stats", timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def queue_stats(self, queue: str) -> Dict[str, Any]:
        """Get statistics for a specific queue."""
        resp = requests.get(f"{self.base_url}/queue-stats/{queue}", timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def queue_metrics(self, queue: str) -> Dict[str, Any]:
        """Get time-series metrics for a queue."""
        resp = requests.get(f"{self.base_url}/queues/{queue}/metrics", timeout=10)
        resp.raise_for_status()
        return cast(Dict[str, Any], resp.json())

    def list_queues(self) -> list[str]:
        """
        List all active queue names.
        :return: List of queue names
        """
        resp = requests.get(f"{self.base_url}/queues", timeout=10)
        resp.raise_for_status()
        return cast(List[str], resp.json())
