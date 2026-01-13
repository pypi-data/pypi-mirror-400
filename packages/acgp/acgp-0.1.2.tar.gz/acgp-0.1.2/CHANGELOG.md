# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-04

### Changed

- **Package Renamed**: Renamed from `cgp-sdk` to `acgp` (Agentic Cognitive Governance Protocol)
  - Package import changed from `cgp_sdk` to `acgp`
  - `CGPClient` renamed to `ACGPClient`
  - `CGPConfig` renamed to `ACGPConfig`
  - `@cgp_trace` decorator renamed to `@acgp_trace`
  - Environment variables prefix changed from `CGP_` to `ACGP_`

### Added

- **Real-time SSE Feedback**: Stream feedback from Steward Agent backend via Server-Sent Events
  - `on_feedback` callback parameter for real-time feedback handling
  - `SSEConfig` class for customizing SSE behavior
  - Auto-reconnection with exponential backoff
  - Background thread processing

- **Core Tracing API**:
  - `ACGPClient` - Main client class for agent oversight integration
  - `trace()` context manager for wrapping agent execution
  - `capture_trace()` for manual trace submission
  - `TraceContext` with `set_output()`, `set_reasoning()`, `add_context()`, `set_documents()`

- **Batch Processing**:
  - Automatic batching with configurable `batch_size` and `flush_interval`
  - Background flush thread for non-blocking trace submission
  - `flush()` method for immediate trace submission
  - `on_flush_complete` callback for batch results

- **Feedback Retrieval**:
  - `wait_for_feedback()` with auto-flush and configurable timeout
  - `get_score()` for CTQ score retrieval with retry
  - `get_feedback()` for oversight feedback retrieval
  - `get_metrics()` for SDK statistics

- **Configuration**:
  - Environment variable support (`ACGP_API_KEY`, `ACGP_ENDPOINT`, etc.)
  - `.env` file auto-loading via python-dotenv
  - `enabled` flag for disabling SDK in specific environments
  - `fail_silently` mode for production resilience
  - `debug` mode for troubleshooting

- **Decorator Support**:
  - `@acgp_trace` decorator for function-based agents

- **Documentation**:
  - Comprehensive README with quick start and examples
  - API reference documentation
  - Framework integration guides (CrewAI, LangChain, AutoGen, GPT-Researcher)
  - Configuration guide
  - Best practices
  - Troubleshooting guide

### Framework Integrations

- CrewAI integration example
- LangChain / LangGraph integration example
- AutoGen integration example
- GPT-Researcher integration example
- OpenAI Assistants API integration example
- Custom agent integration patterns

## [Unreleased]

### Planned

- Async/await support for async agent frameworks
- OpenTelemetry integration for distributed tracing
- Prometheus metrics export
- Rate limiting and circuit breaker patterns
- Multi-tenant support improvements
