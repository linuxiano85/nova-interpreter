"""
Intent routing for Nova Prime voice assistant.

Simple rule-based intent routing with keyword mapping and entity extraction.
"""

import re
from typing import Dict, List, Optional, Tuple, Any


class IntentRouter:
    """Simple rule-based intent router with keyword mapping."""
    
    def __init__(self, intent_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize the intent router.
        
        Args:
            intent_mappings: Dictionary mapping keywords to intent names.
                           If None, uses default mappings.
        """
        self.intent_mappings = intent_mappings or self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, str]:
        """Get default intent mappings."""
        return {
            "apri ": "open_app",
            "open ": "open_app",
            "launch ": "open_app",
            "start ": "open_app",
            "volume": "system_volume",
            "volumen": "system_volume",  # Spanish
            "volume ": "system_volume",
            "sound": "system_volume",
        }
    
    def route_intent(self, text: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Route text to an intent and extract entities.
        
        Args:
            text: Input text to route
            
        Returns:
            Tuple of (intent_name, entities_dict) or (None, {}) if no match
        """
        text_lower = text.lower().strip()
        
        # Find matching intent
        intent_name = None
        for keyword, intent in self.intent_mappings.items():
            if keyword.lower() in text_lower:
                intent_name = intent
                break
        
        if not intent_name:
            return None, {}
        
        # Extract entities based on intent
        entities = self._extract_entities(intent_name, text_lower)
        
        return intent_name, entities
    
    def _extract_entities(self, intent_name: str, text: str) -> Dict[str, Any]:
        """Extract entities from text based on intent."""
        entities = {}
        
        if intent_name == "open_app":
            entities.update(self._extract_app_name(text))
        elif intent_name == "system_volume":
            entities.update(self._extract_volume_info(text))
        
        return entities
    
    def _extract_app_name(self, text: str) -> Dict[str, str]:
        """Extract app name from open_app intent."""
        # Remove trigger words
        for trigger in ["apri ", "open ", "launch ", "start "]:
            text = text.replace(trigger, "")
        
        # Clean up the remaining text
        app_name = text.strip()
        
        # Common app name mappings
        app_mappings = {
            "calcolatrice": "calculator",
            "calculadora": "calculator",  # Spanish
            "calc": "calculator",
            "notepad": "notepad",
            "blocco note": "notepad",
            "browser": "browser",
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "edge",
        }
        
        # Try to map to known app
        normalized_app = app_mappings.get(app_name, app_name)
        
        return {"app_name": normalized_app, "original_name": app_name}
    
    def _extract_volume_info(self, text: str) -> Dict[str, Any]:
        """Extract volume information from system_volume intent."""
        entities = {}
        
        # Check for action
        if any(word in text for word in ["set", "change", "imposta", "cambia"]):
            entities["action"] = "set"
        elif any(word in text for word in ["get", "show", "mostra", "qual"]):
            entities["action"] = "get"
        elif any(word in text for word in ["up", "increase", "su", "alza"]):
            entities["action"] = "increase"
        elif any(word in text for word in ["down", "decrease", "giù", "abbassa"]):
            entities["action"] = "decrease"
        else:
            entities["action"] = "get"  # Default action
        
        # Extract percentage if present
        percentage_match = re.search(r'(\d+)\s*%', text)
        if percentage_match:
            entities["volume_percent"] = int(percentage_match.group(1))
        
        # Extract number without percentage
        number_match = re.search(r'\b(\d+)\b', text)
        if number_match and "volume_percent" not in entities:
            number = int(number_match.group(1))
            if number <= 100:  # Assume it's a percentage
                entities["volume_percent"] = number
        
        return entities
    
    def add_intent_mapping(self, keyword: str, intent_name: str) -> None:
        """Add a new intent mapping."""
        self.intent_mappings[keyword] = intent_name
    
    def remove_intent_mapping(self, keyword: str) -> None:
        """Remove an intent mapping."""
        self.intent_mappings.pop(keyword, None)
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent names."""
        return list(set(self.intent_mappings.values()))