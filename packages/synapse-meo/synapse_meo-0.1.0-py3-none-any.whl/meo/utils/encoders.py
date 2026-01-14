from abc import ABC, abstractmethod
from typing import List, Union, Optional
import hashlib
import numpy as np


class Encoder(ABC):
    @abstractmethod
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        pass


class SimpleEncoder(Encoder):
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            return self._encode_single(text)
        else:
            return np.array([self._encode_single(t) for t in text])
    
    def _encode_single(self, text: str) -> np.ndarray:
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        seed = int.from_bytes(hash_bytes[:4], byteorder='big')
        rng = np.random.RandomState(seed)
        
        embedding = rng.randn(self.dimension)
        
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def get_dimension(self) -> int:
        return self.dimension


class DummyTransformerEncoder(Encoder):
    def __init__(self, model_name: str = "default", dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension
        self._simple_encoder = SimpleEncoder(dimension)
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        return self._simple_encoder.encode(text)
    
    def get_dimension(self) -> int:
        return self.dimension


def embed_text(
    text: Union[str, List[str]],
    encoder: Optional[Encoder] = None,
    dimension: int = 384,
) -> np.ndarray:
    if encoder is None:
        encoder = SimpleEncoder(dimension=dimension)
    
    return encoder.encode(text)


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def find_most_similar(
    query_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    top_k: int = 5,
) -> List[tuple]:
    similarities = []
    
    for idx, candidate in enumerate(candidate_embeddings):
        similarity = cosine_similarity(query_embedding, candidate)
        similarities.append((idx, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]
