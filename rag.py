# rag.py
import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer

INDEX_PATH    = 'data/faiss_index.bin'
PROFILES_PATH = 'data/profiles.json'


def load_profiles(path: str = PROFILES_PATH) -> list:
    for encoding in ("utf-8", "cp1252"):
        try:
            with open(path, encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    with open(path) as f:
        return json.load(f)


class MatchRAG:
    def __init__(self):
        self.model    = SentenceTransformer('all-MiniLM-L6-v2')
        self.index    = None
        self.profiles = []

    def build_index(self, profiles: list):
        self.profiles = profiles
        bios    = [p.get('bio', '') for p in profiles]
        vectors = self.model.encode(bios, show_progress_bar=True)
        vectors = vectors.astype(np.float32)
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.save_index()
        print(f"✓ Built and saved FAISS index — {len(profiles)} profiles")

    def save_index(self):
        os.makedirs('data', exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

    def load_index(self) -> bool:
        if os.path.exists(INDEX_PATH) and os.path.exists(PROFILES_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            self.profiles = load_profiles(PROFILES_PATH)
            if self.index.ntotal != len(self.profiles):
                print(
                    f"⚠️ FAISS/profile mismatch — rebuilding index "
                    f"({self.index.ntotal} vectors, {len(self.profiles)} profiles)"
                )
                self.build_index(self.profiles)
            print(f"✓ Loaded FAISS index — {len(self.profiles)} profiles")
            return True
        return False

    def _gender_compatible(self, user: dict, candidate: dict) -> bool:
        """Simple rule: homme matches with femme and vice versa."""
        user_gender = user.get('gender', '').lower().strip()
        cand_gender = candidate.get('gender', '').lower().strip()

        if not user_gender or not cand_gender:
            return True  # no data = don't filter

        # Opposite genders only
        if user_gender == 'homme':
            return cand_gender == 'femme'
        if user_gender == 'femme':
            return cand_gender == 'homme'

        return True  # autre = no filter

    def search(self, query_bio: str, top_k: int = 5, user_profile: dict = None) -> list:
        if self.index is None:
            return []

        # Search extra to cover filtered-out results
        search_k = min(top_k * 4, len(self.profiles))
        q = self.model.encode([query_bio]).astype(np.float32)
        faiss.normalize_L2(q)
        _, ids = self.index.search(q, search_k)

        results = []
        for i in ids[0]:
            if i < 0 or i >= len(self.profiles):
                continue
            candidate = self.profiles[i]
            # Skip the user themselves
            if user_profile and candidate.get('id') == user_profile.get('id'):
                continue
            # Gender filter
            if user_profile and not self._gender_compatible(user_profile, candidate):
                continue
            results.append(candidate)
            if len(results) >= top_k:
                break

        return results

    def add_profile(self, profile: dict):
        """Add a single new profile to the live index."""
        if any(p.get('id') == profile.get('id') for p in self.profiles):
            return
        self.profiles.append(profile)
        if self.index is None or self.index.ntotal != len(self.profiles) - 1:
            self.build_index(self.profiles)
            return
        vec = self.model.encode([profile['bio']]).astype(np.float32)
        faiss.normalize_L2(vec)
        self.index.add(vec)
        self.save_index()
