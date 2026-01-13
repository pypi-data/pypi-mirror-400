"""
API Routes for chat functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import logging

from ameck_copilot.app.models import (
    ChatRequest, ChatResponse, CodeRequest, CodeResponse,
    GenerateRequest, MessageRole, ErrorResponse
)
from ameck_copilot.app.services import get_groq_service, GroqService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


async def stream_response(
    service: GroqService,
    message: str,
    conversation_history: list,
    mode: str = "ask",
    temperature: float = None,
    max_tokens: int = None,
    model: str = None
) -> AsyncGenerator[str, None]:
    """Generate SSE stream for chat response. Supports mode-specific prompts."""
    try:
        # Build a mode-aware prompt when necessary
        if mode == "plan":
            prompt = f"""You are in Plan mode. Produce a concise summary followed by a numbered, actionable plan with acceptance criteria. Include a JSON: marker containing the steps as objects.\n\nUser request:\n{message}"""
        elif mode == "edit":
            prompt = f"""You are in Edit mode. The user will supply code or text and desired edits. Output a unified diff or patch and, if unclear, ask a clarifying question.\n\nUser input:\n{message}"""
        elif mode == "agent":
            prompt = f"""You are in Agent mode. Summarize the goal, propose prioritized actions with expected outcomes, and ask clarifying questions if needed.\n\nUser request:\n{message}"""
        else:
            prompt = message

        async for chunk in service.chat_stream(
            message=prompt,
            conversation_history=conversation_history,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model
        ):
            # Send as Server-Sent Event format
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI assistant.
    
    Supports both streaming and non-streaming responses.
    """
    service = get_groq_service()
    
    try:
        if request.stream:
            return StreamingResponse(
                stream_response(
                    service=service,
                    message=request.message,
                    conversation_history=request.conversation_history,
                    mode=(request.mode.value if hasattr(request.mode, 'value') else request.mode),
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    model=request.model
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Non-streaming: dispatch to mode-specific handlers
            if getattr(request, 'mode', None) and getattr(request.mode, 'value', str(request.mode)) == 'plan':
                raw = await service.plan(
                    message=request.message,
                    conversation_history=request.conversation_history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    model=request.model
                )
                structured = None
                message_text = raw
                # Try to parse JSON after 'JSON:' marker
                if 'JSON:' in raw:
                    try:
                        parts = raw.split('JSON:', 1)
                        message_text = parts[0].strip()
                        json_part = parts[1].strip()
                        # Attempt to find the JSON array bounds
                        start = json_part.find('[')
                        end = json_part.rfind(']')
                        if start != -1 and end != -1 and end > start:
                            json_str = json_part[start:end+1]
                            structured = json.loads(json_str)
                    except Exception:
                        structured = None

                return ChatResponse(
                    message=message_text,
                    model=request.model or service.settings.model_name,
                    structured={'plan': structured} if structured is not None else None
                )
            elif getattr(request, 'mode', None) and getattr(request.mode, 'value', str(request.mode)) == 'edit':
                response = await service.edit(
                    message=request.message,
                    conversation_history=request.conversation_history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    model=request.model
                )
            elif getattr(request, 'mode', None) and getattr(request.mode, 'value', str(request.mode)) == 'agent':
                response = await service.agent(
                    message=request.message,
                    conversation_history=request.conversation_history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    model=request.model
                )
            else:
                response = await service.chat(
                    message=request.message,
                    conversation_history=request.conversation_history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    model=request.model
                )
            
            return ChatResponse(
                message=response,
                model=request.model or service.settings.model_name
            )
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code", response_model=CodeResponse)
async def analyze_code(request: CodeRequest):
    """
    Perform code analysis operations.
    
    Supported operations:
    - explain: Explain what the code does
    - review: Review code for quality and issues
    - optimize: Suggest optimizations
    - fix: Identify and fix bugs
    - document: Add documentation
    - test: Generate unit tests
    """
    service = get_groq_service()
    
    try:
        result = await service.analyze_code(
            code=request.code,
            operation=request.operation,
            language=request.language,
            context=request.context,
            model=request.model
        )
        
        return CodeResponse(
            result=result,
            operation=request.operation,
            language=request.language
        )
        
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_code(request: GenerateRequest):
    """
    Generate code from a natural language description.
    """
    service = get_groq_service()
    
    try:
        result = await service.generate_code(
            prompt=request.prompt,
            language=request.language,
            framework=request.framework,
            style=request.style,
            model=request.model
        )
        
        return {
            "code": result,
            "language": request.language,
            "framework": request.framework
        }
        
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_code(
    code_prefix: str,
    language: str,
    context: str = None
):
    """
    Complete partial code (inline suggestions).
    """
    service = get_groq_service()
    
    try:
        completion = await service.complete_code(
            code_prefix=code_prefix,
            language=language,
            context=context
        )
        
        return {
            "completion": completion,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Code completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
