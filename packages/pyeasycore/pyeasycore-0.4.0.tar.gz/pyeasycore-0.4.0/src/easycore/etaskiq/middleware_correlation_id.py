# -*- coding: utf-8 -*-
from taskiq import TaskiqMessage, TaskiqMiddleware

from ..elogger import get_correlation_id, set_correlation_id


class CorrelationIdMiddlewareWorker(TaskiqMiddleware):
    async def pre_send(self, message: TaskiqMessage) -> TaskiqMessage:
        cid = get_correlation_id()
        message.labels["correlation_id"] = cid
        return message

    async def pre_execute(self, message: TaskiqMessage) -> None:
        cid = message.labels.get("correlation_id")
        if cid:
            set_correlation_id(cid)
        return message
