# rag.py
import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer

INDEX_PATH   = 'data/faiss_index.bin'
PROFILES_PATH = 'data/profiles.json'

class MatchRAG:
    def __init__(self):
        self.model    = SentenceTransformer('all-MiniLM-L6-v2')
        self.index    = None
        self.profiles = []

    def build_index(self, profiles: list):
        """Encode all profile bios and build FAISS index."""
        self.profiles = profiles
        bios    = [p['bio'] for p in profiles]
        vectors = self.model.encode(bios, show_progress_bar=True)
        vectors = vectors.astype(np.float32)
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        # Save to disk so next startup is instant
        self.save_index()
        print(f"✓ Built and saved FAISS index — {len(profiles)} profiles")

    def save_index(self):
        """Persist index to disk."""
        os.makedirs('data', exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

    def load_index(self) -> bool:
        """Load index from disk if it exists. Returns True if successful."""
        if os.path.exists(INDEX_PATH) and os.path.exists(PROFILES_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(PROFILES_PATH) as f:
                self.profiles = json.load(f)
            print(f"✓ Loaded FAISS index — {len(self.profiles)} profiles")
            return True
        return False

    def search(self, query_bio: str, top_k: int = 5) -> list:
        """Find top-k most similar profiles to the query bio."""
        if self.index is None:
            return []
        q = self.model.encode([query_bio]).astype(np.float32)
        faiss.normalize_L2(q)
        _, ids = self.index.search(q, top_k)
        return [self.profiles[i] for i in ids[0] if i >= 0]

    def add_profile(self, profile: dict):
        """Add a single new profile to the live index."""
        self.profiles.append(profile)
        vec = self.model.encode([profile['bio']]).astype(np.float32)
        faiss.normalize_L2(vec)
        self.index.add(vec)
        self.save_index()