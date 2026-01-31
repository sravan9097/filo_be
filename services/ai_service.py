"""AI service for Gemini (Google Generative AI) reasoning and prompt building."""
from typing import List, Dict, Optional
import google.generativeai as genai
import logging
from config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.main_model)
        self.summarize_model = genai.GenerativeModel(settings.summarize_model)
    
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
            # Build prompt for summarization
            summary_prompt = """You are a summarization assistant. Summarize the GST-related conversation history, focusing on:
- Key GST questions asked
- Important GST advice provided (mention relevant Sections/Rules)
- Business context mentioned (state, business type, turnover if relevant)
- Any pending questions or unresolved issues
Keep the summary concise but comprehensive. Preserve all GST Act Sections, Rules, and Notifications mentioned.

Conversation to summarize:
"""
            
            # Add conversation messages
            for msg in conversation_messages:
                if msg.get("role") in ["user", "assistant"]:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    summary_prompt += f"\n{role}: {msg['content']}"
            
            # Get summary using cheaper model
            response = self.summarize_model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=500
                )
            )
            
            summary = response.text.strip()
            logger.info(f"Summarized {len(conversation_messages)} messages into summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing conversation: {str(e)}")
            # Fallback: return a simple note
            return f"Previous conversation with {len(conversation_messages)} messages (summary unavailable)"
    
    def build_messages_prompt(self, conversation_messages: List[Dict[str, str]], user_message: str, user_info: Optional[Dict] = None) -> str:
        """
        Build the prompt for Gemini API.
        Summarizes long conversation history if needed.
        
        Args:
            conversation_messages: Existing conversation messages from Supabase
            user_message: Latest user message
            user_info: Optional user information for context
            
        Returns:
            Complete prompt string for Gemini
        """
        # Start with system prompt
        prompt = self.build_system_prompt(user_info) + "\n\n"
        
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
                prompt += f"Previous conversation summary:\n{summary}\n\n"
            
            # Add recent messages (keep full context for recent exchanges)
            prompt += "Recent conversation:\n"
            for msg in recent_messages:
                if msg.get("role") in ["user", "assistant"]:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    prompt += f"{role}: {msg['content']}\n"
        else:
            # Add all conversation messages if within threshold
            if conversation_messages:
                prompt += "Conversation history:\n"
                for msg in conversation_messages:
                    if msg.get("role") in ["user", "assistant"]:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        prompt += f"{role}: {msg['content']}\n"
        
        # Add latest user message
        prompt += f"\nUser: {user_message}\nAssistant:"
        
        return prompt
    
    def get_completion(self, conversation_messages: List[Dict[str, str]], user_message: str, user_info: Optional[Dict] = None) -> str:
        """
        Get completion from Gemini API.
        
        Args:
            conversation_messages: Existing conversation messages
            user_message: Latest user message
            user_info: Optional user information for context
            
        Returns:
            Assistant's response text
        """
        try:
            prompt = self.build_messages_prompt(conversation_messages, user_message, user_info)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more deterministic, law-based responses
                    max_output_tokens=2000
                )
            )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")
