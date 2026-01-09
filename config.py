"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # OpenAI configuration
    openai_api_key: Optional[str] = None
    
    # OpenAI model configuration
    summarize_model: str = "gpt-4o-mini"  # Cheap model for conversation summarization (fast and cost-effective)
    main_model: str = "gpt-4o"  # Main model for GST reasoning (most capable)
    
    # Conversation summarization configuration
    summarize_threshold: int = 10  # Summarize if conversation has more than this many messages
    keep_recent_messages: int = 4  # Keep this many recent messages before summarizing older ones
    
    # Application configuration
    app_name: str = "GST CA Copilot Backend"
    app_version: str = "1.0.0"
    cors_origins: List[str] = ["*"]  # Allow all origins by default
    
    class Config:
        # Check .env.local first (for local secrets), then .env
        env_file = [".env.local", ".env"]
        case_sensitive = False
    
    def validate_required(self) -> None:
        """Validate that all required settings are present."""
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_key:
            missing.append("SUPABASE_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        
        if missing:
            env_local = Path(".env.local")
            env_file = Path(".env")
            env_example = Path(".env.example")
            
            error_msg = f"\n❌ Missing required environment variables: {', '.join(missing)}\n\n"
            
            if not env_local.exists() and not env_file.exists():
                error_msg += f"📝 Neither .env.local nor .env file exists.\n"
                error_msg += f"   Create a .env.local or .env file with the following variables:\n"
                if env_example.exists():
                    error_msg += f"   $ cp .env.example .env.local\n\n"
            elif env_local.exists():
                error_msg += f"📝 The .env.local file exists but is missing required variables.\n\n"
            else:
                error_msg += f"📝 The .env file exists but is missing required variables.\n\n"
            
            error_msg += f"Required variables:\n"
            error_msg += f"  - SUPABASE_URL=your_supabase_project_url\n"
            error_msg += f"  - SUPABASE_KEY=your_supabase_anon_key\n"
            error_msg += f"  - OPENAI_API_KEY=your_openai_api_key\n"
            
            raise ValueError(error_msg)


# Global settings instance
try:
    settings = Settings()
    settings.validate_required()
except ValueError as e:
    import sys
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Configuration Error", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"{e}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)
    sys.exit(1)

