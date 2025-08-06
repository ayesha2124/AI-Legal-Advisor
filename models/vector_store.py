import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorStore:
    def __init__(self, index_path="faiss_index.idx", chunk_path="chunks.pkl"):
        self.index_path = index_path
        self.chunk_path = chunk_path
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        self.index = None
        self.chunks = []

    def build_index_from_text(self, text):
        splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        self.chunks = splitter.split_text(text)

        embeddings = self.embedding_model.encode(self.chunks, show_progress_bar=True).astype("float32")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        # Save index and chunks
        faiss.write_index(self.index, self.index_path)
        with open(self.chunk_path, "wb") as f:
            pickle.dump(self.chunks, f)

    def load_index(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.chunk_path, "rb") as f:
            self.chunks = pickle.load(f)

    def search(self, query, top_k=3):
        if self.index is None or not self.chunks:
            self.load_index()

        q_embed = self.embedding_model.encode([query]).astype("float32")
        D, I = self.index.search(q_embed, top_k)
        return [self.chunks[i] for i in I[0]]
