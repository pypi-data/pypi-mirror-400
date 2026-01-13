# File: src/iotopen_bridge/converters/mapping/function_to_topics.py

from ...models.lynx import FunctionX
from ...models.mqtt import Qos, TopicSpec


def function_to_topics(fx: FunctionX):
    out = {
        "read": TopicSpec(topic=fx.topic_read, qos=Qos.AT_MOST_ONCE, retain=False, purpose="read")
    }
    if fx.topic_set:
        out["set"] = TopicSpec(
            topic=fx.topic_set, qos=Qos.AT_LEAST_ONCE, retain=False, purpose="set"
        )
    return out
