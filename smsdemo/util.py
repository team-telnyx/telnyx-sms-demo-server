"""
Various helpers.

This module contains the actual logic that does message validation and sending.
"""

import hmac
from base64 import b64encode
from collections import namedtuple
from datetime import datetime
from typing import Optional, Union

import requests
from aiohttp import ClientSession, ClientError

from smsdemo.constants import SMS_URL
from smsdemo.message import SMSMessage


ServerConfig = namedtuple("ServerConfig", "host port secret")


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

    r = requests.post(SMS_URL, headers=headers, data=data)

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
            async with session.post(SMS_URL, headers=headers, data=data) as resp:
                resp_text = await resp.text()
                if resp.status != 200:
                    raise SMSSendError(resp_text)
                return resp_text

    except ClientError as e:
        raise SMSSendError(e)


def get_expected_signature(secret: str, sig_header_value: str, raw_payload: bytes):
    """Extracts signature from the X-Telnyx-Signature header value"""

    epoch = get_epoch_from_sig_header_value(sig_header_value)
    expected_sig = webhook_sig_hs256(secret, raw_payload, epoch)

    return expected_sig


def get_epoch_from_sig_header_value(sig_header_value: str)-> str:
    """Extracts signature from the X-Telnyx-Signature header value"""

    sig_key_value = dict(param.split("=", 1) for param in sig_header_value.split(","))
    epoch = sig_key_value["t"]

    return epoch


def webhook_sig_hs256(secret: str, body: Union[bytes, str], epoch: Optional[str]=None) -> str:
    """Generate header-signature value for webhook. Header value
    consists of concatenation of an epoch timestamp seconds and
    an HMAC-SHA256 signature of the given payload as a JSON string.
    e.g. 't=1510139799,h=kWxvGoHJz3ToJLO1s86cBWu1ZV0hFNmVU45bY5BTlm8='

    Returns a webhook signature header value.
    """

    epoch = epoch or str(int(datetime.utcnow().timestamp()))
    body_bytes = body if isinstance(body, bytes) else body.encode("UTF-8")
    msg = epoch.encode("ascii") + b"." + body_bytes

    hash_bytes = hmac.new(secret.encode("utf-8"),
                          msg=msg,
                          digestmod="sha256").digest()
    b64_encoded_hash = b64encode(hash_bytes).decode("ascii")
    header_value = "t={},h={}".format(epoch, b64_encoded_hash)

    return header_value
