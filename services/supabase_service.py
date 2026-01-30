"""Supabase service for database operations."""
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from supabase.client import SupabaseException
from config import settings


class SupabaseService:
    """Service for interacting with Supabase database."""
    
    def __init__(self):
        """Initialize Supabase service (client created lazily)."""
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get or create Supabase client (lazy initialization)."""
        if self._client is None:
            try:
                # Validate settings before creating client
                if not settings.supabase_url:
                    raise ValueError("SUPABASE_URL is not set in environment variables")
                if not settings.supabase_key:
                    raise ValueError("SUPABASE_KEY is not set in environment variables")
                
                
                self._client = create_client(settings.supabase_url, settings.supabase_key)
            except SupabaseException as e:
                raise ValueError(
                    f"Failed to create Supabase client: {str(e)}\n"
                ) from e
            except Exception as e:
                raise ValueError(f"Error initializing Supabase client: {str(e)}") from e
        
        return self._client
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch conversation from Supabase.
        
        Args:
            conversation_id: UUID of the conversation
            
        Returns:
            Conversation record with messages, or None if not found
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] Querying conversations table - conversation_id: {conversation_id}, supabase_url: {settings.supabase_url[:30]}...")
        try:
            response = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
            logger.info(f"[DEBUG] Supabase response - has_data: {bool(response.data)}, data_length: {len(response.data) if response.data else 0}")
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"[DEBUG] Supabase query exception - error: {str(e)}, type: {type(e).__name__}", exc_info=True)
            raise Exception(f"Error fetching conversation: {str(e)}")
    
    def update_conversation_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Update conversation messages in Supabase.
        
        Args:
            conversation_id: UUID of the conversation
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            response = self.client.table("conversations").update({
                "messages": messages,
                "updated_at": "now()"
            }).eq("id", conversation_id).execute()
            
            return response.data is not None
        except Exception as e:
            raise Exception(f"Error updating conversation messages: {str(e)}")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user information from Supabase.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User record with business details, or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            raise Exception(f"Error fetching user: {str(e)}")
    
    def create_conversation(self, conversation_id: str, user_id: str, initial_message: Dict[str, str]) -> bool:
        """
        Create a new conversation in Supabase.
        
        Args:
            conversation_id: UUID of the conversation
            user_id: UUID of the user
            initial_message: First message dictionary with 'role' and 'content'
            
        Returns:
            True if creation successful, False otherwise
        """
        try:
            response = self.client.table("conversations").insert({
                "id": conversation_id,
                "user_id": user_id,
                "messages": [initial_message]
            }).execute()
            
            return response.data is not None
        except Exception as e:
            raise Exception(f"Error creating conversation: {str(e)}")
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all conversations for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of conversation records, ordered by updated_at descending
        """
        try:
            response = self.client.table("conversations").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            raise Exception(f"Error fetching user conversations: {str(e)}")


# Global service instance
supabase_service = SupabaseService()

