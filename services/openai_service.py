"""OpenAI service for GPT reasoning and prompt building."""
from typing import List, Dict, Optional
from openai import OpenAI
import logging
from config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.main_model
        self.summarize_model = settings.summarize_model  # Use cheaper model for summarization
    
    def build_system_prompt(self, user_info: Optional[Dict] = None) -> str:
        """
        Build the system prompt for GST CA Copilot.
        
        Args:
            user_info: Optional user information dictionary with business details
            
        Returns:
            System prompt string
        """
        base_prompt = """You are a Chartered Accountant specialized EXCLUSIVELY in Indian GST (Goods and Services Tax) law.

STRICT SCOPE RULES:
- You ONLY answer questions related to GST, CGST, SGST, IGST, GST compliance, GST registration, GST filing, GST rates, GST returns, Input Tax Credit (ITC), GST Act, GST Rules, GST Notifications, and GST-related tax matters.
- You MUST decline and politely redirect any questions that are NOT related to GST, such as:
  * Income Tax, TDS, TCS questions
  * Company Law, Corporate Law questions
  * General accounting or bookkeeping
  * Other tax laws (Customs, Excise, Service Tax - unless related to GST transition)
  * Personal questions or casual conversation
- When declining, say: "I specialize only in GST matters. Please ask me about GST-related questions such as GST registration, rates, compliance, filing, Input Tax Credit, or GST Act provisions."

GST-SPECIFIC RULES:
- Never assume missing values.
- If GST-related information is missing, ask specific follow-up questions.
- Always mention relevant GST Act Section, Rule, or Notification when answering.
- Be concise and professional.
- Do not hallucinate. If unsure about GST law, say so.
- Focus on Indian GST law only (CGST Act, SGST Act, IGST Act, GST Rules, and Notifications).

You are answering GST client queries using verified law-based reasoning. Stay strictly within GST domain."""
        
        # Add user context if available
        if user_info:
            context_parts = ["\n\nClient Context:"]
            
            if user_info.get("name"):
                context_parts.append(f"- Name: {user_info['name']}")
            
            if user_info.get("business_type"):
                context_parts.append(f"- Business Type: {user_info['business_type']}")
            
            if user_info.get("state"):
                context_parts.append(f"- State: {user_info['state']}")
            
            if user_info.get("gstin"):
                context_parts.append(f"- GSTIN: {user_info['gstin']}")
            
            if user_info.get("turnover"):
                turnover = user_info['turnover']
                # Format turnover for readability
                if turnover >= 10000000:
                    turnover_str = f"₹{turnover/10000000:.2f} crores"
                elif turnover >= 100000:
                    turnover_str = f"₹{turnover/100000:.2f} lakhs"
                else:
                    turnover_str = f"₹{turnover:,.0f}"
                context_parts.append(f"- Annual Turnover: {turnover_str}")
            
            context_parts.append("\nUse this context to provide more relevant and accurate GST advice. Consider state-specific rules, turnover thresholds, and business type when applicable.")
            
            base_prompt += "\n".join(context_parts)
        
        return base_prompt
    
    def summarize_conversation(self, conversation_messages: List[Dict[str, str]]) -> str:
        """
        Summarize conversation history using AI.
        
        Args:
            conversation_messages: List of conversation messages to summarize
            
        Returns:
            Summary string of the conversation
        """
        try:
            # Build messages for summarization
            summary_messages = [
                {
                    "role": "system",
                    "content": "You are a summarization assistant. Summarize the GST-related conversation history, focusing on:\n"
                               "- Key GST questions asked\n"
                               "- Important GST advice provided (mention relevant Sections/Rules)\n"
                               "- Business context mentioned (state, business type, turnover if relevant)\n"
                               "- Any pending questions or unresolved issues\n"
                               "Keep the summary concise but comprehensive. Preserve all GST Act Sections, Rules, and Notifications mentioned."
                }
            ]
            
            # Add conversation messages to summarize
            for msg in conversation_messages:
                if msg.get("role") in ["user", "assistant"]:
                    summary_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Get summary using cheaper model
            response = self.client.chat.completions.create(
                model=self.summarize_model,
                messages=summary_messages,
                temperature=0.2,  # Low temperature for consistent summarization
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Summarized {len(conversation_messages)} messages into summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing conversation: {str(e)}")
            # Fallback: return a simple note
            return f"Previous conversation with {len(conversation_messages)} messages (summary unavailable)"
    
    def build_messages(self, conversation_messages: List[Dict[str, str]], user_message: str, user_info: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        Build the message list for OpenAI API.
        Summarizes long conversation history if needed.
        
        Args:
            conversation_messages: Existing conversation messages from Supabase
            user_message: Latest user message
            user_info: Optional user information for context
            
        Returns:
            List of message dictionaries formatted for OpenAI API
        """
        messages = []
        
        # Add system prompt with user context
        messages.append({
            "role": "system",
            "content": self.build_system_prompt(user_info)
        })
        
        # Check if conversation history needs summarization
        if conversation_messages and len(conversation_messages) > settings.summarize_threshold:
            logger.info(f"Conversation has {len(conversation_messages)} messages, summarizing...")
            
            # Split into older messages (to summarize) and recent messages (to keep)
            keep_count = settings.keep_recent_messages
            older_messages = conversation_messages[:-keep_count] if len(conversation_messages) > keep_count else []
            recent_messages = conversation_messages[-keep_count:] if len(conversation_messages) > keep_count else conversation_messages
            
            # Summarize older messages
            if older_messages:
                summary = self.summarize_conversation(older_messages)
                # Add summary as a system-like message for context
                messages.append({
                    "role": "system",
                    "content": f"Previous conversation summary:\n{summary}"
                })
            
            # Add recent messages (keep full context for recent exchanges)
            for msg in recent_messages:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        else:
            # Add all conversation messages if within threshold
            if conversation_messages:
                for msg in conversation_messages:
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
        
        # Add latest user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def get_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Get completion from OpenAI API.
        
        Args:
            messages: List of message dictionaries for the conversation
            
        Returns:
            Assistant's response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more deterministic, law-based responses
                max_tokens=2000  # Increased for gpt-4o's enhanced capabilities
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

