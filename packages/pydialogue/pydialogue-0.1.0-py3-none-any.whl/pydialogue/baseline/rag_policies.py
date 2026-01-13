import faiss
import numpy as np
from . import llm_base_policies as mlp


class OAIRAGPolicy(mlp.OAIPolicy):
    def __init__(self, player, database, main_model_kwargs, ser_model_kwargs,
                 main_instr_filename, ser_instr_filename, trimmer, client,
                 sent_transformer, top_k, last_k, sort_indices=True):
        super().__init__(player, database, main_model_kwargs, ser_model_kwargs,
                         main_instr_filename, ser_instr_filename, trimmer, client)

        self.sent_transformer = sent_transformer
        self.top_k = top_k
        self.last_k = last_k

        embedding_dim = self.sent_transformer.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.last_context_id = 0
        self.sort_indices = sort_indices

    def add_to_index(self, sentences):
        """Add text and its embedding into FAISS index."""
        for sent in sentences:
            embedding = self.sent_transformer.encode(sent, normalize_embeddings=True)  # normalized for cosine similarity
            self.index.add(np.array([embedding], dtype=np.float32))

    def search_context(self, query, top_k):
        """Retrieve top_k most relevant texts using FAISS."""
        query_emb = self.sent_transformer.encode(query, normalize_embeddings=True)
        scores, ids = self.index.search(np.array([query_emb], dtype=np.float32), top_k)
        return [int(idx) for idx in ids[0] if idx != -1]

    def generate_main_output(self):

        sentences = self.dialogue.dia_generator.context_strings[self.last_context_id:]
        self.add_to_index(sentences)
        len_context = len(self.dialogue.dia_generator.context_strings)
        self.last_context_id = len_context

        top_k = min(len_context, self.top_k)
        query = self.dialogue.utterances[0].to_string()
        indices = self.search_context(query, top_k)

        last_k = min(len_context, self.last_k)
        indices += list(range(len_context - last_k, len_context))

        unique_indices = []
        for idx in indices:
            if idx not in unique_indices:
                unique_indices.append(idx)
        if self.sort_indices:
            unique_indices.sort()

        selected_sentences = [self.dialogue.dia_generator.context_strings[idx] for idx in unique_indices]
        chat = [self.messages_main[0], {'role': 'user', 'content': "\n".join(selected_sentences)}]

        main_output_str = self.generate_output(chat, self.main_model_kwargs)
        self.messages_main.append({'role': 'assistant', 'content': main_output_str})

        main_cleaned = mlp.extract_from_tags("next_response", main_output_str)

        return main_cleaned

