"""
Groq AI Service - Handles all interactions with Groq's FREE API
Using Llama 3.3 70B for excellent reasoning capabilities
"""

from groq import Groq, AsyncGroq
from typing import AsyncGenerator, List, Optional
import logging

from ameck_copilot.app.config import get_settings
from ameck_copilot.app.models import Message, MessageRole

logger = logging.getLogger(__name__)


class GroqService:
    """Service class for Groq API interactions (FREE tier)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key)
        self.async_client = AsyncGroq(api_key=self.settings.groq_api_key)
        
        # System prompt for the AI assistant
        self.system_prompt = """You are Ameck Copilot, an expert AI programming assistant powered by Llama 3.3 70B. You help developers with:

1. **Code Generation**: Write clean, efficient, and well-documented code in any programming language.
2. **Code Explanation**: Explain complex code snippets, algorithms, and design patterns clearly.
3. **Debugging**: Help identify and fix bugs, suggest improvements, and optimize code.
4. **Best Practices**: Recommend coding standards, design patterns, and architectural decisions.
5. **Documentation**: Generate comprehensive documentation, comments, and README files.
6. **Code Review**: Provide constructive feedback on code quality, security, and performance.
7. **Learning**: Teach programming concepts with examples and practical exercises.

Guidelines:
- Always provide accurate, well-tested code
- Use proper formatting with syntax highlighting (use markdown code blocks with language tags)
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

    def _format_messages(self, conversation_history: List[Message], current_message: str) -> List[dict]:
        """Format conversation history for Groq API"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
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
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """Send a chat message and get a response (non-streaming)"""
        
        messages = self._format_messages(conversation_history or [], message)
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model or self.settings.model_name,
                messages=messages,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    async def chat_stream(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Send a chat message and stream the response"""
        
        messages = self._format_messages(conversation_history or [], message)
        
        try:
            stream = await self.async_client.chat.completions.create(
                model=model or self.settings.model_name,
                messages=messages,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq API streaming error: {e}")
            raise
    
    async def analyze_code(
        self,
        code: str,
        operation: str,
        language: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
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
        
        return await self.chat(prompt, model=model)
    
    async def generate_code(
        self,
        prompt: str,
        language: str,
        framework: Optional[str] = None,
        style: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """Generate code based on a description"""
        
        generation_prompt = f"Generate {language} code for the following requirement:\n\n{prompt}"
        
        if framework:
            generation_prompt += f"\n\nUse the {framework} framework."
        
        if style:
            generation_prompt += f"\n\nFollow this coding style: {style}"
        
        generation_prompt += "\n\nProvide clean, well-documented, production-ready code with proper error handling."
        
        return await self.chat(generation_prompt, model=model)
    
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

    async def plan(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """Produce a clear, actionable plan with numbered steps and a short summary."""
        plan_prompt = f"""You are in Plan mode. Given the user's request, produce a concise 1-2 sentence summary followed by a numbered list of actionable steps. For each step provide a short acceptance criteria. Finally, include a JSON array under a 'JSON:' marker with the steps as objects {{"id": <n>, "title": "...", "description": "...", "estimate": "<optional>"}}.

User request:
{message}
"""
        if conversation_history:
            plan_prompt = f"Context: {conversation_history[-1].content}\n\n{plan_prompt}"
        return await self.chat(
            plan_prompt,
            conversation_history=conversation_history,
            temperature=temperature if temperature is not None else 0.0,
            max_tokens=max_tokens or self.settings.max_tokens,
            model=model
        )

    async def edit(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """Produce a clear set of edits or a unified diff to apply to the user's code or text."""
        edit_prompt = f"""You are in Edit mode. The user will supply code or text and a description of desired edits. Produce a clear unified diff or a set of patch instructions (use '---' and '+++' / unified diff format if possible). If the instructions are ambiguous, ask a clarifying question. User input:

{message}
"""
        return await self.chat(
            edit_prompt,
            conversation_history=conversation_history,
            temperature=temperature if temperature is not None else 0.2,
            max_tokens=max_tokens or self.settings.max_tokens,
            model=model
        )

    async def agent(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """Act as an Agent: propose objectives, step-by-step actions, and when appropriate, ask clarifying questions or propose follow-ups.

        Include clear actions, estimated effort, and explicit next steps that a developer could follow."""
        agent_prompt = f"""You are in Agent mode. Read the user's request and respond with:
1) A short goal statement summarizing what you will accomplish;
2) A prioritized, numbered list of actions with expected outcomes and rough effort estimates;
3) Explicit next steps and any clarifying questions.

Format the actions as a numbered list and include a JSON block only if the user asks for machine-readable output.

User request:

{message}
"""
        return await self.chat(
            agent_prompt,
            conversation_history=conversation_history,
            temperature=temperature if temperature is not None else 0.2,
            max_tokens=max_tokens or self.settings.max_tokens,
            model=model
        )


# Singleton instance
_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton"""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
