import copy
import json
import re
from collections import OrderedDict
from typing import Any

from message import Message
from prompt import DISTIL_MESSAGE, RELEVANCE
from topic import (
    init_message_topic,
    nth_message_topic,
    anchored_topic_evaluation
)


class Record:
    def __init__(
            self,
            capacity: int = None,
            synapse: Any = None,  # A subclass of Synapse
            archive: bool = False,
            pertinence_filter: bool = False,
            topic_evaluation_algorithm: str = 'NSIMT'
    ):
        if capacity is not None and (not isinstance(capacity, int) or capacity <= 0):
            raise ValueError(f'Capacity must be a positive integer, got {capacity} !')

        if (archive or pertinence_filter) and not synapse:
            raise ValueError('Synapse must be provided for archiving or pertinence filtering !')

        if not self._is_topic_evaluation_algorithm_valid(topic_evaluation_algorithm):
            raise ValueError(
                f'Invalid topic evaluation algorithm {topic_evaluation_algorithm} !\n'
                f'Acceptable algorithms:\n'
                f'- Static algorithms: SIMT, NSIMT, SATE, NSATE\n'
                f'- Dynamic algorithms: SNMT<N>, NSNMT<N>, SATE<N>, NSATE<N> (e.g. SNMT2, NSNMT3, SATE4, NSATE5)\n'
            )

        if not topic_evaluation_algorithm and pertinence_filter:
            raise ValueError('Pertinence filtering requires topic evaluation algorithm !')

        self.standard_messages = OrderedDict()
        self.pinned_messages = OrderedDict()
        self.archived_messages = OrderedDict()
        self.topic = None
        self._capacity = capacity
        self._synapse = synapse
        self._archive = archive
        self._pertinence_filter = pertinence_filter
        self._topic_evaluation_algorithm = topic_evaluation_algorithm

    # noinspection PyMethodMayBeStatic
    def _is_topic_evaluation_algorithm_valid(self, algorithm: str) -> bool:
        """
        Check if a topic evaluation algorithm is valid

        - Static algorithms: SIMT, NSIMT, SATE, NSATE
        - Dynamic algorithms: SNMT<N>, NSNMT<N>, SATE<N>, NSATE<N>
          where <N> is a positive integer
        """
        # Static Algorithms
        if algorithm in {'SIMT', 'NSIMT', 'SATE', 'NSATE'}:
            return True

        # Dynamic Algorithms
        return bool(re.fullmatch(r'(SNMT|NSNMT|SATE|NSATE)(\d+)', algorithm))

    def _get_n_init_messages(self, n: int) -> list[Message] or None:
        """
        Return the oldest n messages from standard or pinned messages
        If a message is archived, return the original archived message
        If there are fewer than n messages, return None
        """
        messages = self.get_messages()
        if len(messages) < n:
            return None

        result = []
        for uid in messages[:n]:
            if uid in self.archived_messages:
                result.append(self.archived_messages[uid])
            elif uid in self.standard_messages:
                result.append(self.standard_messages[uid])
            elif uid in self.pinned_messages:
                result.append(self.pinned_messages[uid])
        return result

    def get_messages(self):
        """ Return Standard + Pinned messages """
        return list(self.standard_messages.keys()) + list(self.pinned_messages.keys())

    def evaluate_topic(self, message: Message = None) -> str or None:
        """
        Evaluate the topic of the conversation based on the selected topic evaluation algorithm

        Supports:
            - SIMT / NSIMT: strict or non-strict initial message topic evaluation
            - SNMT<N> / NSNMT<N>: strict or non-strict evaluation using the first N messages
            - SATE<N> / NSATE<N>: strict or non-strict anchored topic evaluation with N initial messages

        If the conversation topic is not yet set, uses the initial N messages for topic inference
        If a topic already exists, performs anchored evaluation using the new message

        Returns:
            The evaluated topic as a string, or None if it could not be determined
        """
        # Strict Init Message Topic (SIMT)
        if self._topic_evaluation_algorithm == 'SIMT' and not self.topic:
            return init_message_topic(message, self._synapse, strict=True)
        # Non-Strict Init Message Topic (NSIMT)
        elif self._topic_evaluation_algorithm == 'NSIMT' and not self.topic:
            return init_message_topic(message, self._synapse, strict=False)
        # Strict Nth Message Topic (SNMT)
        elif self._topic_evaluation_algorithm.startswith('SNMT') and not self.topic:
            match = re.fullmatch(r'SNMT(\d+)', self._topic_evaluation_algorithm)
            n = int(match.group(1))
            messages = self._get_n_init_messages(n)
            if messages:
                return nth_message_topic(messages, n, self._synapse, strict=True)
        # Non-Strict Nth Message Topic (NSNMT)
        elif self._topic_evaluation_algorithm.startswith('NSNMT') and not self.topic:
            match = re.fullmatch(r'NSNMT(\d+)', self._topic_evaluation_algorithm)
            n = int(match.group(1))
            messages = self._get_n_init_messages(n)
            if messages:
                return nth_message_topic(messages, n, self._synapse, strict=False)
        # Strict Anchored Topic Evaluation (SATE)
        elif self._topic_evaluation_algorithm.startswith('SATE'):
            match = re.fullmatch(r'SATE(\d+)', self._topic_evaluation_algorithm)
            n = int(match.group(1))
            messages = self._get_n_init_messages(n)
            if messages:
                if not self.topic:
                    return nth_message_topic(messages, n, self._synapse, strict=True)
                else:
                    return anchored_topic_evaluation(message, n, self._synapse, self.topic, strict=True)
        # Non-Strict Anchored Topic Evaluation (SATE)
        elif self._topic_evaluation_algorithm.startswith('NSATE'):
            match = re.fullmatch(r'NSATE(\d+)', self._topic_evaluation_algorithm)
            n = int(match.group(1))
            messages = self._get_n_init_messages(n)
            if messages:
                if not self.topic:
                    return nth_message_topic(messages, n, self._synapse, strict=False)
                else:
                    return anchored_topic_evaluation(message, n, self._synapse, self.topic, strict=False)
        return None

    def add(self, message: Message, pinned: bool = False) -> None:
        # Topic Evaluation
        if self._topic_evaluation_algorithm:
            self.topic = self.evaluate_topic(message) or self.topic
        #  Pertinence Filter
        if self._pertinence_filter and self.topic:
            return
        # Archive
        summarized_message = None
        if self._archive:
            summarized_message = self.archive_message(message)
        # Store
        if pinned:
            self.pinned_messages[message.uid] = summarized_message or message
        else:
            if self._capacity and len(self.standard_messages) >= self._capacity:
                self.standard_messages.popitem(last=False)
            self.standard_messages[message.uid] = summarized_message or message

    def pin_message(self, message_uid: str) -> None:
        if message_uid not in self.standard_messages:
            raise ValueError(f'Message with UID {message_uid} not found in standard messages !')
        message = self.standard_messages.pop(message_uid)
        self.pinned_messages[message_uid] = message

    def unpin_message(self, message_uid: str) -> None:
        """ Unpin a message """
        if message_uid not in self.pinned_messages:
            raise ValueError(f'Message with UID {message_uid} not found in pinned messages !')
        message = self.pinned_messages.pop(message_uid)
        self.add(message, pinned=False)

    def archive_message(self, message: Message) -> Message:
        """ Archive the original message, return a summarized version in the standard messages """
        summary = self._synapse.prompt(DISTIL_MESSAGE.format(text=message.text)) + ' ' + f'(Archived {message.uid})'  # noqa
        self.archived_messages[message.uid] = message
        summarized_message = copy.deepcopy(message)
        summarized_message.text = summary
        return summarized_message

    def restore_message(self, message_uid: str) -> None:
        """ Restore a message from the archive """
        message = self.archived_messages.pop(message_uid, None)
        if not message:
            raise ValueError(f'Message with UID {message_uid} not found in archive !')
        self.standard_messages.pop(message_uid, None)
        self.pinned_messages.pop(message_uid, None)
        self.add(message, pinned=False)

    def is_pertinence(self, message: Message) -> bool:
        """ Determine whether a message is relevant to the conversation topic """
        res = self._synapse.prompt(RELEVANCE.format(topic=self.topic, text=message.text))  # noqa
        prediction = ''.join(c for c in res if c.isalpha()).upper()

        if prediction == 'YES':
            return True
        elif prediction == 'NO':
            return False
        else:
            raise ValueError(f'Invalid Synapse response: "{res}" !')

    def __str__(self):
        return json.dumps(
            {
                'standard_messages': {uid: msg.to_dict() for uid, msg in self.standard_messages.items()},
                'pinned_messages': {uid: msg.to_dict() for uid, msg in self.pinned_messages.items()},
                'archived_messages': {uid: msg.to_dict() for uid, msg in self.archived_messages.items()},
                'topic': self.topic or 'Unspecified',
                'capacity': self._capacity or 'Off',
                'archive': 'On' if self._archive else 'Off',
                'classification': 'On' if self._pertinence_filter else 'Off'
            },
            indent=4
        )

    def __repr__(self):
        return self.__str__()
