"""
aiohttp demo server.
"""

import logging

from aiohttp import web

from smsdemo.constants import MDR_POST_PATH, SIGNATURE_HEADER_KEY, SMS_POST_PATH
from smsdemo.message import SMSMessage
from smsdemo.util import (
    get_expected_signature,
    ServerConfig,
    SMSSendError,
    async_send,
)


async def receive_and_echo_sms(request):
    """Accept, validate, and echo back an SMS delivery."""

    secret = request.app["secret"]

    raw_payload = await request.read()
    payload = await request.json()

    msg = SMSMessage.from_payload(payload)
    logging.info("Received message: %s", msg)

    signature = request.headers[SIGNATURE_HEADER_KEY]
    expected_signature = get_expected_signature(secret, signature, raw_payload)
    if signature != expected_signature:
        logging.error("Invalid signature: %s (expected %s)", signature, expected_signature)
        return web.HTTPBadRequest(text="Invalid signature")

    try:
        echo_msg = msg.echo_message()
        await async_send(echo_msg, secret)
    except SMSSendError as e:
        logging.error("Echo failed: %s", e)
        return web.HTTPBadGateway(text="Echo failed")

    logging.info("Echoed message: %s", echo_msg)
    return web.Response(text="Echo OK")


async def receive_and_log_mdr(request):
    """Accept, validate, and log an MDR delivery"""

    secret = request.app["secret"]

    raw_payload =  await request.read()
    payload = await request.json()

    logging.info("Received MDR: %s", payload)

    signature = request.headers[SIGNATURE_HEADER_KEY]
    expected_signature = get_expected_signature(secret, signature, raw_payload)
    if signature != expected_signature:
        logging.error("Invalid signature: %s (expected %s)", signature, expected_signature)
        return web.HTTPBadRequest(text="Invalid signature")

    return web.Response(text="MDR OK")


def run(conf: ServerConfig):
    """Run the aiohttp-based demo server."""

    app = web.Application()
    app["secret"] = conf.secret
    app.router.add_post(SMS_POST_PATH, receive_and_echo_sms)
    app.router.add_post(MDR_POST_PATH, receive_and_log_mdr)

    logging.info("SMS echo server (aiohttp) running on %s:%d", conf.host, conf.port)
    web.run_app(app, host=conf.host, port=conf.port)
