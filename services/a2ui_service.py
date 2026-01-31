"""A2UI (Agent-to-UI) response generation helpers."""
from typing import Dict, List, Any, Optional
import json


class A2UIBuilder:
    """Helper class to build A2UI protocol v0.8 responses."""
    
    def __init__(self):
        self.version = "0.8"
        self.surfaces = []
    
    def add_surface(self, surface_id: str, components: List[Dict[str, Any]]) -> 'A2UIBuilder':
        """Add a surface with components."""
        self.surfaces.append({
            "id": surface_id,
            "components": components
        })
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the A2UI message."""
        return {
            "version": self.version,
            "surfaces": self.surfaces
        }
    
    # Component builders
    @staticmethod
    def heading(component_id: str, text: str, level: int = 2) -> Dict[str, Any]:
        """Create a heading component."""
        return {
            "id": component_id,
            "type": "Heading",
            "level": level,
            "text": text
        }
    
    @staticmethod
    def text(component_id: str, text: str) -> Dict[str, Any]:
        """Create a text component."""
        return {
            "id": component_id,
            "type": "Text",
            "text": text
        }
    
    @staticmethod
    def text_input(
        component_id: str,
        label: str,
        value_path: str,
        placeholder: str = "",
        required: bool = False,
        disabled: bool = False
    ) -> Dict[str, Any]:
        """Create a text input component."""
        return {
            "id": component_id,
            "type": "TextInput",
            "label": label,
            "placeholder": placeholder,
            "value": value_path,
            "required": required,
            "disabled": disabled
        }
    
    @staticmethod
    def number_input(
        component_id: str,
        label: str,
        value_path: str,
        placeholder: str = "0",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        required: bool = False
    ) -> Dict[str, Any]:
        """Create a number input component."""
        component = {
            "id": component_id,
            "type": "NumberInput",
            "label": label,
            "placeholder": placeholder,
            "value": value_path,
            "required": required
        }
        if min_value is not None:
            component["min"] = min_value
        if max_value is not None:
            component["max"] = max_value
        return component
    
    @staticmethod
    def select(
        component_id: str,
        label: str,
        value_path: str,
        options: List[Dict[str, str]],
        required: bool = False
    ) -> Dict[str, Any]:
        """Create a select/dropdown component."""
        return {
            "id": component_id,
            "type": "Select",
            "label": label,
            "value": value_path,
            "options": options,
            "required": required
        }
    
    @staticmethod
    def checkbox(
        component_id: str,
        label: str,
        value_path: str
    ) -> Dict[str, Any]:
        """Create a checkbox component."""
        return {
            "id": component_id,
            "type": "Checkbox",
            "label": label,
            "value": value_path
        }
    
    @staticmethod
    def radio(
        component_id: str,
        label: str,
        value_path: str,
        options: List[Dict[str, str]],
        required: bool = False
    ) -> Dict[str, Any]:
        """Create a radio button group component."""
        return {
            "id": component_id,
            "type": "Radio",
            "label": label,
            "value": value_path,
            "options": options,
            "required": required
        }
    
    @staticmethod
    def date_input(
        component_id: str,
        label: str,
        value_path: str,
        required: bool = False
    ) -> Dict[str, Any]:
        """Create a date input component."""
        return {
            "id": component_id,
            "type": "DateInput",
            "label": label,
            "value": value_path,
            "required": required
        }
    
    @staticmethod
    def button(
        component_id: str,
        label: str,
        action_type: str,
        action_data: Dict[str, Any],
        variant: str = "primary",
        disabled: bool = False
    ) -> Dict[str, Any]:
        """Create a button component with action."""
        return {
            "id": component_id,
            "type": "Button",
            "label": label,
            "variant": variant,
            "disabled": disabled,
            "action": {
                "type": action_type,
                "data": action_data
            }
        }
    
    @staticmethod
    def stack(
        component_id: str,
        children: List[str],
        direction: str = "vertical",
        spacing: int = 2
    ) -> Dict[str, Any]:
        """Create a stack layout component."""
        return {
            "id": component_id,
            "type": "Stack",
            "direction": direction,
            "spacing": spacing,
            "children": children
        }
    
    @staticmethod
    def container(
        component_id: str,
        children: List[str]
    ) -> Dict[str, Any]:
        """Create a container layout component."""
        return {
            "id": component_id,
            "type": "Container",
            "children": children
        }


def parse_a2ui_action(message: str) -> Optional[Dict[str, Any]]:
    """
    Parse A2UI action from message string.
    
    Args:
        message: The message string (might be JSON or plain text)
        
    Returns:
        Parsed action dict with 'type' and 'data', or None if not an action
    """
    if not message or not message.strip():
        return None
    
    # Check if message is JSON (A2UI action)
    if message.strip().startswith('{'):
        try:
            action = json.loads(message)
            if isinstance(action, dict) and 'type' in action:
                return action
        except json.JSONDecodeError:
            pass
    
    return None


def create_response_with_a2ui(reply: str, a2ui_message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a chat response with both text and A2UI components.
    
    Args:
        reply: Plain text reply
        a2ui_message: A2UI message dict (from A2UIBuilder.build())
        
    Returns:
        Complete response dict for frontend
    """
    return {
        "success": True,
        "reply": reply,
        "a2ui_message": a2ui_message
    }
