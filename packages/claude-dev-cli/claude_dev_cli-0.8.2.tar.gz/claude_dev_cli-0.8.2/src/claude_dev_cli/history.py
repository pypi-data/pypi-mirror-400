"""Conversation history management for interactive mode."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class Message:
    """Represents a single message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class Conversation:
    """Represents a conversation with messages."""
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.conversation_id = conversation_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        message = Message(role, content)
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_summary(self, max_length: int = 100) -> str:
        """Get a summary of the conversation (first user message)."""
        for msg in self.messages:
            if msg.role == "user":
                summary = msg.content[:max_length]
                if len(msg.content) > max_length:
                    summary += "..."
                return summary
        return "(empty conversation)"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create from dictionary."""
        conv = cls(
            conversation_id=data["conversation_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        conv.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        return conv


class ConversationHistory:
    """Manages conversation history storage and retrieval."""
    
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_conversation_file(self, conversation_id: str) -> Path:
        """Get the file path for a conversation."""
        return self.history_dir / f"{conversation_id}.json"
    
    def save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation to disk."""
        file_path = self._get_conversation_file(conversation.conversation_id)
        with open(file_path, 'w') as f:
            json.dump(conversation.to_dict(), f, indent=2)
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a conversation from disk."""
        file_path = self._get_conversation_file(conversation_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Conversation.from_dict(data)
        except Exception:
            return None
    
    def list_conversations(
        self,
        limit: Optional[int] = None,
        search_query: Optional[str] = None
    ) -> List[Conversation]:
        """List all conversations, optionally filtered and limited."""
        conversations = []
        
        for file_path in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                conv = Conversation.from_dict(data)
                
                # Apply search filter if provided
                if search_query:
                    search_lower = search_query.lower()
                    found = False
                    for msg in conv.messages:
                        if search_lower in msg.content.lower():
                            found = True
                            break
                    if not found:
                        continue
                
                conversations.append(conv)
                
                if limit and len(conversations) >= limit:
                    break
            except Exception:
                continue
        
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        file_path = self._get_conversation_file(conversation_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_latest_conversation(self) -> Optional[Conversation]:
        """Get the most recent conversation."""
        conversations = self.list_conversations(limit=1)
        return conversations[0] if conversations else None
    
    def export_conversation(
        self,
        conversation_id: str,
        output_format: str = "markdown"
    ) -> Optional[str]:
        """Export a conversation to a specific format."""
        conv = self.load_conversation(conversation_id)
        if not conv:
            return None
        
        if output_format == "markdown":
            lines = [f"# Conversation: {conv.conversation_id}"]
            lines.append(f"\nCreated: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Updated: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            for msg in conv.messages:
                role_display = "**You:**" if msg.role == "user" else "**Claude:**"
                lines.append(f"\n## {role_display}\n")
                lines.append(msg.content)
                lines.append("")
            
            return "\n".join(lines)
        
        elif output_format == "json":
            return json.dumps(conv.to_dict(), indent=2)
        
        return None
