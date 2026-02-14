"""
Long-Term Memory Plugin for ANSE

Provides persistent knowledge storage and retrieval beyond the world model's event log.
Simple text-based implementation with semantic search via substring matching.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LongTermMemoryPlugin:
    """Persistent agent memory with semantic search."""

    name = "long_term_memory"
    description = "Persistent memory storage and semantic search"
    version = "1.0.0"

    def __init__(self):
        """Initialize memory store."""
        self.memories: Dict[str, Dict[str, Any]] = {}

    async def remember(self, text: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Store a fact or observation in memory.

        Args:
            text: Text to remember
            category: Optional category (e.g., 'observation', 'lesson', 'goal')

        Returns:
            Memory entry with ID
        """
        memory_id = str(uuid.uuid4())[:8]

        self.memories[memory_id] = {
            "id": memory_id,
            "text": text,
            "category": category or "general",
            "created_at": datetime.now().isoformat(),
            "accessed_count": 0
        }

        logger.info(f"[MEMORY] Remembered [{category or 'general'}] {memory_id}: {text[:50]}")

        return {
            "status": "success",
            "memory_id": memory_id,
            "message": f"Stored memory {memory_id}"
        }

    async def recall(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve memories matching a query.

        Args:
            query: Search term
            category: Optional category filter
            limit: Maximum results

        Returns:
            Dict with status and matching memory entries
        """
        results = []

        for memory_id, memory in self.memories.items():
            # Filter by category if specified
            if category and memory["category"] != category:
                continue

            # Simple substring match (can be upgraded to semantic similarity)
            if query.lower() in memory["text"].lower():
                memory["accessed_count"] += 1
                results.append(memory.copy())

        # Sort by relevance (accessed count) and return top N
        results.sort(key=lambda m: m["accessed_count"], reverse=True)
        logger.info(f"[MEMORY] Recalled {len(results[:limit])} memories for query: {query}")

        return {
            "status": "success",
            "results": results[:limit],
            "count": len(results[:limit])
        }

    async def forget(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a specific memory.

        Args:
            memory_id: ID of memory to delete

        Returns:
            Confirmation dict
        """
        if memory_id in self.memories:
            memory_text = self.memories[memory_id]["text"]
            del self.memories[memory_id]
            logger.info(f"[MEMORY] Forgot {memory_id}: {memory_text[:30]}")
            return {"status": "success", "message": f"Memory {memory_id} deleted"}
        else:
            return {"status": "error", "message": f"Memory {memory_id} not found"}

    async def list_memories(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        List all memories (optionally filtered by category).

        Args:
            category: Optional category filter

        Returns:
            Dict with status and list of memory entries
        """
        results = list(self.memories.values())

        if category:
            results = [m for m in results if m["category"] == category]

        logger.info(f"[MEMORY] Listed {len(results)} memories" + (f" (category: {category})" if category else ""))

        return {
            "status": "success",
            "memories": results,
            "count": len(results)
        }

    async def clear_memory(self) -> Dict[str, Any]:
        """
        Delete all memories (use with caution!).

        Returns:
            Confirmation dict with count deleted
        """
        count = len(self.memories)
        self.memories.clear()
        logger.warning(f"[MEMORY] CLEARED ALL {count} MEMORIES")

        return {
            "status": "success",
            "message": f"Cleared {count} memories",
            "count": count
        }
