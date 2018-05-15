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

from smsdemo.constants import MDR_POST_PATH, SIGNATURE_HEADER_KEY, SMS_POST_PATH
from smsdemo.message import SMSMessage
from smsdemo.util import (
    get_expected_signature,
    ServerConfig,
    SMSSendError,
    sync_send,
)


def handler_factory(conf: ServerConfig):
    """
    Return an HTTPServer request handler class that uses the given messaging
    profile settings.
    """

    class SMSHandler(http.server.BaseHTTPRequestHandler):

        def do_POST(self):
            if self.path == SMS_POST_PATH:
                self.receive_and_echo_sms()
            elif self.path == MDR_POST_PATH:
                self.receive_and_log_mdr()
            else:
                self.send_error(404)

        def receive_and_echo_sms(self):
            """Accept, validate, and echo back an SMS delivery."""

            content_length = int(self.headers["Content-Length"])
            raw_payload = self.rfile.read(content_length)
            payload = json.loads(raw_payload)

            msg = SMSMessage.from_payload(payload)
            logging.info("Received message: %s", msg)

            signature = self.headers[SIGNATURE_HEADER_KEY]
            expected_signature = get_expected_signature(conf.secret, signature, raw_payload)
            if signature != expected_signature:
                logging.error("Invalid signature: %s (expected %s)",
                              signature, expected_signature)
                self.send_error(400, "Invalid signature")
                return

            try:
                echo_msg = msg.echo_message()
                sync_send(echo_msg, conf.secret)
            except SMSSendError as e:
                logging.error("Echo failed: %s", e)
                self.send_error(502, "Echo failed")
                return

            logging.info("Echoed message: %s", echo_msg)
            self.send_response(200, message="Echo OK")

        def receive_and_log_mdr(self):
            """Accept, validate and logan MDR delivery"""

            content_length = int(self.headers["Content-Length"])
            raw_payload = self.rfile.read(content_length)
            payload = json.loads(raw_payload)

            logging.info("Received MDR: %s", payload)

            signature = self.headers[SIGNATURE_HEADER_KEY]
            expected_signature = get_expected_signature(conf.secret, signature, raw_payload)
            if signature != expected_signature:
                logging.error("Invalid signature: %s (expected %s)", signature, expected_signature)
                self.send_error(400, "Invalid signature")
                return

            self.send_response(200, "MDR OK")

    return SMSHandler
