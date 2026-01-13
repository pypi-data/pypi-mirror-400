import gc
import re

import torch

from pydialogue.baseline import serializers
from pydialogue.baseline.llm_base_policies import LLMPolicyBase, extract_from_tags, logger
from pydialogue.language import components as lc
from pydialogue.policies import base_policies as bp


class LLMPolicy(LLMPolicyBase):
    def __init__(self, player, database, main_model_kwargs, ser_model_kwargs, main_instr_filename, ser_instr_filename,
                 trimmer, model, tokenizer, device, gc_after=True, autoregressive=True, interrupt_dialogue=True,
                 dialogue=None):
        super().__init__(player, database, main_model_kwargs, ser_model_kwargs, main_instr_filename, ser_instr_filename,
                         trimmer, interrupt_dialogue, dialogue=dialogue)
        self.model = model
        self.model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.gc_after = gc_after
        self.autoregressive = autoregressive

    def execute(self, include_goal=False, **params):
        result = super().execute(include_goal, **params)
        if self.gc_after:
            gc.collect()
            torch.cuda.empty_cache()
        return result

    def generate_output(self, messages, model_kwargs):
        chat = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        tokenized_chat = self.tokenizer(chat, return_tensors="pt")
        tokenized_chat = {k: v.to(self.device) for k, v in tokenized_chat.items()}

        with torch.no_grad():
            main_outputs = self.model.generate(**tokenized_chat, **model_kwargs)

        if self.autoregressive:
            start_idx = tokenized_chat["input_ids"].shape[1]
        else:
            start_idx = 0

        output_str = self.tokenizer.decode(main_outputs[0][start_idx:], skip_special_tokens=True)
        return output_str


class LLMPolicyAlt(bp.Policy):

    def __init__(self, player, database, model, main_model_kwargs, ser_model_kwargs, tokenizer, device,
                 main_instr_filename, ser_instr_filename, max_context_len, gc_after=True, autoregressive=True, dialogue=None):
        super().__init__(player, dialogue)
        self.database = database
        self.model = model
        self.main_model_kwargs = main_model_kwargs
        self.ser_model_kwargs = ser_model_kwargs
        self.model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        with open(main_instr_filename, "r", encoding="utf-8") as file:
            content = file.read()
            self.main_instr = content
        with open(ser_instr_filename, "r", encoding="utf-8") as file:
            content = file.read()
            self.ser_instr = content
        self.messages_main = list()
        self.messages_main.append({'role': 'system', 'content': self.main_instr})
        tokenize_main_instr = tokenizer.apply_chat_template(self.messages_main, tokenize=False, add_generation_prompt=True)
        tokenize_main_instr = tokenizer(tokenize_main_instr, return_tensors="pt")
        self.num_main_instr = tokenize_main_instr["input_ids"].shape[1]
        self.messages_ser = list()
        self.messages_ser.append({'role': 'system', 'content': self.ser_instr})
        self.max_context_len = max_context_len
        self.gc_after = gc_after
        self.autoregressive = autoregressive
        self.last_context_id = 0

    def execute(self, include_goal=False, **params):
        """ Uses the model to utter a sentence. If there is an error in the self, an empty sentence is returned.

        """
        main_cleaned, output = None, None

        try:
            self.messages_main.append({'role': 'user', 'content': "\n".join(self.dialogue.dia_generator.context_strings[self.last_context_id:])})
            self.last_context_id = len(self.dialogue.dia_generator.context_strings)

            chat = self.tokenizer.apply_chat_template(self.messages_main, tokenize=False, add_generation_prompt=True)
            tokenized_chat = self.tokenizer(chat, return_tensors="pt")

            if tokenized_chat["input_ids"].shape[1] > self.max_context_len:
                main_instr_ids = tokenized_chat["input_ids"][:, 0:self.num_main_instr]
                main_instr_mask = tokenized_chat["attention_mask"][:, 0:self.num_main_instr]
                input_ids = tokenized_chat["input_ids"][:, -self.max_context_len+self.num_main_instr:]
                attention_mask = tokenized_chat["attention_mask"][:, -self.max_context_len+self.num_main_instr:]
                concatenated_input_ids = torch.cat([main_instr_ids, input_ids], dim=1).to(self.device)
                concatenated_attention_mask = torch.cat([main_instr_mask, attention_mask], dim=1).to(self.device)

                with torch.no_grad():
                    main_outputs = self.model.generate(input_ids=concatenated_input_ids, attention_mask=concatenated_attention_mask, **self.main_model_kwargs)
            else:
                tokenized_chat = {k: v.to(self.device) for k, v in tokenized_chat.items()}
                with torch.no_grad():
                    main_outputs = self.model.generate(**tokenized_chat, **self.main_model_kwargs)

            if self.autoregressive:
                start_idx = tokenized_chat["input_ids"].shape[1]
            else:
                start_idx = 0

            main_output_str = self.tokenizer.decode(main_outputs[0][start_idx:], skip_special_tokens=True)
            self.messages_main.append({'role': 'assistant', 'content': main_output_str})

            main_cleaned = extract_from_tags("next_response", main_output_str)
            if main_cleaned is not None:
                self.messages_ser.append({'role': 'user', 'content': "<input>" + main_cleaned + "</input>"})
                if main_cleaned.strip() != "":
                    tokenized_input = self.tokenizer.apply_chat_template([self.messages_ser[0], self.messages_ser[-1]], tokenize=False, add_generation_prompt=True)
                    tokenized_input = self.tokenizer(tokenized_input, return_tensors="pt")
                    tokenized_input = {k: v.to(self.device) for k, v in tokenized_input.items()}

                    with torch.no_grad():
                        ser_outputs = self.model.generate(**tokenized_input, **self.ser_model_kwargs)

                    if self.autoregressive:
                        start_idx = tokenized_input["input_ids"].shape[1]
                    else:
                        start_idx = 0

                    ser_output_str = self.tokenizer.decode(ser_outputs[0][start_idx:], skip_special_tokens=True)
                    self.messages_ser.append({'role': 'assistant', 'content': ser_output_str})

                    ser_cleaned = extract_from_tags("output", ser_output_str)
                    if ser_cleaned is not None:
                        ser_cleaned = re.sub(r"\s+", "", ser_cleaned)
                        output = ser_cleaned.split(",")
                else:
                    self.messages_ser.append({'role': 'assistant', 'content': ''})
            else:
                self.messages_ser.append({'role': 'user', 'content': main_output_str})
                self.messages_ser.append({'role': 'assistant', 'content': ''})

        except Exception as err:
            logger.error(err, exc_info=True)
        finally:
            for name in ["tokenized_chat", "tokenized_input", "main_outputs", "ser_outputs", "concatenated_input_ids", "concatenated_attention_mask"]:
                if name in locals():
                    del locals()[name]
            if self.gc_after:
                gc.collect()
                torch.cuda.empty_cache()

        if main_cleaned is not None and main_cleaned.strip() == "":
            # an empty sentence. the player is waiting for other players.
            unconverted = lc.Sentence(speaker=self.player)
        else:
            if output is not None:
                try:
                    unconverted = serializers.deserialize(output, self.dialogue.dia_generator.world)
                    if unconverted is not None:
                        unconverted = self.database.query_sentence(unconverted.describers, speaker=self.player)
                except Exception as err:
                    logger.error(err, exc_info=True)
                    unconverted = None
            else:
                unconverted = None

        if unconverted is not None:
            unconverted.trusted_source = False

        if include_goal is False:
            return unconverted

        return unconverted, None

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


class ChatTrimmer:
    def __init__(self, tokenizer, max_input_tokens, encode_kwargs=None, per_message_overhead=6):
        self.tokenizer = tokenizer
        self.max_input_tokens = max_input_tokens
        self.encode_kwargs = encode_kwargs if encode_kwargs is not None else {}
        self.per_message_overhead = per_message_overhead

    def count_tokens(self, text):
        return len(self.tokenizer.encode(text, **self.encode_kwargs))

    def encode_text(self, text):
        return self.tokenizer.encode(text, **self.encode_kwargs)

    def decode_text(self, tokens):
        return self.tokenizer.decode(tokens)

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
                remaining = self.max_input_tokens - total_tokens - self.per_message_overhead
                if remaining > 0:
                    encoded = self.encode_text(msg["content"])
                    partial = self.decode_text(encoded[-remaining:])
                    trimmed.insert(0, {
                        "role": msg["role"],
                        "content": "[...] " + partial
                    })
                    total_tokens += remaining + self.per_message_overhead
                break

        if system_msg:
            trimmed.insert(0, system_msg)

        return trimmed
