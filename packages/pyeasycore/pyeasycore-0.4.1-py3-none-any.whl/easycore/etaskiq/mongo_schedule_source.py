# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import List

import motor.motor_asyncio
from taskiq import ScheduleSource
from taskiq.scheduler.scheduler import ScheduledTask


class MongoScheduleSource(ScheduleSource):
    """A custom schedule source to load tasks from a MongoDB collection."""

    def __init__(
        self,
        mongo_url: str,
        db_name: str = "taskiq_db",
        collection_name: str = "taskiq_schedules",
    ):
        # 1. Store connection details
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.collection = self.client[db_name][collection_name]

    async def startup(self) -> None:
        """Create necessary indexes on startup."""
        # Ensure the task_name and cron fields exist, or create indexes as needed
        # For dynamic scheduling, you might want to index on fields relevant to your queries.
        await self.collection.create_index("schedule_id", unique=True)
        # print("MongoScheduleSource started and indexes ensured.")

    async def shutdown(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()
        # print("MongoScheduleSource shut down.")

    async def get_schedules(self) -> List[ScheduledTask]:
        """
        Retrieves all active scheduled tasks from the MongoDB collection.
        """
        schedules: List[ScheduledTask] = []
        # Find all documents in the collection
        cursor = self.collection.find({})

        async for doc in cursor:
            # 2. Construct the ScheduledTask object from the MongoDB document
            schedule_id = str(doc.get("schedule_id", doc.get("_id")))

            # The structure of the MongoDB document must match the ScheduledTask model
            sch = ScheduledTask(
                source=self,
                schedule_id=schedule_id,
                task_id=doc.get("task_id"),
                task_name=doc.get("task_name"),
                cron=doc.get("cron"),
                cron_offset=doc.get("cron_offset"),
                time=doc.get("time"),
                args=doc.get("args", []),
                kwargs=doc.get("kwargs", {}),
                # Add the schedule_id to labels for reference/removal
                labels={"schedule_id": schedule_id, **doc.get("labels", {})},
            )
            schedules.append(sch)

        return schedules

    # Optional: Add methods to dynamically insert/remove schedules
    async def add_schedule(
        self,
        schedule_task: ScheduledTask,
    ) -> None:
        """Add a NEW schedule. Fail if schedule_id already exists."""

        document = {
            "schedule_id": schedule_task.schedule_id,
            "task_id": schedule_task.task_id,
            "task_name": schedule_task.task_name,
            "cron": schedule_task.cron,
            "cron_offset": schedule_task.cron_offset,
            "time": schedule_task.time,
            "args": schedule_task.args or [],
            "kwargs": schedule_task.kwargs or {},
            "labels": schedule_task.labels or {},
            "created_at": datetime.now(tz=timezone.utc),
        }

        try:
            await self.collection.insert_one(document)
        except Exception as exc:
            raise exc

    # Note: When implementing interval/time schedules, you must handle the
    # removal after execution yourself using the post_send method.

    async def delete_schedule(self, schedule_id):
        await self.collection.delete_one({"schedule_id": schedule_id})
        # print(f"Deleted schedule: {schedule_id}")

    async def post_send(self, task: ScheduledTask) -> None:
        """
        Remove the schedule from MongoDB after it has been sent for execution.
        This is particularly useful for one-time schedules.
        """
        if task.time is not None:
            await self.delete_schedule(task.schedule_id)
