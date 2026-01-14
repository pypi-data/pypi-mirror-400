WORKER_BACKGROUND_GROUP = "workers.background"
"""Kafka group where background workers consume cooperatively."""
WORKER_IMMEDIATE_GROUP = "workers.immediate"
"""Kafka group where immediate workers consume cooperatively."""
WORKER_CROSSROADS_GROUP = "workers.crossroads"
"""Kafka group where crossroads workers consume cooperatively."""

def build_group(namespace: str, group: str) -> str:
    """
    Builds a Kafka group ID string in a consistent way using a namespace (usually rita or rita-test) and a group name.
    See the constants in bb_integrations_lib.workers.groups for group names.
    """
    return f"{namespace}.{group}"
