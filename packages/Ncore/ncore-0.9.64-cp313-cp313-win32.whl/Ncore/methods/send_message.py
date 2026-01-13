from typing import overload

import Ncore

from Ncore import types


class SendMessage:
    @overload
    async def send_message(
        self,
        message: str,
        peer: types.InputPeerUser,
        random_id: int,
        entities: list[types.MessageEntity] | None = None,
        reply_to: types.InputReplyTo | None = None,
        reply_markup: types.ReplyMarkup | None = None,
        no_webpage: bool = False,
        silent: bool = False,
        background: bool = False,
        clear_draft: bool = False,
        noforwards: bool = False,
        update_stickersets_order: bool = False,
        invert_media: bool = False,
        allow_paid_floodskip: bool = False,
        schedule_date: int | None = None,
        send_as: types.InputPeer | None = None,
        quick_reply_shortcut: types.InputQuickReplyShortcut | None = None,
        effect: int | None = None,
        allow_paid_stars: int | None = None,
        suggested_post: types.SuggestedPost | None = None,
    ) -> dict:
        ...

    async def send_message(self, message, peer, random_id, **params):
        params["_"] = "messages.sendMessage"
        params["message"] = message
        params["peer"] = peer
        params["random_id"] = random_id
        return await self.session.invoke(params)
