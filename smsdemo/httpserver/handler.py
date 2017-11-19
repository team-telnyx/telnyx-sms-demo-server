"""
Simple SMS Echo Server.

The server inherits from http.server.BaseHTTPRequestHandler and implements a
POST handler.

The webhook signature is verified before Validation is performed on the
integrity of the message before echoing the message back to the sender.
"""

import http.server
import json
import logging
import urllib.parse
from typing import Mapping

from smsdemo.constants import POST_PATH
from smsdemo.message import SMSMessage
from smsdemo.util import (
    ServerConfig, SMSSendError,
    get_epoch_from_header, webhook_sig_hs256,
    sync_send,
)


def handler_factory(conf: ServerConfig):
    """
    Return an HTTPServer request handler class that uses the given messaging
    profile settings.
    """

    class SMSHandler(http.server.BaseHTTPRequestHandler):

        def do_POST(self):
            if self.path != POST_PATH:
                self.send_error(404)
                return

            content_type = self.headers["Content-Type"]
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = _extract_payload(post_data, content_type)
            msg = SMSMessage.from_payload(payload)
            logging.info("Received message: %s", msg)

            sig = self.headers["X-Telnyx-Signature"]
            epoch = get_epoch_from_header(sig)
            expected_sig = webhook_sig_hs256(conf.secret, post_data, epoch)
            if sig != expected_sig:
                logging.error("Invalid signature: %s (expected %s)",
                              sig, expected_sig)
                self.send_error(400, "Invalid signature")
                return
            logging.info("Validated signature: %s", msg)

            try:
                echo_msg = msg.echo_message()
                sync_send(echo_msg, conf.secret)
            except SMSSendError as e:
                logging.error("Echo failed: %s", e)
                self.send_error(502, "Echo failed")
                return

            logging.info("Echoed message: %s", echo_msg)
            self.send_response(200, message="Echo OK")

    return SMSHandler


def _extract_payload(data: bytes, content_type: str) -> Mapping:
    if content_type == "application/json":
        return json.loads(data)
    else:
        payload = urllib.parse.parse_qs(data.decode("utf-8"))
        return {k: v[0] for k, v in payload.items()}
