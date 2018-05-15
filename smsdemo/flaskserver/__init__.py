"""
Flask demo server.
"""

import json

from flask import Flask, request

from smsdemo.constants import MDR_POST_PATH, SIGNATURE_HEADER_KEY, SMS_POST_PATH
from smsdemo.message import SMSMessage
from smsdemo.util import (
    get_expected_signature,
    ServerConfig,
    SMSSendError,
    sync_send,
)


app = Flask(__name__)


@app.route(SMS_POST_PATH, methods=["POST"])
def receive_and_echo_sms():
    """Accept, validate, and echo back an SMS delivery."""

    secret = app.config["secret"]

    raw_payload = request.data
    payload = json.loads(raw_payload.decode("UTF-8"))

    msg = SMSMessage.from_payload(payload)
    app.logger.info("Received message: %s", msg)

    signature = request.headers[SIGNATURE_HEADER_KEY]
    expected_signature = get_expected_signature(secret, signature, raw_payload)
    if signature != expected_signature:
        app.logger.error("Invalid signature: %s (expected %s)", signature, expected_signature)
        return "Invalid signature", 400

    try:
        echo_msg = msg.echo_message()
        sync_send(echo_msg, secret)
    except SMSSendError as e:
        app.logger.error("Echo failed: %s", e)
        return "Echo failed", 502

    app.logger.info("Echoed message: %s", echo_msg)
    return "Echo OK", 200


@app.route(MDR_POST_PATH, methods=["POST"])
def receive_and_log_mdr():
    """Accept, validate and logan MDR delivery"""

    secret = app.config["secret"]

    raw_payload = request.data
    payload = json.loads(raw_payload.decode("UTF-8"))

    app.logger.info("Received MDR: %s", payload)

    signature = request.headers[SIGNATURE_HEADER_KEY]
    expected_signature = get_expected_signature(secret, signature, raw_payload)
    if signature != expected_signature:
        app.logger.error("Invalid signature: %s (expected %s)", signature, expected_signature)
        return "Invalid signature", 400

    return "MDR OK", 200


def run(conf: ServerConfig):
    """Run the flask-based demo server."""

    app.config["secret"] = conf.secret

    app.logger.info("SMS echo server (Flask) running on %s:%d", conf.host, conf.port)
    app.run(host=conf.host, port=conf.port)
