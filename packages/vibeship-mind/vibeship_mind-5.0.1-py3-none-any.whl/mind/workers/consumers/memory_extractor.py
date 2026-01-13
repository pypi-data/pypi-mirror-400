"""Memory extractor consumer.

This consumer listens for InteractionRecorded events and uses an LLM
to extract memories from the interaction content.

Flow:
    InteractionRecorded → MemoryExtractor → MemoryCreated events

The extraction uses a structured prompt to identify:
- Facts about the user
- Preferences expressed
- Goals mentioned
- Skills demonstrated
- Relationships/patterns

Each extracted memory is stored and indexed for retrieval.

Sensitivity levels control extraction aggressiveness:
- minimal: Only core identity traits and strong preferences
- balanced: Important context plus preferences
- detailed: Most useful information
- everything: Capture as much as possible

LLM Provider:
- Default: Claude Haiku (fast, cheap, reliable)
- Fallback: GPT-4o-mini (if Anthropic key not available)
"""

import json
import os
import time
from typing import Literal
from uuid import UUID, uuid4

import httpx
import structlog

from mind.core.events.base import EventEnvelope, EventType
from mind.core.events.interaction import (
    ExtractionPriority,
    ExtractionResult,
    ExtractedMemory,
)
from mind.core.memory.models import Memory, TemporalLevel
from mind.infrastructure.nats.client import NatsClient
from mind.infrastructure.nats.consumer import EventConsumer
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import MemoryRepository
from mind.services.events import get_event_service

logger = structlog.get_logger()

# Type alias for sensitivity levels
MemorySensitivity = Literal["minimal", "balanced", "detailed", "everything"]

# Base prompt structure (shared across all sensitivity levels)
PROMPT_BASE = """You are a memory extraction system for a personal AI assistant. Extract information worth remembering for future interactions.

<conversation_context>
{context}
</conversation_context>

<current_message>
{content}
</current_message>

## Extraction Guidelines

**GROUNDED INFERENCE**: You may make reasonable inferences, but they must be grounded in evidence:
- ✓ "User is working with FastAPI" (they're debugging FastAPI code)
- ✓ "User appears experienced with async Python" (they're handling complex async patterns)
- ✗ "User has 10 years experience" (never fabricate specific numbers)
- ✗ "User is a senior engineer" (don't assume titles/roles unless stated)

**CONFIDENCE LEVELS**:
- 1.0: Explicitly stated fact ("I prefer TypeScript")
- 0.8: Strong inference from clear evidence
- 0.6: Reasonable inference from context
- 0.4: Weak inference, might be temporary

**WHAT TO EXTRACT**:
- Facts: Concrete information about the user
- Preferences: Likes, dislikes, choices, opinions
- Goals: What they're trying to achieve
- Skills: Technologies, tools, expertise demonstrated
- Projects: What they're building or working on
- Patterns: Recurring behaviors or workflows
- Relationships: Connections between concepts, tools, people

**ENTITIES**: Extract key entities mentioned (technologies, tools, projects, concepts, people)

**RELATIONSHIPS**: Note how entities relate to each other or to the user

{sensitivity_rules}

## Output Format

```json
{{{{
  "memories": [
    {{{{
      "content": "User prefers TypeScript over JavaScript for type safety",
      "content_type": "preference",
      "temporal_level": 4,
      "salience": 0.9,
      "confidence": 1.0,
      "reasoning": "Explicitly stated preference with reasoning",
      "entities": ["TypeScript", "JavaScript"],
      "source": "direct statement"
    }}}},
    {{{{
      "content": "User is building a decision intelligence system called Mind v5",
      "content_type": "project",
      "temporal_level": 3,
      "salience": 0.85,
      "confidence": 0.9,
      "reasoning": "Project context from conversation",
      "entities": ["Mind v5", "decision intelligence"],
      "related_to": ["Python", "FastAPI", "PostgreSQL"],
      "source": "inferred from context"
    }}}}
  ]
}}}}
```

If nothing meaningful to extract:
```json
{{{{"memories": []}}}}
```"""

# Sensitivity-specific rules
SENSITIVITY_RULES = {
    "minimal": """**MINIMAL EXTRACTION MODE** - Be very selective. Only extract:
- Core identity traits explicitly stated
- Strong, clearly stated preferences (confidence >= 0.9)
- Permanent characteristics that define who the user is

Skip:
- Current tasks or projects (unless they reveal core expertise)
- Temporary states, moods, or frustrations
- Specific technical details or problems
- Anything situational or time-bound
- Inferences with confidence < 0.8

Identity-level (4) memories only. When unsure, don't extract.""",

    "balanced": """**BALANCED EXTRACTION MODE** - Extract important, lasting context:
- Identity traits and preferences (level 4, confidence >= 0.7)
- Recurring patterns and workflows (level 3)
- Significant projects or long-running work (level 3)
- Tools and technologies being used regularly (level 3-4)
- Skills demonstrated through actions (level 3-4)

Skip:
- Trivial statements or greetings
- Very specific debugging details
- Temporary frustrations or states
- Information with no future usefulness

Prefer level 3-4 memories. Extract entities and relationships.""",

    "detailed": """**DETAILED EXTRACTION MODE** - Capture comprehensive context:
- Identity, preferences, and traits (level 4)
- Projects, goals, and ongoing work (level 2-3)
- Technical context and decisions made (level 2-3)
- Challenges and problems being solved (level 2)
- Team and collaboration context (level 2-3)
- Skills and expertise demonstrated (level 3-4)
- Tools and workflows used (level 2-3)
- Opinions and perspectives shared (level 3)

Extract rich entity relationships. Note how things connect.

Skip:
- Pure greetings or acknowledgments
- "Okay", "thanks", "hmm" type responses
- Information only relevant for seconds

Capture anything useful for future conversations.""",

    "everything": """**MAXIMUM EXTRACTION MODE** - Comprehensive memory capture:
- All identity information (level 4)
- All preferences and opinions (level 3-4)
- All projects and tasks (level 2-3)
- All technical details and decisions (level 1-3)
- Emotional states and frustrations (level 1-2)
- Learning moments and discoveries (level 2-3)
- Questions asked and topics explored (level 1-2)
- Even minor observations (level 1)

Extract ALL entities mentioned. Map ALL relationships.
Include lower confidence inferences (>= 0.4).

Only skip:
- Pure greetings like "hi" or "hello"
- Single-word acknowledgments
- Completely empty content

When in doubt, extract it. More context is better.""",
}


def get_extraction_prompt(sensitivity: MemorySensitivity) -> str:
    """Get the extraction prompt for the given sensitivity level."""
    rules = SENSITIVITY_RULES.get(sensitivity, SENSITIVITY_RULES["minimal"])
    return PROMPT_BASE.format(
        context="{context}",
        content="{content}",
        sensitivity_rules=rules,
    )


# Default prompt (minimal) for backwards compatibility
EXTRACTION_PROMPT = get_extraction_prompt("minimal")


class MemoryExtractor:
    """Extracts memories from user interactions using LLM.

    Listens for InteractionRecorded events and:
    1. Extracts relevant memories using Claude Haiku (or GPT-4o-mini fallback)
    2. Creates Memory entities in the database
    3. Publishes MemoryCreated events

    Uses Claude Haiku by default for:
    - Lower cost than GPT-4o-mini
    - Better context understanding
    - Reliable structured output
    """

    CONSUMER_NAME = "memory-extractor"

    def __init__(self, client: NatsClient):
        self._client = client
        self._consumer = EventConsumer(client, self.CONSUMER_NAME)
        self._http = httpx.AsyncClient(timeout=30.0)
        self._anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self._openai_key = os.environ.get("MIND_OPENAI_API_KEY")
        self._provider = "anthropic" if self._anthropic_key else "openai"
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register event handlers."""
        self._consumer.on(EventType.INTERACTION_RECORDED, self._handle_interaction)

    async def start(self) -> None:
        """Start the consumer."""
        logger.info("memory_extractor_starting")
        await self._consumer.start(subjects=["mind.interaction.recorded.*"])

    async def stop(self) -> None:
        """Stop the consumer."""
        await self._consumer.stop()
        await self._http.aclose()
        logger.info("memory_extractor_stopped")

    async def _get_user_sensitivity(self, user_id: UUID) -> MemorySensitivity:
        """Get user's memory sensitivity setting from preferences API."""
        try:
            # Try to get from the preferences API
            # Use Docker service name 'api' for container-to-container communication
            api_host = os.environ.get("MIND_API_HOST", "api")
            response = await self._http.get(
                f"http://{api_host}:8080/v1/users/preferences/{user_id}",
                timeout=5.0,
            )
            if response.status_code == 200:
                data = response.json()
                sensitivity = data.get("memory_sensitivity", "minimal")
                if sensitivity in ("minimal", "balanced", "detailed", "everything"):
                    return sensitivity
        except Exception as e:
            logger.debug("preferences_fetch_failed", error=str(e))
        return "minimal"  # Default to minimal

    async def _handle_interaction(self, envelope: EventEnvelope) -> None:
        """Handle InteractionRecorded events.

        Extracts memories from the interaction and stores them.
        """
        log = logger.bind(
            event_id=str(envelope.event_id),
            user_id=str(envelope.user_id),
        )

        try:
            payload = envelope.payload
            interaction_id = UUID(payload["interaction_id"])
            content = payload.get("content", "")
            context = payload.get("context", {})
            priority = payload.get("extraction_priority", "normal")
            skip = payload.get("skip_extraction", False)

            log = log.bind(
                interaction_id=str(interaction_id),
                content_length=len(content),
                priority=priority,
            )

            # Skip if marked
            if skip:
                log.debug("extraction_skipped", reason="skip_flag")
                return

            # Skip empty content
            if not content or len(content.strip()) < 10:
                log.debug("extraction_skipped", reason="content_too_short")
                return

            # Skip if no API key for either provider
            if not self._anthropic_key and not self._openai_key:
                log.warning("extraction_skipped", reason="no_api_key")
                return

            # Get user's sensitivity setting
            sensitivity = await self._get_user_sensitivity(envelope.user_id)
            log = log.bind(sensitivity=sensitivity)

            # Extract memories
            start_time = time.time()
            extraction_result = await self._extract_memories(
                content=content,
                context=context,
                interaction_id=interaction_id,
                sensitivity=sensitivity,
            )
            extraction_time_ms = (time.time() - start_time) * 1000

            log = log.bind(
                memories_extracted=len(extraction_result.memories),
                extraction_time_ms=extraction_time_ms,
            )

            if not extraction_result.memories:
                log.debug("no_memories_extracted")
                return

            # Store memories
            await self._store_memories(
                user_id=envelope.user_id,
                interaction_id=interaction_id,
                memories=extraction_result.memories,
                correlation_id=envelope.correlation_id,
            )

            log.info(
                "memories_extracted_and_stored",
                count=len(extraction_result.memories),
            )

        except Exception as e:
            log.error("memory_extraction_failed", error=str(e))
            raise  # Let consumer handle retry

    async def _extract_memories(
        self,
        content: str,
        context: dict,
        interaction_id: UUID,
        sensitivity: MemorySensitivity = "minimal",
    ) -> ExtractionResult:
        """Use LLM to extract memories from interaction content."""
        # Format context for prompt
        context_str = ""
        if context.get("previous_turns"):
            turns = context["previous_turns"][-5:]  # Last 5 turns
            context_str = "\n".join(
                f"{t.get('role', 'unknown')}: {t.get('content', '')[:200]}"
                for t in turns
            )
        else:
            context_str = "(No previous context)"

        # Get sensitivity-specific prompt
        extraction_prompt = get_extraction_prompt(sensitivity)
        prompt = extraction_prompt.format(
            context=context_str,
            content=content[:2000],  # Limit content length
        )

        logger.debug("using_sensitivity", sensitivity=sensitivity, provider=self._provider)

        # Call LLM API (Anthropic preferred, OpenAI fallback)
        start_time = time.time()
        try:
            if self._provider == "anthropic" and self._anthropic_key:
                # Use Claude Haiku
                response = await self._http.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self._anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "claude-3-5-haiku-latest",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                response.raise_for_status()
                result = response.json()
                response_text = result["content"][0]["text"]
                tokens_used = result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
                model_used = "claude-3-5-haiku"
            else:
                # Fallback to OpenAI
                response = await self._http.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                response.raise_for_status()
                result = response.json()
                response_text = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                model_used = "gpt-4o-mini"
            logger.debug("llm_response_raw", response_preview=response_text[:200])

            # Extract JSON from response - handle both arrays and objects
            # Also handle markdown code blocks
            clean_text = response_text.strip()
            logger.debug("clean_text_start", starts_with=clean_text[:20] if clean_text else "empty")
            if clean_text.startswith("```"):
                # Remove markdown code block
                lines = clean_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]  # Remove opening ```json
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]  # Remove closing ```
                clean_text = "\n".join(lines).strip()

            # Try to find JSON (array or object)
            json_data = None
            if clean_text.startswith("["):
                # It's an array
                json_end = clean_text.rfind("]") + 1
                json_str = clean_text[:json_end]
                try:
                    json_data = json.loads(json_str)
                except json.JSONDecodeError:
                    json_data = []
            elif clean_text.startswith("{"):
                # It's an object
                json_end = clean_text.rfind("}") + 1
                json_str = clean_text[:json_end]
                try:
                    json_data = json.loads(json_str)
                except json.JSONDecodeError:
                    json_data = {"memories": []}
            else:
                # Try to find embedded JSON
                json_start = clean_text.find("[")
                if json_start == -1:
                    json_start = clean_text.find("{")
                if json_start >= 0:
                    remaining = clean_text[json_start:]
                    if remaining.startswith("["):
                        json_end = remaining.rfind("]") + 1
                    else:
                        json_end = remaining.rfind("}") + 1
                    if json_end > 0:
                        try:
                            json_data = json.loads(remaining[:json_end])
                        except json.JSONDecodeError:
                            json_data = {"memories": []}
                    else:
                        json_data = {"memories": []}
                else:
                    json_data = {"memories": []}

            # Normalize to list of memory dicts
            if isinstance(json_data, list):
                memory_list = json_data
            elif isinstance(json_data, dict):
                memory_list = json_data.get("memories", [])
            else:
                memory_list = []

            logger.debug("parsed_memories", count=len(memory_list), sample=str(memory_list)[:100] if memory_list else "empty")

            # Convert to ExtractedMemory objects (handle case-insensitive keys)
            memories = []
            for m in memory_list:
                # Normalize keys to lowercase
                m_lower = {k.lower(): v for k, v in m.items()}
                memories.append(
                    ExtractedMemory(
                        content=m_lower.get("content", ""),
                        content_type=m_lower.get("content_type", m_lower.get("type", "observation")),
                        temporal_level=m_lower.get("temporal_level", m_lower.get("level", 2)),
                        suggested_salience=m_lower.get("salience", 0.8),
                        extraction_reasoning=m_lower.get("reasoning", ""),
                        confidence=m_lower.get("confidence", 0.8),
                        source=m_lower.get("source", "inferred"),
                        entity_mentions=m_lower.get("entities", []),
                        related_to=m_lower.get("related_to", []),
                    )
                )

            return ExtractionResult(
                interaction_id=interaction_id,
                extraction_model=model_used,
                memories=memories,
                extraction_time_ms=(time.time() - start_time) * 1000,
                tokens_used=tokens_used,
                extraction_confidence=0.8 if memories else 0.0,
            )

        except Exception as e:
            logger.error("llm_extraction_failed", error=str(e))
            return ExtractionResult(
                interaction_id=interaction_id,
                memories=[],
                extraction_confidence=0.0,
            )

    async def _store_memories(
        self,
        user_id: UUID,
        interaction_id: UUID,
        memories: list[ExtractedMemory],
        correlation_id: UUID,
    ) -> None:
        """Store extracted memories in the database and publish events."""
        db = get_database()
        event_service = get_event_service()

        async with db.session() as session:
            memory_repo = MemoryRepository(session)

            for extracted in memories:
                # Create Memory object
                from datetime import UTC, datetime
                memory = Memory(
                    memory_id=uuid4(),
                    user_id=user_id,
                    content=extracted.content,
                    content_type=extracted.content_type,
                    temporal_level=TemporalLevel(extracted.temporal_level),
                    valid_from=datetime.now(UTC),
                    base_salience=extracted.suggested_salience,
                )

                # Store memory in database
                result = await memory_repo.create(memory)

                if result.is_ok:
                    memory = result.value

                    # Publish MemoryCreated event (uses Memory object)
                    await event_service.publish_memory_created(
                        memory=memory,
                        correlation_id=correlation_id,
                    )

                    logger.debug(
                        "memory_stored",
                        memory_id=str(memory.memory_id),
                        content_preview=memory.content[:50],
                    )
                else:
                    logger.warning(
                        "memory_store_failed",
                        error=str(result.error),
                        content_preview=extracted.content[:50],
                    )


async def create_memory_extractor() -> MemoryExtractor:
    """Factory to create and initialize the memory extractor."""
    from mind.infrastructure.nats.client import get_nats_client

    client = await get_nats_client()
    return MemoryExtractor(client)
