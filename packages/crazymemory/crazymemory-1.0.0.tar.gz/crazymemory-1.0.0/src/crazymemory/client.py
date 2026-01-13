"""
CrazyMemory Core Client
The AI Operating System - Universal Memory Layer for all your AIs

Version: 1.0.0
"""

import requests
import json
import os
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

SDK_VERSION = "1.0.0"


class CrazyMemory:
    """
    Main CrazyMemory client - The AI Operating System
    
    Usage:
        from crazymemory import CrazyMemory
        
        memory = CrazyMemory(ai_source="my_ai")
        memory.sync()  # One line to connect all your AIs!
    """
    
    def __init__(
        self,
        api_url: str = None,
        api_key: Optional[str] = None,
        ai_source: str = "custom_ai",
        user_id: str = "default",
        debug: bool = False
    ):
        self.api_url = (api_url or os.getenv('CRAZYMEMORY_API_URL') or 'http://127.0.0.1:8000').rstrip('/')
        self.api_key = api_key or os.getenv('CRAZYMEMORY_API_KEY')
        self.ai_source = ai_source
        self.user_id = user_id
        self.debug = debug
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-NFX-Version': SDK_VERSION,
            'X-NFX-Agent': ai_source
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
        
        self._log(f"CrazyMemory SDK v{SDK_VERSION} initialized", {"ai_source": ai_source})
    
    def _log(self, message: str, data: Any = None):
        if self.debug:
            print(f"[CrazyMemory] {message}", data or "")
    
    # ============ CORE METHODS ============
    
    def sync(self) -> Dict[str, Any]:
        """
        ONE-LINE SYNC: Get all cross-AI context instantly
        This is the magic - one line to connect all your AIs
        """
        self._log("Syncing with Neural Fabric...")
        
        context = self.get_context("recent conversation", exclude_self=True)
        notes = self.get_notes()
        status = self.get_fabric_status()
        
        return {
            "success": True,
            "context_available": len(context) > 0,
            "context": context,
            "memories": len(context.split('\n')) if context else 0,
            "pending_notes": len(notes),
            "active_agents": list(status.get('active_agents', {}).keys()) if status else []
        }
    
    def remember(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Store a memory (alias for store)"""
        return self.store(content, metadata)
    
    def store(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Store a memory"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/memory/store",
                headers=self.headers,
                json={
                    "content": content,
                    "ai_source": self.ai_source,
                    "metadata": metadata or {}
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def recall(self, query: str, limit: int = 5, exclude_self: bool = False) -> List[Dict[str, Any]]:
        """Search memories (alias for search)"""
        return self.search(query, limit, exclude_self)
    
    def search(self, query: str, limit: int = 5, exclude_self: bool = False) -> List[Dict[str, Any]]:
        """Search all memories"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/memory/search",
                headers=self.headers,
                json={
                    "query": query,
                    "limit": limit,
                    "exclude_source": self.ai_source if exclude_self else None
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('memories', [])
        except Exception as e:
            return []
    
    def get_context(self, query: str, max_tokens: int = 2000, exclude_self: bool = True) -> str:
        """Get formatted context from other AIs"""
        memories = self.search(query, limit=5, exclude_self=exclude_self)
        
        if not memories:
            return ""
        
        context_parts = ["=== CRAZYMEMORY CONTEXT ===\n"]
        for mem in memories:
            source = mem.get('source', 'unknown')
            content = mem.get('content', '')
            similarity = mem.get('similarity', 0.0)
            context_parts.append(f"[{source.upper()} - {similarity:.0%}] {content}\n")
        
        context_parts.append("=== END CONTEXT ===")
        return "\n".join(context_parts)
    
    def sync_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Sync entire conversation"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/conversation/sync",
                headers=self.headers,
                json={"messages": messages, "ai_source": self.ai_source},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def leave_note(self, for_ai: str, message: str) -> Dict[str, Any]:
        """Leave note for another AI"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/notes",
                headers=self.headers,
                json={"from_agent": self.ai_source, "to_agent": for_ai, "note": message},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_notes(self) -> List[Dict[str, Any]]:
        """Get notes from other AIs"""
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/notes/{self.ai_source}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('notes', [])
        except Exception as e:
            return []
    
    def nfp_handoff(self, from_ai: str, recent_messages: List[Dict] = None) -> str:
        """Get NFP context from another AI"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/nfp/handoff",
                headers=self.headers,
                json={
                    "from_ai": from_ai,
                    "to_ai": self.ai_source,
                    "user_id": self.user_id,
                    "recent_messages": recent_messages or []
                },
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            return data.get('system_prompt', '')
        except Exception as e:
            return ""
    
    def predict_context(self, current_messages: List[Dict]) -> Dict[str, Any]:
        """Get predictive context loading"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/predictive/context",
                headers=self.headers,
                json={
                    "current_messages": current_messages,
                    "ai_source": self.ai_source,
                    "user_id": self.user_id
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"should_push": False, "error": str(e)}
    
    # ============ NEW V2 METHODS ============
    
    def register(self, capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Register this agent with the Neural Fabric
        Call this when your AI starts up
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/agents/register",
                headers=self.headers,
                json={
                    "name": self.ai_source,
                    "agent_type": "custom",
                    "capabilities": capabilities or ["chat"]
                },
                timeout=10
            )
            response.raise_for_status()
            self._log("Agent registered", {"agent_id": self.ai_source})
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_fabric_status(self) -> Optional[Dict[str, Any]]:
        """Get the status of the Neural Fabric"""
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/fabric/status",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log("Failed to get fabric status", str(e))
            return None
    
    def cross_ai_search(
        self, 
        query: str, 
        time_range_hours: int = 168, 
        exclude_self: bool = True
    ) -> Dict[str, Any]:
        """
        Search across ALL AI histories (the killer feature!)
        Returns memories grouped by AI source
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/memory/cross-ai-search",
                headers=self.headers,
                json={
                    "query": query,
                    "time_range_hours": time_range_hours,
                    "exclude_source": self.ai_source if exclude_self else None
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"query": query, "total_results": 0, "results_by_ai": {}, "error": str(e)}
    
    def broadcast(self, message: str, priority: str = "normal") -> Dict[str, Any]:
        """
        Broadcast a message to all connected AI agents
        priority: 'low', 'normal', 'high', 'critical'
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/agent/broadcast",
                headers=self.headers,
                json={
                    "from_agent": self.ai_source,
                    "message": message,
                    "priority": priority
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_session(
        self, 
        summary: str, 
        key_decisions: List[str] = None, 
        action_items: List[str] = None
    ) -> Dict[str, Any]:
        """
        Sync a conversation summary to the Fabric
        Use this at the end of a conversation session
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/session/sync",
                headers=self.headers,
                json={
                    "agent_id": self.ai_source,
                    "conversation_summary": summary,
                    "key_decisions": key_decisions or [],
                    "action_items": action_items or []
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_handoff(
        self, 
        to_ai: str, 
        task_summary: str,
        key_decisions: List[str] = None,
        action_items: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a handoff context for switching to another AI
        This notifies the target AI and provides them with context
        """
        handoff = {
            "from_ai": self.ai_source,
            "to_ai": to_ai,
            "task_summary": task_summary,
            "key_decisions": key_decisions or [],
            "action_items": action_items or [],
            "context_snapshot": self.get_context(task_summary, max_tokens=2000)
        }
        
        # Leave note for the target AI
        self.leave_note(to_ai, f"Handoff: {task_summary}")
        
        # Store the handoff
        self.store(f"[HANDOFF to {to_ai}] {task_summary}", {
            "type": "handoff",
            "to_ai": to_ai,
            "decisions": key_decisions,
            "action_items": action_items
        })
        
        return handoff


# Aliases for backwards compatibility
FabricClient = CrazyMemory
NeuralFabricX = CrazyMemory


def quick_sync(ai_source: str = "custom_ai") -> str:
    """Ultra-simple one-liner"""
    memory = CrazyMemory(ai_source=ai_source)
    return memory.get_context("recent conversation")


def fabric_aware(api_url: str = None, ai_source: str = "custom_ai"):
    """Decorator to make functions memory-aware"""
    memory = CrazyMemory(api_url=api_url, ai_source=ai_source)
    
    def decorator(func: Callable):
        def wrapper(user_input: str, *args, **kwargs):
            # Inject context
            kwargs['crazymemory_context'] = memory.get_context(user_input)
            
            # Call function
            result = func(user_input, *args, **kwargs)
            
            # Auto-store
            memory.store(f"User: {user_input}\nAI: {result}")
            
            return result
        return wrapper
    return decorator
