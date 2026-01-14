from typing import Any

from message import Message
from prompt import (
    STRICT_IMT,
    NON_STRICT_IMT,
    STRICT_NMT,
    NON_STRICT_NMT,
    STRICT_ATM,
    NON_STRICT_ATM
)


def init_message_topic(message: Message, synapse: Any, strict: bool = False) -> str:
    """
    Init Message Topic (IMT) - The conversation topic is inferred solely from the content of the first message

    Strict: Very literal, narrow, tied closely to the specific message
    Non-Strict: Broader, conceptual, higher-level category
    """
    if strict:
        return synapse.prompt(STRICT_IMT.format(message=str(message.to_dict())))  # noqa
    return synapse.prompt(NON_STRICT_IMT.format(message=str(message.to_dict())))  # noqa


def nth_message_topic(messages: list[Message], n: int, synapse: Any, strict: bool = False) -> str:
    """
    Nth Message Topic (NMT) - The conversation topic is inferred from the content of the first N messages

    Strict: Very literal, narrow, tied closely to the specific message
    Non-Strict: Broader, conceptual, higher-level category
    """
    if strict:
        return synapse.prompt(STRICT_NMT.format(n=n, messages='\n'.join([str(message.to_dict()) for message in messages])))  # noqa
    return synapse.prompt(NON_STRICT_NMT.format(n=n, messages='\n'.join([str(message.to_dict()) for message in messages])))  # noqa


def anchored_topic_evaluation(message: Message, n: int, synapse: Any, topic: str, strict: bool = False) -> str:
    """
    Anchored Topic Evaluation (ATE) - The conversation topic is initially anchored using the first N messages
    Afterward, the topic is dynamically re-evaluated with each new message,
    allowing the model to adapt to topic shifts while maintaining stability around the original anchor
    A new message may or may not affect the topic, depending on whether it introduces a significant shift in content relative to the anchor

    Strict: Very literal, narrow, tied closely to the specific message
    Non-Strict: Broader, conceptual, higher-level category
    """
    if strict:
        return synapse.prompt(STRICT_ATM.format(n=n, topic=topic, message=str(message.to_dict())))  # noqa
    return synapse.prompt(NON_STRICT_ATM.format(n=n, topic=topic, message=str(message.to_dict())))  # noqa
