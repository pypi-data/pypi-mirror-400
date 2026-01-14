# Deep Runtime Telemetry for LLM Observability

This document describes advanced telemetry capabilities that can be captured from LLM runtime interactions beyond basic usage metrics. These layers enable comprehensive governance, debugging, and optimization of agentic systems.

---

## Table of Contents

1. [Overview](#overview)
2. [Layer 0: Raw Content Capture](#layer-0-raw-content-capture)
3. [Layer 1: Raw Protocol Data](#layer-1-raw-protocol-data)
4. [Layer 2: Streaming Token Economics](#layer-2-streaming-token-economics)
5. [Layer 3: Model Behavioral Signals](#layer-3-model-behavioral-signals)
6. [Layer 4: Semantic Fingerprinting](#layer-4-semantic-fingerprinting)
7. [Layer 5: Context Window Forensics](#layer-5-context-window-forensics)
8. [Layer 6: Tool Call Deep Inspection](#layer-6-tool-call-deep-inspection)
9. [Layer 7: Python Runtime Context](#layer-7-python-runtime-context)
10. [Layer 8: Framework Interception](#layer-8-framework-interception)
11. [Layer 9: Conversation State Machine](#layer-9-conversation-state-machine)
12. [Layer 10: Structured Output Validation](#layer-10-structured-output-validation)
13. [Implementation Architecture](#implementation-architecture)
14. [IMJDF Protocol Mapping](#imjdf-protocol-mapping)

---

## Overview

The current `MetricEvent` captures essential usage data:

| Category | Fields |
|----------|--------|
| Identity | `trace_id`, `span_id`, `parent_span_id`, `request_id` |
| Request | `provider`, `model`, `stream`, `timestamp` |
| Tokens | `input_tokens`, `output_tokens`, `cached_tokens`, `reasoning_tokens` |
| Performance | `latency_ms`, `status_code`, `error` |
| Attribution | `call_site_file`, `call_site_line`, `call_stack`, `agent_stack` |
| Tools | `tool_call_count`, `tool_names` |

The following layers extend this foundation to enable deep observability for governance systems like the Queen architecture.

---

## Telemetry Layers at a Glance

### Layer Summary

| Layer | Name | Source | Latency | Key Signals |
|-------|------|--------|---------|-------------|
| **0** | Raw Content Capture | Request/Response objects | < 1ms | Full input/output text, tool args, system prompts |
| **1** | Raw Protocol Data | HTTP transport | < 1ms | DNS, TLS, TTFB, headers, retries |
| **2** | Streaming Token Economics | Stream iterators | Real-time | TTFT, inter-token latency, throughput |
| **3** | Model Behavioral Signals | Response metadata | < 1ms | Logprobs, confidence, stop reason, refusals |
| **4** | Semantic Fingerprinting | Computed (models) | 10-200ms | Embeddings, PII scores, injection detection |
| **5** | Context Window Forensics | Request analysis | < 1ms | Token composition, RAG detection, utilization |
| **6** | Tool Call Deep Inspection | Tool call data | < 1ms | Full args, validation, execution graph |
| **7** | Python Runtime Context | Runtime introspection | < 1ms | Memory, threads, async state, GC |
| **8** | Framework Interception | Callback systems | Event-driven | Chain/agent traces, RAG retrievals |
| **9** | Conversation State Machine | Session aggregation | Per-turn | Drift score, topics, frustration signals |
| **10** | Structured Output Validation | Response parsing | < 5ms | Schema validation, repairs, retries |

### Capture Depth by Use Case

| Use Case | Required Layers | Compute Cost |
|----------|-----------------|--------------|
| **Basic Metering** | Current MetricEvent only | Negligible |
| **Cost Attribution** | 0, 5 | Low |
| **Debugging** | 0, 2, 3, 6, 7 | Low |
| **Prompt Injection Defense** | 0, 4 (LSH) | Low-Medium |
| **Hallucination Detection** | 0, 4, 5 | Medium |
| **Full Governance (Queen)** | 0, 3, 4, 5, 6, 9 | Medium-High |
| **Complete Observability** | All layers | High |

### Data Volume & Privacy Impact

| Layer | Data Size/Request | Contains PII Risk | Retention Recommendation |
|-------|-------------------|-------------------|--------------------------|
| **0** | 1-100 KB | **High** | 7 days (or hash only) |
| **1** | ~500 bytes | Low | 90 days |
| **2** | ~1 KB | Low | 30 days |
| **3** | ~200 bytes | Low | 90 days |
| **4** | 1-3 KB | Medium (derived) | 30 days |
| **5** | ~500 bytes | Low | 90 days |
| **6** | 1-10 KB | **High** (args) | 7 days |
| **7** | ~300 bytes | None | 90 days |
| **8** | Variable | Medium | 30 days |
| **9** | ~1 KB | Medium | 30 days |
| **10** | 1-5 KB | Medium | 30 days |

### Integration Complexity

| Layer | Integration Point | Dependencies | Effort |
|-------|-------------------|--------------|--------|
| **0** | Wrapper kwargs/response | None | Low |
| **1** | HTTP transport hook | httpx internals | Medium |
| **2** | Stream iterator wrapper | Existing wrappers | Low |
| **3** | Response extraction | None | Low |
| **4** | Post-processing pipeline | Embedding model, classifiers | High |
| **5** | Request kwargs analysis | tiktoken | Low |
| **6** | Response + schema access | jsonschema | Low |
| **7** | Context manager | psutil | Low |
| **8** | Framework callbacks | Per-framework | Medium each |
| **9** | Session state management | Embedding model | Medium |
| **10** | Response parsing | jsonschema | Low |

### Quick Reference: What Each Layer Captures

```
Layer 0 - CONTENT
├── Input: system prompt, user messages, assistant history, tools schema
├── Output: response text, tool calls with args, refusals
└── Metadata: temperature, seed, model version

Layer 1 - NETWORK
├── Timing: DNS, TCP, TLS, TTFB, download
├── Connection: reuse, pool size, keep-alive
└── Reliability: retries, status codes, rate limits

Layer 2 - STREAMING
├── UX: time to first token, inter-token latency
├── Throughput: tokens/sec, chunk sizes
└── Reliability: interruptions, resumption

Layer 3 - BEHAVIOR
├── Confidence: logprobs, entropy, perplexity
├── Termination: stop reason, truncation
└── Safety: refusals, content filters

Layer 4 - SEMANTIC
├── Embeddings: input/output vectors
├── Classification: intent, topic, sentiment
└── Risk: PII score, injection score, jailbreak score

Layer 5 - CONTEXT
├── Utilization: tokens used vs max
├── Composition: by role (system/user/assistant/tool)
└── Detection: RAG patterns, history truncation

Layer 6 - TOOLS
├── Arguments: raw JSON, parsed, validated
├── Execution: timing, results, errors
└── Sequence: parallel groups, dependency graph

Layer 7 - RUNTIME
├── Process: PID, threads, async tasks
├── Resources: memory delta, CPU time, GC
└── SDK: version, config, timeouts

Layer 8 - FRAMEWORK
├── LangChain: chains, agents, retrievers, tools
├── PydanticAI: runs, validations, retries
└── CrewAI: crews, agents, tasks

Layer 9 - CONVERSATION
├── Progress: turn number, tokens spent
├── Drift: intent embedding distance over time
└── Quality: corrections, repetitions, frustration

Layer 10 - STRUCTURED
├── Parsing: success/failure, errors
├── Validation: schema compliance, coverage
└── Repair: strategies, token waste
```

### Insights & Analytics Derived from Telemetry

#### Operational Intelligence

| Insight | Layers Used | Metric/Signal | Business Value |
|---------|-------------|---------------|----------------|
| **Cost per task completion** | 0, 5, 9 | Total tokens × price, grouped by goal | Budget forecasting, ROI analysis |
| **Latency breakdown** | 1, 2 | Network vs inference vs streaming | Identify bottlenecks, SLA compliance |
| **Token efficiency** | 0, 5 | Output tokens / input tokens ratio | Prompt optimization opportunities |
| **Cache hit potential** | 0 (LSH) | % of duplicate/similar prompts | Cost savings via caching |
| **Rate limit headroom** | 1 | Remaining requests/tokens over time | Capacity planning |
| **Retry economics** | 1, 10 | Tokens wasted on retries × cost | Reliability investment ROI |

#### Quality & Reliability

| Insight | Layers Used | Metric/Signal | Business Value |
|---------|-------------|---------------|----------------|
| **Model confidence distribution** | 3 | Mean logprob histogram by task type | Identify uncertain domains |
| **Hallucination rate** | 0, 3, 4 | Low confidence + fact-check failures | Quality SLA tracking |
| **Task completion rate** | 9 | Goals completed / goals started | Agent effectiveness |
| **Conversation efficiency** | 9 | Turns to completion, tokens per goal | UX optimization |
| **Structured output reliability** | 10 | Parse success rate by schema | Schema design feedback |
| **Tool call accuracy** | 6 | Valid args / total calls by tool | Tool documentation quality |

#### Security & Compliance

| Insight | Layers Used | Metric/Signal | Business Value |
|---------|-------------|---------------|----------------|
| **Injection attack patterns** | 0, 4 (LSH) | Similar inputs clustered | Threat intelligence |
| **PII exposure frequency** | 0, 4 | PII detected in outputs by category | Compliance risk scoring |
| **Prompt leakage incidents** | 0, 3 | System prompt in output + refusal patterns | Security posture |
| **Jailbreak attempt rate** | 0, 4 | Known technique similarity scores | User risk profiling |
| **Data exfiltration signals** | 0, 6 | Sensitive data in tool call args | DLP alerting |
| **Policy violation rate** | 0, 3 | Refusals + content filter triggers | Compliance reporting |

#### Agent Behavior Analysis

| Insight | Layers Used | Metric/Signal | Business Value |
|---------|-------------|---------------|----------------|
| **Decision confidence correlation** | 3, 6 | Logprob vs tool call success | Trust calibration |
| **Reasoning path efficiency** | 0, 8 | Tokens in reasoning vs outcome quality | Prompt engineering |
| **Tool selection patterns** | 6, 8 | Tool call sequences by task type | Agent design optimization |
| **Context utilization efficiency** | 5 | % context used vs task success | Memory management tuning |
| **Multi-agent coordination** | 7, 8 | Concurrent requests, handoff patterns | Swarm architecture insights |
| **Failure mode taxonomy** | 0, 3, 6, 10 | Error types clustered by root cause | Targeted improvements |

#### Predictive Analytics

| Insight | Layers Used | Metric/Signal | Prediction |
|---------|-------------|---------------|------------|
| **Cost forecasting** | 0, 5, 9 | Token usage trends by task type | Budget projection |
| **Capacity planning** | 1, 7 | Request rate, latency percentiles | Infrastructure scaling |
| **Quality degradation** | 3, 9 | Confidence drift, completion rate trends | Model/prompt drift detection |
| **User frustration prediction** | 9 | Correction rate, repetition patterns | Proactive escalation |
| **Attack surge detection** | 0, 4 | Injection similarity spike | Security alerting |
| **SLA breach probability** | 1, 2, 3 | Latency + error rate trends | Incident prevention |

#### Cross-Layer Composite Insights

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AGENT PERFORMANCE SCORECARD                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  EFFICIENCY                          QUALITY                            │
│  ├── Cost/Task: $0.12 (↓15%)        ├── Completion Rate: 94%           │
│  ├── Tokens/Goal: 2,400             ├── Hallucination Rate: 2.1%       │
│  ├── Cache Hit Rate: 23%            ├── User Corrections: 0.3/session  │
│  └── Context Utilization: 67%       └── Avg Confidence: 0.89           │
│                                                                         │
│  RELIABILITY                         SECURITY                           │
│  ├── Parse Success: 99.2%           ├── Injection Attempts: 12/day     │
│  ├── Tool Validation: 97.8%         ├── PII Exposures: 0               │
│  ├── Retry Rate: 3.1%               ├── Policy Violations: 2           │
│  └── P95 Latency: 2.3s              └── Jailbreak Blocks: 8            │
│                                                                         │
│  TRENDS (7 day)                                                         │
│  ├── Cost:        ████████░░ -15%   (good)                             │
│  ├── Quality:     ██████████ +3%    (good)                             │
│  ├── Latency:     ███████░░░ +8%    (watch)                            │
│  └── Attacks:     ██████████ +45%   (alert)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Example Queries

```sql
-- Cost attribution by agent and task type
SELECT
    agent_stack[1] as agent,
    intent_category,
    SUM(total_tokens * price_per_token) as total_cost,
    COUNT(*) as request_count,
    AVG(total_tokens) as avg_tokens
FROM telemetry
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY agent_stack[1], intent_category
ORDER BY total_cost DESC;

-- Hallucination detection: low confidence + high drift
SELECT
    trace_id,
    content_preview,
    mean_logprob,
    intent_drift_score
FROM telemetry
WHERE mean_logprob < -2.0
  AND intent_drift_score > 0.6
  AND timestamp > NOW() - INTERVAL '24 hours';

-- Tool reliability by model
SELECT
    model,
    tool_name,
    COUNT(*) as calls,
    AVG(CASE WHEN arguments_valid THEN 1 ELSE 0 END) as validation_rate,
    AVG(execution_duration_ms) as avg_duration
FROM tool_events
GROUP BY model, tool_name
HAVING COUNT(*) > 100
ORDER BY validation_rate ASC;

-- Prompt injection surge detection
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) FILTER (WHERE injection_score > 0.7) as high_risk,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE injection_score > 0.7)::float / COUNT(*) as risk_rate
FROM telemetry
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
HAVING COUNT(*) FILTER (WHERE injection_score > 0.7)::float / COUNT(*) > 0.05;

-- Conversation failure analysis
SELECT
    session_id,
    turn_number,
    user_corrections,
    user_repetitions,
    intent_drift_score,
    frustration_score
FROM conversation_state
WHERE (user_corrections > 2 OR frustration_score > 0.7)
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY frustration_score DESC
LIMIT 100;
```

#### Real-Time Dashboards

| Dashboard | Key Metrics | Refresh Rate | Audience |
|-----------|-------------|--------------|----------|
| **Operations** | Latency P50/P95, Error rate, Throughput | 10s | SRE/Ops |
| **Cost Center** | Spend rate, Token burn, Cache savings | 1m | Finance |
| **Security** | Injection attempts, PII alerts, Blocks | Real-time | Security |
| **Quality** | Confidence, Completion rate, Corrections | 5m | Product |
| **Agent Health** | Per-agent success rate, Tool reliability | 1m | ML Eng |
| **Governance (Queen)** | Judgments/min, Block rate, Drift alerts | Real-time | Platform |

---

## Layer 0: Raw Content Capture

**Status**: ✅ **IMPLEMENTED** (v0.3.3)

**Source**: Request parameters and response objects

The most fundamental telemetry layer - capturing the actual content flowing through LLM calls. This is the foundation for all governance, debugging, and compliance use cases.

### Usage

Enable content capture with the `capture_content` flag:

```python
from aden import instrument, MeterOptions, ContentCaptureOptions

await instrument(MeterOptions(
    capture_content=True,
    content_capture_options=ContentCaptureOptions(
        max_content_bytes=4096,  # Content larger than this stored separately
        capture_system_prompt=True,
        capture_messages=True,
        capture_tools_schema=True,
        capture_response=True,
    ),
))
```

Content larger than `max_content_bytes` is stored on the control server with a `ContentReference` containing:
- `content_id`: Unique identifier
- `content_hash`: SHA-256 hash for integrity
- `byte_size`: Size of the content
- `truncated_preview`: First portion of the content for quick inspection

The `MetricEvent` will include a `content_capture` field with:
- `system_prompt`: Captured system prompt (string or ContentReference)
- `messages`: List of MessageCapture objects
- `tools`: List of ToolSchemaCapture objects
- `params`: Request parameters (temperature, max_tokens, etc.)
- `response_content`: Model response text
- `finish_reason`: Why the model stopped (stop, length, tool_calls)
- `has_images`: Whether the request included images
- `image_urls`: URLs of any images (not base64 data)

```python
@dataclass
class ContentCapture:
    """Complete input/output capture for LLM interactions."""

    # === INPUT: What was sent to the model ===

    # System prompt (often contains persona, rules, constraints)
    system_prompt: str | None
    system_prompt_tokens: int

    # User messages (the actual user input)
    user_messages: list[UserMessage]
    user_messages_tokens: int

    # Assistant messages (conversation history)
    assistant_messages: list[AssistantMessage]
    assistant_messages_tokens: int

    # Full message array as sent (preserves order)
    messages: list[Message]
    messages_raw_json: str                 # Exact JSON sent to API

    # Request parameters
    temperature: float | None
    top_p: float | None
    max_tokens: int | None
    stop_sequences: list[str] | None
    presence_penalty: float | None
    frequency_penalty: float | None
    seed: int | None                       # For reproducibility

    # Tools/functions provided
    tools_schema: list[dict] | None        # Full tool definitions
    tool_choice: str | dict | None         # "auto", "none", or specific

    # === OUTPUT: What the model returned ===

    # Primary response content
    response_content: str | None           # Text response
    response_content_tokens: int

    # For multi-modal responses
    response_parts: list[ContentPart]      # Text, images, audio, etc.

    # Reasoning (for o1/o3 models, Claude with extended thinking)
    reasoning_content: str | None          # Internal reasoning trace
    reasoning_tokens: int
    reasoning_encrypted: bool              # Some providers encrypt this

    # Tool calls made by the model
    tool_calls: list[ToolCallCapture]

    # Multiple choices (if n > 1)
    choices: list[ChoiceCapture]
    choice_count: int

    # Refusals
    refusal: str | None                    # Model's refusal message
    refusal_detected: bool

    # === METADATA ===

    # Response identifiers
    response_id: str                       # Provider's response ID
    model_version: str | None              # Exact model version used
    system_fingerprint: str | None         # Model deployment identifier


@dataclass
class UserMessage:
    """Captured user message with full detail."""
    role: str                              # "user"
    content: str | list[ContentPart]       # Text or multimodal
    content_text: str                      # Flattened text representation
    tokens: int
    name: str | None                       # Optional user identifier

    # Multimodal content
    has_images: bool
    image_count: int
    image_urls: list[str]
    image_tokens: int

    has_files: bool
    file_names: list[str]
    file_types: list[str]


@dataclass
class AssistantMessage:
    """Captured assistant message from history."""
    role: str                              # "assistant"
    content: str | None
    tokens: int

    # Tool interactions in this message
    tool_calls: list[ToolCallCapture]
    tool_call_count: int


@dataclass
class ToolCallCapture:
    """Complete tool call capture."""
    id: str
    type: str                              # "function"
    name: str                              # Function name

    # Arguments - the key data for governance
    arguments_raw: str                     # Raw JSON string
    arguments_parsed: dict                 # Parsed arguments
    arguments_tokens: int

    # Result (if this is from history or we captured execution)
    result: str | None
    result_tokens: int | None


@dataclass
class ContentPart:
    """Multimodal content part."""
    type: str                              # "text", "image_url", "image_file", "audio"
    text: str | None
    image_url: str | None
    image_base64: str | None               # If inline image (be careful with size!)
    image_detail: str | None               # "low", "high", "auto"
    audio_data: bytes | None
    audio_format: str | None


@dataclass
class ChoiceCapture:
    """Individual choice from response."""
    index: int
    content: str | None
    role: str
    tool_calls: list[ToolCallCapture]
    finish_reason: str
    logprobs: list[float] | None
```

### Provider-Specific Extraction

**OpenAI Chat Completions:**

```python
def capture_openai_content(
    request_kwargs: dict,
    response: ChatCompletion
) -> ContentCapture:
    """Extract full content from OpenAI request/response."""

    capture = ContentCapture()

    # === INPUT CAPTURE ===

    messages = request_kwargs.get("messages", [])
    capture.messages = messages
    capture.messages_raw_json = json.dumps(messages)

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "system":
            capture.system_prompt = _extract_text(content)
            capture.system_prompt_tokens = _count_tokens(content)

        elif role == "user":
            user_msg = UserMessage(
                role=role,
                content=content,
                content_text=_extract_text(content),
                tokens=_count_tokens(content),
                name=msg.get("name"),
                has_images=_has_images(content),
                image_count=_count_images(content),
                image_urls=_extract_image_urls(content),
                image_tokens=_estimate_image_tokens(content),
            )
            capture.user_messages.append(user_msg)

        elif role == "assistant":
            asst_msg = AssistantMessage(
                role=role,
                content=_extract_text(content),
                tokens=_count_tokens(content),
                tool_calls=_extract_tool_calls(msg.get("tool_calls", [])),
            )
            capture.assistant_messages.append(asst_msg)

    # Request parameters
    capture.temperature = request_kwargs.get("temperature")
    capture.top_p = request_kwargs.get("top_p")
    capture.max_tokens = request_kwargs.get("max_tokens")
    capture.stop_sequences = request_kwargs.get("stop")
    capture.seed = request_kwargs.get("seed")
    capture.tools_schema = request_kwargs.get("tools")
    capture.tool_choice = request_kwargs.get("tool_choice")

    # === OUTPUT CAPTURE ===

    choice = response.choices[0]

    capture.response_content = choice.message.content
    capture.response_id = response.id
    capture.system_fingerprint = response.system_fingerprint
    capture.model_version = response.model

    # Tool calls
    if choice.message.tool_calls:
        capture.tool_calls = [
            ToolCallCapture(
                id=tc.id,
                type=tc.type,
                name=tc.function.name,
                arguments_raw=tc.function.arguments,
                arguments_parsed=json.loads(tc.function.arguments),
            )
            for tc in choice.message.tool_calls
        ]

    # Refusal detection
    if hasattr(choice.message, 'refusal') and choice.message.refusal:
        capture.refusal = choice.message.refusal
        capture.refusal_detected = True

    # Multiple choices
    if len(response.choices) > 1:
        capture.choices = [
            ChoiceCapture(
                index=c.index,
                content=c.message.content,
                role=c.message.role,
                tool_calls=_extract_tool_calls(c.message.tool_calls),
                finish_reason=c.finish_reason,
            )
            for c in response.choices
        ]
        capture.choice_count = len(response.choices)

    return capture


def _extract_text(content) -> str:
    """Extract text from string or content parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(part.get("text", ""))
            elif isinstance(part, str):
                texts.append(part)
        return "\n".join(texts)
    return ""


def _has_images(content) -> bool:
    """Check if content contains images."""
    if isinstance(content, list):
        return any(
            isinstance(p, dict) and p.get("type") in ("image_url", "image_file")
            for p in content
        )
    return False
```

**Anthropic Messages:**

```python
def capture_anthropic_content(
    request_kwargs: dict,
    response: Message
) -> ContentCapture:
    """Extract full content from Anthropic request/response."""

    capture = ContentCapture()

    # System prompt (top-level in Anthropic)
    capture.system_prompt = request_kwargs.get("system")

    # Messages
    messages = request_kwargs.get("messages", [])
    capture.messages = messages

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "user":
            # Anthropic content can be string or list of blocks
            user_msg = UserMessage(
                role=role,
                content=content,
                content_text=_extract_anthropic_text(content),
                tokens=_count_tokens_anthropic(content),
                has_images=_has_anthropic_images(content),
                image_count=_count_anthropic_images(content),
            )
            capture.user_messages.append(user_msg)

        elif role == "assistant":
            asst_msg = AssistantMessage(
                role=role,
                content=_extract_anthropic_text(content),
                tokens=_count_tokens_anthropic(content),
            )
            capture.assistant_messages.append(asst_msg)

    # === OUTPUT ===

    # Response content (can have multiple content blocks)
    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            capture.tool_calls.append(ToolCallCapture(
                id=block.id,
                type="function",
                name=block.name,
                arguments_raw=json.dumps(block.input),
                arguments_parsed=block.input,
            ))

    capture.response_content = "\n".join(text_parts)
    capture.response_id = response.id

    # Stop reason
    if response.stop_reason == "end_turn":
        pass  # Normal completion
    elif response.stop_reason == "tool_use":
        pass  # Tool call
    elif response.stop_reason == "max_tokens":
        capture.truncated = True

    return capture


def _extract_anthropic_text(content) -> str:
    """Extract text from Anthropic content format."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
        return "\n".join(texts)
    return ""
```

### Integration Point

In [instrument_openai.py](../src/aden/instrument_openai.py) and [instrument_anthropic.py](../src/aden/instrument_anthropic.py), the wrappers have full access to `kwargs` (input) and `response` (output):

```python
def _create_sync_wrapper(original_fn, get_options):
    @wraps(original_fn)
    def wrapper(self, *args, **kwargs):
        options = get_options()

        # >>> FULL INPUT ACCESS HERE <<<
        # kwargs contains: messages, model, tools, temperature, etc.

        response = original_fn(self, *args, **kwargs)

        # >>> FULL OUTPUT ACCESS HERE <<<
        # response contains: choices, content, tool_calls, usage, etc.

        # Current implementation only extracts metrics
        # ADD: content capture
        if options.capture_content:
            content = capture_openai_content(kwargs, response)
            emit_content(options, content)

        return response
    return wrapper
```

### Streaming Content Capture

For streaming responses, content must be accumulated:

```python
class ContentAccumulatingStream:
    """Accumulates streaming content for capture."""

    def __init__(self, stream, request_kwargs: dict):
        self._stream = stream
        self._request_kwargs = request_kwargs
        self._accumulated_content = ""
        self._accumulated_tool_calls: dict[int, ToolCallCapture] = {}
        self._chunks: list[StreamChunk] = []

    async def __anext__(self):
        chunk = await self._stream.__anext__()

        # Accumulate content
        delta = chunk.choices[0].delta
        if delta.content:
            self._accumulated_content += delta.content
            self._chunks.append(StreamChunk(
                content=delta.content,
                timestamp=time.time(),
            ))

        # Accumulate tool calls (they come in pieces)
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in self._accumulated_tool_calls:
                    self._accumulated_tool_calls[idx] = ToolCallCapture(
                        id=tc.id or "",
                        name=tc.function.name or "",
                        arguments_raw="",
                    )
                if tc.function.arguments:
                    self._accumulated_tool_calls[idx].arguments_raw += tc.function.arguments

        return chunk

    def get_captured_content(self) -> ContentCapture:
        """Get accumulated content after stream completes."""
        capture = ContentCapture(
            messages=self._request_kwargs.get("messages"),
            response_content=self._accumulated_content,
            tool_calls=list(self._accumulated_tool_calls.values()),
        )

        # Parse accumulated tool call arguments
        for tc in capture.tool_calls:
            try:
                tc.arguments_parsed = json.loads(tc.arguments_raw)
            except json.JSONDecodeError:
                pass

        return capture
```

### Storage Considerations

Raw content is high-volume and sensitive. Consider:

```python
@dataclass
class ContentStorageConfig:
    # What to capture
    capture_system_prompt: bool = True
    capture_user_messages: bool = True
    capture_assistant_messages: bool = True
    capture_tool_calls: bool = True
    capture_tool_results: bool = True
    capture_images: bool = False           # Large! Usually skip
    capture_reasoning: bool = True         # o1/Claude thinking

    # How to store
    storage_backend: str = "s3"            # "s3", "postgres", "file", "memory"
    compress: bool = True                  # gzip content
    encrypt: bool = True                   # Encrypt at rest

    # Retention
    retention_days: int = 7                # Short due to privacy
    retention_on_error: int = 30           # Keep longer for debugging

    # Sampling (for cost control)
    sample_rate: float = 1.0               # 1.0 = capture all
    sample_on_anomaly: float = 1.0         # Always capture anomalies
    sample_on_error: float = 1.0           # Always capture errors

    # Privacy
    redact_pii: bool = True                # Run PII detection and mask
    hash_user_content: bool = False        # Store hash instead of content
    exclude_patterns: list[str] = None     # Regex patterns to never capture


@dataclass
class ContentReference:
    """Lightweight reference to stored content."""
    content_id: str                        # UUID
    storage_location: str                  # S3 URI, file path, etc.
    content_hash: str                      # SHA256 for integrity
    captured_at: datetime
    expires_at: datetime

    # Summary (always stored, even if content redacted)
    input_tokens: int
    output_tokens: int
    has_tool_calls: bool
    has_images: bool
    model: str
```

### LSH (Locality Sensitive Hashing) for Content Analysis

LSH enables efficient similarity operations on content without storing or comparing raw text. This is critical for privacy-preserving governance at scale.

```python
@dataclass
class LSHConfig:
    """Configuration for LSH-based content analysis."""
    # Algorithm selection
    algorithm: str = "minhash"             # "minhash", "simhash", "random_projection"

    # MinHash settings (for Jaccard similarity)
    num_permutations: int = 128            # More = higher accuracy, slower
    ngram_size: int = 3                    # Character n-grams

    # SimHash settings (for Hamming distance)
    hash_bits: int = 64                    # 64 or 128 bit hashes

    # LSH index settings
    num_bands: int = 20                    # For banding technique
    rows_per_band: int = 5                 # num_permutations / num_bands
    similarity_threshold: float = 0.5     # Jaccard threshold for "similar"


@dataclass
class ContentFingerprint:
    """LSH-based content fingerprint for similarity operations."""
    # Identity
    content_id: str
    timestamp: datetime

    # Hash signatures (store these, not content)
    input_minhash: list[int]               # MinHash signature of input
    output_minhash: list[int]              # MinHash signature of output
    input_simhash: int                     # SimHash of input (single int)
    output_simhash: int                    # SimHash of output

    # Semantic hash (from embedding)
    input_semantic_hash: str               # LSH of embedding vector
    output_semantic_hash: str

    # Quick stats (no content needed)
    input_tokens: int
    output_tokens: int
    input_char_count: int
    output_char_count: int


class ContentLSH:
    """LSH-based content analysis engine."""

    def __init__(self, config: LSHConfig):
        self.config = config
        self._index = MinHashLSH(
            threshold=config.similarity_threshold,
            num_perm=config.num_permutations
        )
        self._known_injections: MinHashLSH = None  # Pre-loaded attack patterns

    def fingerprint(self, input_text: str, output_text: str) -> ContentFingerprint:
        """Generate LSH fingerprint for content."""
        return ContentFingerprint(
            content_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            input_minhash=self._minhash(input_text),
            output_minhash=self._minhash(output_text),
            input_simhash=self._simhash(input_text),
            output_simhash=self._simhash(output_text),
            input_tokens=len(input_text.split()),
            output_tokens=len(output_text.split()),
            input_char_count=len(input_text),
            output_char_count=len(output_text),
        )

    def _minhash(self, text: str) -> list[int]:
        """Generate MinHash signature."""
        m = MinHash(num_perm=self.config.num_permutations)
        # Shingle the text
        for i in range(len(text) - self.config.ngram_size + 1):
            shingle = text[i:i + self.config.ngram_size]
            m.update(shingle.encode('utf-8'))
        return list(m.hashvalues)

    def _simhash(self, text: str) -> int:
        """Generate SimHash signature."""
        # Weight features by TF-IDF or similar
        features = self._extract_features(text)
        v = [0] * self.config.hash_bits

        for feature, weight in features.items():
            h = self._hash_feature(feature)
            for i in range(self.config.hash_bits):
                if h & (1 << i):
                    v[i] += weight
                else:
                    v[i] -= weight

        # Convert to binary
        fingerprint = 0
        for i in range(self.config.hash_bits):
            if v[i] > 0:
                fingerprint |= (1 << i)

        return fingerprint

    # === GOVERNANCE OPERATIONS ===

    def find_similar_inputs(
        self,
        fingerprint: ContentFingerprint,
        top_k: int = 10
    ) -> list[tuple[str, float]]:
        """Find similar past inputs (for deduplication, caching)."""
        minhash = MinHash(hashvalues=fingerprint.input_minhash)
        return self._index.query(minhash, top_k)

    def detect_injection_similarity(
        self,
        input_text: str,
        threshold: float = 0.6
    ) -> list[InjectionMatch]:
        """Check if input is similar to known injection patterns."""
        input_hash = self._minhash(input_text)
        minhash = MinHash(hashvalues=input_hash)

        matches = []
        for pattern_id, similarity in self._known_injections.query(minhash):
            if similarity >= threshold:
                matches.append(InjectionMatch(
                    pattern_id=pattern_id,
                    similarity=similarity,
                    pattern_category=self._get_pattern_category(pattern_id),
                ))

        return matches

    def measure_output_drift(
        self,
        baseline_fingerprint: ContentFingerprint,
        current_fingerprint: ContentFingerprint,
    ) -> DriftMetrics:
        """Measure how much output has drifted from baseline."""
        # Jaccard similarity via MinHash
        jaccard = self._estimate_jaccard(
            baseline_fingerprint.output_minhash,
            current_fingerprint.output_minhash
        )

        # Hamming distance via SimHash
        hamming = bin(
            baseline_fingerprint.output_simhash ^
            current_fingerprint.output_simhash
        ).count('1')

        return DriftMetrics(
            jaccard_similarity=jaccard,
            jaccard_distance=1 - jaccard,
            hamming_distance=hamming,
            hamming_normalized=hamming / self.config.hash_bits,
            significant_drift=jaccard < 0.5 or hamming > 20,
        )

    def cluster_interactions(
        self,
        fingerprints: list[ContentFingerprint],
        similarity_threshold: float = 0.7
    ) -> list[list[str]]:
        """Cluster similar interactions together."""
        # Build LSH forest
        forest = MinHashLSHForest(num_perm=self.config.num_permutations)

        for fp in fingerprints:
            minhash = MinHash(hashvalues=fp.input_minhash)
            forest.add(fp.content_id, minhash)

        forest.index()

        # Find clusters via connected components
        clusters = self._find_clusters(forest, fingerprints, similarity_threshold)
        return clusters

    def deduplicate_prompts(
        self,
        fingerprints: list[ContentFingerprint],
        threshold: float = 0.9
    ) -> DeduplicationResult:
        """Find near-duplicate prompts for caching/consolidation."""
        duplicates = []
        unique = []

        seen_hashes = MinHashLSH(threshold=threshold, num_perm=self.config.num_permutations)

        for fp in fingerprints:
            minhash = MinHash(hashvalues=fp.input_minhash)

            # Check if we've seen something similar
            matches = seen_hashes.query(minhash)
            if matches:
                duplicates.append((fp.content_id, matches[0]))
            else:
                unique.append(fp.content_id)
                seen_hashes.insert(fp.content_id, minhash)

        return DeduplicationResult(
            unique_count=len(unique),
            duplicate_count=len(duplicates),
            duplicate_pairs=duplicates,
            deduplication_ratio=len(duplicates) / len(fingerprints),
        )


@dataclass
class InjectionMatch:
    pattern_id: str
    similarity: float
    pattern_category: str                  # "jailbreak", "prompt_leak", "instruction_override"


@dataclass
class DriftMetrics:
    jaccard_similarity: float              # 0-1, higher = more similar
    jaccard_distance: float                # 0-1, higher = more different
    hamming_distance: int                  # Bit flips between SimHashes
    hamming_normalized: float              # 0-1
    significant_drift: bool


@dataclass
class DeduplicationResult:
    unique_count: int
    duplicate_count: int
    duplicate_pairs: list[tuple[str, str]]
    deduplication_ratio: float             # % that were duplicates
```

**LSH Governance Use Cases:**

| Use Case | LSH Technique | Value |
|----------|--------------|-------|
| **Prompt Injection Detection** | MinHash against known attack corpus | Fast similarity check without storing attack patterns in plaintext |
| **Response Caching** | Input MinHash deduplication | Identify cacheable prompts without semantic analysis |
| **Conversation Drift** | SimHash Hamming distance over turns | Detect when agent strays from original intent |
| **Anomaly Detection** | LSH Forest outlier detection | Find unusual prompts that don't cluster with normal traffic |
| **Privacy-Preserving Audit** | Store only fingerprints | Full audit capability without storing PII |
| **Attack Pattern Clustering** | MinHash LSH clustering | Group similar attack attempts for analysis |
| **A/B Test Bucketing** | Consistent hashing on input | Deterministic experiment assignment |
| **Duplicate Request Detection** | Near-duplicate via SimHash | Prevent billing for retried/duplicate requests |

**Comparison with Embeddings:**

| Aspect | LSH | Embeddings |
|--------|-----|------------|
| **Speed** | O(1) lookup | O(n) or O(log n) with index |
| **Storage** | ~128 bytes per doc | ~1.5KB per doc (768 dims) |
| **Privacy** | One-way hash | Invertible with enough samples |
| **Semantic** | Syntactic similarity | Semantic similarity |
| **Cost** | Zero (local compute) | API call or GPU |

**Hybrid Approach:**

```python
@dataclass
class HybridContentFingerprint:
    """Combined LSH + Embedding fingerprint."""

    # Fast path: LSH (always computed)
    minhash: list[int]
    simhash: int

    # Slow path: Embedding (computed on-demand or async)
    embedding: list[float] | None
    embedding_model: str | None
    embedding_lsh: str | None              # LSH of embedding for fast semantic search

    # Flags
    lsh_only: bool                         # True if embedding not computed


class HybridAnalyzer:
    """Two-tier analysis: fast LSH, then semantic if needed."""

    def analyze(self, content: str) -> AnalysisResult:
        # Tier 0: LSH (< 1ms)
        fingerprint = self.lsh.fingerprint(content)

        # Check against known bad patterns
        injection_matches = self.lsh.detect_injection_similarity(content)
        if injection_matches:
            return AnalysisResult(
                risk_level="high",
                reason="Similar to known injection pattern",
                matches=injection_matches,
                used_embedding=False,
            )

        # Check for anomaly via LSH clustering
        cluster_id = self.lsh.find_cluster(fingerprint)
        if cluster_id is None:  # Outlier
            # Tier 1: Compute embedding for deeper analysis
            embedding = self.embedder.embed(content)
            semantic_risk = self.classifier.classify(embedding)

            return AnalysisResult(
                risk_level=semantic_risk.level,
                reason="Outlier prompt - semantic analysis performed",
                embedding=embedding,
                used_embedding=True,
            )

        return AnalysisResult(
            risk_level="low",
            reason="Normal traffic pattern",
            cluster_id=cluster_id,
            used_embedding=False,
        )
```

### Governance Use Cases

| Use Case | Required Content | Why |
|----------|-----------------|-----|
| **Hallucination Detection** | Output content + Ground Truth | Compare response against facts |
| **Prompt Injection Detection** | User messages + LSH patterns | Scan for injection patterns (fast path with LSH) |
| **PII Leakage** | Output content | Detect leaked sensitive data |
| **Policy Compliance** | System prompt + Output | Verify agent followed rules |
| **Fact Checking** | Output content | Verify against Honey Store |
| **Tone/Safety Analysis** | Output content | Check for harmful content |
| **Debug Failures** | Full input + output | Reproduce and diagnose issues |
| **Audit Trail** | Full input + output (or fingerprints) | Compliance and accountability |
| **A/B Testing** | Input + multiple outputs | Compare model versions |
| **Fine-tuning Data** | Full conversations | Training data collection |
| **Caching Optimization** | Input LSH fingerprints | Identify duplicate/similar prompts |
| **Drift Detection** | LSH fingerprints over time | Monitor conversation divergence |

### Example: Full Content Event

```python
@dataclass
class ContentEvent(BaseEvent):
    """Complete content capture event."""
    trace_id: str
    span_id: str
    timestamp: datetime

    # The captured content
    capture: ContentCapture

    # Or reference if stored externally
    content_ref: ContentReference | None

    # Quick-access fields (always populated)
    input_preview: str                     # First 200 chars of input
    output_preview: str                    # First 200 chars of output
    input_hash: str                        # For deduplication
    output_hash: str

    # Flags
    contains_pii: bool
    contains_tool_calls: bool
    contains_images: bool
    was_redacted: bool
    was_sampled_out: bool                  # True if we skipped full capture
```

**Governance Value**:
- **Foundation for all semantic analysis** - Can't check facts without the actual content
- **Complete audit trail** - What exactly did the agent say?
- **Debugging** - Reproduce exact failures
- **Training data** - Collect successful interactions
- **Compliance** - Prove what was/wasn't said

---

## Layer 1: Raw Protocol Data

**Source**: HTTP client transport layer (httpx/aiohttp)

Captures network-level telemetry for infrastructure monitoring and latency attribution.

```python
@dataclass
class ProtocolMetrics:
    # DNS & Connection
    dns_resolution_ms: float | None
    tcp_connect_ms: float | None
    tls_handshake_ms: float | None

    # Request Timing
    time_to_first_byte_ms: float
    content_download_ms: float
    total_request_ms: float

    # Connection State
    connection_reused: bool
    connection_pool_size: int
    keep_alive: bool

    # TLS Details
    tls_version: str | None
    cipher_suite: str | None
    certificate_issuer: str | None
    certificate_expiry: datetime | None

    # Retry Behavior
    retry_count: int
    retry_delays_ms: list[float]
    final_status_code: int

    # Headers
    request_headers: dict[str, str]
    response_headers: dict[str, str]
    rate_limit_remaining: int | None
    rate_limit_reset: datetime | None
```

**Integration Point**: Wrap the HTTP transport in `openai._base_client` or instrument `httpx.Client`.

```python
import httpx

class InstrumentedTransport(httpx.HTTPTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        start = time.perf_counter()

        # Capture request details
        metrics = ProtocolMetrics(
            request_headers=dict(request.headers),
            # ... timing captured via extensions
        )

        response = super().handle_request(request)

        metrics.total_request_ms = (time.perf_counter() - start) * 1000
        metrics.response_headers = dict(response.headers)

        return response
```

**Governance Value**:
- Latency attribution (network vs model inference)
- Provider reliability monitoring
- Rate limit forecasting
- MITM detection via certificate validation

---

## Layer 2: Streaming Token Economics

**Source**: Stream iterator wrappers

Captures per-token timing for UX optimization and throughput analysis.

```python
@dataclass
class StreamingMetrics:
    # Critical UX Metrics
    time_to_first_token_ms: float          # TTFT - user-perceived latency
    time_to_last_token_ms: float           # Total stream duration

    # Token Timing Distribution
    inter_token_latencies_ms: list[float]  # Time between each token
    mean_inter_token_ms: float
    p50_inter_token_ms: float
    p95_inter_token_ms: float
    p99_inter_token_ms: float
    variance_inter_token_ms: float         # High variance = model "thinking"

    # Throughput
    tokens_per_second: float
    chunks_received: int
    chunk_sizes: list[int]                 # Tokens per chunk

    # Reliability
    stream_interruptions: int              # Partial failures
    stream_resumed: bool
    bytes_received: int

    # Content Accumulation
    partial_content_snapshots: list[str]   # Content at each chunk (optional)
    final_content: str
```

**Integration Point**: Enhance `MeteredAsyncStream` and `MeteredSyncStream` in instrumentation modules.

```python
class MeteredAsyncStream:
    async def __anext__(self):
        chunk_start = time.perf_counter()

        try:
            chunk = await self._iterator.__anext__()
        except StopAsyncIteration:
            self._finalize_metrics()
            raise

        chunk_latency = (time.perf_counter() - chunk_start) * 1000

        if self._first_token_time is None:
            self._first_token_time = chunk_latency
            self._metrics.time_to_first_token_ms = chunk_latency
        else:
            self._inter_token_latencies.append(chunk_latency)

        return chunk
```

**Governance Value**:
- TTFT optimization for user experience
- Detect model degradation via latency variance
- Capacity planning via throughput metrics
- Early termination decisions based on streaming patterns

---

## Layer 3: Model Behavioral Signals

**Source**: Response metadata and logprobs

Captures model confidence and decision signals for quality assessment.

```python
@dataclass
class ModelBehavior:
    # Termination
    stop_reason: str                       # "stop", "length", "tool_calls", "content_filter"
    stop_sequence: str | None              # Which stop sequence triggered
    truncated: bool                        # Hit max tokens

    # Confidence (requires logprobs=True)
    logprobs: list[float] | None           # Per-token log probabilities
    mean_logprob: float | None             # Average confidence
    min_logprob: float | None              # Lowest confidence token
    entropy: float | None                  # Overall uncertainty
    perplexity: float | None               # Exp of cross-entropy

    # Alternatives (requires top_logprobs)
    top_alternatives: list[list[TokenAlternative]] | None
    alternative_paths_explored: int

    # Safety Signals
    refusal_detected: bool                 # Model refused to respond
    refusal_reason: str | None
    content_filter_triggered: bool
    content_filter_categories: list[str]   # "hate", "violence", etc.

    # Model-Specific
    service_tier: str | None               # OpenAI service tier
    system_fingerprint: str | None         # Model version identifier


@dataclass
class TokenAlternative:
    token: str
    logprob: float
    bytes: list[int] | None
```

**Integration Point**: Extract from response objects in instrumentation wrappers.

```python
def _extract_behavior(response) -> ModelBehavior:
    choice = response.choices[0]

    behavior = ModelBehavior(
        stop_reason=choice.finish_reason,
        truncated=choice.finish_reason == "length",
        refusal_detected=_detect_refusal(choice.message.content),
    )

    if hasattr(choice, 'logprobs') and choice.logprobs:
        probs = [t.logprob for t in choice.logprobs.content]
        behavior.logprobs = probs
        behavior.mean_logprob = statistics.mean(probs)
        behavior.min_logprob = min(probs)
        behavior.entropy = -sum(p * math.exp(p) for p in probs)

    return behavior
```

**Governance Value**:
- Low confidence + high-risk action = escalate to Tier 2 judge
- Refusal detection for policy compliance
- Content filter monitoring for safety
- Model version tracking for reproducibility

---

## Layer 4: Semantic Fingerprinting

**Source**: Computed at capture time via lightweight models

Enables drift detection, clustering, and real-time risk scoring.

```python
@dataclass
class SemanticFingerprint:
    # Embeddings (for similarity/clustering)
    input_embedding: list[float] | None    # Embed the prompt
    output_embedding: list[float] | None   # Embed the response
    embedding_model: str                   # Model used for embedding

    # Classification
    intent_category: str                   # "query", "command", "creative", "code"
    intent_confidence: float
    topic_tags: list[str]                  # Auto-detected topics
    topic_confidences: list[float]

    # Language Analysis
    input_language: str                    # ISO 639-1 code
    output_language: str
    language_consistent: bool              # Same language in/out

    # Sentiment
    input_sentiment: float                 # -1 to 1
    output_sentiment: float
    sentiment_shift: float                 # Change in sentiment

    # Risk Scoring (Tier 0 Reflex)
    pii_detected: bool
    pii_types: list[str]                   # "email", "phone", "ssn", etc.
    pii_score: float                       # 0-1 probability

    injection_score: float                 # Prompt injection likelihood
    injection_patterns: list[str]          # Which patterns matched

    jailbreak_score: float                 # Jailbreak attempt likelihood
    jailbreak_techniques: list[str]        # "DAN", "roleplay", etc.

    # Quality Signals
    coherence_score: float                 # Does response make sense
    relevance_score: float                 # Does it answer the question
    factuality_signals: list[str]          # Hedging language, uncertainty markers


@dataclass
class SemanticAnalyzerConfig:
    embedding_model: str = "text-embedding-3-small"
    classifier_model: str = "distilbert-base-uncased"
    pii_detector: str = "presidio"
    injection_detector: str = "rebuff"
    batch_embeddings: bool = True
    cache_embeddings: bool = True
```

**Integration Point**: Post-processing pipeline after response capture.

```python
class SemanticAnalyzer:
    def analyze(self, input_text: str, output_text: str) -> SemanticFingerprint:
        fingerprint = SemanticFingerprint(
            embedding_model=self.config.embedding_model
        )

        # Parallel analysis
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._embed, input_text): "input_embedding",
                executor.submit(self._embed, output_text): "output_embedding",
                executor.submit(self._classify_intent, input_text): "intent",
                executor.submit(self._detect_pii, output_text): "pii",
                executor.submit(self._score_injection, input_text): "injection",
            }

            for future in as_completed(futures):
                field = futures[future]
                setattr(fingerprint, field, future.result())

        return fingerprint
```

**Governance Value**:
- Real-time Tier 0 filtering (< 10ms for pattern matching)
- Drift detection via embedding similarity over time
- PII masking before sending to external judges
- Injection attack detection before execution

---

## Layer 5: Context Window Forensics

**Source**: Request parameters analysis

Understand what information the model had access to when making decisions.

```python
@dataclass
class ContextAnalysis:
    # Utilization
    context_tokens_used: int
    context_max_tokens: int
    utilization_percent: float
    headroom_tokens: int                   # Remaining capacity

    # Composition by Role
    system_tokens: int
    user_tokens: int
    assistant_tokens: int
    tool_tokens: int                       # Tool call results

    # Message Analysis
    message_count: int
    system_message_count: int
    user_message_count: int
    assistant_message_count: int
    tool_message_count: int

    # Conversation Structure
    conversation_turns: int                # Back-and-forth exchanges
    avg_user_message_tokens: float
    avg_assistant_message_tokens: float

    # History Management
    history_truncated: bool
    messages_truncated: int
    truncation_strategy: str | None        # "sliding_window", "summarize", etc.

    # Multimodal
    images_count: int
    image_tokens: int
    image_detail_levels: list[str]         # "low", "high", "auto"
    files_count: int
    file_tokens: int

    # RAG Signals (if detectable)
    retrieved_context_detected: bool
    retrieved_chunks_estimate: int
    retrieval_tokens_estimate: int
    source_documents: list[str]            # Document identifiers if available


def _analyze_context(messages: list[dict], model: str) -> ContextAnalysis:
    """Analyze the context window composition."""

    analysis = ContextAnalysis(
        context_max_tokens=MODEL_CONTEXT_LIMITS.get(model, 128000),
        message_count=len(messages),
    )

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Estimate tokens (use tiktoken for accuracy)
        tokens = _estimate_tokens(content, model)

        if role == "system":
            analysis.system_tokens += tokens
            analysis.system_message_count += 1
        elif role == "user":
            analysis.user_tokens += tokens
            analysis.user_message_count += 1
            # Check for RAG patterns
            if _looks_like_retrieved_context(content):
                analysis.retrieved_context_detected = True
        elif role == "assistant":
            analysis.assistant_tokens += tokens
            analysis.assistant_message_count += 1
        elif role == "tool":
            analysis.tool_tokens += tokens
            analysis.tool_message_count += 1

    analysis.context_tokens_used = (
        analysis.system_tokens +
        analysis.user_tokens +
        analysis.assistant_tokens +
        analysis.tool_tokens
    )
    analysis.utilization_percent = (
        analysis.context_tokens_used / analysis.context_max_tokens * 100
    )

    return analysis
```

**Governance Value**:
- Understand what data the agent had when making decisions
- Detect context overflow before it causes issues
- Identify RAG retrieval for fact-checking
- Audit trail for compliance (what info was provided)

---

## Layer 6: Tool Call Deep Inspection

**Status**: ✅ **IMPLEMENTED** (v0.3.3)

**Source**: Request and response tool call data

Full visibility into function calling behavior.

### Usage

Enable tool call capture with the `capture_tool_calls` flag:

```python
from aden import instrument, MeterOptions

await instrument(MeterOptions(
    capture_tool_calls=True,
    validate_tool_schemas=True,  # Validate arguments against tool schemas
))
```

The `MetricEvent` will include:
- `tool_calls_captured`: List of `ToolCallCapture` objects with full details
- `tool_validation_errors_count`: Count of validation errors across all tool calls

Each `ToolCallCapture` contains:
- `id`: Tool call ID from the provider
- `name`: Function/tool name
- `arguments`: Parsed arguments dict (or ContentReference if large)
- `arguments_raw`: Raw JSON string of arguments
- `validation_errors`: List of schema validation errors
- `is_valid`: Whether arguments passed schema validation
- `index`: Position in the tool calls array

### Schema Validation

When `validate_tool_schemas=True`, tool arguments are validated against the schemas provided in the request. Validation checks:
- Required properties presence
- Type constraints (string, number, integer, boolean, array, object, null)
- Nested object validation
- Array item type validation

Validation errors are captured as `ToolCallValidationError` with:
- `path`: JSON path to the error (e.g., "user.email")
- `message`: Human-readable error description
- `expected_type`: What type was expected
- `actual_type`: What type was received

```python
@dataclass
class ToolInteraction:
    # Identity
    tool_call_id: str
    tool_name: str
    tool_index: int                        # Order in response

    # Arguments
    arguments_raw: str                     # Raw JSON string
    arguments_parsed: dict                 # Parsed arguments
    arguments_valid: bool                  # Schema validation result
    validation_errors: list[str]

    # Schema (if available)
    expected_schema: dict | None
    schema_version: str | None

    # Execution (if captured)
    executed: bool
    execution_start: datetime | None
    execution_end: datetime | None
    execution_duration_ms: float | None

    result: Any | None
    result_type: str | None
    result_tokens: int | None

    execution_error: str | None
    error_type: str | None

    # Sequence Analysis
    parallel_group_id: str | None          # Tools called in parallel
    depends_on: list[str]                  # Tool IDs this depends on
    depended_by: list[str]                 # Tool IDs depending on this


@dataclass
class ToolCallSequence:
    # Summary
    total_calls: int
    unique_tools: set[str]
    unique_tools_count: int

    # Execution Pattern
    parallel_groups: int                   # Number of parallel batches
    sequential_chains: int
    max_parallel_calls: int

    # Calls
    calls: list[ToolInteraction]

    # Dependency Graph
    call_graph: dict[str, list[str]]       # tool_id -> dependent_tool_ids
    execution_order: list[str]             # Actual execution sequence

    # Aggregates
    total_execution_time_ms: float
    total_result_tokens: int
    error_count: int
    validation_error_count: int


def _extract_tool_calls_deep(response, request_tools: list) -> ToolCallSequence:
    """Extract comprehensive tool call information."""

    schema_map = {t["function"]["name"]: t["function"] for t in request_tools}
    calls = []

    for idx, tc in enumerate(response.choices[0].message.tool_calls or []):
        interaction = ToolInteraction(
            tool_call_id=tc.id,
            tool_name=tc.function.name,
            tool_index=idx,
            arguments_raw=tc.function.arguments,
        )

        # Parse and validate
        try:
            interaction.arguments_parsed = json.loads(tc.function.arguments)
            interaction.arguments_valid = True

            # Validate against schema if available
            if tc.function.name in schema_map:
                schema = schema_map[tc.function.name].get("parameters", {})
                errors = _validate_json_schema(
                    interaction.arguments_parsed,
                    schema
                )
                if errors:
                    interaction.arguments_valid = False
                    interaction.validation_errors = errors

        except json.JSONDecodeError as e:
            interaction.arguments_valid = False
            interaction.validation_errors = [str(e)]

        calls.append(interaction)

    return ToolCallSequence(
        total_calls=len(calls),
        unique_tools={c.tool_name for c in calls},
        unique_tools_count=len({c.tool_name for c in calls}),
        calls=calls,
        # ... compute graph analysis
    )
```

**Governance Value**:
- Validate tool arguments against Ground Truth before execution
- Detect malformed or malicious tool calls
- Understand multi-tool workflows for debugging
- Audit trail for tool-based actions

---

## Layer 7: Python Runtime Context

**Source**: Python runtime introspection

Capture execution environment for debugging and resource monitoring.

```python
@dataclass
class RuntimeContext:
    # Process Identity
    process_id: int
    process_name: str
    parent_process_id: int

    # Threading
    thread_id: int
    thread_name: str
    active_threads: int

    # Async Context
    asyncio_task_name: str | None
    asyncio_task_id: int | None
    event_loop_running: bool
    pending_tasks: int

    # Timing
    wall_time_ms: float
    cpu_time_user_ms: float
    cpu_time_system_ms: float

    # Memory
    memory_before_mb: float
    memory_after_mb: float
    memory_delta_mb: float
    memory_peak_mb: float

    # GC
    gc_collections_gen0: int
    gc_collections_gen1: int
    gc_collections_gen2: int
    gc_objects_tracked: int

    # Concurrency
    concurrent_llm_requests: int           # Other LLM calls in flight
    request_queue_depth: int

    # SDK State
    sdk_name: str                          # "openai", "anthropic", etc.
    sdk_version: str
    python_version: str

    # Client Configuration
    client_timeout: float | None
    client_max_retries: int
    client_base_url: str


@contextmanager
def capture_runtime_context():
    """Context manager to capture runtime metrics."""

    import gc
    import psutil
    import threading
    import asyncio

    process = psutil.Process()

    # Before
    gc_before = gc.get_count()
    mem_before = process.memory_info().rss / 1024 / 1024
    cpu_before = process.cpu_times()
    start_time = time.perf_counter()

    context = RuntimeContext(
        process_id=os.getpid(),
        thread_id=threading.current_thread().ident,
        thread_name=threading.current_thread().name,
        active_threads=threading.active_count(),
        memory_before_mb=mem_before,
        python_version=sys.version,
    )

    # Async context
    try:
        loop = asyncio.get_running_loop()
        context.event_loop_running = loop.is_running()
        context.pending_tasks = len(asyncio.all_tasks(loop))

        task = asyncio.current_task()
        if task:
            context.asyncio_task_name = task.get_name()
    except RuntimeError:
        context.event_loop_running = False

    yield context

    # After
    gc_after = gc.get_count()
    mem_after = process.memory_info().rss / 1024 / 1024
    cpu_after = process.cpu_times()

    context.wall_time_ms = (time.perf_counter() - start_time) * 1000
    context.cpu_time_user_ms = (cpu_after.user - cpu_before.user) * 1000
    context.cpu_time_system_ms = (cpu_after.system - cpu_before.system) * 1000
    context.memory_after_mb = mem_after
    context.memory_delta_mb = mem_after - mem_before
    context.gc_collections_gen0 = gc_after[0] - gc_before[0]
    context.gc_collections_gen1 = gc_after[1] - gc_before[1]
    context.gc_collections_gen2 = gc_after[2] - gc_before[2]
```

**Governance Value**:
- Identify memory leaks in long-running agents
- Debug async deadlocks via task introspection
- Capacity planning via resource utilization
- Performance optimization via CPU/wall time analysis

---

## Layer 8: Framework Interception

**Source**: Agent framework callback systems

Capture framework-specific events for multi-framework observability.

### LangChain Integration

```python
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult, AgentAction, AgentFinish

class QueenCallbackHandler(BaseCallbackHandler):
    """Deep instrumentation for LangChain."""

    def __init__(self, emitter: Callable):
        self.emitter = emitter
        self.run_stack: list[RunContext] = []

    # Chain Events
    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs):
        """Capture chain structure and inputs."""
        self.emitter(ChainStartEvent(
            chain_type=serialized.get("_type"),
            chain_name=serialized.get("name"),
            inputs=inputs,
            run_id=kwargs.get("run_id"),
        ))

    def on_chain_end(self, outputs: dict, **kwargs):
        """Capture chain outputs."""
        self.emitter(ChainEndEvent(
            outputs=outputs,
            run_id=kwargs.get("run_id"),
        ))

    # LLM Events
    def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs):
        """Capture prompts AFTER template rendering."""
        self.emitter(LLMStartEvent(
            model_name=serialized.get("model_name"),
            prompts=prompts,  # Actual prompts sent to LLM
            invocation_params=kwargs.get("invocation_params"),
        ))

    def on_llm_end(self, response: LLMResult, **kwargs):
        """Capture full LLM response."""
        self.emitter(LLMEndEvent(
            generations=response.generations,
            llm_output=response.llm_output,
        ))

    # Tool Events
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Capture tool invocations."""
        self.emitter(ToolStartEvent(
            tool_name=serialized.get("name"),
            tool_input=input_str,
        ))

    def on_tool_end(self, output: str, **kwargs):
        """Capture tool results."""
        self.emitter(ToolEndEvent(
            tool_output=output,
        ))

    # Retrieval Events
    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        """Capture RAG queries."""
        self.emitter(RetrieverStartEvent(
            retriever_type=serialized.get("_type"),
            query=query,
        ))

    def on_retriever_end(self, documents: list, **kwargs):
        """Capture retrieved documents."""
        self.emitter(RetrieverEndEvent(
            documents=[{
                "content": doc.page_content[:500],
                "metadata": doc.metadata,
                "score": getattr(doc, "score", None),
            } for doc in documents],
            document_count=len(documents),
        ))

    # Agent Events
    def on_agent_action(self, action: AgentAction, **kwargs):
        """Capture agent reasoning."""
        self.emitter(AgentActionEvent(
            tool=action.tool,
            tool_input=action.tool_input,
            reasoning=action.log,  # Agent's reasoning trace
        ))

    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Capture agent completion."""
        self.emitter(AgentFinishEvent(
            output=finish.return_values,
            reasoning=finish.log,
        ))
```

### PydanticAI Integration

```python
from pydantic_ai import Agent
from pydantic_ai.result import RunResult

def instrument_pydantic_ai():
    """Patch PydanticAI for deep instrumentation."""

    original_run = Agent.run
    original_run_sync = Agent.run_sync

    async def instrumented_run(self, *args, **kwargs):
        context = AgentRunContext(
            agent_name=self.name,
            model=str(self.model),
            system_prompt=self.system_prompt,
        )

        result = await original_run(self, *args, **kwargs)

        # Capture structured output validation
        context.output_type = self.result_type.__name__
        context.validation_passed = True  # Would have raised otherwise
        context.retries = result._retries if hasattr(result, '_retries') else 0

        emit(context)
        return result

    Agent.run = instrumented_run
```

### CrewAI Integration

```python
from crewai import Crew, Agent, Task

def instrument_crewai():
    """Deep instrumentation for CrewAI."""

    original_kickoff = Crew.kickoff

    def instrumented_kickoff(self, *args, **kwargs):
        crew_context = CrewExecutionContext(
            crew_name=getattr(self, 'name', 'unnamed'),
            agents=[{
                'name': a.name,
                'role': a.role,
                'goal': a.goal,
                'tools': [t.name for t in a.tools],
            } for a in self.agents],
            tasks=[{
                'description': t.description,
                'agent': t.agent.name if t.agent else None,
            } for t in self.tasks],
        )

        emit(CrewStartEvent(crew_context))

        result = original_kickoff(self, *args, **kwargs)

        emit(CrewEndEvent(
            crew_name=crew_context.crew_name,
            result=result,
        ))

        return result

    Crew.kickoff = instrumented_kickoff
```

**Governance Value**:
- Framework-agnostic observability
- RAG retrieval auditing (what docs influenced the response)
- Agent reasoning traces for debugging
- Multi-step workflow visualization

---

## Layer 9: Conversation State Machine

**Source**: Session-level aggregation

Track conversation dynamics over multiple turns.

```python
@dataclass
class ConversationState:
    # Identity
    session_id: str
    conversation_id: str

    # Progress
    turn_number: int
    total_tokens_spent: int
    total_latency_ms: float

    # Intent Tracking
    initial_intent: str
    initial_intent_embedding: list[float]
    current_context_embedding: list[float]
    intent_drift_score: float              # Cosine distance from initial
    intent_drift_threshold_exceeded: bool

    # Topic Analysis
    topics_discussed: list[TopicSegment]
    current_topic: str
    topic_transitions: int

    # Goal Progress
    goal_statements: list[str]             # Extracted goals
    goals_completed: list[str]
    goals_pending: list[str]
    estimated_completion: float            # 0-1

    # Quality Signals
    user_corrections: int                  # Times user corrected model
    user_repetitions: int                  # Times user repeated themselves
    model_contradictions: int              # Model contradicted itself
    clarification_requests: int            # Model asked for clarification

    # Efficiency
    tokens_per_goal: dict[str, int]
    turns_per_goal: dict[str, int]

    # Sentiment Arc
    sentiment_history: list[float]         # Per-turn sentiment
    sentiment_trend: str                   # "improving", "declining", "stable"
    frustration_score: float               # Detected user frustration


@dataclass
class TopicSegment:
    topic: str
    start_turn: int
    end_turn: int | None
    tokens_spent: int
    resolved: bool


class ConversationTracker:
    """Track conversation state across turns."""

    def __init__(self, session_id: str, embedder: Callable):
        self.state = ConversationState(
            session_id=session_id,
            turn_number=0,
        )
        self.embedder = embedder

    def on_turn(self, user_message: str, assistant_message: str):
        self.state.turn_number += 1

        # First turn: capture initial intent
        if self.state.turn_number == 1:
            self.state.initial_intent = user_message
            self.state.initial_intent_embedding = self.embedder(user_message)

        # Track drift
        current_context = f"{user_message}\n{assistant_message}"
        self.state.current_context_embedding = self.embedder(current_context)
        self.state.intent_drift_score = 1 - cosine_similarity(
            self.state.initial_intent_embedding,
            self.state.current_context_embedding
        )

        # Detect patterns
        self._detect_corrections(user_message)
        self._detect_repetitions(user_message)
        self._detect_frustration(user_message)
        self._update_sentiment(user_message, assistant_message)

        return self.state

    def _detect_frustration(self, message: str):
        """Detect signs of user frustration."""
        frustration_signals = [
            r"i (already|just) (said|told|asked)",
            r"no,?\s+(that's not|i meant|i said)",
            r"why (won't|can't|don't) you",
            r"this is (frustrating|annoying|ridiculous)",
        ]
        # ... pattern matching
```

**Governance Value**:
- Detect semantic drift from original user intent
- Identify failing conversations early
- Measure agent effectiveness across sessions
- Trigger human escalation on frustration detection

---

## Layer 10: Structured Output Validation

**Source**: Response parsing and schema validation

Track structured output quality and repair attempts.

```python
@dataclass
class StructuredOutputMetrics:
    # Request
    output_format_requested: str           # "json", "json_object", "json_schema"
    schema_provided: dict | None
    schema_name: str | None
    strict_mode: bool

    # Response Parsing
    raw_output: str
    parse_attempted: bool
    parse_successful: bool
    parse_error: str | None

    # Validation
    validation_attempted: bool
    validation_passed: bool
    validation_errors: list[ValidationError]

    # Repair
    repair_attempted: bool
    repair_successful: bool
    repair_strategy: str | None            # "llm_retry", "regex_fix", "default_fill"
    repair_changes: list[str]

    # Retries
    format_retry_count: int
    tokens_spent_on_retries: int

    # Final Output
    final_output: dict | None
    output_type: str                       # Python type name

    # Quality
    schema_coverage: float                 # % of schema fields populated
    null_fields: list[str]
    default_fields: list[str]


@dataclass
class ValidationError:
    path: str                              # JSON path to error
    error_type: str                        # "type", "required", "format", etc.
    message: str
    expected: Any
    actual: Any


def _validate_structured_output(
    response: str,
    schema: dict,
    repair: bool = True
) -> StructuredOutputMetrics:
    """Comprehensive structured output validation."""

    metrics = StructuredOutputMetrics(
        raw_output=response,
        schema_provided=schema,
    )

    # Parse JSON
    metrics.parse_attempted = True
    try:
        parsed = json.loads(response)
        metrics.parse_successful = True
    except json.JSONDecodeError as e:
        metrics.parse_successful = False
        metrics.parse_error = str(e)

        if repair:
            metrics.repair_attempted = True
            parsed = _attempt_json_repair(response)
            if parsed:
                metrics.repair_successful = True
                metrics.repair_strategy = "regex_fix"
            else:
                return metrics
        else:
            return metrics

    # Validate against schema
    metrics.validation_attempted = True
    errors = _json_schema_validate(parsed, schema)

    if errors:
        metrics.validation_passed = False
        metrics.validation_errors = [
            ValidationError(
                path=e.path,
                error_type=e.validator,
                message=e.message,
                expected=e.schema.get(e.validator),
                actual=e.instance,
            ) for e in errors
        ]
    else:
        metrics.validation_passed = True
        metrics.final_output = parsed

    # Calculate coverage
    required_fields = schema.get("required", [])
    all_fields = list(schema.get("properties", {}).keys())
    populated = [f for f in all_fields if f in parsed and parsed[f] is not None]
    metrics.schema_coverage = len(populated) / len(all_fields) if all_fields else 1.0
    metrics.null_fields = [f for f in all_fields if f in parsed and parsed[f] is None]

    return metrics
```

**Governance Value**:
- Track structured output reliability per model
- Identify schemas that cause frequent failures
- Monitor token waste from retries
- Quality metrics for downstream data pipelines

---

## Implementation Architecture

### Configuration

```python
from enum import Flag, auto

class CaptureLevel(Flag):
    """Bitwise flags for capture levels."""
    METRICS_ONLY = 0
    PROTOCOL = auto()        # Layer 1
    STREAMING = auto()       # Layer 2
    BEHAVIOR = auto()        # Layer 3
    SEMANTIC = auto()        # Layer 4
    CONTEXT = auto()         # Layer 5
    TOOLS = auto()           # Layer 6
    RUNTIME = auto()         # Layer 7
    FRAMEWORK = auto()       # Layer 8
    CONVERSATION = auto()    # Layer 9
    STRUCTURED = auto()      # Layer 10

    STANDARD = METRICS_ONLY | STREAMING | BEHAVIOR | TOOLS
    GOVERNANCE = STANDARD | SEMANTIC | CONTEXT | CONVERSATION
    FULL = ~0  # All layers


@dataclass
class MeterOptions:
    # Existing
    emit_metric: MetricEmitter | None = None
    before_request: BeforeRequestHook | None = None

    # Capture configuration
    capture_level: CaptureLevel = CaptureLevel.METRICS_ONLY

    # Layer-specific emitters (optional, defaults to emit_metric)
    streaming_emitter: StreamingEmitter | None = None
    behavior_emitter: BehaviorEmitter | None = None
    semantic_emitter: SemanticEmitter | None = None
    tool_emitter: ToolEmitter | None = None

    # Analyzers
    semantic_analyzer: SemanticAnalyzer | None = None
    conversation_tracker: ConversationTracker | None = None

    # Privacy
    redact_content: bool = True
    redact_pii: bool = True
    content_hash_only: bool = False  # Only emit hashes, not content
```

### Event Hierarchy

```python
@dataclass
class BaseEvent:
    """Base class for all telemetry events."""
    trace_id: str
    span_id: str
    timestamp: datetime

@dataclass
class MetricEvent(BaseEvent):
    """Layer 0: Core metrics (existing)."""
    # ... existing fields

@dataclass
class ProtocolEvent(BaseEvent):
    """Layer 1: Network/protocol data."""
    metrics: ProtocolMetrics

@dataclass
class StreamingEvent(BaseEvent):
    """Layer 2: Streaming metrics."""
    metrics: StreamingMetrics

@dataclass
class BehaviorEvent(BaseEvent):
    """Layer 3: Model behavior signals."""
    behavior: ModelBehavior

@dataclass
class SemanticEvent(BaseEvent):
    """Layer 4: Semantic analysis."""
    fingerprint: SemanticFingerprint

@dataclass
class ContextEvent(BaseEvent):
    """Layer 5: Context window analysis."""
    analysis: ContextAnalysis

@dataclass
class ToolEvent(BaseEvent):
    """Layer 6: Tool call details."""
    sequence: ToolCallSequence

@dataclass
class RuntimeEvent(BaseEvent):
    """Layer 7: Runtime context."""
    context: RuntimeContext

@dataclass
class FrameworkEvent(BaseEvent):
    """Layer 8: Framework-specific events."""
    framework: str
    event_type: str
    data: dict

@dataclass
class ConversationEvent(BaseEvent):
    """Layer 9: Conversation state."""
    state: ConversationState

@dataclass
class StructuredOutputEvent(BaseEvent):
    """Layer 10: Structured output validation."""
    metrics: StructuredOutputMetrics
```

---

## IMJDF Protocol Mapping

How these layers map to the Queen governance architecture:

| IMJDF Phase | Primary Layers | Use Case |
|-------------|---------------|----------|
| **INTENT** | Layer 4 (Semantic), Layer 5 (Context) | Capture and embed user intent for drift detection |
| **METRIC** | Layer 1-3, Layer 6-7 | Full telemetry stream from workers |
| **JUDGMENT** | Layer 4 (Semantic) | Risk scores, PII detection, injection detection for Tier 0 |
| **DECISION** | Layer 6 (Tools), Layer 10 (Structured) | Validate tool calls and outputs before execution |
| **FEEDBACK** | Layer 9 (Conversation), Layer 3 (Behavior) | Track outcomes, drift, and quality over time |

### Example: Queen Governance Pipeline

```python
async def govern_worker_action(event: MetricEvent, layers: dict):
    """Queen governance using deep telemetry."""

    # Tier 0: Reflex (< 10ms)
    semantic = layers.get('semantic')
    if semantic:
        if semantic.injection_score > 0.8:
            return Decision.BLOCK("Prompt injection detected")
        if semantic.pii_score > 0.9:
            return Decision.ALERT("PII detected in output")

    # Tier 1: Clerk (< 200ms)
    behavior = layers.get('behavior')
    if behavior:
        if behavior.refusal_detected:
            return Decision.ESCALATE("Model refused - needs review")
        if behavior.mean_logprob and behavior.mean_logprob < -2.0:
            return Decision.ESCALATE("Low confidence response")

    # Tier 1: Tool validation
    tools = layers.get('tools')
    if tools:
        for call in tools.calls:
            if not call.arguments_valid:
                return Decision.BLOCK(f"Invalid tool args: {call.validation_errors}")

    # Tier 2: Magistrate (complex checks)
    conversation = layers.get('conversation')
    if conversation and conversation.intent_drift_score > 0.7:
        # Escalate to LLM judge
        return await tier2_judge.evaluate(event, layers)

    return Decision.ALLOW()
```

---

## Privacy and Security Considerations

### Content Redaction

```python
@dataclass
class RedactionConfig:
    redact_messages: bool = True
    redact_tool_args: bool = True
    redact_tool_results: bool = True

    # Strategies
    strategy: str = "hash"  # "hash", "mask", "remove"
    hash_algorithm: str = "sha256"
    mask_char: str = "*"

    # Selective
    preserve_structure: bool = True  # Keep JSON keys, redact values
    preserve_types: bool = True      # Keep type info

    # PII-specific
    pii_patterns: list[str] = field(default_factory=list)
    pii_replacement: str = "[REDACTED]"
```

### Data Retention

```python
@dataclass
class RetentionPolicy:
    # By layer
    metrics_retention_days: int = 90
    content_retention_days: int = 7       # Shorter for privacy
    semantic_retention_days: int = 30

    # By sensitivity
    pii_retention_days: int = 1
    error_retention_days: int = 30

    # Sampling
    content_sample_rate: float = 0.1      # Only capture 10% of content
    full_capture_on_error: bool = True    # Always capture on errors
```

---

## Implementation Status

| Layer | Name | Status | Version |
|-------|------|--------|---------|
| **0** | Raw Content Capture | ✅ Implemented | v0.3.3 |
| **1** | Raw Protocol Data | ⏳ Planned | - |
| **2** | Streaming Token Economics | ⏳ Planned | - |
| **3** | Model Behavioral Signals | ⏳ Planned | - |
| **4** | Semantic Fingerprinting | ⏳ Planned | - |
| **5** | Context Window Forensics | ⏳ Planned | - |
| **6** | Tool Call Deep Inspection | ✅ Implemented | v0.3.3 |
| **7** | Python Runtime Context | ⏳ Planned | - |
| **8** | Framework Interception | ⏳ Planned | - |
| **9** | Conversation State Machine | ⏳ Planned | - |
| **10** | Structured Output Validation | ⏳ Planned | - |

## Next Steps

1. ~~**Phase 1**: Implement Layers 0 and 6 (Content, Tools) - foundation for governance~~ ✅ **Done in v0.3.3**
2. **Phase 2**: Implement Layers 2-3 (Streaming, Behavior) - highest value, lowest complexity
3. **Phase 3**: Implement Layer 5 (Context) - context window analysis
4. **Phase 4**: Implement Layer 4 (Semantic) - requires external dependencies
5. **Phase 5**: Implement Layers 8-9 (Framework, Conversation) - framework-specific work
6. **Phase 6**: Implement Layers 1, 7, 10 - infrastructure and edge cases
