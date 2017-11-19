"""
Flask demo server.
"""

from flask import Flask, request

from smsdemo.constants import POST_PATH
from smsdemo.message import SMSMessage
from smsdemo.util import (
    ServerConfig, SMSSendError,
    get_epoch_from_header, webhook_sig_hs256,
    sync_send,
)


app = Flask(__name__)


@app.route(POST_PATH, methods=["POST"])
def receive_and_echo():
    secret = app.config["secret"]

    if request.headers.get("Content-Type") == "application/json":
        payload = request.get_json()
    else:
        payload = request.form

    msg = SMSMessage.from_payload(payload)
    app.logger.info("Received message: %s", msg)

    sig = request.headers.get("X-Telnyx-Signature")
    raw_payload = request.data
    epoch = get_epoch_from_header(sig)
    expected_sig = webhook_sig_hs256(secret, raw_payload, epoch)
    if sig != expected_sig:
        app.logger.error("Invalid signature: %s (expected %s)", sig, expected_sig)
        return "Invalid signature", 400

    try:
        echo_msg = msg.echo_message()
        sync_send(echo_msg, secret)
    except SMSSendError as e:
        app.logger.error("Echo failed: %s", e)
        return "Echo failed", 502

    app.logger.info("Echoed message: %s", echo_msg)
    return "Echo OK", 200


def run(conf: ServerConfig):
    """Run the flask-based demo server."""

    app.config["secret"] = conf.secret

    app.logger.info("SMS echo server (Flask) running on %s:%d", conf.host, conf.port)
    app.run(host=conf.host, port=conf.port)
