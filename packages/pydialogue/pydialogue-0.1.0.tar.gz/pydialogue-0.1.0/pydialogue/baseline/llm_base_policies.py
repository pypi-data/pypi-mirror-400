#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module introduces classes and functions needed to implement the baseline model.
"""
import logging
import re
import math

from abc import ABC, abstractmethod

from . import serializers
from ..language import components as lc
from ..policies import base_policies as bp
from ..language import sentences as tsentences

logger = logging.getLogger(__name__)


def extract_from_tags(tag, text):
    """ Extracts the text inside the tags. """
    pattern = fr"<{tag}>(.*?)</{tag}>"  # Use f-string for dynamic tag
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1] if matches else None


class LLMPolicyBase(bp.Policy, ABC):
    def __init__(self, player, database, main_model_kwargs, ser_model_kwargs, main_instr_filename, ser_instr_filename,
                 trimmer, interrupt_dialogue=True, dialogue=None):
        super().__init__(player, dialogue)
        self.database = database
        self.main_model_kwargs = main_model_kwargs
        self.ser_model_kwargs = ser_model_kwargs
        with open(main_instr_filename, "r", encoding="utf-8") as file:
            content = file.read()
            main_instr = content
        with open(ser_instr_filename, "r", encoding="utf-8") as file:
            content = file.read()
            ser_instr = content
        self.messages_main = list()
        self.messages_main.append({'role': 'system', 'content': main_instr})
        self.messages_ser = list()
        self.messages_ser.append({'role': 'system', 'content': ser_instr})
        self.trimmer = trimmer
        self.last_context_id = 0
        self.last_save_idx = 0
        self.interrupt_dialogue = interrupt_dialogue

    def execute(self, include_goal=False, **params):
        """ Uses the model to utter a sentence. If there is an error in the self, an empty sentence is returned.
        """
        main_output_str, output = None, None

        try:
            main_output_str = self.generate_main_output()
        except Exception as err:
            logger.error(err, exc_info=True)
            if self.interrupt_dialogue:
                self.dialogue.interrupt = True

        try:
            output = self.generate_ser_output(main_output_str)
        except Exception as err:
            logger.error(err, exc_info=True)
            if self.interrupt_dialogue:
                self.dialogue.interrupt = True

        unconverted = self.deserialize(output)

        if unconverted is None:
            unconverted = lc.Sentence(speaker=self.player)

        last_utter = self.dialogue.utterances[-1]

        ser_error = tsentences.be(None, "was", None, ["an", "error", "in", "the", "serialization"])
        not_inacc = tsentences.be(["The", "sentence"],
                                  "is",
                                  "not",
                                  "inaccurate")
        not_inacc.parts.insert(4, lc.Word("necessarily"))
        not_inacc.describers[0].args["AM-ADV"] = "necessarily"
        ser_error = tsentences.cont([ser_error, not_inacc])

        if last_utter == ser_error and self.interrupt_dialogue:
            self.dialogue.interrupt = True
        if include_goal is False:
            return unconverted

        return unconverted, None

    @abstractmethod
    def generate_output(self, messages, model_kwargs):
        pass

    def generate_main_output(self):
        self.messages_main.append(
            {'role': 'user', 'content': "\n".join(self.dialogue.dia_generator.context_strings[self.last_context_id:])})
        self.last_context_id = len(self.dialogue.dia_generator.context_strings)

        trimmed_chat = self.trimmer.trim_messages(self.messages_main)
        main_output_str = self.generate_output(trimmed_chat, self.main_model_kwargs)
        self.messages_main.append({'role': 'assistant', 'content': main_output_str})

        return main_output_str

    def generate_ser_output(self, main_output_str):
        output = None
        main_cleaned = extract_from_tags("next_response", main_output_str)
        if main_cleaned is not None:
            self.messages_ser.append({'role': 'user', 'content': "<input>" + main_cleaned + "</input>"})
            if main_cleaned.strip() != "":
                ser_output_str = self.generate_output([self.messages_ser[0], self.messages_ser[-1]],
                                                      self.ser_model_kwargs)
                self.messages_ser.append({'role': 'assistant', 'content': ser_output_str})
                ser_cleaned = extract_from_tags("output", ser_output_str)
                if ser_cleaned is not None:
                    ser_cleaned = re.sub(r"\s+", "", ser_cleaned)
                    output = ser_cleaned.split(",")
            else:
                output = []
                self.messages_ser.append({'role': 'assistant', 'content': ''})
        else:
            self.messages_ser.append({'role': 'user', 'content': main_output_str})
            self.messages_ser.append({'role': 'assistant', 'content': ''})

        return output

    def deserialize(self, serialized_output):
        if not isinstance(serialized_output, list):
            return None

        if len(serialized_output) == 0:
            # an empty sentence. the player is waiting for other players.
            deserialized_sent = lc.Sentence(speaker=self.player)
        else:
            try:
                deserialized_sent = serializers.deserialize(serialized_output, self.dialogue.dia_generator.world)
                if deserialized_sent is not None:
                    deserialized_sent = self.database.query_sentence(deserialized_sent.describers, speaker=self.player)
            except Exception as err:
                logger.error(err, exc_info=True)
                deserialized_sent = None

        if deserialized_sent is not None:
            deserialized_sent.trusted_source = False

        return deserialized_sent

    def save_msgs_to_file(self, filename_main, filename_ser):
        messages = [self.messages_main, self.messages_ser]
        for idx, filename in enumerate([filename_main, filename_ser]):
            with open(filename, "a") as outfile:
                for msg in messages[idx][self.last_save_idx:]:
                    outfile.write(f"({msg['role']}, {msg['content']})\n")
        self.last_save_idx = len(self.messages_main)

        print(f"Messages saved to {filename_main} and {filename_ser}")

    def get_steps(self, **params):
        """ Returns the list of valid responses. """
        steps = self.execute(include_goal=False, **params)
        return steps

    def get_goal(self, **params):
        """ Returns the goal of the self. """
        return None

    def save_state(self):
        """ Saves the members that change with time when the dialogue is run. """
        return self.last_context_id

    def recover_state(self, state):
        """ Recovers the members that change with time when the dialogue is run. """
        self.last_context_id = state


class OAIPolicy(LLMPolicyBase):
    def __init__(self, player, database, main_model_kwargs, ser_model_kwargs,
                 main_instr_filename, ser_instr_filename, trimmer, client, interrupt_dialogue=True):
        super().__init__(player, database, main_model_kwargs, ser_model_kwargs, main_instr_filename, ser_instr_filename,
                         trimmer, interrupt_dialogue)

        self.client = client

    def generate_output(self, messages, model_kwargs):
        output = self.client.chat.completions.create(messages=messages, **model_kwargs)
        return output.choices[0].message.content


class ChatTrimmerBase:
    def __init__(self, max_input_tokens, chars_per_token=4, per_message_overhead=4):
        self.max_input_tokens = max_input_tokens
        self.chars_per_token = chars_per_token
        self.per_message_overhead = per_message_overhead

    def count_tokens(self, text):
        # Rough estimate based on average characters per token
        return math.ceil(len(text) / self.chars_per_token)

    def trim_messages(self, messages, preserve_system=True):
        system_msg = messages[0] if preserve_system and messages and messages[0]["role"] == "system" else None
        other_msgs = messages[1:] if system_msg else messages

        trimmed = []
        total_tokens = self.count_tokens(system_msg["content"]) + self.per_message_overhead if system_msg else 0

        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens(msg["content"]) + self.per_message_overhead
            if total_tokens + msg_tokens <= self.max_input_tokens:
                trimmed.insert(0, msg)
                total_tokens += msg_tokens
            else:
                remaining_tokens = self.max_input_tokens - total_tokens - self.per_message_overhead
                if remaining_tokens > 0:
                    remaining_chars = math.ceil(remaining_tokens * self.chars_per_token)
                    partial = msg["content"][-remaining_chars:]
                    trimmed.insert(0, {
                        "role": msg["role"],
                        "content": "[...] " + partial
                    })

                    total_tokens += remaining_tokens + self.per_message_overhead

                break

        if system_msg:
            trimmed.insert(0, system_msg)
        return trimmed




