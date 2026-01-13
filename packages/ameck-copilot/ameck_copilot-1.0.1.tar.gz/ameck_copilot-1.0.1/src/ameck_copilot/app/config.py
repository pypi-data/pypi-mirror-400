"""
Configuration settings for Ameck Copilot
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Groq API Configuration (FREE)
    groq_api_key: str = ""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Model Configuration (Llama 3.3 70B - excellent reasoning)
    model_name: str = "llama-3.3-70b-versatile"
    max_tokens: int = 8192
    temperature: float = 0.7
    
    # Application Settings
    app_name: str = "Ameck Copilot"
    app_version: str = "1.0.0"
    
    # System prompt for the AI assistant
    system_prompt: str = """You are Ameck Copilot, an expert AI programming assistant powered by Claude Opus 4.5. You help developers with:

1. **Code Generation**: Write clean, efficient, and well-documented code in any programming language.
2. **Code Explanation**: Explain complex code snippets, algorithms, and design patterns clearly.
3. **Debugging**: Help identify and fix bugs, suggest improvements, and optimize code.
4. **Best Practices**: Recommend coding standards, design patterns, and architectural decisions.
5. **Documentation**: Generate comprehensive documentation, comments, and README files.
6. **Code Review**: Provide constructive feedback on code quality, security, and performance.
7. **Learning**: Teach programming concepts with examples and practical exercises.

Guidelines:
- Always provide accurate, well-tested code
- Use proper formatting with syntax highlighting
- Include comments explaining complex logic
- Suggest alternatives when appropriate
- Be concise but thorough
- Ask clarifying questions when the request is ambiguous
- Consider security, performance, and maintainability
- Use markdown formatting for better readability

When writing code:
- Use appropriate language idioms and conventions
- Handle edge cases and errors gracefully
- Write readable, self-documenting code
- Include type hints where applicable
- Follow the DRY (Don't Repeat Yourself) principle"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
