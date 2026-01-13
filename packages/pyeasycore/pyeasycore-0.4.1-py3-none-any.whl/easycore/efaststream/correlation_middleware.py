# -*- coding: utf-8 -*-
from typing import Any

from faststream import BaseMiddleware
from faststream.rabbit import RabbitMessage
from faststream.types import AsyncFunc, DecodedMessage

from ..elogger import get_correlation_id, set_correlation_id


class CorrelationIdMiddlewareFaststream(BaseMiddleware):
    async def on_consume(self, msg: RabbitMessage) -> DecodedMessage:
        if msg.correlation_id:
            set_correlation_id(msg.correlation_id)
        return await super().on_consume(msg)

    async def publish_scope(
        self,
        call_next: "AsyncFunc",
        msg: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        cid = get_correlation_id()
        if cid:
            kwargs.update({"correlation_id": cid})
        return await super().publish_scope(call_next, msg, *args, **kwargs)
