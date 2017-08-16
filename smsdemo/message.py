"""
Message implementation.
"""

from typing import Mapping


class SMSMessage:

    def __init__(self, from_: str, to: str, body: str):
        self.from_ = from_
        self.to = to
        self.body = body

    def __str__(self) -> str:
        return "SMS {}→{}: {}".format(self.from_, self.to, self.body)

    @classmethod
    def from_payload(cls, payload: Mapping) -> "SMSMessage":
        """Construct an SMSMessage from the given payload."""

        return cls(
            from_=payload["from"],
            to=payload["to"],
            body=payload["body"],
        )

    def as_dict(self) -> dict:
        return {
            "from": self.from_,
            "to": self.to,
            "body": self.body,
        }

    def echo_message(self) -> "SMSMessage":
        """Return a reversed version of the message for echoing."""

        return self.__class__(
            from_=self.to,
            to=self.from_,
            body="Echo: {}".format(self.body),
        )
