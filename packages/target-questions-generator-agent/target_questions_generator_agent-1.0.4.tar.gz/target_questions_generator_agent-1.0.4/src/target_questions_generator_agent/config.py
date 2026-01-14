"""
Configuration for the Target Questions Generator Agent.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os
from typing import Dict, Any, Optional, List


class TargetQuestionsGeneratorConfig(BaseSettings):
    """Configuration settings for the Target Questions Generator Agent."""
    
    model_config = ConfigDict(
        env_prefix="TARGET_QUESTIONS_GENERATOR_",
        case_sensitive=False
    )
    
    # AI Provider Configuration
    ai_provider: str = Field(
        default=os.getenv("LLM_PROVIDER", "openai"),
        description="AI provider to use (e.g., openai, anthropic, etc.)"
    )
    ai_task_type: str = Field(
        default="suggestions_generator",
        description="Task type for AI requests"
    )
    model_name: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        description="AI model to use (e.g., gpt-4, claude-2, etc.)"
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="AI model temperature"
    )
    max_tokens: int = Field(
        default=4000,
        ge=100,
        le=8000,
        description="Maximum tokens for AI response"
    )
    api_key: str = Field(
        default=os.getenv("LLM_API_KEY", ""),
        description="API key for the LLM provider"
    )

