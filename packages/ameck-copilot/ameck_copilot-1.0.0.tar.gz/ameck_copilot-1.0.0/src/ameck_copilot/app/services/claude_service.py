"""
Claude AI Service - Handles all interactions with Anthropic's Claude API
"""

import anthropic
from typing import AsyncGenerator, List, Optional
import json
import logging

from app.config import get_settings
from app.models import Message, MessageRole

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service class for Claude API interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        self.async_client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)
    
    def _format_messages(self, conversation_history: List[Message], current_message: str) -> List[dict]:
        """Format conversation history for Claude API"""
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg.role != MessageRole.SYSTEM:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send a chat message and get a response (non-streaming)"""
        
        messages = self._format_messages(conversation_history or [], message)
        
        try:
            response = await self.async_client.messages.create(
                model=self.settings.model_name,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature,
                system=self.settings.system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def chat_stream(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Send a chat message and stream the response"""
        
        messages = self._format_messages(conversation_history or [], message)
        
        try:
            async with self.async_client.messages.stream(
                model=self.settings.model_name,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature,
                system=self.settings.system_prompt,
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except anthropic.APIError as e:
            logger.error(f"Claude API streaming error: {e}")
            raise
    
    async def analyze_code(
        self,
        code: str,
        operation: str,
        language: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Analyze code based on the specified operation"""
        
        operation_prompts = {
            "explain": f"Please explain the following code in detail. Break down what each part does and explain the overall logic:\n\n```{language or ''}\n{code}\n```",
            
            "review": f"Please review the following code for quality, best practices, potential bugs, security issues, and performance concerns. Provide specific, actionable feedback:\n\n```{language or ''}\n{code}\n```",
            
            "optimize": f"Please optimize the following code for better performance, readability, and efficiency. Explain the changes you make:\n\n```{language or ''}\n{code}\n```",
            
            "fix": f"Please identify and fix any bugs or issues in the following code. Explain what was wrong and how you fixed it:\n\n```{language or ''}\n{code}\n```",
            
            "document": f"Please add comprehensive documentation to the following code, including docstrings, comments, and type hints where applicable:\n\n```{language or ''}\n{code}\n```",
            
            "test": f"Please generate comprehensive unit tests for the following code. Include edge cases and use appropriate testing frameworks:\n\n```{language or ''}\n{code}\n```"
        }
        
        prompt = operation_prompts.get(operation, f"Please analyze this code:\n\n```{language or ''}\n{code}\n```")
        
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        
        return await self.chat(prompt)
    
    async def generate_code(
        self,
        prompt: str,
        language: str,
        framework: Optional[str] = None,
        style: Optional[str] = None
    ) -> str:
        """Generate code based on a description"""
        
        generation_prompt = f"Generate {language} code for the following requirement:\n\n{prompt}"
        
        if framework:
            generation_prompt += f"\n\nUse the {framework} framework."
        
        if style:
            generation_prompt += f"\n\nFollow this coding style: {style}"
        
        generation_prompt += "\n\nProvide clean, well-documented, production-ready code with proper error handling."
        
        return await self.chat(generation_prompt)
    
    async def complete_code(
        self,
        code_prefix: str,
        language: str,
        context: Optional[str] = None
    ) -> str:
        """Complete partial code (like GitHub Copilot's inline suggestions)"""
        
        prompt = f"""Complete the following {language} code. Continue from where it left off, maintaining the same style and conventions:

```{language}
{code_prefix}
```

{f'Additional context: {context}' if context else ''}

Provide only the completion, not the entire code. The completion should naturally continue from the existing code."""

        return await self.chat(prompt, temperature=0.3)  # Lower temperature for more deterministic completions


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create the Claude service singleton"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
