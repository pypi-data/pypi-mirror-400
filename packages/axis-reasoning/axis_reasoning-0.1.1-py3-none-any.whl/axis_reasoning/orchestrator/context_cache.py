"""
ContextCacheManager — Manages Gemini Context Caching state.
Tracks cache_id, expiration, and content hashes to enable multi-turn reuse.
"""

from __future__ import annotations

import json
import logging
import os
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from axis_reasoning.engine import Engine
    from axis_reasoning.planner.planner import SovereignPlanner

logger = logging.getLogger(__name__)

CACHE_DATA_PATH = "data/context_cache.json"
DEFAULT_TTL_HOURS = 1

class ContextCacheManager:
    def __init__(self):
        self.data_file = CACHE_DATA_PATH
        self._ensure_data_dir()
        self.state = self._load_state()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                logger.error(f"Failed to load context cache state: {e}")
        return {"caches": {}} # {agent_id: {content_hash: {cache_id: ID, expires_at: ISO}}}

    def _save_state(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save context cache state: {e}")

    def generate_content_hash(self, content: str) -> str:
        """Generates a stable hash for the content to use as a cache key."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_cache_id(self, agent_id: str, content: str) -> Optional[str]:
        """
        Retrieve a valid cache_id if exists and not expired.
        """
        content_hash = self.generate_content_hash(content)
        agent_caches = self.state["caches"].get(agent_id, {})
        cache_info = agent_caches.get(content_hash)
        
        if cache_info:
            expires_at = datetime.fromisoformat(cache_info["expires_at"])
            if expires_at > datetime.now(timezone.utc):
                logger.info(f"🎯 CACHE HIT for agent {agent_id} (hash: {content_hash[:8]})")
                return cache_info["cache_id"]
            else:
                logger.info(f"⏱️ CACHE EXPIRED for agent {agent_id}")
                # Clean up expired entry
                del self.state["caches"][agent_id][content_hash]
                self._save_state()
        
        logger.info(f"🌑 CACHE MISS for agent {agent_id}")
        return None

    def set_cache_id(self, agent_id: str, content: str, cache_id: str, ttl_hours: int = DEFAULT_TTL_HOURS):
        """
        Register a new cache_id.
        """
        content_hash = self.generate_content_hash(content)
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat()
        
        if agent_id not in self.state["caches"]:
            self.state["caches"][agent_id] = {}
            
        self.state["caches"][agent_id][content_hash] = {
            "cache_id": cache_id,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self._save_state()
        logger.info(f"💾 CACHE SAVED: {cache_id} for agent {agent_id}")

    def prune_expired(self):
        """Removes all expired entries from the cache state."""
        now = datetime.now(timezone.utc)
        count = 0
        for agent_id, agent_caches in list(self.state["caches"].items()):
            for content_hash, info in list(agent_caches.items()):
                if datetime.fromisoformat(info["expires_at"]) <= now:
                    del self.state["caches"][agent_id][content_hash]
                    count += 1
        if count > 0:
            self._save_state()
            logger.info(f"🧹 Pruned {count} expired context cache entries.")

# Global Instance
context_cache_manager = ContextCacheManager()
