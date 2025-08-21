"""Memory store for Nova Prime."""

import os
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryEvent:
    """Represents a memory event."""
    user_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: float
    event_id: str
    
    
class MemoryStore:
    """Simple memory store implementation."""
    
    def __init__(self):
        """Initialize the memory store."""
        self._data_dir = self._get_data_dir()
        self._events: List[MemoryEvent] = []
        self._load_events()
    
    def _get_data_dir(self) -> str:
        """Get the data directory for storing memory events."""
        # Use XDG_DATA_HOME if set, otherwise default to ~/.local/share
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home:
            base_dir = data_home
        else:
            base_dir = os.path.expanduser("~/.local/share")
        
        data_dir = os.path.join(base_dir, "nova_prime", "memory")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _load_events(self) -> None:
        """Load events from storage."""
        events_file = os.path.join(self._data_dir, "events.json")
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r') as f:
                    data = json.load(f)
                    for event_data in data:
                        event = MemoryEvent(**event_data)
                        self._events.append(event)
            except (json.JSONDecodeError, TypeError):
                # If file is corrupted, start fresh
                self._events = []
    
    def _save_events(self) -> None:
        """Save events to storage."""
        events_file = os.path.join(self._data_dir, "events.json")
        with open(events_file, 'w') as f:
            events_data = [asdict(event) for event in self._events]
            json.dump(events_data, f, indent=2)
    
    def add_event(self, user_id: str, event_type: str, data: Dict[str, Any]) -> MemoryEvent:
        """Add a new memory event."""
        import uuid
        
        event = MemoryEvent(
            user_id=user_id,
            event_type=event_type,
            data=data,
            timestamp=time.time(),
            event_id=str(uuid.uuid4())
        )
        
        self._events.append(event)
        self._save_events()
        return event
    
    def query(self, user_id: Optional[str] = None, event_type: Optional[str] = None, 
              limit: Optional[int] = None) -> List[MemoryEvent]:
        """Query memory events."""
        results = self._events
        
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        
        # Sort by timestamp, newest first
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            results = results[:limit]
        
        return results