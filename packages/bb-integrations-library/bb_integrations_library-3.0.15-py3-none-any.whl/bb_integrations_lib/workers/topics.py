WORKER_BACKGROUND_REQUEST = "worker.background.request"
"""The Kafka topic that is used to send requests to background workers."""
WORKER_BACKGROUND_RESPONSE = "worker.background.response"
"""The Kafka topic that background workers will use to reply with status updates."""
WORKER_IMMEDIATE_REQUEST = "worker.immediate.request"
"""The Kafka topic that immediate (semi-synchronous / RPC) worker requests are sent to."""
WORKER_IMMEDIATE_RESPONSE = "worker.immediate.response"
"""The Kafka topic that immediate (semi-synchronous / RPC) worker responses are sent to."""
WORKER_CROSSROADS_REQUEST = "worker.crossroads.request"
"""The Kafka topic that crossroads worker requests are sent to."""
WORKER_CROSSROADS_RESPONSE = "worker.crossroads.response"
"""The Kafka topic that crossroads workers will send responses to."""


def build_topic(namespace: str, topic: str) -> str:
    """
    Builds a Kafka topic string in a consistent way using a namespace (usually rita or rita-test) and a topic name.
    See the constants in bb_integrations_lib.workers.topics for topic names.
    """
    return f"{namespace}.{topic}"
