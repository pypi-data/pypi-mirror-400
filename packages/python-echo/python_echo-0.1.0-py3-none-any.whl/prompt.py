NON_STRICT_IMT = """
Based on the following message, infer the general topic of the conversation.

Guidelines:
- Provide a concise, high-level topic.
- Do not be overly literal or specific to individual entities.
  (e.g., for "What sound does a dog make?", the topic may be "Animals" or "Animal behavior", not "Dog".)
- Prefer broader conceptual categories when appropriate.
- Be cautious with ambiguous inputs and avoid overly narrow topics.

Message:
{message}
"""

STRICT_IMT = """
Based on the following message, infer the specific, literal topic of the conversation.

Guidelines:
- Provide a concise topic directly tied to the main subject of the message.
- Be precise and avoid broad conceptual categories.
- Focus on the exact entities, objects, or concepts mentioned.
  (e.g., for "What sound does a dog make?", the topic should be "Dog Sounds" or "Dog", not "Animals".)
- Avoid ambiguity; choose the most literal, message-specific interpretation.

Message:
{message}
"""

NON_STRICT_NMT = """
Based on the following {n} messages, infer the general topic of the conversation.

Guidelines:
- Provide a concise, high-level topic that captures the overall intent of the messages.
- Do not be overly literal or specific to individual entities.
  (e.g., for "What sound does a dog make?", the topic may be "Animals" or "Animal behavior", not "Dog".)
- Prefer broader conceptual categories when appropriate.
- Be cautious with ambiguous inputs and avoid overly narrow topics.

Messages:
{messages}
"""

STRICT_NMT = """
Based on the following {n} messages, infer the specific, literal topic of the conversation.

Guidelines:
- Provide a concise topic directly tied to the main subjects of the messages.
- Be precise and avoid broad conceptual categories.
- Focus on the exact entities, objects, or concepts mentioned.
  (e.g., for "What sound does a dog make?", the topic should be "Dog Sounds" or "Dog", not "Animals".)
- Avoid ambiguity; choose the most literal, message-specific interpretation.

Messages:
{messages}
"""

NON_STRICT_ATM = """
The current conversation topic is: "{topic}"
A new message has been added: "{message}"

Guidelines:
- Determine if the new message affects the topic.
- If it does, provide a concise, high-level topic that captures the overall intent of the conversation.
- Do not be overly literal or specific to individual entities.
  (e.g., for "What sound does a dog make?", the topic may be "Animals" or "Animal behavior", not "Dog".)
- Prefer broader conceptual categories when appropriate.
- If the new message does not meaningfully shift the topic, return the current topic.

What is the updated topic?
"""

STRICT_ATM = """
The current conversation topic is: "{topic}"
A new message has been added: "{message}"

Guidelines:
- Determine if the new message changes the topic.
- If it does, provide the new topic in a precise, literal, message-specific way.
- Focus on the exact entities, objects, or concepts mentioned.
  (e.g., for "What sound does a dog make?", the topic should be "Dog Sounds" or "Dog", not "Animals".)
- Avoid broad or conceptual categories; remain strictly literal.
- If the topic does not change, return the current topic.

What is the updated topic?
"""

DISTIL_MESSAGE = """
Identify what this message is about.

Purpose:
- Extract the main topic or intent of the message.
- The full message is stored separately in an archive.
- This topic serves as a concise pointer to the archived message.
- Be specific enough to uniquely reference the message, but do not summarize it.

Message: {text}
"""

RELEVANCE = """
The current topic of the conversation is: {topic}.

Is the following text relevant to this topic? Answer strictly YES or NO.

Text: {text}
"""
