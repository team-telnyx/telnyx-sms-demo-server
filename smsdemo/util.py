"""
Various helpers.

This module contains the actual logic that does message validation and sending.
"""

import base64
import hmac
from collections import namedtuple
from typing import Mapping

import requests
from aiohttp import ClientSession, ClientError

from smsdemo.constants import SEND_URL
from smsdemo.message import SMSMessage


ServerConfig = namedtuple("ServerConfig", "host port secret url")


class SMSSendError(Exception):
    pass


def sync_send(msg: SMSMessage, secret: str) -> str:
    """Synchronously send an SMSMessage, using the requests library.

    Returns:
        The response from the server.
    Raises:
        SMSSendError if sending failed.
    """

    headers = {"X-Profile-Secret": secret}
    data = msg.as_dict()

    r = requests.post(SEND_URL, headers=headers, data=data)

    # Check return code and log the action
    if r.status_code != requests.codes.ok:
        raise SMSSendError(r.text)

    return r.text


async def async_send(msg: SMSMessage, secret: str) -> str:
    """Asynchronously send an SMSMessage, using the aiohttp client.

    Returns:
        The response from the server.
    Raises:
        SMSSendError if sending failed.
    """

    headers = {"X-Profile-Secret": secret}
    data = msg.as_dict()

    try:
        async with ClientSession() as session:
            async with session.post(SEND_URL, headers=headers, data=data) as resp:
                resp_text = await resp.text()
                if resp.status != 200:
                    raise SMSSendError(resp_text)
                return resp_text

    except ClientError as e:
        raise SMSSendError(e)


def webhook_sig_hs256(secret: str, url: str, payload: Mapping) -> str:
    """Generate an HMAC-SHA256 signature for the given payload.

    Returns the base64-encoded signature as a str.
    """

    parts = [url]
    for item in sorted(payload.items()):
        parts.extend(item)
    msg = "".join(parts)

    h = hmac.new(secret.encode("utf-8"),
                 msg=msg.encode("utf-8"),
                 digestmod="sha256")
    return base64.b64encode(h.digest()).decode("ascii")  # return a str
