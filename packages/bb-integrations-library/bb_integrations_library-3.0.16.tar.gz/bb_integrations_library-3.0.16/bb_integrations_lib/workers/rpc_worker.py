from asyncio import Future, wait_for
from uuid import uuid4

from faststream.kafka.fastapi import KafkaRouter, Context

from bb_integrations_lib.models.rita.workers import WorkerRequest, WorkerResponse
from bb_integrations_lib.workers.topics import WORKER_IMMEDIATE_REQUEST, WORKER_IMMEDIATE_RESPONSE, build_topic


class RPCWorker:
    """An async interface for sending awaitable remote procedure calls over Kafka to workers."""
    def __init__(self, router: KafkaRouter, namespace: str) -> None:
        self.responses: dict[str, Future[WorkerResponse]] = {}
        self.reply_topic = build_topic(namespace, WORKER_IMMEDIATE_RESPONSE)
        self.send_topic = build_topic(namespace, WORKER_IMMEDIATE_REQUEST)

        self.router = router
        self.subscriber = self.router.subscriber(self.reply_topic)
        self.subscriber(self._handle_responses)

    async def _handle_responses(self, response: WorkerResponse, message = Context("message")) -> None:
        if future := self.responses.pop(message.correlation_id, None):
            future.set_result(response)

    async def request(
            self,
            runnable_name: str,
            tenant_name: str,
            send_topic: str | None = None,
            reply_topic: str | None = None,
            runnable_kwargs: dict | None = None,
            timeout: float = 30.0,
    ) -> WorkerResponse:
        """Send a request to be executed on a worker, but wait for the response with a configurable timeout."""
        send_topic = send_topic or self.send_topic
        reply_topic = reply_topic or self.reply_topic

        correlation_id = str(uuid4())
        future = self.responses[correlation_id] = Future[WorkerResponse]()

        # Use an originator of "other" so that status reports don't get reported to the backend task tracker.
        request = WorkerRequest(runnable_name=runnable_name, tenant_name=tenant_name, originator="other", runnable_kwargs=runnable_kwargs)
        await self.router.broker.publish(request, topic=send_topic, reply_to=reply_topic, correlation_id=correlation_id)

        try:
            response: WorkerResponse= await wait_for(future, timeout=timeout)
        except TimeoutError:
            _ = self.responses.pop(correlation_id, None)
            raise
        return response
