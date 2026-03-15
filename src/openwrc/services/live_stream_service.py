import asyncio
from collections import defaultdict
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.services.base_service import BaseService

# info held by live stream service
# - currently live stage
# - subscribers count
# - live data cache with ttl & invalidation logic

ChannelId = tuple[int, int, int]
STAGE_SPLIT_POLLER_TIMEOUT = (
    3 * 60 * 60 * 1000
)  # 3 hours in miliseconds for stage polling timeout
STAGE_SPLIT_POLLER_SLEEP = 30


class LiveStreamService(BaseService):

    def __init__(self):
        super().__init__()
        self._external_api_client = None
        self._subscriber_registry = None
        self._poll_task_registry = None

    @property
    def external_api_client(self):
        if not self._external_api_client:
            self._external_api_client = WrcApiClient()
        return self._external_api_client

    @property
    def subscriber_registry(self):
        if not self._subscriber_registry:
            self._subscriber_registry: defaultdict[ChannelId, set[asyncio.Queue]] = (
                defaultdict(set)
            )
        return self._subscriber_registry

    @property
    def poll_task_registry(self):
        if not self._poll_task_registry:
            self._poll_task_registry: defaultdict[
                ChannelId, asyncio.Task[any] | None
            ] = defaultdict(lambda: None)
        return self._poll_task_registry

    def _register_subscriber(self, channel_id: ChannelId, queue: asyncio.Queue):
        self.subscriber_registry[channel_id].add(queue)

    async def _unregister_subscriber(self, channel_id: ChannelId, queue: asyncio.Queue):
        self.subscriber_registry[channel_id].remove(queue)
        if not self.subscriber_registry[channel_id]:
            await self._stop_poll(channel_id=channel_id)

    async def _stop_poll(self, channel_id: ChannelId):
        task = self.poll_task_registry[channel_id]
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        del self.poll_task_registry[channel_id]

    async def _poll_live_stage(
        self,
    ):
        raise NotImplementedError("do not support auto finding a live stage")

    # TODO: polling split times alone does not capture stage finish times. A complete
    # live stage feed requires also polling the stage times endpoint
    # (/{event_id}/stages/{stage_id}/stagetimes.json) and merging the finish time as
    # the final split. Consider a combined subscribe_stage method that runs both
    # pollers concurrently and emits a unified event with splits + finish.
    async def _poll_split_point_data(self, channel_id: ChannelId):
        event_id, rally_id, stage_id = channel_id
        print(f"[poller] started for channel {channel_id}")
        try:
            while True:
                print(f"[poller] fetching split times for stage {stage_id}...")
                try:
                    split_point_results = await self.external_api_client.get_rally_stage_split_time_results(
                        event_id=event_id, rally_id=rally_id, stage_id=stage_id
                    )
                    print(
                        f"[poller] got response, broadcasting to {len(self.subscriber_registry[channel_id])} subscriber(s)"
                    )
                    for queue in self.subscriber_registry[channel_id]:
                        queue.put_nowait(split_point_results)
                except Exception as e:
                    print(f"[poller] fetch error: {e}")
                print(f"[poller] sleeping {STAGE_SPLIT_POLLER_SLEEP}s...")
                await asyncio.sleep(STAGE_SPLIT_POLLER_SLEEP)
        except asyncio.CancelledError as e:
            print(f"[poller] cancelled for channel {channel_id}")
            raise e

    async def _register_poll_task(self, channel_id: ChannelId):
        if self.poll_task_registry[channel_id]:
            return
        task = asyncio.create_task(self._poll_split_point_data(channel_id=channel_id))
        self.poll_task_registry[channel_id] = task

    async def subscribe(self, event_id: int, rally_id: int, stage_id: int):
        # register the subscriber
        channel_id: ChannelId = (event_id, rally_id, stage_id)
        queue = asyncio.Queue()
        self._register_subscriber(channel_id=channel_id, queue=queue)
        await self._register_poll_task(channel_id=channel_id)
        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self._unregister_subscriber(channel_id=channel_id, queue=queue)
        # push all available data

    async def unsubscribe(
        self,
    ):

        # close down service if no subscribers exist
        pass
