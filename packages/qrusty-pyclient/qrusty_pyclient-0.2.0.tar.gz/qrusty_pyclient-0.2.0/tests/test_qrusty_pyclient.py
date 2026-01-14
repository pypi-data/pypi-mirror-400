import unittest
from unittest.mock import patch
from typing import Any
import json

from qrusty_pyclient import QrustyClient


class TestQrustyClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = QrustyClient(base_url="http://localhost:6784")

    @patch("qrusty_pyclient.requests.post")
    def test_publish(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "msg-1"}
        resp = self.client.publish(
            queue="orders", priority=100, payload={"order_id": 123}
        )
        self.assertEqual(resp["id"], "msg-1")

        args, kwargs = mock_post.call_args
        self.assertTrue(str(args[0]).endswith("/publish"))
        sent = kwargs.get("json")
        self.assertIsInstance(sent, dict)
        self.assertEqual(sent["queue"], "orders")
        self.assertEqual(sent["priority"], 100)
        self.assertEqual(sent["payload"], json.dumps({"order_id": 123}))

    @patch("qrusty_pyclient.requests.get")
    def test_stats(self, mock_get: Any) -> None:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"queues": [], "summary": {}}
        resp = self.client.stats()
        self.assertIn("queues", resp)
        self.assertIn("summary", resp)

    @patch("qrusty_pyclient.requests.post")
    def test_ack_and_nack_paths_and_status(self, mock_post: Any) -> None:
        # Ack success
        mock_post.return_value.status_code = 200
        ok = self.client.ack(queue="orders", message_id="m1", consumer_id="c1")
        self.assertTrue(ok)
        self.assertTrue(str(mock_post.call_args[0][0]).endswith("/ack/orders/m1"))

        # Nack not found
        mock_post.return_value.status_code = 404
        ok2 = self.client.nack(queue="orders", message_id="m1", consumer_id="c1")
        self.assertFalse(ok2)
        self.assertTrue(str(mock_post.call_args[0][0]).endswith("/nack/orders/m1"))


if __name__ == "__main__":
    unittest.main()
