from __future__ import annotations

"""This module contains the types related to message echoes (SMB message echoes)."""

__all__ = ["MessageEcho"]

import dataclasses
import datetime
from typing import TYPE_CHECKING, ClassVar

from .base_update import BaseUpdate, RawUpdate
from .media import Audio, Document, Image, Sticker, Video
from .others import (
    Contact,
    Location,
    MessageType,
    Metadata,
    Order,
    Reaction,
    Unsupported,
)

if TYPE_CHECKING:
    from ..client import WhatsApp


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class MessageEcho(BaseUpdate):
    """
    A message echo - a message sent by the business (echoed back).

    This is received when a message is sent from the business phone number,
    allowing the application to track outgoing messages.

    - `'Message Echoes' on developers.facebook.com <https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components>`_

    Attributes:
        id: The message ID.
        metadata: The metadata of the message (to which phone number it was sent).
        type: The message type (See :class:`MessageType`).
        from_phone: The phone number that sent the message (the business phone number).
        to_phone: The phone number that received the message (the customer).
        timestamp: The timestamp when the message was sent (in UTC).
        text: The text of the message.
        image: The image of the message.
        video: The video of the message.
        sticker: The sticker of the message.
        document: The document of the message.
        audio: The audio of the message.
        caption: The caption of the message (Optional, only available for image, video, and document messages).
        reaction: The reaction of the message.
        location: The location of the message.
        contacts: The contacts of the message.
        order: The order of the message.
        unsupported: The unsupported content of the message.
    """

    type: MessageType
    from_phone: str
    to_phone: str
    metadata: Metadata
    text: str | None = None
    image: Image | None = None
    video: Video | None = None
    sticker: Sticker | None = None
    document: Document | None = None
    audio: Audio | None = None
    caption: str | None = None
    reaction: Reaction | None = None
    location: Location | None = None
    contacts: tuple[Contact, ...] | None = None
    order: Order | None = None
    unsupported: Unsupported | None = None

    _media_objs: ClassVar[dict] = {
        "image": Image,
        "video": Video,
        "sticker": Sticker,
        "document": Document,
        "audio": Audio,
    }
    _txt_fields = ("text", "caption")
    _webhook_field = "smb_message_echoes"

    @property
    def has_media(self) -> bool:
        """
        Whether the message has any media. (image, video, sticker, document or audio)

        - If you want to get the media of the message, use :attr:`~MessageEcho.media` instead.
        """
        return self.media is not None

    @property
    def media(
        self,
    ) -> Image | Video | Sticker | Document | Audio | None:
        """
        The media of the message, if any, otherwise ``None``. (image, video, sticker, document or audio)

        - If you want to check whether the message has any media, use :attr:`~MessageEcho.has_media` instead.
        """
        return next(
            (
                getattr(self, media_type)
                for media_type in self._media_objs
                if getattr(self, media_type)
            ),
            None,
        )

    @classmethod
    def _resolve_msg_content(
        cls,
        *,
        client: WhatsApp,
        msg_type: MessageType,
        msg: dict,
        timestamp: datetime.datetime,
        recipient: str,
    ) -> dict:
        match msg_type:
            case MessageType.TEXT:
                return {msg_type.value: msg[msg_type.value]["body"]}
            case (
                MessageType.IMAGE
                | MessageType.VIDEO
                | MessageType.STICKER
                | MessageType.DOCUMENT
                | MessageType.AUDIO
            ):
                return {
                    msg_type.value: cls._media_objs[msg_type.value].from_dict(
                        client=client,
                        data=msg[msg_type.value],
                        arrived_at=timestamp,
                        received_to=recipient,
                    )
                }
            case MessageType.REACTION:
                return {msg_type.value: Reaction.from_dict(msg[msg_type.value])}
            case MessageType.LOCATION:
                return {msg_type.value: Location.from_dict(msg[msg_type.value])}
            case MessageType.CONTACTS:
                return {
                    msg_type.value: tuple(
                        Contact.from_dict(c) for c in msg[msg_type.value]
                    )
                }
            case MessageType.ORDER:
                return {msg_type.value: Order.from_dict(msg[msg_type.value])}
            case MessageType.UNSUPPORTED:
                return (
                    {msg_type.value: Unsupported(type=msg["unsupported"]["type"])}
                    if "unsupported" in msg
                    else {}
                )
            case _:
                return {}

    @classmethod
    def from_update(cls, client: WhatsApp, update: RawUpdate) -> MessageEcho:
        msg = (value := (entry := update["entry"][0])["changes"][0]["value"])[
            "message_echoes"
        ][0]
        msg_type = msg["type"]
        metadata = Metadata.from_dict(value["metadata"])
        timestamp = datetime.datetime.fromtimestamp(
            int(msg["timestamp"]),
            datetime.timezone.utc,
        )
        msg_type_enum = MessageType(msg_type)
        msg_content = cls._resolve_msg_content(
            client=client,
            msg_type=msg_type_enum,
            msg=msg,
            timestamp=timestamp,
            recipient=metadata.phone_number_id,
        )
        return cls(
            _client=client,
            raw=update,
            id=msg["id"],
            type=msg_type_enum,
            **msg_content,
            from_phone=msg["from"],
            to_phone=msg["to"],
            timestamp=timestamp,
            metadata=metadata,
            caption=msg.get(msg_type, {}).get("caption")
            if msg_type in cls._media_objs
            else None,
        )

