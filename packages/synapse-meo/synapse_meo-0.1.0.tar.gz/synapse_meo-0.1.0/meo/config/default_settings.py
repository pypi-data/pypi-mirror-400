import os
from typing import Dict, Any


class DefaultConfig:
    STORAGE_DIR: str = os.path.join(os.getcwd(), ".meo_storage")
    EPISODIC_MEMORY_FILE: str = os.path.join(STORAGE_DIR, "episodic_memory.jsonl")
    SEMANTIC_MEMORY_FILE: str = os.path.join(STORAGE_DIR, "semantic_memory.jsonl")
    SQLITE_DB_PATH: str = os.path.join(STORAGE_DIR, "meo.db")
    
    STORAGE_BACKEND: str = "jsonl"
    
    REWARD_WEIGHTS: Dict[str, float] = {
        "success": 1.0,
        "cost": -0.1,
        "latency": -0.05,
        "error_rate": -0.5,
    }
    
    SEMANTIC_COMPRESSION_THRESHOLD: int = 10
    
    ENABLE_POLICY_ADAPTATION: bool = True
    
    LOG_LEVEL: str = "INFO"
    
    EMBEDDING_MODEL: str = "default"
    EMBEDDING_DIM: int = 384
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("_") and not callable(value)
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DefaultConfig":
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
